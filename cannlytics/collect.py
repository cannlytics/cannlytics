"""
Collect | Cannlytics
Copyright (c) 2024-2026 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
Created: 2/1/2026
Updated: 9/26/2026
License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description:
    The infrastructure every data collector shares: an HTTP session that
    retries politely, a document fetcher that throttles and caches, and
    the ``COACollector`` base class that the laboratory-result
    collectors subclass. Before 1.0.4 the base class lived in
    ``cannabis_results/results_base.py`` (31 collectors import it) and
    the session in ``cannabis_licenses/algorithms/polite_session.py``.

    What changed in the move, all of it covered by tests:

    - URLs are keyed by SHA-256 (``cannlytics.utils.hashing``), the key
      the cache's own ``hash_url`` already used. Collectors had also
      keyed by MD5 and by the first 12 characters of the SHA-256.
      Entries under either old key are still found, and
      ``migrate_legacy_keys`` re-keys them.
    - Downloads are written to a temporary file and moved into place,
      so an interrupted download never leaves a truncated file under
      the final name.
    - A download bound for a ``.pdf`` is checked with ``is_valid_pdf``
      before it is kept: an HTML error page served with status 200 is
      rejected instead of being saved, cached, and parsed later.
    - The file's SHA-256 is recorded in the cache entry, which links
      the source URL to the ``pdf_hash`` of every downloaded COA.
    - One retry policy, in the session (429 and 5xx with exponential
      backoff and ``Retry-After``). The base class also looped, so a
      failure cost up to nine attempts, and it retried 404s.
    - No file is written unless asked: file logging needs ``log_dir``.

        from cannlytics.collect import COACollector

        class MyLabCollector(COACollector):
            def get_results(self, **kwargs):
                for url in self.list_coa_urls():
                    self.download_file(url, self.pdf_dir / url.split('/')[-1])
                    self.rate_limit()
                ...

    Selenium is imported only when a browser is started (the ``web``
    extra).
"""
# Standard imports:
from __future__ import annotations

import logging
import os
import random
import tempfile
import time
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, Iterable, Optional, Union

# External imports:
import pandas as pd
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Internal imports:
from cannlytics.data.cache import Bogart
from cannlytics.data.coas.pdf_utils import is_valid_pdf
from cannlytics.utils.hashing import hash_file, hash_text

PathLike = Union[str, 'os.PathLike[str]']

# Statuses worth retrying: rate limiting and transient server errors.
# A 4xx other than 429 is an answer, not a failure, and is not retried.
RETRY_STATUSES = (429, 500, 502, 503, 504)

# A browser User-Agent: several state portals refuse the `requests` one.
DEFAULT_USER_AGENT = (
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
    '(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
)

# ╔══════════════════════════════════════════════════════════════════╗
# ║ One retry policy                                                 ║
# ╚══════════════════════════════════════════════════════════════════╝

def retrying_session(
        retries: int = 3,
        backoff: float = 1.0,
        user_agent: Optional[str] = None,
        pool_size: int = 10,
    ) -> requests.Session:
    """Create a ``requests`` session that retries politely.

    Connection errors and the statuses in ``RETRY_STATUSES`` are retried
    up to ``retries`` times with exponential backoff
    (``backoff * 2 ** (attempt - 1)`` seconds), honouring a server's
    ``Retry-After``. After the last attempt the final response is
    returned rather than raised, so the caller sees the real status.

    Args:
        retries: Retry attempts after the first request.
        backoff: The backoff factor, in seconds.
        user_agent: The User-Agent header; ``None`` keeps the default.
        pool_size: Connections kept open per host.

    Returns:
        The configured session. Close it (or use it as a context
        manager) when done.
    """
    session = requests.Session()
    retry = Retry(
        total=retries,
        connect=retries,
        read=retries,
        status=retries,
        status_forcelist=RETRY_STATUSES,
        allowed_methods=frozenset({'GET', 'HEAD', 'OPTIONS'}),
        backoff_factor=backoff,
        respect_retry_after_header=True,
        raise_on_status=False,
    )
    adapter = HTTPAdapter(max_retries=retry, pool_connections=pool_size, pool_maxsize=pool_size)
    session.mount('https://', adapter)
    session.mount('http://', adapter)
    if user_agent:
        session.headers.update({'User-Agent': user_agent})
    return session

def _retries_taken(response: requests.Response) -> int:
    """How many retries the adapter spent on a response (best effort)."""
    retries = getattr(getattr(response, 'raw', None), 'retries', None)
    history = getattr(retries, 'history', None)
    return len(history) if isinstance(history, tuple) else 0

def _atomic_path(destination: Path) -> str:
    """A temporary file beside ``destination``, for an atomic replace."""
    destination.parent.mkdir(parents=True, exist_ok=True)
    handle, path = tempfile.mkstemp(dir=destination.parent, prefix=f'.{destination.name}.', suffix='.part')
    os.close(handle)
    return path

# ╔══════════════════════════════════════════════════════════════════╗
# ║ Polite session                                                   ║
# ╚══════════════════════════════════════════════════════════════════╝

class PoliteSession:
    """A throttled, retrying, caching session for fetching documents.

    Made for collectors that fetch many documents from one agency: every
    request waits at least ``delay`` seconds after the last, retryable
    failures back off, and each document is cached on disk for
    ``cache_ttl_days`` so that a monthly run does not fetch unchanged
    documents again. (Motivated by Rhode Island, where eighteen
    unthrottled consecutive requests came back 429 on 2026-09-01.)

        with PoliteSession(cache_dir='.cache/ri-forms') as session:
            content = session.get_bytes('https://ccc.ri.gov/media/1466/download')
            print(session.report())
    """

    def __init__(
            self,
            cache_dir: Optional[PathLike] = None,
            delay: float = 1.0,
            retries: int = 4,
            backoff: float = 1.5,
            cache_ttl_days: float = 180,
            user_agent: Optional[str] = DEFAULT_USER_AGENT,
            timeout: float = 30,
            logger: Optional[logging.Logger] = None,
        ):
        """Create the session.

        Args:
            cache_dir: Directory of the on-disk cache; ``None`` disables
                caching.
            delay: Minimum seconds between two requests.
            retries: Retry attempts for connection errors and retryable
                statuses.
            backoff: Backoff factor, in seconds.
            cache_ttl_days: How long a cached document stays current.
            user_agent: The User-Agent header.
            timeout: Seconds to wait for a response.
            logger: Where to log; defaults to this module's logger.
        """
        self.cache_dir = os.fspath(cache_dir) if cache_dir else None
        self.delay = delay
        self.cache_ttl = timedelta(days=cache_ttl_days)
        self.timeout = timeout
        self.logger = logger or logging.getLogger(__name__)
        self.session = retrying_session(retries, backoff, user_agent, pool_size=4)
        self.stats: Dict[str, Any] = {'cache_hits': 0, 'fetched': 0, 'failed': 0, 'failed_statuses': []}
        self._last_request = float('-inf')
        if self.cache_dir:
            os.makedirs(self.cache_dir, exist_ok=True)

    # --- Cache -------------------------------------------------------------

    def _cache_path(self, url: str) -> Optional[str]:
        """The cache file of a URL: its SHA-256, in full."""
        if not self.cache_dir:
            return None
        return os.path.join(self.cache_dir, f'{hash_text(url)}.bin')

    def _legacy_cache_path(self, url: str) -> Optional[str]:
        """The file name the first version used: the digest's first 32 characters."""
        if not self.cache_dir:
            return None
        return os.path.join(self.cache_dir, f'{hash_text(url)[:32]}.bin')

    def _read_cache(self, url: str) -> Optional[bytes]:
        """Cached bytes of a URL, if present and current."""
        for path in (self._cache_path(url), self._legacy_cache_path(url)):
            if not path or not os.path.exists(path):
                continue
            age = datetime.now() - datetime.fromtimestamp(os.path.getmtime(path))
            if age > self.cache_ttl:
                return None
            try:
                with open(path, 'rb') as file:
                    return file.read()
            except OSError:
                return None
        return None

    def _write_cache(self, url: str, content: bytes) -> None:
        """Store bytes atomically; a failed cache write is not an error."""
        path = self._cache_path(url)
        if not path:
            return
        temporary = None
        try:
            temporary = _atomic_path(Path(path))
            with open(temporary, 'wb') as file:
                file.write(content)
            os.replace(temporary, path)
        except OSError as error:
            self.logger.debug('Cache write failed for %s: %s', url, error)
        finally:
            if temporary and os.path.exists(temporary):
                os.remove(temporary)

    # --- Fetching ----------------------------------------------------------

    def _throttle(self) -> None:
        """Wait until at least ``delay`` seconds have passed since the last request."""
        wait = self.delay - (time.monotonic() - self._last_request)
        if wait > 0:
            time.sleep(wait)
        self._last_request = time.monotonic()

    def get(self, url: str, **kwargs) -> requests.Response:
        """A throttled, retrying ``GET`` without the document cache.

        For pages that change, such as listings. The caller owns the
        response.
        """
        self._throttle()
        kwargs.setdefault('timeout', self.timeout)
        return self.session.get(url, **kwargs)

    def get_bytes(self, url: str, use_cache: bool = True, verbose: bool = False) -> Optional[bytes]:
        """Fetch a document, from the cache when possible.

        Args:
            url: The document's address.
            use_cache: Read from and write to the cache.
            verbose: Log each request at INFO rather than DEBUG.

        Returns:
            The document's bytes, or ``None`` if it could not be fetched.
        """
        level = logging.INFO if verbose else logging.DEBUG
        if use_cache:
            cached = self._read_cache(url)
            if cached is not None:
                self.stats['cache_hits'] += 1
                self.logger.log(level, 'Cache hit: %s', url)
                return cached
        try:
            response = self.get(url)
        except requests.RequestException as error:
            self.stats['failed'] += 1
            self.logger.warning('Fetch failed: %s: %s', url, error)
            return None
        if not response.ok:
            self.stats['failed'] += 1
            self.stats['failed_statuses'].append(response.status_code)
            self.logger.warning('HTTP %s after retries: %s', response.status_code, url)
            return None
        self.stats['fetched'] += 1
        self.logger.log(level, 'Fetched: %s', url)
        if use_cache:
            self._write_cache(url, response.content)
        return response.content

    def report(self) -> str:
        """Summarize the session's activity, log it, and return it.

        A rising failure count, or 429s among the failures, is the early
        sign that an agency has tightened its limits.
        """
        stats = self.stats
        attempted = stats['cache_hits'] + stats['fetched'] + stats['failed']
        summary = (f"HTTP: {stats['fetched']} fetched, {stats['cache_hits']} from cache, "
                   f"{stats['failed']} failed (of {attempted} attempted)")
        if stats['failed_statuses']:
            counts: Dict[int, int] = {}
            for status in stats['failed_statuses']:
                counts[status] = counts.get(status, 0) + 1
            summary += f'; failing statuses {counts}'
            if 429 in counts:
                summary += ': rate limited after retries, so increase `delay` or reduce the batch'
        self.logger.info(summary)
        return summary

    def close(self) -> None:
        """Close the underlying session."""
        self.session.close()

    def __enter__(self) -> 'PoliteSession':
        return self

    def __exit__(self, *exc) -> None:
        self.close()

# ╔══════════════════════════════════════════════════════════════════╗
# ║ COA collector                                                    ║
# ╚══════════════════════════════════════════════════════════════════╝

class COACollector(ABC):
    """Base class for collectors of certificates of analysis.

    A subclass implements ``get_results`` and uses the helpers here:
    ``download_file`` (cached, atomic, validated), ``rate_limit``,
    ``init_selenium`` and ``wait_for_element`` for pages that need a
    browser, and ``save_results``. Use a collector as a context manager
    so that the browser, the HTTP session, and the log file are released.
    """

    def __init__(
            self,
            state: str,
            source: str,
            data_dir: Optional[PathLike] = None,
            pdf_dir: Optional[PathLike] = None,
            cache_path: Optional[PathLike] = None,
            log_dir: Optional[PathLike] = None,
            log_name: Optional[str] = None,
            pause_time: Optional[float] = 3.33,
            max_retries: Optional[int] = 3,
            verbose: bool = True,
            timeout: float = 30,
            backoff: float = 1.0,
            user_agent: Optional[str] = DEFAULT_USER_AGENT,
        ):
        """Set up directories, logging, the cache, and the HTTP session.

        Args:
            state: Two-letter jurisdiction code (``'ca'``).
            source: The source's identifier (``'flower_company'``).
            data_dir: The state's data directory; ``./data/{state}``.
            pdf_dir: Where PDFs are saved; ``{data_dir}/pdfs/{source}``.
            cache_path: The download cache (JSONL);
                ``./.cache/results-{state}-{source}.jsonl``.
            log_dir: Write a log file here. No file is written without it.
            log_name: The logger's name; ``get_results_{state}_{source}``.
            pause_time: Base seconds between requests (``rate_limit``);
                ``None`` means the default, 3.33.
            max_retries: Retry attempts for retryable failures; ``None``
                means the default, 3.
            verbose: Log progress to the console at INFO (else WARNING).
            timeout: Seconds to wait for a response.
            backoff: Backoff factor, in seconds, between retries.
            user_agent: The User-Agent header.
        """
        self.state = state.lower()
        self.source = source
        self.verbose = verbose
        self.data_dir = Path(data_dir) if data_dir else Path('data') / self.state
        self.pdf_dir = Path(pdf_dir) if pdf_dir else self.data_dir / 'pdfs' / source
        self.datasets_dir = self.data_dir / 'datasets'
        self.cache_path = os.fspath(cache_path) if cache_path else os.path.join('.cache', f'results-{self.state}-{source}.jsonl')
        self.pause_time = 3.33 if pause_time is None else pause_time
        self.max_retries = 3 if max_retries is None else max_retries
        self.timeout = timeout
        for directory in (self.pdf_dir, self.datasets_dir):
            directory.mkdir(parents=True, exist_ok=True)
        self.log_name = log_name or f'get_results_{self.state}_{source}'
        self._handlers: list = []
        self.logger = self._setup_logging(Path(log_dir) if log_dir else None)
        self.cache = Bogart(self.cache_path)
        self.driver: Any = None
        self._session = retrying_session(self.max_retries, backoff, user_agent)
        self._stats: Dict[str, Any] = {
            'started_at': datetime.now(), 'downloads': 0, 'cached': 0,
            'errors': 0, 'retries': 0, 'rejected': 0,
        }

    @abstractmethod
    def get_results(self, **kwargs) -> pd.DataFrame:
        """Collect the source's results. Implemented by each collector."""

    # --- Logging -----------------------------------------------------------

    def _setup_logging(self, log_dir: Optional[Path]) -> logging.Logger:
        """A logger with a console handler and, given ``log_dir``, a file.

        The handlers are attached to this collector's own logger, which
        does not propagate to the root, so nothing is printed twice and
        the application's logging is untouched.
        """
        logger = logging.getLogger(self.log_name)
        logger.setLevel(logging.INFO)
        logger.propagate = False
        formatter = logging.Formatter('%(asctime)s | %(name)s | %(levelname)s | %(message)s', datefmt='%Y-%m-%dT%H:%M:%S')
        names = {handler.get_name() for handler in logger.handlers}
        console_name = f'{self.log_name}:console'
        if console_name not in names:
            console = logging.StreamHandler()
            console.set_name(console_name)
            console.setLevel(logging.INFO if self.verbose else logging.WARNING)
            console.setFormatter(formatter)
            logger.addHandler(console)
            self._handlers.append(console)
        if log_dir is not None:
            log_dir.mkdir(parents=True, exist_ok=True)
            stamp = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
            file_handler = logging.FileHandler(log_dir / f"{self.log_name.replace('_', '-')}-{stamp}.log", encoding='utf-8')
            file_handler.set_name(f'{self.log_name}:file')
            file_handler.setLevel(logging.INFO)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
            self._handlers.append(file_handler)
        return logger

    # --- Cache -------------------------------------------------------------

    @staticmethod
    def hash_url(url: str) -> str:
        """The cache key of a URL: its SHA-256."""
        return hash_text(url)

    # The name the collectors in cannabis_results call.
    _hash_url = hash_url

    @staticmethod
    def legacy_url_key(url: str) -> str:
        """The key the first version of this class used (MD5)."""
        return hash_text(url, algorithm='md5')

    @classmethod
    def legacy_url_keys(cls, url: str) -> tuple:
        """Every key collectors used before 1.0.4: MD5, and SHA-256 cut to 12 characters."""
        return cls.legacy_url_key(url), hash_text(url)[:12]

    def cached_entry(self, url: str) -> Optional[Dict[str, Any]]:
        """The cache entry of a URL, under its current or a legacy key."""
        for key in (self.hash_url(url), *self.legacy_url_keys(url)):
            entry = self.cache.get(key)
            if entry is not None:
                return entry
        return None

    def is_cached(self, url: str) -> bool:
        """Whether a URL has been downloaded before."""
        return bool(self.cached_entry(url))

    def migrate_legacy_keys(self) -> int:
        """Add a SHA-256 key for every entry stored under a legacy URL key.

        Entries record their URL, so the new key can be computed; the old
        entry is left in place. Run once per cache after upgrading.

        Returns:
            How many entries were re-keyed.
        """
        added = 0
        for key, value in list(self.cache.cache.items()):
            url = value.get('url') if isinstance(value, dict) else None
            if url and key in self.legacy_url_keys(url) and self.cache.get(self.hash_url(url)) is None:
                self.cache.set(self.hash_url(url), value)
                added += 1
        return added

    # --- HTTP --------------------------------------------------------------

    def download_file(
            self,
            url: str,
            destination: PathLike,
            headers: Optional[Dict[str, str]] = None,
            skip_cached: bool = True,
            require_pdf: Optional[bool] = None,
        ) -> bool:
        """Download a file, once.

        Args:
            url: The file's address.
            destination: Where to save it.
            headers: Extra request headers.
            skip_cached: Skip a URL already in the cache.
            require_pdf: Keep the file only if it is a valid PDF. Defaults
                to whether ``destination`` ends in ``.pdf``.

        Returns:
            ``True`` if the file is (or already was) downloaded.
        """
        if skip_cached and self.cached_entry(url):
            self.logger.info('Skipped (cached): %s', url)
            self._stats['cached'] += 1
            return True
        destination = Path(destination)
        if require_pdf is None:
            require_pdf = destination.suffix.lower() == '.pdf'
        temporary = None
        try:
            with self._session.get(url, headers=headers, timeout=self.timeout, stream=True) as response:
                self._stats['retries'] += _retries_taken(response)
                if not response.ok:
                    self.logger.error('HTTP %s: %s', response.status_code, url)
                    self._stats['errors'] += 1
                    return False
                temporary = _atomic_path(destination)
                with open(temporary, 'wb') as file:
                    for chunk in response.iter_content(chunk_size=65_536):
                        if chunk:
                            file.write(chunk)
            if require_pdf:
                valid, reason = is_valid_pdf(temporary)
                if not valid:
                    self.logger.error('Not a valid PDF (%s): %s', reason, url)
                    self._stats['rejected'] += 1
                    self._stats['errors'] += 1
                    return False
            digest, size = hash_file(temporary), os.path.getsize(temporary)
            os.replace(temporary, destination)
            temporary = None
        except (requests.RequestException, OSError) as error:
            self.logger.error('Download failed: %s: %s', url, error)
            self._stats['errors'] += 1
            return False
        finally:
            if temporary and os.path.exists(temporary):
                os.remove(temporary)
        self.cache.set(self.hash_url(url), {
            'url': url,
            'file': str(destination),
            'sha256': digest,
            'bytes': size,
            'downloaded_at': datetime.now().isoformat(),
        })
        self.logger.info('Downloaded: %s', destination)
        self._stats['downloads'] += 1
        return True

    def rate_limit(self, multiplier: float = 1.0, jitter: bool = True) -> None:
        """Pause between requests: ``pause_time * multiplier``, plus up to 20% jitter."""
        delay = self.pause_time * multiplier
        if jitter:
            delay += random.uniform(0, self.pause_time * 0.2)
        time.sleep(delay)

    # --- Browser -----------------------------------------------------------

    def init_selenium(
            self,
            headless: bool = True,
            download_dir: Optional[PathLike] = None,
            arguments: Iterable[str] = (),
        ) -> None:
        """Start a Chrome browser that saves downloads to ``pdf_dir``.

        Args:
            headless: Run without a window.
            download_dir: Where the browser saves files; ``pdf_dir``.
            arguments: Extra Chrome command-line arguments.
        """
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
        except ImportError as error:
            raise ImportError(
                'A browser needs Selenium from the `web` extra. Install it with:\n\n'
                '    pip install "cannlytics[web]"\n'
            ) from error
        options = Options()
        standard = ['--no-sandbox', '--disable-dev-shm-usage', '--disable-gpu', '--window-size=1920,1080']
        if headless:
            standard.insert(0, '--headless=new')
        for argument in standard + list(arguments):
            options.add_argument(argument)
        options.add_experimental_option('prefs', {
            'download.default_directory': os.fspath(download_dir or self.pdf_dir.resolve()),
            'download.prompt_for_download': False,
            'download.directory_upgrade': True,
            'plugins.always_open_pdf_externally': True,
        })
        self.driver = webdriver.Chrome(options=options)
        self.driver.implicitly_wait(10)
        self.logger.info('Browser started (headless=%s)', headless)

    # The name the collectors in cannabis_results call.
    _init_selenium = init_selenium

    def quit_driver(self) -> None:
        """Close the browser, if one is running."""
        if self.driver is None:
            return
        try:
            self.driver.quit()
            self.logger.info('Browser closed')
        except Exception as error:  # the browser may already be gone
            self.logger.warning('Error closing the browser: %s', error)
        finally:
            self.driver = None

    _quit_driver = quit_driver

    def wait_for_element(self, by: str, value: str, timeout: float = 10, condition: str = 'presence'):
        """Wait for an element and return it.

        Args:
            by: ``'css selector'``, ``'id'``, ``'xpath'``, ``'class name'``,
                or ``'tag name'``.
            value: The locator.
            timeout: Seconds to wait.
            condition: ``'presence'`` or ``'clickable'``.
        """
        from selenium.webdriver.support import expected_conditions
        from selenium.webdriver.support.ui import WebDriverWait
        wait = WebDriverWait(self.driver, timeout)
        if condition == 'clickable':
            return wait.until(expected_conditions.element_to_be_clickable((by, value)))
        return wait.until(expected_conditions.presence_of_element_located((by, value)))

    # --- Saving ------------------------------------------------------------

    def save_results(
            self,
            df: pd.DataFrame,
            prefix: Optional[str] = None,
            include_date: bool = True,
            save_latest: bool = True,
        ) -> str:
        """Save results as CSV in ``datasets_dir``, atomically.

        Args:
            df: The results.
            prefix: The file-name prefix; ``results-{state}-{source}``.
            include_date: Write a time-stamped file.
            save_latest: Write (or replace) the ``-latest`` file.

        Returns:
            The time-stamped file's path, else the latest file's.
        """
        if not include_date and not save_latest:
            raise ValueError('Nothing to save: set include_date or save_latest.')
        prefix = prefix or f'results-{self.state}-{self.source}'
        stamp = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
        names = ([f'{prefix}-{stamp}.csv'] if include_date else []) + ([f'{prefix}-latest.csv'] if save_latest else [])
        paths = []
        for name in names:
            destination = self.datasets_dir / name
            temporary = _atomic_path(destination)
            try:
                df.to_csv(temporary, index=False)
                os.replace(temporary, destination)
            finally:
                if os.path.exists(temporary):
                    os.remove(temporary)
            self.logger.info('Saved: %s', destination)
            paths.append(str(destination))
        return paths[0]

    _save_results = save_results

    # --- Statistics and clean-up -------------------------------------------

    def get_stats(self) -> Dict[str, Any]:
        """Download, cache, error, and retry counts, and the elapsed time."""
        self._stats['duration_seconds'] = (datetime.now() - self._stats['started_at']).total_seconds()
        return self._stats

    def log_stats(self) -> None:
        """Log the statistics."""
        stats = self.get_stats()
        self.logger.info(
            'Collection complete: %s downloads, %s cached, %s errors (%s rejected), %s retries in %.1fs',
            stats['downloads'], stats['cached'], stats['errors'], stats['rejected'],
            stats['retries'], stats['duration_seconds'],
        )

    def close(self) -> None:
        """Release the browser, the HTTP session, and the log handlers."""
        self.quit_driver()
        self._session.close()
        for handler in self._handlers:
            self.logger.removeHandler(handler)
            handler.close()
        self._handlers = []

    def __enter__(self) -> 'COACollector':
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> bool:
        self.log_stats()
        self.close()
        return False

__all__ = [
    'COACollector',
    'DEFAULT_USER_AGENT',
    'PoliteSession',
    'RETRY_STATUSES',
    'retrying_session',
]

"""
COAdoc — Hybrid Certificate of Analysis Parsing Engine
Copyright (c) 2024-2026 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
Created: 10/7/2024
Updated: 3/19/2026
License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description:
    COAdoc is Cannlytics' premier COA parsing technology. It routes
    each Certificate of Analysis to the optimal parsing method:

    1. **Algorithmic parsing** (free, fast, deterministic): For COAs
       from recognized labs with battle-tested parsing algorithms.
    2. **AI-powered parsing** (flexible, comprehensive): For
       unrecognized COAs or when algorithmic parsing fails.

    COAdoc supports two usage modes:
      - **Single-file mode** (API and interactive use): Parse one COA
        at a time from a file path, URL, or raw bytes. No caching
        infrastructure required.
      - **Pipeline mode** (batch data collection): Parse thousands of
        COAs for a state with JSONL caching, cost budgets, and
        progress tracking.

    Usage::

        from cannlytics.data.coas import COAdoc

        # Single-file (API / interactive)
        parser = COAdoc(provider='anthropic', api_key='sk-ant-...')
        result = parser.parse('path/to/coa.pdf')

        # Pipeline (batch)
        parser = COAdoc(
            provider='openai',
            state='ny',
            data_dir=Path('.datasets'),
            cache_dir=Path('.cache'),
        )
        summary = parser.parse_all(source='prr')

    Hybrid Routing Flow:
        COA PDF → validate → lab identification → algorithm → AI fallback
        → QR scan for coa_url

    AI Provider Priority:
        1. Anthropic Claude (highest quality)
        2. OpenAI (reliable structured output)
        3. Google Gemini (free tier available)
        4. xAI Grok (low cost bulk)

    QR Code Scanning:
        After parsing, COAdoc scans the PDF for QR codes and extracts
        the ``coa_url`` (the lab portal URL linking to the original
        COA). This uses the ``qrustie`` Rust binary when available,
        with a Python fallback (pyzbar/zxingcpp). QR scanning is
        best-effort and can be disabled via ``qrustie_path=False``.
"""
# Standard imports:
import importlib
import importlib.util
import json
import logging
import os
import tempfile
import time
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

# External imports (optional):
try:
    import pdfplumber
except ImportError:
    pdfplumber = None

# Internal imports:
from cannlytics.data.coas.ai_client import AIClient, CostTracker
from cannlytics.data.coas.config import (
    AI_PROVIDERS,
    ANALYSIS_SKIP_RULES,
)
from cannlytics.data.coas.pdf_utils import (
    is_valid_pdf,
    InvalidPDFCache,
    get_pdf_info,
    get_pdf_pages_as_images,
    extract_pdf_text,
    long_path,
    safe_file_size,
    IS_WINDOWS,
    WIN_MAX_PATH,
)
from cannlytics.data.coas.registry import LAB_REGISTRY
from cannlytics.utils.hashing import hash_bytes, hash_file, hash_file_multi
from cannlytics.data.coas.schema import (
    ANALYSIS_CONFIGS,
    normalize_product_type,
)
from cannlytics.data.coas.qr import scan_qr

# Suppress pdfminer noise.
logging.getLogger('pdfminer').setLevel(logging.ERROR)

# ╔══════════════════════════════════════════════════════════════════╗
# ║ Lab Identification & Algorithm Loading                           ║
# ╚══════════════════════════════════════════════════════════════════╝

def identify_lab(
        pdf_path: str,
        lab_registry: Optional[Dict[str, Dict]] = None,
        deep_search: bool = True,
        qr_fallback: bool = False,
        qrustie_path: Optional[str] = None,
        logger: Optional[logging.Logger] = None,
    ) -> Optional[str]:
    """Identify the originating lab/LIMS from a COA PDF.

    This is the routing decision function for COAdoc's hybrid
    architecture. It determines whether a COA comes from a
    recognized lab with an algorithmic parser available.

    Strategy (in order of confidence):
      1. Extract text from page 1 via pdfplumber.
      2. Search for known lab URLs in text (highest confidence).
      3. Search for known lab/LIMS names in text.
      4. Optionally search page 2 text (``deep_search``).
      5. Optionally decode QR codes via qrustie (``qr_fallback``).

    Args:
        pdf_path:       Path to the COA PDF file.
        lab_registry:   Lab registry dict. Defaults to ``LAB_REGISTRY``.
        deep_search:    Whether to also search page 2 text.
        qr_fallback:    Whether to attempt QR code identification.
        qrustie_path:   Path to qrustie binary (for QR fallback).
        logger:         Optional logger for debug messages.

    Returns:
        Lab registry key (e.g., ``'kaycha'``) if identified, ``None``
        otherwise.
    """
    if lab_registry is None:
        lab_registry = LAB_REGISTRY
    _log = logger or logging.getLogger(__name__)

    if pdfplumber is None:
        _log.debug('identify_lab: pdfplumber not installed')
        return None

    # ── Step 1: Extract text from page(s) ─────────────────────
    texts = []
    try:
        with pdfplumber.open(long_path(pdf_path)) as pdf:
            if not pdf.pages:
                return None
            page1_text = pdf.pages[0].extract_text() or ''
            texts.append(page1_text)
            if deep_search and len(pdf.pages) > 1:
                page2_text = pdf.pages[1].extract_text() or ''
                texts.append(page2_text)
    except Exception as e:
        _log.debug(f'identify_lab: Failed to extract text: {e}')
        return None

    combined_text = '\n'.join(texts)
    if not combined_text.strip():
        _log.debug('identify_lab: No extractable text (image-only PDF)')
        if not qr_fallback:
            return None

    # ── Step 2: Search for known lab URLs (highest confidence) ─
    for lab_key, config in lab_registry.items():
        for url in config.get('urls', []):
            if url in combined_text:
                _log.debug(f'identify_lab: URL match "{url}" -> {lab_key}')
                return lab_key

    # ── Step 3: Search for known lab/LIMS names ───────────────
    text_lower = combined_text.lower()
    for lab_key, config in lab_registry.items():
        for pattern in config.get('text_patterns', []):
            if pattern.lower() in text_lower:
                _log.debug(f'identify_lab: Text match "{pattern}" -> {lab_key}')
                return lab_key

    # ── Step 4: QR code fallback ──────────────────────────────
    if qr_fallback and qrustie_path:
        import subprocess
        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                images = get_pdf_pages_as_images(
                    pdf_path, page_indexes=[0], output_dir=tmpdir,
                )
                if images:
                    result = subprocess.run(
                        [qrustie_path, '--input', images[0], '--first-only'],
                        capture_output=True, text=True, timeout=30,
                    )
                    if result.returncode == 0 and result.stdout.strip():
                        qr_data = json.loads(result.stdout.strip())
                        if qr_data.get('found') and qr_data.get('data'):
                            qr_url = qr_data['data'][0]
                            for lab_key, config in lab_registry.items():
                                for url_fragment in config.get('urls', []):
                                    if url_fragment in qr_url:
                                        _log.debug(
                                            f'identify_lab: QR URL match '
                                            f'"{url_fragment}" -> {lab_key}'
                                        )
                                        return lab_key
        except Exception as e:
            _log.debug(f'identify_lab: QR fallback failed: {e}')

    return None

def load_algorithm(
        lab_key: str,
        lab_registry: Optional[Dict] = None,
        local_paths: Optional[List[str]] = None,
        logger: Optional[logging.Logger] = None,
    ) -> Optional[Callable]:
    """Load a COA parsing algorithm with local override.

    Import priority:
      1. Local override directories (for development).
      2. ``cannlytics.data.coas.algorithms`` package (canonical).

    Args:
        lab_key:        Registry key (e.g., ``'kaycha'``).
        lab_registry:   Lab registry dict. Defaults to ``LAB_REGISTRY``.
        local_paths:    List of local directories to search first.
        logger:         Optional logger.

    Returns:
        The parsing function, or ``None`` if not loadable.
    """
    if lab_registry is None:
        lab_registry = LAB_REGISTRY
    _log = logger or logging.getLogger(__name__)

    config = lab_registry.get(lab_key)
    if not config:
        _log.debug(f'load_algorithm: Unknown lab key "{lab_key}"')
        return None

    module_name = config['module']
    func_name = config['algorithm']

    if local_paths is None:
        local_paths = [
            'algorithms/coa_parsers',
            '../algorithms/coa_parsers',
        ]

    # ── Try local override first ──────────────────────────────
    for local_dir in local_paths:
        local_path = Path(local_dir)
        module_file = local_path / f'{module_name}.py'
        if module_file.exists():
            try:
                spec = importlib.util.spec_from_file_location(
                    f'coa_parsers.{module_name}', str(module_file),
                )
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                func = getattr(mod, func_name, None)
                if func and callable(func):
                    _log.debug(
                        f'load_algorithm: Loaded {func_name} '
                        f'from local {module_file}'
                    )
                    return func
            except Exception as e:
                _log.warning(
                    f'load_algorithm: Failed to load local '
                    f'{module_file}: {e}'
                )

    # ── Fall back to cannlytics package ───────────────────────
    try:
        mod = importlib.import_module(
            f'cannlytics.data.coas.algorithms.{module_name}'
        )
        func = getattr(mod, func_name, None)
        if func and callable(func):
            _log.debug(
                f'load_algorithm: Loaded {func_name} '
                f'from cannlytics package'
            )
            return func
    except (ImportError, AttributeError) as e:
        _log.debug(
            f'load_algorithm: cannlytics package import failed: {e}'
        )

    _log.warning(f'load_algorithm: Could not load algorithm for "{lab_key}"')
    return None

def adapt_algorithm_output(
        raw_output: Dict,
        pdf_hash: str,
        lab_key: str,
        lab_registry: Optional[Dict] = None,
        elapsed: float = 0.0,
    ) -> Optional[Dict]:
    """Adapt legacy algorithmic parser output to the hybrid schema.

    Legacy CoADoc algorithms return a flat dictionary with mixed
    metadata and a nested ``'results'`` list. This function transforms
    that into the standardized format: ``{'metadata': {...}, 'analyses': {...}}``.

    Args:
        raw_output:     Raw dict from the algorithmic parser.
        pdf_hash:       SHA-256 hash of the source PDF.
        lab_key:        Lab registry key (e.g., ``'kaycha'``).
        lab_registry:   Lab registry dict.
        elapsed:        Parse time in seconds.

    Returns:
        Dict with ``'metadata'`` and ``'analyses'`` keys, or ``None``.
    """
    if lab_registry is None:
        lab_registry = LAB_REGISTRY
    if not raw_output or not isinstance(raw_output, dict):
        return None

    config = lab_registry.get(lab_key, {})
    version = config.get('version', '0.0.0')

    attribution = {
        'pdf_hash': pdf_hash,
        'parsing_method': 'algorithm',
        'parsing_algorithm': f'{lab_key}_v{version}',
        'parsing_model': None,
        'parsing_provider': 'local',
        'parsing_time': round(elapsed, 2),
        'parsing_cost': 0.0,
    }

    metadata_keys = {
        'product_name', 'strain_name', 'product_type',
        'date_tested', 'date_received', 'date_collected',
        'batch_number', 'batch_size',
        'lab', 'lab_license_number', 'lab_address', 'lab_city',
        'lab_state', 'lab_zipcode',
        'producer', 'producer_street', 'producer_city',
        'producer_state', 'producer_zipcode',
        'producer_license_number',
        'distributor', 'distributor_license_number',
        'sample_id', 'lab_id', 'sample_weight',
        'total_cannabinoids', 'total_cbd', 'total_thc',
        'total_terpenes', 'status',
    }
    metadata = {**attribution}
    for key in metadata_keys:
        if key in raw_output:
            metadata[key] = raw_output[key]

    # Parse analyses list.
    analyses_raw = raw_output.get('analyses', '[]')
    if isinstance(analyses_raw, str):
        try:
            analyses_list = json.loads(analyses_raw)
        except (json.JSONDecodeError, TypeError):
            analyses_list = []
    elif isinstance(analyses_raw, list):
        analyses_list = analyses_raw
    else:
        analyses_list = []
    metadata['analyses'] = analyses_list

    # Parse and group results by analysis.
    results_raw = raw_output.get('results', '[]')
    if isinstance(results_raw, str):
        try:
            results_list = json.loads(results_raw)
        except (json.JSONDecodeError, TypeError):
            results_list = []
    elif isinstance(results_raw, list):
        results_list = results_raw
    else:
        results_list = []

    analysis_groups: Dict[str, List[Dict]] = {}
    for result in results_list:
        if not isinstance(result, dict):
            continue
        analysis = result.get('analysis', 'unknown')
        analysis_normalized = analysis.lower().replace(' ', '_')
        if 'cannab' in analysis_normalized:
            analysis_normalized = 'cannabinoids'
        elif 'terp' in analysis_normalized:
            analysis_normalized = 'terpenes'
        elif 'pestic' in analysis_normalized:
            analysis_normalized = 'pesticides'
        elif 'heavy' in analysis_normalized or 'metal' in analysis_normalized:
            analysis_normalized = 'heavy_metals'
        elif 'micro' in analysis_normalized:
            analysis_normalized = 'microbials'
        elif 'solvent' in analysis_normalized:
            analysis_normalized = 'residual_solvents'
        elif 'moisture' in analysis_normalized or 'water' in analysis_normalized:
            analysis_normalized = 'moisture_foreign_matter'
        if analysis_normalized not in analysis_groups:
            analysis_groups[analysis_normalized] = []
        analysis_groups[analysis_normalized].append(result)

    analysis_entries = {}
    for analysis_name, results in analysis_groups.items():
        analysis_entries[analysis_name] = {
            **attribution,
            'results': results,
        }

    return {
        'metadata': metadata,
        'analyses': analysis_entries,
    }

# ╔══════════════════════════════════════════════════════════════════╗
# ║ File Hashing                                                     ║
# ╚══════════════════════════════════════════════════════════════════╝

def _hash_file(path: str, size: int = 65536) -> str:
    """Compute the SHA-256 of a whole file, the canonical ``pdf_hash``.

    Before 1.0.0 this hashed only the first ``size`` bytes, so two
    different COAs that opened with the same 64 KB (a shared lab logo)
    received the same ``pdf_hash``, and an unreadable file silently
    received the digest of zero bytes. ``size`` is now a chunk size.

    Raises:
        OSError: If the file cannot be read.
    """
    return hash_file(long_path(path), size=size)

def _hash_bytes(data: bytes) -> str:
    """Compute a SHA-256 hash of raw bytes."""
    return hash_bytes(data)

# ╔══════════════════════════════════════════════════════════════════╗
# ║ COAdoc — The Main Parser Class                                   ║
# ╚══════════════════════════════════════════════════════════════════╝

class COAdoc:
    """COAdoc — Hybrid Certificate of Analysis parsing engine.

    Routes each COA to the optimal parsing method: algorithmic
    (free, fast, deterministic) for recognized labs, or AI-powered
    (flexible, comprehensive) for unrecognized formats.

    **Single-file mode** (for API and interactive use)::

        parser = COAdoc(provider='anthropic', api_key='sk-ant-...')
        result = parser.parse('path/to/coa.pdf')
        result = parser.parse('https://example.com/coa.pdf')
        result = parser.parse(pdf_bytes, filename='coa.pdf')

        # Access the QR-scanned COA URL (if found).
        print(result['metadata'].get('coa_url'))

    **Disable QR scanning** (if you don't need coa_url)::

        parser = COAdoc(provider='anthropic', qrustie_path=False)

    **Pipeline mode** (for batch data collection)::

        parser = COAdoc(
            provider='openai',
            state='ny',
            data_dir=Path('.datasets'),
            cache_dir=Path('.cache'),
        )
        summary = parser.parse_all(source='prr')

    Args:
        provider: AI provider (``'anthropic'``, ``'openai'``,
            ``'gemini'``, ``'xai'``). Default: ``'anthropic'``.
        model: Specific model ID. Defaults to the provider's default.
        api_key: Explicit API key. Falls back to env vars if not set.
        method: Parsing method: ``'auto'`` (algorithm-first, AI fallback),
            ``'algorithm'`` (deterministic only), ``'ai'`` (AI only).
        local_algorithm_paths: Directories to search for local
            algorithm overrides before the package.
        qrustie_path: Explicit path to the ``qrustie`` Rust binary
            for QR code scanning. If ``None`` (default), auto-discovers
            via ``QRUSTIE_PATH`` env var and standard search paths.
            Set to ``False`` to disable QR scanning entirely.
        state: State code for pipeline mode (e.g., ``'ny'``).
        data_dir: Root data directory for pipeline mode.
        cache_dir: JSONL cache directory for pipeline mode.
        budget: Maximum AI spend in USD for pipeline mode.
        max_parses: Maximum COAs to parse in pipeline mode.
        logger: Optional logger instance.
    """

    def __init__(
            self,
            provider: str = 'anthropic',
            model: Optional[str] = None,
            api_key: Optional[str] = None,
            method: str = 'auto',
            local_algorithm_paths: Optional[List[str]] = None,
            qrustie_path: Optional[Union[str, bool]] = None,
            # Pipeline-mode options:
            state: Optional[str] = None,
            data_dir: Optional[Path] = None,
            cache_dir: Optional[Path] = None,
            budget: Optional[float] = None,
            max_parses: Optional[int] = None,
            logger: Optional[logging.Logger] = None,
        ):
        self.method = method
        self.budget = budget
        self.max_parses = max_parses
        self.local_algorithm_paths = local_algorithm_paths
        self.logger = logger or logging.getLogger('cannlytics.coadoc')

        # QR scanning: False disables entirely, None auto-discovers,
        # str uses the explicit path.
        if qrustie_path is False:
            self._qrustie_path = None
            self._scan_qr_enabled = False
        else:
            self._qrustie_path = qrustie_path if isinstance(qrustie_path, str) else None
            self._scan_qr_enabled = True

        # Pipeline-mode state.
        self.state = state.lower() if state else None
        self.data_dir = data_dir
        self.cache_dir = cache_dir

        # AI client (only if method allows AI).
        if method != 'algorithm':
            self.ai_client = AIClient(
                provider=provider,
                model=model,
                api_key=api_key,
                logger=self.logger,
            )
        else:
            self.ai_client = None

        # Cost tracker (shared across all parses).
        self.costs = CostTracker()

        # Algorithm cache (keyed by lab_key → callable).
        self._algorithm_cache: Dict[str, Optional[Callable]] = {}

    # ══════════════════════════════════════════════════════════════
    # SINGLE-FILE MODE
    # ══════════════════════════════════════════════════════════════

    def parse(
            self,
            source: Union[str, bytes, 'Path'],
            filename: Optional[str] = None,
            analyses: Optional[List[str]] = None,
        ) -> Dict:
        """Parse a single COA file, URL, or bytes.

        After parsing metadata and analyses, scans the COA for QR
        codes and adds ``coa_url`` to the metadata if a URL is found.
        QR scanning is best-effort — if it fails (e.g., no decoder
        available), the parse result is still returned without a
        ``coa_url``. Disable QR scanning by passing
        ``qrustie_path=False`` to the constructor.

        Args:
            source: One of:
                - ``str``: File path or URL.
                - ``bytes``: Raw PDF bytes.
                - ``Path``: File path.
            filename: Optional filename (used for bytes input).
            analyses: Optional list of specific analyses to extract.

        Returns:
            Dict with ``'metadata'`` and ``'analyses'`` keys. The
            metadata dict will contain ``'coa_url'`` if a QR code
            URL was found. On failure, returns
            ``{'error': '...', 'metadata': {}}``.

        Example::

            result = parser.parse('coa.pdf')
            print(result['metadata']['product_name'])
            print(result['metadata'].get('coa_url'))
            print(result['analyses']['cannabinoids'])
        """
        # ── Resolve source to a local file path ──────────────────
        temp_path = None
        try:
            if isinstance(source, bytes):
                temp_path = self._bytes_to_temp(source, filename)
                file_path = temp_path
            elif isinstance(source, Path):
                file_path = str(source)
            elif isinstance(source, str) and (
                source.startswith('http://') or source.startswith('https://')
            ):
                temp_path = self._url_to_temp(source)
                file_path = temp_path
            else:
                file_path = str(source)

            # ── Validate ─────────────────────────────────────────
            valid, reason = is_valid_pdf(file_path)
            if not valid:
                return {'error': f'Invalid PDF: {reason}', 'metadata': {}}

            pdf_hash = _hash_file(file_path)

            # ── Parse ────────────────────────────────────────────
            return self._parse_single(
                pdf_hash=pdf_hash,
                file_path=file_path,
                analyses=analyses,
            )

        except Exception as e:
            self.logger.error(f'COAdoc.parse() error: {e}')
            return {'error': str(e), 'metadata': {}}

        finally:
            if temp_path and os.path.exists(temp_path):
                os.unlink(temp_path)

    def _bytes_to_temp(self, data: bytes, filename: Optional[str] = None) -> str:
        """Write raw bytes to a temp file and return the path."""
        ext = '.pdf'
        if filename:
            _, ext = os.path.splitext(filename)
            ext = ext or '.pdf'
        fd, path = tempfile.mkstemp(suffix=ext)
        with os.fdopen(fd, 'wb') as f:
            f.write(data)
        return path

    def _url_to_temp(self, url: str) -> str:
        """Download a URL to a temp file and return the path."""
        import requests
        response = requests.get(url, timeout=60)
        response.raise_for_status()
        fd, path = tempfile.mkstemp(suffix='.pdf')
        with os.fdopen(fd, 'wb') as f:
            f.write(response.content)
        return path

    def _parse_single(
            self,
            pdf_hash: str,
            file_path: str,
            analyses: Optional[List[str]] = None,
        ) -> Dict:
        """Core single-file parse logic (no caching).

        Returns dict with 'metadata' and 'analyses' keys.
        After parsing, scans the PDF for QR codes and adds
        ``coa_url`` to metadata if a URL is found.
        """
        result = None

        # ── Try algorithmic parsing first ─────────────────────
        if self.method in ('auto', 'algorithm'):
            algo_result = self._try_algorithm(pdf_hash, file_path)
            if algo_result is not None:
                result = algo_result
            elif self.method == 'algorithm':
                return {
                    'error': 'No algorithm available for this COA',
                    'metadata': {},
                }

        # ── AI parsing (if algorithm didn't produce a result) ─
        if result is None:
            if self.ai_client is None or not self.ai_client.is_available:
                return {
                    'error': 'AI client not available',
                    'metadata': {},
                }

            pdf_info = get_pdf_info(file_path)
            num_pages = pdf_info.get('num_pages', 1)
            is_single_page = num_pages == 1

            if is_single_page:
                result = self._ai_parse_single_page(
                    pdf_hash, file_path, pdf_info, analyses,
                )
            else:
                result = self._ai_parse_multi_page(
                    pdf_hash, file_path, pdf_info, analyses,
                )

        # ── QR code scanning for coa_url ──────────────────────
        # Scan the PDF for QR codes and extract the COA URL.
        # Only runs if: (1) QR scanning is enabled, (2) the parse
        # succeeded, and (3) coa_url is not already populated
        # (e.g., by an algorithmic parser that found it directly).
        if (
            result is not None
            and not result.get('error')
            and self._scan_qr_enabled
        ):
            metadata = result.get('metadata', {})
            existing_url = metadata.get('coa_url')
            if not existing_url:
                try:
                    coa_url = scan_qr(
                        file_path,
                        qrustie_path=self._qrustie_path,
                        logger=self.logger,
                    )
                    if coa_url:
                        metadata['coa_url'] = coa_url
                        self.logger.info(f'QR scan found coa_url: {coa_url}')
                except Exception as e:
                    # QR scanning is best-effort — never block the parse.
                    self.logger.debug(f'QR scan failed (non-fatal): {e}')

        return result

    def _try_algorithm(
            self,
            pdf_hash: str,
            file_path: str,
        ) -> Optional[Dict]:
        """Try algorithmic parsing. Returns result dict or None."""
        lab_key = identify_lab(
            pdf_path=file_path,
            logger=self.logger,
        )
        if lab_key is None:
            return None

        lab_name = LAB_REGISTRY[lab_key]['name']
        self.logger.info(f'Lab identified: {lab_name} ({lab_key})')

        # Load algorithm.
        if lab_key not in self._algorithm_cache:
            self._algorithm_cache[lab_key] = load_algorithm(
                lab_key,
                local_paths=self.local_algorithm_paths,
                logger=self.logger,
            )
        algorithm = self._algorithm_cache[lab_key]
        if algorithm is None:
            self.logger.info(f'No loadable algorithm for {lab_name}.')
            return None

        # Run algorithm.
        self.logger.info(f'Running algorithm: {lab_key}')
        start = time.time()
        try:
            raw_output = algorithm(None, file_path)
        except Exception as e:
            self.logger.warning(f'Algorithm {lab_key} failed: {e}')
            return None

        elapsed = time.time() - start

        if not raw_output or not isinstance(raw_output, dict):
            self.logger.warning(f'Algorithm {lab_key} returned empty output.')
            return None

        adapted = adapt_algorithm_output(
            raw_output, pdf_hash, lab_key, elapsed=elapsed,
        )
        if adapted is None:
            return None

        adapted['parse_method'] = 'algorithm'
        adapted['lab_identified'] = lab_key
        adapted['hash'] = pdf_hash
        return adapted

    def _ai_parse_single_page(
            self,
            pdf_hash: str,
            file_path: str,
            pdf_info: Dict,
            analyses: Optional[List[str]] = None,
        ) -> Dict:
        """AI parse for single-page COAs (one-shot extraction)."""
        self.logger.info('Single-page COA — one-shot parse...')
        start = time.time()

        with tempfile.TemporaryDirectory() as tmpdir:
            images = get_pdf_pages_as_images(
                file_path, page_indexes=[0], output_dir=tmpdir,
            )
            text = extract_pdf_text(file_path) if not images else None
            parsed, cost, in_tok, out_tok = self.ai_client.parse_single_page(
                page_images=images if images else None,
                page_text=text if not images else None,
            )

        if parsed is None:
            return {'error': 'Single-page parse failed', 'metadata': {}}

        elapsed = time.time() - start
        self.costs.record(
            self.ai_client.provider, self.ai_client.model,
            in_tok, out_tok, cost, 'single_page', pdf_hash,
        )

        # Extract metadata.
        meta_data = parsed.get('metadata', {})
        if not meta_data:
            meta_data = {k: v for k, v in parsed.items()
                         if k not in ANALYSIS_CONFIGS}

        metadata = {
            'pdf_hash': pdf_hash,
            'parsing_method': 'ai',
            'parsing_model': self.ai_client.model,
            'parsing_provider': self.ai_client.provider,
            'parsing_time': round(elapsed, 2),
            'parsing_cost': round(cost, 6),
            **meta_data,
        }

        # Extract analyses.
        analysis_results = {}
        for analysis_name in ANALYSIS_CONFIGS:
            if analyses and analysis_name not in analyses:
                continue
            results = parsed.get(analysis_name, [])
            if isinstance(results, dict):
                results = results.get('results', [])
            if isinstance(results, list) and results:
                analysis_results[analysis_name] = results

        return {
            'metadata': metadata,
            'analyses': analysis_results,
            'parse_method': 'ai',
            'hash': pdf_hash,
        }

    def _ai_parse_multi_page(
            self,
            pdf_hash: str,
            file_path: str,
            pdf_info: Dict,
            analyses: Optional[List[str]] = None,
        ) -> Dict:
        """AI parse for multi-page COAs (metadata + per-analysis)."""
        num_pages = pdf_info.get('num_pages', 1)
        has_text = pdf_info.get('has_text', False)
        detected_from_pdf = pdf_info.get('detected_analyses', [])
        is_image_only = not has_text and not detected_from_pdf

        # ── Step 1: Parse metadata ────────────────────────────
        self.logger.info('Parsing metadata...')
        start = time.time()

        if is_image_only:
            parsed_meta, cost, in_tok, out_tok = self.ai_client.parse_metadata(
                pdf_path=file_path,
            )
        else:
            with tempfile.TemporaryDirectory() as tmpdir:
                images = get_pdf_pages_as_images(
                    file_path, page_indexes=[0], output_dir=tmpdir,
                )
                parsed_meta, cost, in_tok, out_tok = self.ai_client.parse_metadata(
                    pdf_path=None,
                    page_images=images if images else None,
                )

            # Retry with pages 1+2 if key fields missing (cover sheet).
            if parsed_meta and self._metadata_needs_retry(parsed_meta):
                self.logger.info('Key fields missing — retrying with pages 1+2...')
                with tempfile.TemporaryDirectory() as tmpdir:
                    images = get_pdf_pages_as_images(
                        file_path, page_indexes=[0, 1], output_dir=tmpdir,
                    )
                    parsed2, cost2, in2, out2 = self.ai_client.parse_metadata(
                        pdf_path=None,
                        page_images=images if images else None,
                    )
                if parsed2:
                    for k, v in parsed2.items():
                        if v and (not parsed_meta.get(k) or parsed_meta.get(k) in ('', 0.0, [])):
                            parsed_meta[k] = v
                    cost += cost2
                    in_tok += in2
                    out_tok += out2

        if parsed_meta is None:
            return {'error': 'Metadata parse failed', 'metadata': {}}

        elapsed_meta = time.time() - start
        self.costs.record(
            self.ai_client.provider, self.ai_client.model,
            in_tok, out_tok, cost, 'metadata', pdf_hash,
        )

        metadata = {
            'pdf_hash': pdf_hash,
            'parsing_method': 'ai',
            'parsing_model': self.ai_client.model,
            'parsing_provider': self.ai_client.provider,
            'parsing_time': round(elapsed_meta, 2),
            'parsing_cost': round(cost, 6),
            **parsed_meta,
        }

        # ── Step 2: Determine target analyses ─────────────────
        product_type = normalize_product_type(
            parsed_meta.get('product_type', ''),
        )
        detected = parsed_meta.get('analyses', [])

        all_detected = set(detected_from_pdf)
        for a in (detected or []):
            a_lower = a.lower().replace(' ', '_')
            for config_name in ANALYSIS_CONFIGS:
                if config_name in a_lower or a_lower in config_name:
                    all_detected.add(config_name)
        all_detected.add('cannabinoids')
        all_detected.add('terpenes')

        target_analyses = []
        for analysis_name in ANALYSIS_CONFIGS:
            if analyses and analysis_name not in analyses:
                continue
            config = ANALYSIS_CONFIGS[analysis_name]
            allowed_types = config.get('product_types')
            if allowed_types and product_type not in allowed_types:
                continue
            skip_types = ANALYSIS_SKIP_RULES.get(analysis_name, [])
            if product_type in skip_types:
                continue
            if analysis_name in all_detected or not allowed_types:
                target_analyses.append(analysis_name)

        self.logger.info(f'Target analyses: {target_analyses}')

        # ── Step 3: Parse each analysis ───────────────────────
        analysis_results = {}
        for analysis_name in target_analyses:
            if self.budget and self.costs.total_cost >= self.budget:
                self.logger.info('Budget exhausted mid-COA.')
                break

            config = ANALYSIS_CONFIGS[analysis_name]
            keywords = config['keywords']
            analyte_keys = config['keys']

            self.logger.info(f'Parsing {analysis_name}...')
            start = time.time()

            if is_image_only:
                parsed_a, a_cost, a_in, a_out = self.ai_client.parse_analysis(
                    analysis_name=analysis_name,
                    analyte_keys=analyte_keys,
                    pdf_path=file_path,
                )
            else:
                with tempfile.TemporaryDirectory() as tmpdir:
                    images = get_pdf_pages_as_images(
                        file_path, page_indexes='keywords',
                        keywords=keywords, output_dir=tmpdir,
                    )
                    text = extract_pdf_text(
                        file_path, keywords=keywords,
                    ) if not images else None
                    parsed_a, a_cost, a_in, a_out = self.ai_client.parse_analysis(
                        analysis_name=analysis_name,
                        analyte_keys=analyte_keys,
                        pdf_path=None,
                        page_images=images if images else None,
                        page_text=text,
                    )

            elapsed_a = time.time() - start

            if parsed_a is not None:
                results = parsed_a.get('results', [])
                analysis_results[analysis_name] = results
                self.costs.record(
                    self.ai_client.provider, self.ai_client.model,
                    a_in, a_out, a_cost, analysis_name, pdf_hash,
                )
                self.logger.info(
                    f'{analysis_name}: {len(results)} results, '
                    f'${a_cost:.4f}, {round(elapsed_a)}s'
                )
            else:
                self.logger.warning(f'{analysis_name}: parse failed')

        return {
            'metadata': metadata,
            'analyses': analysis_results,
            'parse_method': 'ai',
            'hash': pdf_hash,
        }

    @staticmethod
    def _metadata_needs_retry(parsed: Dict) -> bool:
        """Check if metadata is missing key fields (likely a cover sheet)."""
        product_name = parsed.get('product_name', '') or ''
        date_tested = parsed.get('date_tested', '') or ''
        producer = parsed.get('producer', '') or ''
        missing = sum(1 for v in [product_name, date_tested, producer] if not v.strip())
        return missing >= 2

    # ══════════════════════════════════════════════════════════════
    # PIPELINE MODE (batch parsing with caching)
    # ══════════════════════════════════════════════════════════════

    def parse_all(
            self,
            source: str = '',
            sample_size: Optional[int] = None,
            analyses: Optional[List[str]] = None,
            legacy_keys: bool = True,
        ) -> Dict:
        """Batch-parse all COAs for a state. Pipeline mode only.

        Requires ``state`` and optionally ``data_dir`` / ``cache_dir``
        to be set in the constructor.

        This method uses JSONL caching (via Bogart) to skip previously
        parsed COAs and track progress across runs. Import dependencies
        (``pandas``, ``cannlytics.data.cache.Bogart``) are loaded lazily
        and only required for pipeline mode.

        Cache keys are the whole-file SHA-256 (``pdf_hash``). Caches
        written before 1.0.0 were keyed by SHA-1; with ``legacy_keys``
        a COA already cached under its SHA-1 still counts as parsed, so
        upgrading never re-parses (or re-bills) an existing archive.

        Args:
            source: Optional source filter (e.g., ``'prr'``, ``'flowery'``).
            sample_size: If set, randomly sample this many PDFs.
            analyses: List of analyses to parse. ``None`` = all detected.
            legacy_keys: Also look up each COA under its pre-1.0.0
                SHA-1 key. Turn off once caches are re-keyed with
                ``cannlytics.data.cache.rekey_cache``.

        Returns:
            Summary statistics dict.

        Raises:
            ValueError: If ``state`` was not provided at init.
        """
        if not self.state:
            raise ValueError(
                'Pipeline mode requires state= in the constructor. '
                'For single-file parsing, use parse() instead.'
            )

        # Lazy imports for pipeline dependencies.
        import pandas as pd
        from cannlytics.data.cache import Bogart

        # Resolve directories.
        state_name = self.state
        data_dir = self.data_dir or Path(os.environ.get('CANNLYTICS_DATA_DIR', '.datasets'))
        cache_dir = self.cache_dir or Path('.cache')
        cache_dir.mkdir(parents=True, exist_ok=True)

        pdf_dir = data_dir / state_name / 'results' / 'pdfs'
        search_dir = pdf_dir / source if source else pdf_dir

        if not search_dir.exists():
            self.logger.warning(f'PDF directory not found: {search_dir}')
            return {'parsed': 0, 'skipped': 0, 'errors': 0}

        # Discover PDFs.
        pdf_files = []
        for root, _, files in os.walk(str(search_dir)):
            for f in files:
                if f.lower().endswith('.pdf'):
                    fp = os.path.join(root, f)
                    if safe_file_size(fp):
                        pdf_files.append(fp)
        pdf_files.sort()

        if not pdf_files:
            self.logger.info('No PDFs found.')
            return {'parsed': 0, 'skipped': 0, 'errors': 0}

        # One read per file yields the canonical key and the legacy key.
        algorithms = ('sha256', 'sha1') if legacy_keys else ('sha256',)
        records = []
        for fp in pdf_files:
            try:
                digests = hash_file_multi(long_path(fp), algorithms)
            except OSError as e:
                self.logger.warning('Skipping unreadable PDF %s: %s', fp, e)
                continue
            records.append({
                'file_path': fp,
                'pdf_hash': digests['sha256'],
                'legacy_hash': digests.get('sha1'),
            })
        df = pd.DataFrame(records, columns=['file_path', 'pdf_hash', 'legacy_hash'])
        df.drop_duplicates(subset=['pdf_hash'], inplace=True)

        if sample_size and sample_size < len(df):
            df = df.sample(n=sample_size, random_state=42)

        if self.max_parses:
            df = df.head(self.max_parses)

        # Initialize caches.
        model_tag = 'algorithm'
        if self.ai_client:
            model_tag = self.ai_client.model.replace('.', '_')

        metadata_cache = Bogart(
            str(cache_dir / f'results-{self.state}-metadata-{model_tag}.jsonl')
        )
        analysis_caches = {}
        for a_name in ANALYSIS_CONFIGS:
            analysis_caches[a_name] = Bogart(
                str(cache_dir / f'results-{self.state}-{a_name}-{model_tag}.jsonl')
            )
        algo_cache = Bogart(
            str(cache_dir / f'results-{self.state}-algorithm.jsonl')
        )
        invalid_cache = InvalidPDFCache(
            str(cache_dir / f'invalid-pdfs-{self.state}.txt')
        )

        total = len(df)
        parsed_count = 0
        skipped_count = 0
        error_count = 0

        self.logger.info(f'Starting batch parse of {total:,} COAs...')

        for i, (_, row) in enumerate(df.iterrows()):
            if self.budget and self.costs.total_cost >= self.budget:
                self.logger.info('Budget exhausted.')
                break

            pdf_hash = row['pdf_hash']
            file_path = row['file_path']
            keys = [k for k in (pdf_hash, row['legacy_hash']) if k]

            # Skip invalid PDFs.
            if any(k in invalid_cache for k in keys):
                skipped_count += 1
                continue

            valid, reason = is_valid_pdf(file_path)
            if not valid:
                invalid_cache.add(pdf_hash, reason)
                skipped_count += 1
                continue

            # Skip if already cached, under the canonical or legacy key.
            if any(metadata_cache.get(k) or algo_cache.get(k) for k in keys):
                skipped_count += 1
                continue

            try:
                result = self._parse_single(
                    pdf_hash=pdf_hash,
                    file_path=file_path,
                    analyses=analyses,
                )
                if result.get('error'):
                    error_count += 1
                else:
                    # Cache the result.
                    metadata_cache.set(pdf_hash, result.get('metadata', {}))
                    for a_name, a_results in result.get('analyses', {}).items():
                        if a_name in analysis_caches:
                            analysis_caches[a_name].set(pdf_hash, {
                                'pdf_hash': pdf_hash,
                                'results': a_results if isinstance(a_results, list) else a_results.get('results', []),
                            })
                    parsed_count += 1
            except Exception as e:
                self.logger.error(f'Error parsing {pdf_hash[:12]}: {e}')
                error_count += 1

            if (i + 1) % 50 == 0:
                self.logger.info(
                    f'[{i + 1}/{total}] Parsed: {parsed_count}, '
                    f'Skipped: {skipped_count}, Errors: {error_count}, '
                    f'Cost: ${self.costs.total_cost:.4f}'
                )

        return {
            'state': self.state,
            'method': self.method,
            'total_pdfs': total,
            'parsed': parsed_count,
            'skipped': skipped_count,
            'errors': error_count,
            'costs': self.costs.summary(),
        }

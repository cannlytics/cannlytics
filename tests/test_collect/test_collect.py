"""
Tests for cannlytics.collect
============================
No network: the HTTP session is replaced by a scripted fake. Each test
pins one defect of the copies this module replaces (MD5 URL keys,
non-atomic writes, HTML saved as PDF, 404s retried, the double retry
loop, the crash when both save flags are off).
"""
import os
import time

import pandas as pd
import pytest
import requests
from urllib3.util.retry import Retry

from cannlytics.collect import (
    RETRY_STATUSES,
    COACollector,
    PoliteSession,
    retrying_session,
)
from cannlytics.utils.hashing import hash_file, hash_text

URL = 'https://lab.example.com/coa/123.pdf'

class FakeResponse:
    """Enough of `requests.Response` for the collector."""

    def __init__(self, status=200, body=b'', fail_after=None):
        self.status_code = status
        self.ok = status < 400
        self.content = body
        self._body = body
        self._fail_after = fail_after
        self.raw = None

    def iter_content(self, chunk_size=1):
        for index in range(0, len(self._body), 1024):
            if self._fail_after is not None and index >= self._fail_after:
                raise requests.ConnectionError('connection dropped mid-download')
            yield self._body[index:index + 1024]

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

class FakeSession:
    """Returns scripted responses in order and records every call."""

    def __init__(self, *responses):
        self.responses = list(responses)
        self.calls = []
        self.closed = False

    def get(self, url, **kwargs):
        self.calls.append((url, kwargs))
        response = self.responses.pop(0)
        if isinstance(response, Exception):
            raise response
        return response

    def close(self):
        self.closed = True

class DemoCollector(COACollector):
    def get_results(self, **kwargs):
        return pd.DataFrame()

@pytest.fixture
def pdf_bytes(make_pdf):
    path = make_pdf('coa.pdf', ['Certificate of Analysis\n' + '\n'.join(f'Analyte {i}: {i}.0%' for i in range(40))])
    with open(path, 'rb') as file:
        return file.read()

@pytest.fixture
def collector(tmp_path):
    instance = DemoCollector('CA', 'demo_lab', data_dir=tmp_path / 'data',
                             cache_path=tmp_path / 'cache' / 'results.jsonl', verbose=False)
    yield instance
    instance.close()

class TestConstruction:

    def test_directories_and_names(self, collector, tmp_path):
        assert collector.state == 'ca'
        assert collector.pdf_dir == tmp_path / 'data' / 'pdfs' / 'demo_lab' and collector.pdf_dir.is_dir()
        assert collector.datasets_dir.is_dir()
        assert collector.log_name == 'get_results_ca_demo_lab'

    def test_no_log_file_unless_asked(self, collector, tmp_path):
        assert not any(p.suffix == '.log' for p in tmp_path.rglob('*'))

    def test_log_file_when_asked_and_released_on_close(self, tmp_path):
        instance = DemoCollector('ca', 'logged', data_dir=tmp_path, cache_path=tmp_path / 'c.jsonl',
                                 log_dir=tmp_path / 'logs', verbose=False)
        instance.logger.info('hello')
        instance.close()
        logs = list((tmp_path / 'logs').glob('get-results-ca-logged-*.log'))
        assert len(logs) == 1 and 'hello' in logs[0].read_text(encoding='utf-8')
        os.remove(logs[0])   # would fail on Windows if the handler still held the file
        assert instance.logger.handlers == []

    def test_logger_does_not_propagate_or_duplicate(self, tmp_path):
        first = DemoCollector('ca', 'same', data_dir=tmp_path, cache_path=tmp_path / 'c.jsonl')
        second = DemoCollector('ca', 'same', data_dir=tmp_path, cache_path=tmp_path / 'c.jsonl')
        assert first.logger is second.logger and first.logger.propagate is False
        assert len(first.logger.handlers) == 1
        first.close(); second.close()

    def test_none_means_default(self, tmp_path):
        instance = DemoCollector('ca', 'x', data_dir=tmp_path, cache_path=tmp_path / 'c.jsonl', pause_time=None, max_retries=None)
        assert instance.pause_time == 3.33 and instance.max_retries == 3
        instance.close()

    def test_is_abstract(self):
        with pytest.raises(TypeError):
            COACollector('ca', 'x')

class TestCacheKeys:

    def test_url_key_is_sha256(self, collector):
        assert collector.hash_url(URL) == hash_text(URL) == collector._hash_url(URL)
        assert collector.hash_url(URL) == collector.cache.hash_url(URL)   # one key for the class and its cache

    def test_legacy_md5_entry_is_still_found(self, collector):
        collector.cache.set(collector.legacy_url_key(URL), {'url': URL, 'file': 'old.pdf'})
        collector._session = FakeSession()
        assert collector.is_cached(URL)
        assert collector.download_file(URL, collector.pdf_dir / '123.pdf') is True
        assert collector._session.calls == [] and collector.get_stats()['cached'] == 1

    def test_truncated_sha256_entry_is_found_and_migrated(self, collector):
        # Some collectors keyed their caches by sha256(url)[:12].
        collector.cache.set(hash_text(URL)[:12], {'url': URL, 'file': 'short.pdf'})
        assert collector.is_cached(URL)
        assert collector.migrate_legacy_keys() == 1
        assert collector.cache.get(collector.hash_url(URL))['file'] == 'short.pdf'

    def test_migrate_legacy_keys(self, collector):
        collector.cache.set(collector.legacy_url_key(URL), {'url': URL, 'file': 'old.pdf'})
        collector.cache.set('unrelated', {'url': 'https://other.example.com'})
        assert collector.migrate_legacy_keys() == 1
        assert collector.cache.get(collector.hash_url(URL))['file'] == 'old.pdf'
        assert collector.migrate_legacy_keys() == 0

class TestDownload:

    def test_success_is_atomic_cached_and_hashed(self, collector, pdf_bytes):
        collector._session = FakeSession(FakeResponse(200, pdf_bytes))
        destination = collector.pdf_dir / '123.pdf'
        assert collector.download_file(URL, destination) is True
        assert destination.read_bytes() == pdf_bytes
        entry = collector.cache.get(collector.hash_url(URL))
        assert entry['sha256'] == hash_file(destination) and entry['bytes'] == len(pdf_bytes)
        assert [p.name for p in collector.pdf_dir.iterdir()] == ['123.pdf']   # no temporary left behind
        assert collector._session.calls[0][1]['timeout'] == collector.timeout

    def test_second_call_is_served_by_the_cache(self, collector, pdf_bytes):
        collector._session = FakeSession(FakeResponse(200, pdf_bytes))
        collector.download_file(URL, collector.pdf_dir / '123.pdf')
        assert collector.download_file(URL, collector.pdf_dir / '123.pdf') is True
        assert len(collector._session.calls) == 1 and collector.get_stats()['cached'] == 1

    def test_the_cache_survives_a_new_collector(self, collector, pdf_bytes, tmp_path):
        collector._session = FakeSession(FakeResponse(200, pdf_bytes))
        collector.download_file(URL, collector.pdf_dir / '123.pdf')
        again = DemoCollector('ca', 'demo_lab', data_dir=tmp_path / 'data', cache_path=tmp_path / 'cache' / 'results.jsonl', verbose=False)
        assert again.is_cached(URL)
        again.close()

    def test_html_error_page_is_not_saved_as_a_pdf(self, collector):
        page = b'<!DOCTYPE html><html><body>Session expired. Please log in.</body></html>' * 40
        collector._session = FakeSession(FakeResponse(200, page))
        assert collector.download_file(URL, collector.pdf_dir / '123.pdf') is False
        assert list(collector.pdf_dir.iterdir()) == [] and not collector.is_cached(URL)
        assert collector.get_stats()['rejected'] == 1

    def test_validation_follows_the_destination_unless_told(self, collector):
        page = b'<html>listing</html>'
        collector._session = FakeSession(FakeResponse(200, page), FakeResponse(200, page), FakeResponse(200, page))
        assert collector.download_file('https://lab.example.com/1', collector.data_dir / 'list.html') is True
        assert collector.download_file('https://lab.example.com/2', collector.data_dir / 'x.bin', require_pdf=True) is False
        assert collector.download_file('https://lab.example.com/3', collector.pdf_dir / 'y.pdf', require_pdf=False) is True
        assert (collector.data_dir / 'list.html').read_bytes() == page and not (collector.data_dir / 'x.bin').exists()

    def test_not_found_is_an_answer_not_retried(self, collector):
        collector._session = FakeSession(FakeResponse(404))
        assert collector.download_file(URL, collector.pdf_dir / '123.pdf') is False
        assert len(collector._session.calls) == 1 and not collector.is_cached(URL)

    def test_connection_error(self, collector):
        collector._session = FakeSession(requests.ConnectionError('refused'))
        assert collector.download_file(URL, collector.pdf_dir / '123.pdf') is False
        assert collector.get_stats()['errors'] == 1

    def test_interrupted_download_leaves_nothing(self, collector, pdf_bytes):
        collector._session = FakeSession(FakeResponse(200, pdf_bytes, fail_after=1024))
        assert collector.download_file(URL, collector.pdf_dir / '123.pdf') is False
        assert list(collector.pdf_dir.iterdir()) == [] and not collector.is_cached(URL)

    def test_existing_file_is_replaced_whole(self, collector, pdf_bytes):
        destination = collector.pdf_dir / '123.pdf'
        destination.write_bytes(b'stale')
        collector._session = FakeSession(FakeResponse(200, pdf_bytes))
        assert collector.download_file(URL, destination, skip_cached=False) is True
        assert destination.read_bytes() == pdf_bytes

class TestRetryPolicy:

    def test_one_policy_in_the_session(self):
        session = retrying_session(retries=4, backoff=2.0, user_agent='UA')
        retry = session.get_adapter('https://x.example.com').max_retries
        assert isinstance(retry, Retry) and retry.total == 4 and retry.backoff_factor == 2.0
        assert set(retry.status_forcelist) == set(RETRY_STATUSES) and 404 not in retry.status_forcelist
        assert retry.respect_retry_after_header and retry.raise_on_status is False
        assert 'GET' in retry.allowed_methods and 'POST' not in retry.allowed_methods
        assert session.headers['User-Agent'] == 'UA'
        session.close()

    def test_collector_uses_it(self, collector):
        retry = collector._session.get_adapter('https://x.example.com').max_retries
        assert retry.total == collector.max_retries

class TestSavingAndCleanUp:

    def test_save_results(self, collector):
        frame = pd.DataFrame({'pdf_hash': ['a', 'b'], 'total_thc': [20.1, None]})
        path = collector.save_results(frame)
        names = sorted(p.name for p in collector.datasets_dir.iterdir())
        assert len(names) == 2 and 'results-ca-demo_lab-latest.csv' in names and path.endswith('.csv')
        assert pd.read_csv(path).shape == (2, 2)
        assert collector._save_results == collector.save_results

    def test_save_nothing_is_an_error_not_a_crash(self, collector):
        with pytest.raises(ValueError):
            collector.save_results(pd.DataFrame(), include_date=False, save_latest=False)

    def test_latest_only(self, collector):
        path = collector.save_results(pd.DataFrame({'a': [1]}), include_date=False)
        assert path.endswith('results-ca-demo_lab-latest.csv')

    def test_rate_limit(self, collector, monkeypatch):
        slept = []
        monkeypatch.setattr(time, 'sleep', slept.append)
        collector.pause_time = 1.0
        collector.rate_limit()
        collector.rate_limit(multiplier=2.0, jitter=False)
        assert 1.0 <= slept[0] <= 1.2 and slept[1] == 2.0

    def test_context_manager_releases_everything(self, tmp_path):
        class Driver:
            quit_called = False
            def quit(self):
                Driver.quit_called = True
        with DemoCollector('ca', 'ctx', data_dir=tmp_path, cache_path=tmp_path / 'c.jsonl', verbose=False) as instance:
            instance.driver = Driver()
            fake = instance._session = FakeSession()
        assert Driver.quit_called and instance.driver is None and fake.closed

    def test_browser_needs_the_web_extra(self, collector, monkeypatch):
        import sys
        monkeypatch.setitem(sys.modules, 'selenium', None)
        with pytest.raises(ImportError, match='cannlytics\\[web\\]'):
            collector.init_selenium()

class TestPoliteSession:

    @pytest.fixture
    def session(self, tmp_path):
        instance = PoliteSession(cache_dir=tmp_path / 'docs', delay=0)
        yield instance
        instance.close()

    def test_fetch_then_cache(self, session):
        session.session = FakeSession(FakeResponse(200, b'%PDF-1.4 form'))
        assert session.get_bytes(URL) == b'%PDF-1.4 form'
        assert session.get_bytes(URL) == b'%PDF-1.4 form'
        assert len(session.session.calls) == 1 and session.stats['cache_hits'] == 1
        assert os.path.exists(os.path.join(session.cache_dir, f'{hash_text(URL)}.bin'))

    def test_first_version_cache_files_are_read(self, session):
        legacy = os.path.join(session.cache_dir, f'{hash_text(URL)[:32]}.bin')
        with open(legacy, 'wb') as file:
            file.write(b'old')
        session.session = FakeSession()
        assert session.get_bytes(URL) == b'old'

    def test_expired_entry_is_refetched(self, session):
        session.session = FakeSession(FakeResponse(200, b'v1'), FakeResponse(200, b'v2'))
        session.get_bytes(URL)
        path = os.path.join(session.cache_dir, f'{hash_text(URL)}.bin')
        old = time.time() - 200 * 86_400
        os.utime(path, (old, old))
        assert session.get_bytes(URL) == b'v2'

    def test_failures_are_counted_and_reported(self, session):
        session.session = FakeSession(FakeResponse(429), FakeResponse(404), requests.ConnectionError('x'))
        assert [session.get_bytes(f'{URL}?{i}') for i in range(3)] == [None, None, None]
        assert session.stats['failed'] == 3 and session.stats['failed_statuses'] == [429, 404]
        report = session.report()
        assert '3 failed' in report and 'rate limited' in report

    def test_throttle(self, monkeypatch):
        clock = iter([100.0, 100.0, 100.2, 100.2])
        slept = []
        monkeypatch.setattr(time, 'monotonic', lambda: next(clock))
        monkeypatch.setattr(time, 'sleep', slept.append)
        instance = PoliteSession(delay=1.0)
        instance._throttle()
        instance._throttle()
        assert slept == [pytest.approx(0.8)]
        instance.close()

    def test_no_cache_dir_means_no_files(self, tmp_path):
        with PoliteSession(delay=0) as instance:
            instance.session = FakeSession(FakeResponse(200, b'x'), FakeResponse(200, b'x'))
            instance.get_bytes(URL)
            instance.get_bytes(URL)
            assert len(instance.session.calls) == 2

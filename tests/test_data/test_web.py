"""
Tests for web data tools
========================
`cannlytics.data.web`, with fake HTTP responses and a fake browser: no
network, no Selenium.
"""
import sys
import types

import pytest

bs4 = pytest.importorskip('bs4')

from cannlytics.data.web import web  # noqa: E402

def soup(html):
    return bs4.BeautifulSoup(html, 'html.parser')

class FakeResponse:
    def __init__(self, content=b'', status=200, content_type='application/pdf', url='https://example.com/', cookies=None, text=None):
        self.content, self.status_code, self.url = content, status, url
        self.headers = {'Content-Type': content_type}
        self.cookies = cookies or {}
        self.text = text if text is not None else content.decode('utf-8', 'ignore')

    def raise_for_status(self):
        if self.status_code >= 400:
            import requests
            raise requests.HTTPError(f'{self.status_code}')

    def iter_content(self, chunk_size=1):
        for i in range(0, len(self.content), 4):
            yield self.content[i:i + 4]

class TestMetadata:

    def test_description_reads_name_and_property_meta_tags(self):
        assert web.get_page_description(soup('<meta name="description" content=" Lab data ">')) == 'Lab data'
        assert web.get_page_description(soup('<meta property="og:description" content="OG">')) == 'OG'
        assert web.get_page_description(soup('<meta name="twitter:description" content="TW">')) == 'TW'

    def test_description_falls_back_to_the_first_paragraph_as_text(self):
        assert web.get_page_description(soup('<p>Hello <b>world</b></p><p>Two</p>')) == 'Hello world'
        assert web.get_page_description(soup('<div></div>')) is None

    def test_theme_color_is_a_name_attribute(self):
        assert web.get_page_theme_color(soup('<meta name="theme-color" content="#45B649">')) == '#45B649'

    def test_image_is_resolved_against_the_page(self):
        html = soup('<img src="/a.png"><img src="b.png">')
        assert web.get_page_image(html, url='https://cannlytics.com/x/') == 'https://cannlytics.com/a.png'
        assert web.get_page_image(html, index=1, url='https://cannlytics.com/x/') == 'https://cannlytics.com/x/b.png'
        assert web.get_page_image(html, index=5) is None
        assert web.get_page_image(soup('<meta property="og:image" content="https://cdn/i.jpg">')) == 'https://cdn/i.jpg'

    def test_favicon_absolute_or_the_site_root(self):
        html = soup('<link rel="shortcut icon" href="/static/fav.ico">')
        assert web.get_page_favicon(html, 'https://cannlytics.com/data/') == 'https://cannlytics.com/static/fav.ico'
        assert web.get_page_favicon(soup(''), 'https://cannlytics.com/data/page') == 'https://cannlytics.com/favicon.ico'
        assert web.get_page_favicon(soup('')) is None

    def test_get_page_metadata_has_a_timeout_and_no_cors_headers(self, monkeypatch):
        seen = {}
        def fake_get(url, headers=None, timeout=None):
            seen.update(url=url, headers=headers, timeout=timeout)
            return FakeResponse(b'<meta name="description" content="D"><link rel="icon" href="/f.ico">',
                                content_type='text/html', url='http://example.com/')
        monkeypatch.setattr(web.requests, 'get', fake_get)
        response, html, metadata = web.get_page_metadata('example.com')
        assert seen['url'] == 'http://example.com' and seen['timeout'] == web.TIMEOUT
        assert not any(key.startswith('Access-Control') for key in seen['headers'])
        assert metadata == {'description': 'D', 'image_url': None, 'favicon': 'http://example.com/f.ico', 'brand_color': None}

class TestContacts:

    def test_email_prefers_mailto_and_returns_from_every_branch(self):
        assert web.get_page_email(soup('<a href="mailto:dev@cannlytics.com?subject=hi">Write</a>')) == 'dev@cannlytics.com'

    def test_email_from_text_ignores_image_file_names(self):
        html = soup('<img src="logo@2x.png"><p>Contact contact@cannlytics.com or see logo@2x.png</p>')
        assert web.get_page_email(html) == 'contact@cannlytics.com'
        assert web.get_page_email(soup('<p>none</p>')) == ''

    def test_phone_from_tel_links_then_text(self):
        assert web.get_page_phone_number(soup('<a href="tel:+15095551234">(509) 555-1234</a>')) == '(509) 555-1234'
        assert web.get_page_phone_number(soup('<p>Call 509-555-1234 today</p>')) == '509-555-1234'
        assert web.get_page_phone_number(soup('<p>no number</p>')) == ''

    def test_format_params_drops_empty_values(self):
        assert web.format_params({'limit': '$limit', 'order': '$order'}, limit=10, order=None) == {'$limit': 10}

class TestDownloads:

    def test_download_is_atomic_and_complete(self, monkeypatch, tmp_path):
        monkeypatch.setattr(web.requests, 'get', lambda *a, **k: FakeResponse(b'%PDF-1.7 hello'))
        path = web.download_file_from_url('https://x.org/files/coa.pdf', destination=str(tmp_path / 'new'))
        assert __import__('pathlib').Path(path).read_bytes() == b'%PDF-1.7 hello' and path.endswith('coa.pdf')
        assert [p.name for p in (tmp_path / 'new').iterdir()] == ['coa.pdf']

    def test_an_http_error_writes_nothing(self, monkeypatch, tmp_path):
        monkeypatch.setattr(web.requests, 'get', lambda *a, **k: FakeResponse(b'Not found', status=404))
        import requests
        with pytest.raises(requests.HTTPError):
            web.download_file_from_url('https://x.org/missing.pdf', destination=str(tmp_path))
        assert list(tmp_path.iterdir()) == []

    def test_an_interrupted_stream_leaves_no_partial_file(self, monkeypatch, tmp_path):
        class Broken(FakeResponse):
            def iter_content(self, chunk_size=1):
                yield b'%PDF'
                raise ConnectionError('dropped')
        monkeypatch.setattr(web.requests, 'get', lambda *a, **k: Broken(b''))
        with pytest.raises(ConnectionError):
            web.download_file_from_url('https://x.org/coa.pdf', destination=str(tmp_path))
        assert list(tmp_path.iterdir()) == []

class FakeSession:
    def __init__(self, responses):
        self.responses, self.calls = list(responses), []

    def get(self, url, params=None, **kwargs):
        self.calls.append((url, params))
        return self.responses.pop(0)

class TestGoogleDrive:

    def test_the_confirmation_form_is_submitted(self, monkeypatch, tmp_path):
        page = ('<form id="download-form" action="https://drive.usercontent.google.com/download">'
                '<input type="hidden" name="id" value="FILE1234567"><input type="hidden" name="confirm" value="t">'
                '<input type="hidden" name="uuid" value="u-1"></form>')
        session = FakeSession([FakeResponse(page.encode(), content_type='text/html; charset=utf-8', text=page,
                                            url='https://drive.google.com/uc'), FakeResponse(b'PK\x03\x04zip')])
        monkeypatch.setattr(web.requests, 'Session', lambda: session)
        path = web.download_google_drive_file('https://drive.google.com/file/d/FILE1234567/view', str(tmp_path / 'f.zip'))
        assert __import__('pathlib').Path(path).read_bytes() == b'PK\x03\x04zip'
        assert session.calls[1] == ('https://drive.usercontent.google.com/download', {'id': 'FILE1234567', 'confirm': 't', 'uuid': 'u-1'})

    def test_the_cookie_token_is_still_honored(self, monkeypatch, tmp_path):
        session = FakeSession([FakeResponse(b'', content_type='text/html', cookies={'download_warning_x': 'TOKEN'}),
                               FakeResponse(b'data')])
        monkeypatch.setattr(web.requests, 'Session', lambda: session)
        web.download_google_drive_file('FILE1234567', str(tmp_path / 'f.bin'))
        assert session.calls[1][1]['confirm'] == 'TOKEN'

    def test_a_page_is_never_saved_as_the_file(self, monkeypatch, tmp_path):
        page = '<html>Sign in</html>'
        session = FakeSession([FakeResponse(page.encode(), content_type='text/html', text=page)])
        monkeypatch.setattr(web.requests, 'Session', lambda: session)
        with pytest.raises(ValueError, match='shared publicly'):
            web.download_google_drive_file('FILE1234567', str(tmp_path / 'f.bin'))
        assert list(tmp_path.iterdir()) == []

class TestBrowser:

    def test_selenium_missing_names_the_extra(self, monkeypatch):
        monkeypatch.setitem(sys.modules, 'selenium', None)
        with pytest.raises(ImportError, match=r'cannlytics\[web\]'):
            web.initialize_selenium()

    def test_an_unknown_browser_is_refused(self, monkeypatch):
        monkeypatch.setattr(web, '_selenium', lambda: types.SimpleNamespace())
        with pytest.raises(ValueError):
            web.initialize_selenium('firefox')

    def test_a_started_driver_is_quit_when_the_download_fails(self, monkeypatch):
        # Fake the Selenium modules the function imports, so this runs everywhere.
        for name in ('selenium', 'selenium.webdriver', 'selenium.webdriver.common', 'selenium.webdriver.common.by',
                     'selenium.webdriver.support', 'selenium.webdriver.support.expected_conditions',
                     'selenium.webdriver.support.ui'):
            module = types.ModuleType(name)
            module.By = types.SimpleNamespace(TAG_NAME='tag', ID='id', XPATH='xpath')
            module.WebDriverWait = object
            monkeypatch.setitem(sys.modules, name, module)
        quit_calls = []
        class Driver:
            def get(self, url):
                raise RuntimeError('page failed')
            def quit(self):
                quit_calls.append(True)
        monkeypatch.setattr(web, 'initialize_selenium', lambda **kwargs: Driver())
        with pytest.raises(RuntimeError):
            web.download_file_with_selenium('https://x.org', pause=0)
        assert quit_calls == [True]

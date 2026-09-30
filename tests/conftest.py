"""
Shared Fixtures for Cannlytics Package Test Suite
==================================================
Provides mock Firebase infrastructure, temp directories,
and sample data fixtures used across all test modules.

Usage:
    pytest tests/ -v --cov=cannlytics --cov-report=term-missing
"""
import os
import sys
from unittest.mock import MagicMock, patch

import pytest

# Ensure the package root is importable.
_PACKAGE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _PACKAGE_ROOT not in sys.path:
    sys.path.insert(0, _PACKAGE_ROOT)

# ╔══════════════════════════════════════════════════════════════════╗
# ║ Temp Directory Fixtures                                          ║
# ╚══════════════════════════════════════════════════════════════════╝

@pytest.fixture
def tmp_dir(tmp_path):
    """Provide a clean temporary directory."""
    return tmp_path

# ╔══════════════════════════════════════════════════════════════════╗
# ║ Firebase Mock Infrastructure                                     ║
# ╚══════════════════════════════════════════════════════════════════╝

class MockDocumentSnapshot:
    """Simulates a Firestore document snapshot."""

    def __init__(self, doc_id, data):
        self.id = doc_id
        self._data = data
        self.reference = MagicMock()

    def to_dict(self):
        return self._data

    def exists(self):
        return self._data is not None

class MockDocumentReference:
    """Simulates a Firestore document reference."""

    def __init__(self, doc_id='test_doc', data=None):
        self._id = doc_id
        self._data = data or {}

    def get(self):
        return MockDocumentSnapshot(self._id, self._data)

    def set(self, values, merge=False):
        if merge:
            self._data.update(values)
        else:
            self._data = values

    def delete(self):
        self._data = None

class MockCollectionReference:
    """Simulates a Firestore collection reference."""

    def __init__(self, docs=None):
        self._docs = docs or []
        self._filters = []

    def where(self, *args, **kwargs):
        return self

    def order_by(self, *args, **kwargs):
        return self

    def start_at(self, *args):
        return self

    def start_after(self, *args):
        return self

    def limit(self, n):
        self._docs = self._docs[:n]
        return self

    def stream(self):
        return iter(self._docs)

    def document(self, doc_id=None):
        for doc in self._docs:
            if doc.id == doc_id:
                return MockDocumentReference(doc.id, doc.to_dict())
        return MockDocumentReference(doc_id or 'auto_id', {})

class MockFirestoreClient:
    """Simulates a Firestore client with in-memory storage."""

    def __init__(self):
        self._data = {}

    def collection(self, name):
        return MockCollectionReference(
            [MockDocumentSnapshot(k, v) for k, v in self._data.get(name, {}).items()]
        )

    def document(self, path):
        parts = path.split('/')
        data = self._data
        for part in parts:
            data = data.get(part, {})
        return MockDocumentReference(parts[-1], data if isinstance(data, dict) else {})

    def batch(self):
        return MockBatch()

class MockBatch:
    """Simulates a Firestore batch writer."""

    def __init__(self):
        self._ops = []

    def set(self, ref, data, merge=False):
        self._ops.append(('set', ref, data, merge))

    def commit(self):
        self._ops.clear()

@pytest.fixture
def mock_db():
    """Provide a mock Firestore client."""
    return MockFirestoreClient()

@pytest.fixture
def mock_firestore_client():
    """Patch firestore.client() to return a mock."""
    mock_client = MockFirestoreClient()
    with patch('cannlytics.firebase.core.firestore.client', return_value=mock_client):
        with patch('cannlytics.firebase.core._default_database_id', None):
            yield mock_client

# ╔══════════════════════════════════════════════════════════════════╗
# ║ Storage Mock Fixtures                                            ║
# ╚══════════════════════════════════════════════════════════════════╝

class MockBlob:
    """Simulates a GCS blob."""

    def __init__(self, name):
        self.name = name
        self._data = None

    def upload_from_filename(self, path):
        with open(path, 'rb') as f:
            self._data = f.read()

    def upload_from_string(self, data, content_type=None):
        self._data = data

    def download_to_filename(self, path):
        with open(path, 'wb') as f:
            f.write(self._data or b'mock content')

    def generate_signed_url(self, expiration=None, method=None):
        return f'https://storage.googleapis.com/mock/{self.name}?sig=abc123'

    def make_public(self):
        pass

    @property
    def public_url(self):
        return f'https://storage.googleapis.com/mock/{self.name}'

class MockBucket:
    """Simulates a GCS bucket."""

    def __init__(self):
        self._blobs = {}

    def blob(self, name):
        if name not in self._blobs:
            self._blobs[name] = MockBlob(name)
        return self._blobs[name]

    def list_blobs(self, prefix=''):
        return [b for b in self._blobs.values() if b.name.startswith(prefix)]

    def delete_blob(self, name):
        self._blobs.pop(name, None)

    def rename_blob(self, blob, new_name):
        self._blobs[new_name] = blob
        blob.name = new_name

@pytest.fixture
def mock_storage_bucket():
    """Patch storage.bucket() to return a mock bucket."""
    bucket = MockBucket()
    with patch('cannlytics.firebase.storage.storage.bucket', return_value=bucket):
        yield bucket

# ╔══════════════════════════════════════════════════════════════════╗
# ║ Auth Mock Fixtures                                               ║
# ╚══════════════════════════════════════════════════════════════════╝

class MockUserRecord:
    """Simulates a Firebase Auth UserRecord."""

    def __init__(self, uid='test_uid', email='test@example.com', **kwargs):
        self.uid = uid
        self.email = email
        self.display_name = kwargs.get('display_name', 'Test User')
        self.photo_url = kwargs.get('photo_url', '')
        self.phone_number = kwargs.get('phone_number', None)
        self.email_verified = kwargs.get('email_verified', False)
        self.disabled = kwargs.get('disabled', False)
        self.custom_claims = kwargs.get('custom_claims', {})

@pytest.fixture
def mock_user():
    """Provide a mock Firebase user."""
    return MockUserRecord()

# ╔══════════════════════════════════════════════════════════════════╗
# ║ Sample Data Fixtures                                             ║
# ╚══════════════════════════════════════════════════════════════════╝

@pytest.fixture
def sample_lab_result():
    """Sample lab result for testing."""
    return {
        'id': 'abc123',
        'sample_id': 'SAMPLE-001',
        'product_name': 'Blue Dream',
        'product_type': 'flower',
        'strain_name': 'Blue Dream',
        'producer': 'Test Farm',
        'lab': 'SC Labs',
        'date_tested': '2026-01-15',
        'total_thc': 24.5,
        'total_cbd': 0.5,
        'status': 'pass',
        'state': 'ca',
    }

@pytest.fixture
def sample_lab_results_list(sample_lab_result):
    """List of sample lab results for batch operation tests."""
    results = []
    for i in range(5):
        result = sample_lab_result.copy()
        result['id'] = f'id{i:015d}'
        result['product_name'] = f'Product {i}'
        result['total_thc'] = 20.0 + i
        results.append(result)
    return results

# ╔══════════════════════════════════════════════════════════════════╗
# ║ Synthetic PDF Generation                                         ║
# ╠══════════════════════════════════════════════════════════════════╣
# ║ Generates structurally valid PDFs using reportlab for testing    ║
# ║ COA parsing, lab identification, and PDF validation.             ║
# ╚══════════════════════════════════════════════════════════════════╝

def _make_pdf(path: str, page_texts: list) -> str:
    """Generate a minimal PDF with the given text on each page."""
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas

    c = canvas.Canvas(path, pagesize=letter)
    for i, text in enumerate(page_texts):
        y = 700
        for line in text.split('\n'):
            c.drawString(72, y, line)
            y -= 14
        if i < len(page_texts) - 1:
            c.showPage()
    c.save()
    return path

@pytest.fixture
def make_pdf(tmp_path):
    """Factory fixture that creates synthetic PDFs."""
    def _factory(filename: str, page_texts: list) -> str:
        path = str(tmp_path / filename)
        return _make_pdf(path, page_texts)
    return _factory

# Simulated page 1 text for each lab in the registry.
LAB_PAGE_TEXTS = {
    'acrelabs': (
        'AcreLabs\n'
        'Acre Analytical\n'
        'Certificate of Analysis\n'
        '1823 Highway #546\n'
        'Sample: Sour Diesel Flower\n'
        'Date Tested: 2025-11-20'
    ),
    'cannabusiness': (
        'CANNABUSINESS LABORATORIES\n'
        'Certificate of Analysis\n'
        'cannabusinesslabs.us\n'
        'Sample: Emerald Fire Buds\n'
        'Date Tested: 2025-11-26'
    ),
    'kca': (
        'KCA Laboratories\n'
        'Certificate of Analysis\n'
        'kcalabs.com\n'
        'Sample: Goeing Blue Flower\n'
        'Date Tested: 2025-12-05'
    ),
    'confidentcannabis': (
        'Certificate of Analysis\n'
        'Sample: Blue Dream Flower\n'
        'Powered by Confident Cannabis\n'
        'confidentcannabis.com\n'
        'Producer: ABC Farms\n'
        'Batch: BD-2024-001\n'
        'Date Tested: 2024-06-15'
    ),
    'tagleaf': (
        'Certificate of Analysis\n'
        'Product: OG Kush Pre-Roll\n'
        'LIMS: lims.tagleaf.com\n'
        'TagLeaf LIMS Report\n'
        'Lab: Green Testing Labs\n'
        'Date: 2024-07-20'
    ),
    'sclabs': (
        'SC Labs\n'
        'Certificate of Analysis\n'
        'SC Laboratories, Inc.\n'
        'client.sclabs.com\n'
        'Sample: Gelato Live Resin\n'
        'Batch Number: GL-2024-042\n'
        'Date Tested: 2024-08-10\n'
        'Total THC: 78.4%'
    ),
    'kaycha': (
        'Kaycha Labs — Certificate of Analysis\n'
        'yourcoa.com\n'
        'Product Name: Sour Diesel Cartridge\n'
        'Kaycha Laboratory\n'
        'License: L-FL-12345\n'
        'Date Tested: 2024-09-05'
    ),
    'encore': (
        'Encore Labs\n'
        'Certificate of Analysis\n'
        'encorelabs.com\n'
        'Product: Wedding Cake Flower\n'
        'Batch: WC-100\n'
        'Total THC: 25.3%\n'
        'Date Tested: 2024-05-12'
    ),
    'terplife': (
        'TerpLife Labs\n'
        'Certificate of Analysis Report\n'
        'terplifelabs.com\n'
        'TL LABORATORIES\n'
        'Sample: Purple Punch Rosin\n'
        'Date: 2024-10-01'
    ),
    'acs': (
        'ACS Laboratory\n'
        'Certificate of Analysis\n'
        'acslabcannabis.com\n'
        '721 Cortaro Drive\n'
        'Sun City, AZ 85351\n'
        'Sample: Jack Herer Flower\n'
        'Batch: JH-2024-099'
    ),
    'smithers': (
        'Smithers CTS\n'
        'Certificate of Analysis\n'
        'smithers.com\n'
        'Smithers CTS Arizona\n'
        'Sample: Northern Lights Flower\n'
        'Batch: NL-2024-033\n'
        'Date Tested: 2024-11-15'
    ),
    'phytofarma': (
        'Phyto-Farma Labs\n'
        'Certificate of Analysis\n'
        'phytofarmalabs.com\n'
        'Sample: Diesel Kush Concentrate\n'
        'License: OCM-LAB-20240001\n'
        'Date Tested: 2024-12-01'
    ),
    'green_analytics': (
        'Green Analytics East\n'
        'Certificate of Analysis\n'
        'greenanalyticsllc.com\n'
        'Sample: Cherry Pie Pre-Roll\n'
        'Batch: CP-2024-077\n'
        'Date Tested: 2025-01-10'
    ),
}

@pytest.fixture
def lab_pdf_factory(tmp_path):
    """Factory that creates synthetic COA PDFs for each lab."""
    def _factory(lab_key: str) -> str:
        text = LAB_PAGE_TEXTS.get(lab_key)
        if text is None:
            raise ValueError(f'No fixture text for lab: {lab_key}')
        path = str(tmp_path / f'{lab_key}_coa.pdf')
        return _make_pdf(path, [text])
    return _factory

@pytest.fixture
def unrecognized_pdf(tmp_path):
    """A valid PDF that doesn't match any lab fingerprint."""
    text = (
        'Certificate of Analysis\n'
        'Unknown Laboratory Inc.\n'
        'Product: Mystery Strain\n'
        'Batch: UNK-001\n'
        'Date: 2024-01-01\n'
        'Total THC: 20.0%'
    )
    path = str(tmp_path / 'unrecognized_coa.pdf')
    return _make_pdf(path, [text])

@pytest.fixture
def multipage_pdf(tmp_path):
    """A valid multi-page COA PDF (3 pages)."""
    pages = [
        (
            'Certificate of Analysis — Page 1\n'
            'Product: Blue Dream Pre-Roll\n'
            'Producer: Sunshine Farms LLC\n'
            'Lab: Example Labs Inc.\n'
            'Date Tested: 2024-06-15\n'
            'Total THC: 22.5%\n'
            'Total CBD: 0.3%\n'
            'Status: Pass'
        ),
        (
            'Cannabinoid Profile\n'
            'Analyte         Result(%)  LOD(%)  LOQ(%)\n'
            'Delta-9-THC      2.10      0.01    0.03\n'
            'THCA            23.20      0.01    0.03\n'
            'CBD              0.05      0.01    0.03\n'
            'CBDA             0.28      0.01    0.03\n'
            'CBG              0.15      0.01    0.03\n'
            'Total THC       22.50\n'
            'Total CBD        0.30'
        ),
        (
            'Terpene Profile\n'
            'Analyte              Result(%)\n'
            'beta-Myrcene          0.45\n'
            'd-Limonene            0.32\n'
            'beta-Caryophyllene    0.28\n'
            'Linalool              0.15\n'
            'alpha-Pinene          0.12\n'
            'Total Terpenes        1.85'
        ),
    ]
    path = str(tmp_path / 'multipage_coa.pdf')
    return _make_pdf(path, pages)

# ╔══════════════════════════════════════════════════════════════════╗
# ║ Invalid File Fixtures                                            ║
# ╚══════════════════════════════════════════════════════════════════╝

@pytest.fixture
def empty_file(tmp_path):
    """A zero-byte file."""
    path = tmp_path / 'empty.pdf'
    path.touch()
    return str(path)

@pytest.fixture
def html_as_pdf(tmp_path):
    """An HTML file saved with a .pdf extension (common download error)."""
    path = tmp_path / 'fake.pdf'
    path.write_bytes(b'<html><body>404 Not Found</body></html>' + b' ' * 2000)
    return str(path)

@pytest.fixture
def tiny_pdf(tmp_path):
    """A file with a valid PDF header but too small to be a real COA."""
    path = tmp_path / 'tiny.pdf'
    path.write_bytes(b'%PDF-1.4 tiny content')
    return str(path)

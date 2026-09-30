"""
PDF Utilities for COA Parsing
Copyright (c) 2024-2026 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
Created: 10/7/2024
Updated: 3/19/2026
License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description:
    PDF validation, page-to-image conversion, text extraction,
    image encoding, and JSON parsing utilities used by the COAdoc
    hybrid parsing engine.

    This module is the lowest-level layer in the COA parsing stack.
    It has no dependencies on other ``cannlytics.data.coas`` modules
    (schema, config, registry, prompts, ai_client, parser) — only
    on the Python standard library plus ``pdfplumber`` and ``Pillow``.

    Public API:
        PDF Validation:
            - is_valid_pdf(path) → (bool, reason)
            - InvalidPDFCache — persistent set of known-bad PDF hashes

        PDF Content:
            - get_pdf_info(path) → dict with page count, text, analyses
            - get_pdf_pages_as_images(path, ...) → list of JPEG paths
            - extract_pdf_text(path, keywords) → str

        Encoding / JSON:
            - encode_image(path) → base64 string
            - extract_json(text) → dict or None
            - make_schema_strict(schema) → mutates in place

        Windows Long Path Support:
            - long_path(path) → Windows-safe path string

        JSON Schema Hints (for Anthropic prompt engineering):
            - metadata_json_hint() → str
            - analysis_json_hint() → str
"""
# Standard imports:
import base64
import json
import logging
import os
import platform
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

# External imports (optional — graceful degradation):
try:
    import pdfplumber
except ImportError:
    pdfplumber = None

try:
    from PIL import Image
except ImportError:
    Image = None


# ╔══════════════════════════════════════════════════════════════════╗
# ║ Windows Long Path Support                                        ║
# ╚══════════════════════════════════════════════════════════════════╝

IS_WINDOWS = platform.system() == 'Windows'
WIN_MAX_PATH = 259  # Effective limit (260 minus null terminator).


def long_path(path: str) -> str:
    """Prepend the Windows extended-length path prefix if needed.

    Windows has a default MAX_PATH of 260 characters. Cannabis COA
    files from PRRs often have deeply nested directories and verbose
    filenames that exceed this limit. The ``\\\\?\\`` prefix enables
    paths up to 32,767 characters.

    On non-Windows systems this is a no-op.
    """
    if not IS_WINDOWS:
        return path
    path = str(path)
    if path.startswith('\\\\?\\'):
        return path
    abs_path = os.path.abspath(path)
    if len(abs_path) > WIN_MAX_PATH:
        return f'\\\\?\\{abs_path}'
    return abs_path


def safe_file_size(path: str, min_size: int = 21_000) -> bool:
    """Check if a file meets the minimum size, handling long paths."""
    try:
        return os.path.getsize(long_path(path)) >= min_size
    except (OSError, FileNotFoundError):
        return False


# ╔══════════════════════════════════════════════════════════════════╗
# ║ PDF Validity Detection                                           ║
# ╚══════════════════════════════════════════════════════════════════╝

MIN_VALID_PDF_SIZE = 1_024  # 1 KB — real COAs are typically 50KB+.


def is_valid_pdf(path: str) -> Tuple[bool, str]:
    """Fast structural validation of a PDF file.

    Performs four progressively more expensive checks:

      1. **Header check** (~0.01ms): Verify ``%PDF-`` magic number.
      2. **Size check** (~0.01ms): Reject below ``MIN_VALID_PDF_SIZE``.
      3. **Structure check** (~1-5ms): Open with ``pdfplumber``, verify pages.
      4. **Content access check** (~5-20ms): Read page 1 dimensions and text.

    Args:
        path: Filesystem path to the PDF file.

    Returns:
        Tuple of (is_valid, reason). ``reason`` is ``''`` if valid,
        or a short diagnostic: ``'not_pdf_header'``, ``'too_small'``,
        ``'empty_file'``, ``'no_pages'``, ``'corrupt'``,
        ``'corrupt_pages'``, ``'unreadable'``.
    """
    safe_path = long_path(path)

    # ── Check 1: File existence and size ──────────────────────
    try:
        file_size = os.path.getsize(safe_path)
    except (OSError, FileNotFoundError):
        return False, 'unreadable'

    if file_size == 0:
        return False, 'empty_file'

    if file_size < MIN_VALID_PDF_SIZE:
        return False, 'too_small'

    # ── Check 2: PDF magic number ─────────────────────────────
    try:
        with open(safe_path, 'rb') as f:
            header = f.read(5)
    except (OSError, PermissionError):
        return False, 'unreadable'

    if header != b'%PDF-':
        return False, 'not_pdf_header'

    # ── Check 3: Structural integrity via pdfplumber ──────────
    if pdfplumber is None:
        # Can't validate without pdfplumber; assume valid.
        return True, ''

    try:
        with pdfplumber.open(safe_path) as pdf:
            if not pdf.pages:
                return False, 'no_pages'

            # ── Check 4: Page content accessibility ───────────
            try:
                page = pdf.pages[0]
                _ = page.width
                _ = page.height
                _ = page.extract_text()
            except Exception:
                return False, 'corrupt_pages'

    except Exception:
        return False, 'corrupt'

    return True, ''


class InvalidPDFCache:
    """Persistent set of known-invalid PDF hashes.

    Stores one SHA-256 hash per line in a plain text file. Designed
    for fast ``in`` checks (O(1) set lookup) to skip known-bad PDFs
    without re-validating on every run.

    Thread safety: Not required (single-threaded pipeline).
    """

    def __init__(self, cache_path: str):
        self.path = Path(cache_path)
        self._hashes: set = set()
        self._load()

    def _load(self):
        """Load existing invalid hashes from disk."""
        if self.path.exists():
            with open(self.path, 'r') as f:
                for line in f:
                    h = line.strip()
                    if h and not h.startswith('#'):
                        self._hashes.add(h)

    def __contains__(self, pdf_hash: str) -> bool:
        return pdf_hash in self._hashes

    def __len__(self) -> int:
        return len(self._hashes)

    def add(self, pdf_hash: str, reason: str = ''):
        """Add an invalid hash and flush to disk immediately."""
        if pdf_hash in self._hashes:
            return
        self._hashes.add(pdf_hash)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.path, 'a') as f:
            f.write(f'{pdf_hash}\n')

    def remove(self, pdf_hash: str):
        """Remove a hash (e.g., after re-downloading a valid copy)."""
        self._hashes.discard(pdf_hash)
        self._rewrite()

    def _rewrite(self):
        """Rewrite the file from the in-memory set."""
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.path, 'w') as f:
            f.write('# Invalid PDF hashes — generated by COAdoc\n')
            for h in sorted(self._hashes):
                f.write(f'{h}\n')


# ╔══════════════════════════════════════════════════════════════════╗
# ║ PDF Content Utilities                                            ║
# ╚══════════════════════════════════════════════════════════════════╝

def get_pdf_info(
        pdf_path: str,
        analysis_configs: Optional[Dict] = None,
    ) -> Dict:
    """Get basic info about a PDF (page count, text presence, analyses).

    Args:
        pdf_path: Path to the PDF file.
        analysis_configs: Optional analysis keyword config dict.
            Defaults to importing from ``cannlytics.data.coas.schema``.

    Returns:
        Dict with ``num_pages``, ``has_text``, ``first_page_text``,
        ``detected_analyses``, and optionally ``error``.
    """
    if pdfplumber is None:
        return {'num_pages': 0, 'has_text': False, 'error': 'pdfplumber not installed'}

    # Lazy import to avoid circular dependency.
    if analysis_configs is None:
        from cannlytics.data.coas.schema import ANALYSIS_CONFIGS
        analysis_configs = ANALYSIS_CONFIGS

    try:
        with pdfplumber.open(long_path(pdf_path)) as pdf:
            num_pages = len(pdf.pages)
            first_page_text = (pdf.pages[0].extract_text() or '') if pdf.pages else ''
            has_text = len(first_page_text) > 50

            # Detect analyses mentioned in first 5 pages.
            all_text = ''
            for page in pdf.pages[:5]:
                t = page.extract_text() or ''
                all_text += ' ' + t.lower()

            detected_analyses = []
            for analysis, config in analysis_configs.items():
                for keyword in config['keywords']:
                    if keyword.lower() in all_text:
                        detected_analyses.append(analysis)
                        break

            return {
                'num_pages': num_pages,
                'has_text': has_text,
                'first_page_text': first_page_text[:500],
                'detected_analyses': detected_analyses,
            }
    except Exception as e:
        return {'num_pages': 0, 'has_text': False, 'error': str(e)}


def get_pdf_pages_as_images(
        pdf_path: str,
        page_indexes: Union[int, List[int], str] = 0,
        keywords: Optional[List[str]] = None,
        output_dir: Optional[str] = None,
        resolution: int = 300,
    ) -> List[str]:
    """Convert PDF pages to JPEG images.

    Args:
        pdf_path: Path to the PDF file.
        page_indexes: Which pages to convert. Can be:
            - ``int``: A single page index (0-based).
            - ``list[int]``: Specific page indexes.
            - ``'all'``: All pages.
            - ``'keywords'``: Pages containing any keyword.
        keywords: Keywords for page selection (used when
            ``page_indexes='keywords'``).
        output_dir: Directory for output images. Created if needed.
            Defaults to a new temp directory.
        resolution: Image resolution in DPI (default 300).

    Returns:
        List of paths to the generated JPEG files.
    """
    if pdfplumber is None:
        return []

    if output_dir is None:
        output_dir = tempfile.mkdtemp()
    os.makedirs(output_dir, exist_ok=True)

    pdf_name = os.path.splitext(os.path.basename(pdf_path))[0]
    image_paths = []

    try:
        with pdfplumber.open(long_path(pdf_path)) as pdf:
            total_pages = len(pdf.pages)

            # Determine which pages to process.
            if isinstance(page_indexes, int):
                pages = [min(page_indexes, total_pages - 1)]
            elif isinstance(page_indexes, list):
                pages = [p for p in page_indexes if p < total_pages]
            elif page_indexes == 'all':
                pages = list(range(total_pages))
            elif page_indexes == 'keywords' and keywords:
                pages = []
                for i in range(total_pages):
                    text = (pdf.pages[i].extract_text() or '').lower()
                    if any(kw.lower() in text for kw in keywords):
                        pages.append(i)
                pages = sorted(set(pages))
                if not pages:
                    pages = [0]
            else:
                pages = [0]

            for idx in pages:
                out_path = os.path.join(
                    output_dir,
                    f'{pdf_name}_p{idx + 1:03d}.jpeg',
                )
                pdf.pages[idx].to_image(resolution=resolution).save(out_path)
                image_paths.append(out_path)

    except Exception as e:
        logging.getLogger(__name__).error(f'PDF image conversion failed: {e}')

    return image_paths


def extract_pdf_text(
        pdf_path: str,
        keywords: Optional[List[str]] = None,
    ) -> str:
    """Extract text from PDF pages, optionally filtering by keywords.

    Args:
        pdf_path: Path to the PDF file.
        keywords: If provided, only return text from pages that
            contain at least one keyword. Falls back to page 1
            if no keyword matches.

    Returns:
        Extracted text string (may be empty).
    """
    if pdfplumber is None:
        return ''

    try:
        with pdfplumber.open(long_path(pdf_path)) as pdf:
            if not pdf.pages:
                return ''
            if not keywords:
                return pdf.pages[0].extract_text() or ''
            texts = []
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    text_lower = text.lower()
                    if any(kw.lower() in text_lower for kw in keywords):
                        texts.append(text)
            return '\n\n'.join(texts) if texts else (pdf.pages[0].extract_text() or '')
    except Exception:
        return ''


# ╔══════════════════════════════════════════════════════════════════╗
# ║ Image Encoding & JSON Extraction                                 ║
# ╚══════════════════════════════════════════════════════════════════╝

def encode_image(image_path: str) -> str:
    """Encode an image file as a base64 string.

    Args:
        image_path: Path to an image file (JPEG, PNG, etc.).

    Returns:
        Base64-encoded string of the image bytes.
    """
    with open(image_path, 'rb') as f:
        return base64.b64encode(f.read()).decode('utf-8')


def extract_json(text: str) -> Optional[Dict]:
    """Extract JSON from an AI response, handling markdown code fences.

    Tries three strategies:
      1. Parse the entire text as JSON.
      2. Strip markdown code fences and retry.
      3. Find the first ``{`` to last ``}`` substring and parse.

    Args:
        text: Raw text from an AI model response.

    Returns:
        Parsed dict, or None if no valid JSON found.
    """
    if not text:
        return None
    text = text.strip()

    # Remove markdown code fences.
    if text.startswith('```'):
        lines = text.split('\n')
        lines = [l for l in lines if not l.strip().startswith('```')]
        text = '\n'.join(lines).strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # Try to find JSON within the text.
        start = text.find('{')
        end = text.rfind('}')
        if start >= 0 and end > start:
            try:
                return json.loads(text[start:end + 1])
            except json.JSONDecodeError:
                pass
    return None


def make_schema_strict(schema: Dict) -> None:
    """Make a JSON schema compatible with OpenAI structured output.

    OpenAI's Responses API structured output requires every object
    in the JSON schema to:
      1. Set ``additionalProperties`` to ``false``.
      2. List ALL property keys in ``required``.

    Pydantic's ``model_json_schema()`` omits both for Optional fields.
    This function mutates the schema in-place.
    """
    if not isinstance(schema, dict):
        return

    for defn in schema.get('$defs', {}).values():
        make_schema_strict(defn)

    if schema.get('type') == 'object':
        schema['additionalProperties'] = False
        if 'properties' in schema:
            schema['required'] = list(schema['properties'].keys())

    for prop in schema.get('properties', {}).values():
        make_schema_strict(prop)

    if 'items' in schema:
        make_schema_strict(schema['items'])

    for key in ('anyOf', 'oneOf', 'allOf'):
        for variant in schema.get(key, []):
            make_schema_strict(variant)


# ╔══════════════════════════════════════════════════════════════════╗
# ║ JSON Schema Hints (Anthropic prompt engineering)                 ║
# ╚══════════════════════════════════════════════════════════════════╝

def metadata_json_hint() -> str:
    """Return a JSON schema hint for metadata extraction.

    Used in Anthropic prompts where structured output is not available.
    Totals use ``null`` (not ``0.0``) to signal "not found".
    """
    return json.dumps({
        'product_name': 'str', 'strain_name': 'str', 'product_type': 'str',
        'date_tested': 'YYYY-MM-DD', 'date_received': 'YYYY-MM-DD',
        'date_collected': 'YYYY-MM-DD',
        'batch_number': 'str', 'batch_size': 0.0,
        'lab': 'str', 'lab_license_number': 'str',
        'lab_address': 'str', 'lab_city': 'str', 'lab_state': 'str', 'lab_zipcode': 'str',
        'producer': 'str', 'producer_street': 'str', 'producer_city': 'str',
        'producer_state': 'str', 'producer_zipcode': 'str',
        'producer_license_number': 'str',
        'distributor': 'str', 'distributor_license_number': 'str',
        'sample_id': 'str', 'sample_weight': 0.0,
        'total_cannabinoids': None, 'total_cbd': None, 'total_thc': None,
        'total_terpenes': None, 'status': 'str',
        'analyses': ['cannabinoids', 'terpenes'],
    }, indent=2)


def analysis_json_hint() -> str:
    """Return a JSON schema hint for analysis extraction."""
    return json.dumps({
        'analysis': 'str',
        'results': [
            {'key': 'str', 'name': 'str', 'value': 0.0, 'units': 'str',
             'limit': 0.0, 'lod': 0.0, 'loq': 0.0, 'status': 'str'}
        ],
    }, indent=2)

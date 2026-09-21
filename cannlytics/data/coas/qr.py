"""
QR Code Scanning for COA Parsing
Copyright (c) 2025-2026 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
Created: 2/26/2026
Updated: 3/19/2026
License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description:
    QR code detection and URL extraction from COA PDFs and images.
    This module provides the QR scanning primitives used by the
    COAdoc parser and the batch ``scan_qrcodes.py`` pipeline.

    QRustie (Rust) Integration:
        The preferred decoder is ``qrustie``, a Rust binary that uses
        dual decoding engines (rqrr + bardecoder) with 4 preprocessing
        strategies × 2 engines = 8 decode attempts per image. It
        produces clean errors instead of the segfaults that Python QR
        decoders (pyzbar) trigger on certain COA documents.

        ``qrustie`` is an *optional runtime dependency* — it is NOT
        installed via pip. Users who need QR scanning either:
          - Set the ``QRUSTIE_PATH`` environment variable
          - Place it on the system ``PATH``
          - Pass ``qrustie_path=`` explicitly
          - Build it from source and opt in to the working-directory
            search (``allow_cwd=True`` or
            ``CANNLYTICS_QRUSTIE_ALLOW_CWD=1``)

        Binary discovery deliberately does NOT search the working
        directory by default. See ``find_qrustie()`` for the reasoning.

        When ``qrustie`` is not found, the module falls back to
        Python decoders (pyzbar, zxingcpp) if available.

    Two-Phase Detection Strategy:
        Phase 1: Full-page decode — send the full page image to the
                 decoder. Works for most COAs where the QR code is
                 prominent.
        Phase 2: Region-crop decode — if Phase 1 fails and OpenCV
                 is available, use contour detection to find and crop
                 square-ish regions likely to be QR codes. Resize each
                 to 512px width and decode individually. This handles
                 COAs where the QR code is small.

    Public API:
        High-level:
            - scan_qr(source, ...) → Optional[str]
                One-call convenience: PDF/image → coa_url or None.

        Low-level:
            - find_qrustie(explicit_path, allow_cwd) → Optional[str]
                Locate the qrustie binary on disk, safely.
            - decode_qr_qrustie(image_path, ...) → dict
                Decode using the Rust binary.
            - decode_qr_python(image_path) → dict
                Decode using Python fallback (pyzbar/zxingcpp).
            - extract_qr_regions(image_path, ...) → list[str]
                Crop likely QR regions using OpenCV contour detection.
            - is_url(text) → bool
                Check if a string is a valid HTTP(S) URL.

    Usage::

        from cannlytics.data.coas.qr import scan_qr

        # From a PDF (extracts page 1, scans for QR, returns URL).
        url = scan_qr('path/to/coa.pdf')

        # From an image.
        url = scan_qr('path/to/coa_page1.jpeg')

        # With explicit qrustie path.
        url = scan_qr('coa.pdf', qrustie_path='/usr/local/bin/qrustie')
"""
# Standard imports:
import json
import logging
import os
import platform
import stat
import subprocess
import tempfile
from typing import Dict, List, Optional, Tuple
from urllib.parse import urlparse

# Optional imports (enhance detection when available).
try:
    import cv2
    import numpy as np
    _OPENCV_AVAILABLE = True
except ImportError:
    _OPENCV_AVAILABLE = False


# ╔══════════════════════════════════════════════════════════════════╗
# ║ Configuration Constants                                          ║
# ╚══════════════════════════════════════════════════════════════════╝

_IS_WINDOWS = platform.system() == 'Windows'

# Image resolution for PDF page rendering (DPI).
# 200 DPI balances quality with speed for QR detection.
_RENDER_DPI = 200

# Maximum time (seconds) to wait for qrustie to decode a single image.
_QRUSTIE_TIMEOUT = 30

# Base name of the binary, without a file extension.
_QRUSTIE_BINARY_NAME = 'qrustie'

# Executable file extensions to try on Windows when PATHEXT is unset.
_WINDOWS_DEFAULT_PATHEXT = '.COM;.EXE;.BAT;.CMD'

# Build-tree paths, relative to the current working directory.
#
# SECURITY: these are NOT searched by default. A relative path resolves
# against the process working directory, so searching them by default
# means that parsing a COA from an untrusted directory -- an extracted
# archive, a shared downloads folder, a CI checkout -- would execute any
# file named `qrustie` that happened to be sitting there. That is the
# same defect class as putting `.` on PATH.
#
# They remain available for local qrustie development, behind an
# explicit opt-in: pass ``allow_cwd=True`` or set
# ``CANNLYTICS_QRUSTIE_ALLOW_CWD=1``.
_QRUSTIE_CWD_SEARCH_PATHS = [
    'qrustie/target/release/qrustie',
    'qrustie/target/debug/qrustie',
    '../qrustie/target/release/qrustie',
]

# Environment variable that opts in to the CWD-relative search above.
_QRUSTIE_ALLOW_CWD_ENV = 'CANNLYTICS_QRUSTIE_ALLOW_CWD'


# ╔══════════════════════════════════════════════════════════════════╗
# ║ QRustie Binary Discovery                                        ║
# ╚══════════════════════════════════════════════════════════════════╝

def _executable_names() -> List[str]:
    """Candidate file names for the qrustie binary on this platform.

    On POSIX this is just ``qrustie``. On Windows it is ``qrustie``
    plus each ``PATHEXT`` suffix, matching how the shell resolves a
    bare command name.
    """
    if not _IS_WINDOWS:
        return [_QRUSTIE_BINARY_NAME]
    raw = os.environ.get('PATHEXT') or _WINDOWS_DEFAULT_PATHEXT
    names = []
    for ext in raw.split(os.pathsep):
        ext = ext.strip()
        if ext:
            names.append(_QRUSTIE_BINARY_NAME + ext.lower())
    # Bare name last, so an extensioned match is preferred.
    names.append(_QRUSTIE_BINARY_NAME)
    # Preserve order, drop duplicates.
    return list(dict.fromkeys(names))


def _is_executable_file(path: str) -> bool:
    """Whether ``path`` is a regular file we are allowed to execute.

    Rejects directories, FIFOs, sockets, and device nodes, any of which
    would otherwise be handed to ``subprocess.run``. On POSIX the
    execute bit is required. On Windows the execute bit is meaningless,
    so an executable extension is required instead.
    """
    try:
        st = os.stat(path)
    except OSError:
        return False
    if not stat.S_ISREG(st.st_mode):
        return False
    if _IS_WINDOWS:
        ext = os.path.splitext(path)[1].lower()
        allowed = {
            e.strip().lower()
            for e in (os.environ.get('PATHEXT') or _WINDOWS_DEFAULT_PATHEXT).split(os.pathsep)
            if e.strip()
        }
        return ext in allowed
    return os.access(path, os.X_OK)


def _resolve_named_path(path: Optional[str]) -> Optional[str]:
    """Resolve a path the caller named explicitly.

    Used for the ``explicit_path`` argument and the ``QRUSTIE_PATH``
    environment variable. Both are deliberate, trusted statements of
    intent: the operator named this exact file, so the execute bit is
    not required here -- requiring it would add no security (they chose
    the file) while breaking legitimate wrapper scripts.

    The path is still required to be a regular file, and is returned
    absolute so that nothing downstream re-resolves it against the
    working directory.
    """
    if not path:
        return None
    expanded = os.path.abspath(os.path.expanduser(path))
    candidates = [expanded]
    if _IS_WINDOWS and not os.path.splitext(expanded)[1]:
        candidates = [expanded + ext for ext in
                      ('.exe', '.bat', '.cmd', '.com')] + candidates
    for candidate in candidates:
        try:
            if stat.S_ISREG(os.stat(candidate).st_mode):
                return candidate
        except OSError:
            continue
    return None


def _search_directories(allow_cwd: bool = False) -> List[str]:
    """Absolute directories to search for the binary, in order.

    Entries of ``PATH`` that resolve against the working directory --
    an empty entry, ``.``, or any other relative path -- are dropped
    unless ``allow_cwd`` is set. An empty ``PATH`` entry means "current
    directory" on POSIX, so it is exactly as dangerous as a literal
    ``.`` and is filtered the same way.
    """
    directories = []
    raw = os.environ.get('PATH', os.defpath)
    for entry in raw.split(os.pathsep):
        if not entry:
            if allow_cwd:
                directories.append(os.getcwd())
            continue
        expanded = os.path.expanduser(entry)
        if not os.path.isabs(expanded):
            if allow_cwd:
                directories.append(os.path.abspath(expanded))
            continue
        directories.append(expanded)
    return list(dict.fromkeys(directories))


def find_qrustie(
        explicit_path: Optional[str] = None,
        allow_cwd: bool = False,
    ) -> Optional[str]:
    """Locate the qrustie Rust binary.

    Searches in order:
      1. ``explicit_path``, if given.
      2. The ``QRUSTIE_PATH`` environment variable.
      3. Absolute directories on the system ``PATH``.
      4. Build-tree paths relative to the working directory --
         **only** when ``allow_cwd`` is set.

    Args:
        explicit_path: Path to the binary, named by the caller.
        allow_cwd: Also search working-directory-relative build-tree
            paths (``qrustie/target/release/qrustie`` and friends), and
            honour relative ``PATH`` entries. Defaults to ``False``.
            Set ``CANNLYTICS_QRUSTIE_ALLOW_CWD=1`` to enable it for a
            whole session without changing code.

    Returns:
        Absolute path to the qrustie binary, or ``None`` if not found.

    Security:
        Discovered candidates -- anything found on ``PATH`` or in the
        working directory -- must be regular files with the execute bit
        set, and the resolved path is always absolute. Working-directory
        candidates are off by default, because a relative candidate means
        that parsing a COA from a directory an attacker can write to
        would execute a file of their choosing. Enable ``allow_cwd``
        only in a directory you control, such as your own qrustie
        checkout.
    """
    # 1. Caller-named path.
    found = _resolve_named_path(explicit_path)
    if found:
        return found

    # 2. Operator-set environment variable.
    found = _resolve_named_path(os.environ.get('QRUSTIE_PATH'))
    if found:
        return found

    if not allow_cwd:
        allow_cwd = os.environ.get(_QRUSTIE_ALLOW_CWD_ENV, '').strip().lower() in (
            '1', 'true', 'yes', 'on',
        )

    # 3. Absolute directories on PATH.
    #
    # The search is done explicitly rather than by delegating to
    # shutil.which(), because on Windows shutil.which() inserts the
    # current directory into the search path (see
    # shutil._win_path_needs_curdir), which would silently reintroduce
    # the working-directory hole this function exists to close.
    names = _executable_names()
    for directory in _search_directories(allow_cwd=allow_cwd):
        for name in names:
            candidate = os.path.join(directory, name)
            if _is_executable_file(candidate):
                return os.path.abspath(candidate)

    # 4. Build-tree paths, relative to the working directory. Opt-in.
    if allow_cwd:
        for relative_path in _QRUSTIE_CWD_SEARCH_PATHS:
            for candidate in (relative_path, relative_path + '.exe') \
                    if _IS_WINDOWS else (relative_path,):
                absolute = os.path.abspath(os.path.expanduser(candidate))
                if _is_executable_file(absolute):
                    return absolute

    return None


# ╔══════════════════════════════════════════════════════════════════╗
# ║ URL Validation                                                   ║
# ╚══════════════════════════════════════════════════════════════════╝

def is_url(text: str) -> bool:
    """Check if a string looks like a valid HTTP(S) URL.

    Args:
        text: String to check.

    Returns:
        ``True`` if the string parses as a valid URL with
        ``http`` or ``https`` scheme and a non-empty netloc.
    """
    if not text:
        return False
    try:
        parsed = urlparse(text.strip())
        return parsed.scheme in ('http', 'https') and bool(parsed.netloc)
    except Exception:
        return False


# ╔══════════════════════════════════════════════════════════════════╗
# ║ QR Decoding — QRustie (Rust)                                    ║
# ╚══════════════════════════════════════════════════════════════════╝

def decode_qr_qrustie(
        image_path: str,
        qrustie_path: str,
        timeout: int = _QRUSTIE_TIMEOUT,
    ) -> Dict:
    """Decode QR codes from an image using the qrustie Rust binary.

    ``qrustie`` applies 4 preprocessing strategies × 2 decoder
    engines = 8 decode attempts per image. The first successful
    decode is returned immediately.

    Args:
        image_path: Path to the image file.
        qrustie_path: Absolute path to the qrustie binary.
        timeout: Maximum seconds to wait for decoding.

    Returns:
        Dict with keys: ``found``, ``data``, ``decoder``,
        ``strategy``, ``error``.
    """
    try:
        # S603: the command is a fixed argument vector, never a shell
        # string. `qrustie_path` is expected to come from
        # `find_qrustie()`, which returns only absolute paths to regular
        # executable files and does not search the working directory
        # unless explicitly asked to. `image_path` and the flags are
        # arguments, not commands, so they cannot alter what is run.
        result = subprocess.run(  # noqa: S603
            [qrustie_path, '--input', image_path, '--first-only'],
            capture_output=True,
            text=True,
            timeout=timeout,
            # Explicit: never route through a shell, and never inherit
            # a shell's own working-directory resolution.
            shell=False,
        )
        if result.stdout.strip():
            return json.loads(result.stdout.strip())
        return {
            'found': False,
            'data': [],
            'decoder': '',
            'strategy': '',
            'error': result.stderr.strip() if result.stderr else '',
        }
    except subprocess.TimeoutExpired:
        return {
            'found': False, 'data': [], 'decoder': '',
            'strategy': '', 'error': f'Timeout after {timeout}s',
        }
    except json.JSONDecodeError as e:
        return {
            'found': False, 'data': [], 'decoder': '',
            'strategy': '', 'error': f'JSON parse error: {e}',
        }
    except Exception as e:
        return {
            'found': False, 'data': [], 'decoder': '',
            'strategy': '', 'error': str(e),
        }


# ╔══════════════════════════════════════════════════════════════════╗
# ║ QR Decoding — Python Fallback                                   ║
# ╚══════════════════════════════════════════════════════════════════╝

def decode_qr_python(image_path: str) -> Dict:
    """Fallback QR decoder using Python libraries.

    Tries decoders in order:
      1. ``pyzbar`` (most common Python QR decoder).
      2. ``zxingcpp`` (alternative with broader format support).

    These are optional dependencies — the function returns a
    clean "not available" result if neither is installed.

    Args:
        image_path: Path to the image file.

    Returns:
        Dict with keys: ``found``, ``data``, ``decoder``,
        ``strategy``, ``error``.
    """
    # Try pyzbar first.
    try:
        from pyzbar import pyzbar
        from PIL import Image
        img = Image.open(image_path)
        decoded = pyzbar.decode(img)
        if decoded:
            data = [d.data.decode('utf-8') for d in decoded]
            return {
                'found': True,
                'data': data,
                'decoder': 'pyzbar',
                'strategy': 'direct',
                'error': '',
            }
    except ImportError:
        pass
    except Exception:
        pass

    # Try zxingcpp.
    try:
        import zxingcpp
        from PIL import Image
        img = Image.open(image_path)
        results = zxingcpp.read_barcodes(img)
        if results:
            data = [r.text for r in results if r.text]
            if data:
                return {
                    'found': True,
                    'data': data,
                    'decoder': 'zxingcpp',
                    'strategy': 'direct',
                    'error': '',
                }
    except ImportError:
        pass
    except Exception:
        pass

    return {
        'found': False,
        'data': [],
        'decoder': '',
        'strategy': '',
        'error': 'No Python QR decoder available (install pyzbar or zxingcpp)',
    }


# ╔══════════════════════════════════════════════════════════════════╗
# ║ Region Extraction (OpenCV)                                       ║
# ╚══════════════════════════════════════════════════════════════════╝

def extract_qr_regions(
        image_path: str,
        output_dir: str,
        min_area: int = 1000,
        ar_range: Tuple[float, float] = (0.75, 1.35),
        resize_width: int = 512,
    ) -> List[str]:
    """Extract likely QR code regions from an image using contour detection.

    Uses OpenCV morphological operations to find square-ish,
    high-contrast regions that are likely QR codes. Each region is
    cropped, resized, and saved as a separate image for decoding.

    This technique dramatically improves QR detection on full COA
    pages where the QR code is small relative to the document.

    Requires ``opencv-python`` (optional dependency). Returns an
    empty list if OpenCV is not installed.

    Args:
        image_path: Path to the source image (full COA page).
        output_dir: Directory to save cropped region images.
        min_area: Minimum contour area (pixels²).
        ar_range: Acceptable aspect ratio range for square-ish regions.
        resize_width: Width to resize cropped regions to (pixels).

    Returns:
        List of paths to cropped QR region images.
    """
    if not _OPENCV_AVAILABLE:
        return []

    try:
        image = cv2.imread(image_path)
        if image is None:
            return []

        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (9, 9), 0)
        thresh = cv2.threshold(
            blur, 0, 255,
            cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU,
        )[1]

        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
        closed = cv2.morphologyEx(
            thresh, cv2.MORPH_CLOSE, kernel, iterations=2,
        )

        contours, _ = cv2.findContours(
            closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE,
        )

        regions = []
        ar_min, ar_max = ar_range

        for contour in contours:
            peri = cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, 0.04 * peri, True)
            x, y, w, h = cv2.boundingRect(approx)
            area = cv2.contourArea(contour)
            ar = w / float(h) if h > 0 else 0

            if (len(approx) == 4
                    and area > min_area
                    and ar_min < ar < ar_max):
                cropped = image[y:y + h, x:x + w]
                h_resized = int(resize_width * (h / float(w)))
                resized = cv2.resize(
                    cropped,
                    (resize_width, h_resized),
                    interpolation=cv2.INTER_AREA,
                )
                region_path = os.path.join(
                    output_dir,
                    f'qr_region_{len(regions)}_{x}_{y}.png',
                )
                cv2.imwrite(region_path, resized)
                regions.append(region_path)

        return regions

    except Exception:
        return []


# ╔══════════════════════════════════════════════════════════════════╗
# ║ High-Level API: scan_qr()                                       ║
# ╚══════════════════════════════════════════════════════════════════╝

def scan_qr(
        source: str,
        qrustie_path: Optional[str] = None,
        allow_cwd: bool = False,
        page_index: int = 0,
        use_python_fallback: bool = True,
        use_region_crop: bool = True,
        resolution: int = _RENDER_DPI,
        logger: Optional[logging.Logger] = None,
    ) -> Optional[str]:
    """Scan a COA PDF or image for a QR code and extract its URL.

    This is the one-call convenience function for COAdoc and the
    Cannlytics API. It handles the full pipeline:
      1. Detect input type (PDF vs. image).
      2. If PDF, render page to a temporary JPEG.
      3. Try full-page decode (Phase 1).
      4. If failed, try region-crop decode (Phase 2, if OpenCV available).
      5. Validate that the decoded content is a URL.
      6. Return the ``coa_url`` or ``None``.

    Args:
        source: Path to a PDF file or image file.
        qrustie_path: Explicit path to the qrustie binary. If ``None``,
            searches ``QRUSTIE_PATH`` and the system ``PATH``.
        allow_cwd: Also search working-directory-relative build-tree
            paths for the binary. Off by default; see
            ``find_qrustie()`` for why.
        page_index: PDF page to scan (0-indexed, default 0 = first page).
        use_python_fallback: Fall back to Python decoders if qrustie
            is not available. Default ``True``.
        use_region_crop: Try OpenCV region-crop fallback if full-page
            decode fails. Default ``True``.
        resolution: DPI for PDF-to-image rendering. Default 200.
        logger: Optional logger for debug output.

    Returns:
        The decoded URL string, or ``None`` if no QR code URL was found.

    Example::

        from cannlytics.data.coas.qr import scan_qr

        url = scan_qr('path/to/coa.pdf')
        if url:
            print(f'COA URL: {url}')
    """
    _log = logger or logging.getLogger(__name__)

    # ── Resolve qrustie binary ────────────────────────────────
    qrustie = find_qrustie(qrustie_path, allow_cwd=allow_cwd)
    if not qrustie and not use_python_fallback:
        _log.warning('No QR decoder available (qrustie not found, Python fallback disabled)')
        return None

    # ── Determine the decode function ─────────────────────────
    def _decode(img_path: str) -> Dict:
        if qrustie:
            return decode_qr_qrustie(img_path, qrustie)
        elif use_python_fallback:
            return decode_qr_python(img_path)
        return {'found': False, 'data': [], 'decoder': '', 'strategy': '', 'error': 'No decoder'}

    # ── Resolve source to an image path ───────────────────────
    source_lower = source.lower()
    is_pdf = source_lower.endswith('.pdf')

    temp_dir = None
    image_path = None
    region_paths = []

    try:
        if is_pdf:
            # Import pdfplumber lazily (only for PDF input).
            try:
                import pdfplumber
            except ImportError:
                _log.error('pdfplumber required for PDF QR scanning')
                return None

            # Render PDF page to a temp JPEG.
            from cannlytics.data.coas.pdf_utils import long_path
            temp_dir = tempfile.mkdtemp(prefix='qr_scan_')
            pdf_name = os.path.splitext(os.path.basename(source))[0]
            image_path = os.path.join(temp_dir, f'{pdf_name}_p{page_index}.jpeg')
            try:
                with pdfplumber.open(long_path(source)) as pdf:
                    if page_index >= len(pdf.pages):
                        _log.debug(f'Page {page_index} not in PDF ({len(pdf.pages)} pages)')
                        return None
                    pdf.pages[page_index].to_image(resolution=resolution).save(image_path)
            except Exception as e:
                _log.debug(f'PDF page extraction failed: {e}')
                return None
        else:
            # Source is already an image.
            image_path = source

        if not image_path or not os.path.exists(image_path):
            return None

        # ── Phase 1: Full-page decode ─────────────────────────
        result = _decode(image_path)

        # ── Phase 2: Region-crop fallback ─────────────────────
        if not result.get('found') and use_region_crop and _OPENCV_AVAILABLE:
            crop_dir = temp_dir or tempfile.mkdtemp(prefix='qr_crop_')
            region_paths = extract_qr_regions(image_path, output_dir=crop_dir)
            for region_path in region_paths:
                region_result = _decode(region_path)
                if region_result.get('found'):
                    region_result['strategy'] = (
                        'cv2_crop+' + region_result.get('strategy', '')
                    )
                    result = region_result
                    break

        # ── Extract URL from QR data ──────────────────────────
        if result.get('found') and result.get('data'):
            qr_data = result['data'][0]
            if is_url(qr_data):
                return qr_data.strip()

        return None

    except Exception as e:
        _log.error(f'QR scan error: {e}')
        return None

    finally:
        # Clean up temp files.
        if temp_dir:
            import shutil
            shutil.rmtree(temp_dir, ignore_errors=True)
        for rp in region_paths:
            try:
                if rp and os.path.exists(rp) and not temp_dir:
                    os.remove(rp)
            except OSError:
                pass


def scan_qr_raw(
        source: str,
        qrustie_path: Optional[str] = None,
        allow_cwd: bool = False,
        page_index: int = 0,
        use_python_fallback: bool = True,
        use_region_crop: bool = True,
        resolution: int = _RENDER_DPI,
        logger: Optional[logging.Logger] = None,
    ) -> Dict:
    """Scan a COA for QR codes and return full decode details.

    Like ``scan_qr()`` but returns the complete decode result dict
    instead of just the URL. Useful when you need the raw QR data,
    decoder name, or strategy information.

    Args:
        Same as ``scan_qr()``.

    Returns:
        Dict with keys: ``coa_url``, ``qr_data``, ``decoder``,
        ``strategy``, ``error``.
    """
    _log = logger or logging.getLogger(__name__)

    qrustie = find_qrustie(qrustie_path, allow_cwd=allow_cwd)

    def _decode(img_path: str) -> Dict:
        if qrustie:
            return decode_qr_qrustie(img_path, qrustie)
        elif use_python_fallback:
            return decode_qr_python(img_path)
        return {'found': False, 'data': [], 'decoder': '', 'strategy': '', 'error': 'No decoder'}

    source_lower = source.lower()
    is_pdf = source_lower.endswith('.pdf')

    temp_dir = None
    image_path = None
    region_paths = []

    try:
        if is_pdf:
            try:
                import pdfplumber
            except ImportError:
                return {'coa_url': None, 'qr_data': None, 'decoder': '', 'strategy': '', 'error': 'pdfplumber not installed'}

            from cannlytics.data.coas.pdf_utils import long_path
            temp_dir = tempfile.mkdtemp(prefix='qr_scan_')
            pdf_name = os.path.splitext(os.path.basename(source))[0]
            image_path = os.path.join(temp_dir, f'{pdf_name}_p{page_index}.jpeg')
            try:
                with pdfplumber.open(long_path(source)) as pdf:
                    if page_index >= len(pdf.pages):
                        return {'coa_url': None, 'qr_data': None, 'decoder': '', 'strategy': '', 'error': f'Page {page_index} not in PDF'}
                    pdf.pages[page_index].to_image(resolution=resolution).save(image_path)
            except Exception as e:
                return {'coa_url': None, 'qr_data': None, 'decoder': '', 'strategy': '', 'error': str(e)}
        else:
            image_path = source

        if not image_path or not os.path.exists(image_path):
            return {'coa_url': None, 'qr_data': None, 'decoder': '', 'strategy': '', 'error': 'Image not found'}

        result = _decode(image_path)

        if not result.get('found') and use_region_crop and _OPENCV_AVAILABLE:
            crop_dir = temp_dir or tempfile.mkdtemp(prefix='qr_crop_')
            region_paths = extract_qr_regions(image_path, output_dir=crop_dir)
            for region_path in region_paths:
                region_result = _decode(region_path)
                if region_result.get('found'):
                    region_result['strategy'] = 'cv2_crop+' + region_result.get('strategy', '')
                    result = region_result
                    break

        qr_data = None
        coa_url = None
        if result.get('found') and result.get('data'):
            qr_data = result['data'][0]
            if is_url(qr_data):
                coa_url = qr_data.strip()

        return {
            'coa_url': coa_url,
            'qr_data': qr_data,
            'decoder': result.get('decoder', ''),
            'strategy': result.get('strategy', ''),
            'error': result.get('error', ''),
        }

    except Exception as e:
        return {'coa_url': None, 'qr_data': None, 'decoder': '', 'strategy': '', 'error': str(e)}

    finally:
        if temp_dir:
            import shutil
            shutil.rmtree(temp_dir, ignore_errors=True)
        for rp in region_paths:
            try:
                if rp and os.path.exists(rp) and not temp_dir:
                    os.remove(rp)
            except OSError:
                pass
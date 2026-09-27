"""
Hashing Utilities | Cannlytics
Copyright (c) 2026 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
Created: 9/20/2026
Updated: 9/21/2026
License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description:
    The single definition of every hash used across the Cannlytics
    ecosystem. The house algorithm is SHA-256, hex-encoded, computed
    over the WHOLE input, so that every digest can be reproduced with
    standard tools (``sha256sum``, ``Get-FileHash``, ``shasum -a 256``).

    This is a dependency-free leaf module (standard library only), so
    any subpackage can import it without creating a cycle or pulling in
    an optional extra.

        from cannlytics.utils.hashing import hash_file, hash_text

        pdf_hash = hash_file('coa.pdf')          # 64 hex characters
        key = hash_text('blue dream|model|1024')

    Legacy digests. Before 1.0.0 the field ``pdf_hash`` was produced
    three different ways depending on the code path: SHA-1 of the whole
    file, SHA-256 of the first 64 KB, and SHA-256 of the whole file.
    ``legacy_file_hashes`` and ``build_hash_crosswalk`` reproduce all
    three so that existing caches and datasets can be re-keyed without
    re-parsing a single document.
"""
# Standard imports:
import hashlib
import hmac
import json
import os
from typing import Any, Union
from collections.abc import Iterable, Sequence

# The house algorithm. Every hash is SHA-256 unless a caller names another.
HASH_ALGORITHM = 'sha256'

# Bytes read per chunk when hashing a file. A chunk size, not a limit:
# the whole file is always hashed.
HASH_CHUNK_SIZE = 65536

# Hex characters kept by `short_hash` (16 hex = 64 bits).
SHORT_HASH_LENGTH = 16

# Bytes covered by the pre-1.0.0 prefix hash (see `legacy_file_hashes`).
LEGACY_PREFIX_BYTES = 65536

# The digest of zero bytes. A file hash equal to this value means the
# hasher saw no data, which before 1.0.0 is what an unreadable file
# silently produced.
EMPTY_SHA256 = hashlib.sha256(b'').hexdigest()

# Hex length of each digest `identify_hash` can recognise.
_HEX_LENGTHS = {32: 'md5', 40: 'sha1', 64: 'sha256', 128: 'sha512'}

PathLike = Union[str, 'os.PathLike[str]']

# ╔══════════════════════════════════════════════════════════════════╗
# ║ Canonical hashes                                                 ║
# ╚══════════════════════════════════════════════════════════════════╝

def hash_bytes(data: bytes, algorithm: str = HASH_ALGORITHM) -> str:
    """Compute the hex digest of raw bytes.

    Args:
        data: The bytes to hash.
        algorithm: Any name accepted by ``hashlib.new``.

    Returns:
        Hex-encoded digest.
    """
    return hashlib.new(algorithm, data).hexdigest()

def hash_text(
        text: str,
        algorithm: str = HASH_ALGORITHM,
        encoding: str = 'utf-8',
    ) -> str:
    """Compute the hex digest of a string.

    The text is hashed exactly as given. Normalise (strip, lowercase)
    before calling if two spellings should share a digest.

    Args:
        text: The string to hash.
        algorithm: Any name accepted by ``hashlib.new``.
        encoding: How to encode the string to bytes.

    Returns:
        Hex-encoded digest.
    """
    return hash_bytes(text.encode(encoding), algorithm)

def hash_file(
        path: PathLike,
        size: int = HASH_CHUNK_SIZE,
        algorithm: str = HASH_ALGORITHM,
    ) -> str:
    """Compute the hex digest of a whole file.

    Reads in ``size``-byte chunks so that a large PDF never loads into
    memory at once. ``size`` is a chunk size, never a limit: every byte
    of the file is hashed, so the result equals ``sha256sum <path>``.

    Args:
        path: Path to the file.
        size: Chunk size in bytes.
        algorithm: Any name accepted by ``hashlib.new``. Pass ``'sha1'``
            to reproduce the digest ``hash_file`` returned before 1.0.0.

    Returns:
        Hex-encoded digest.

    Raises:
        OSError: If the file cannot be read. An unreadable file has no
            hash; returning the digest of zero bytes instead would make
            every unreadable file collide.
        ValueError: If ``size`` is not positive.
    """
    return hash_file_multi(path, (algorithm,), size=size)[algorithm]

def hash_file_multi(
        path: PathLike,
        algorithms: Sequence[str] = (HASH_ALGORITHM,),
        size: int = HASH_CHUNK_SIZE,
    ) -> dict[str, str]:
    """Compute several digests of a whole file in a single read.

    Args:
        path: Path to the file.
        algorithms: Names accepted by ``hashlib.new``.
        size: Chunk size in bytes.

    Returns:
        Map of algorithm name to hex-encoded digest.

    Raises:
        OSError: If the file cannot be read.
        ValueError: If ``size`` is not positive.
    """
    if size <= 0:
        raise ValueError(f'size must be a positive chunk size, got {size!r}')
    hashers = {name: hashlib.new(name) for name in algorithms}
    with open(path, 'rb') as file:
        for chunk in iter(lambda: file.read(size), b''):
            for hasher in hashers.values():
                hasher.update(chunk)
    return {name: hasher.hexdigest() for name, hasher in hashers.items()}

def hash_json(data: Any, algorithm: str = HASH_ALGORITHM) -> str:
    """Compute the hex digest of a JSON-serialisable value.

    Keys are sorted so that two dictionaries with the same contents
    share a digest regardless of insertion order. Values that JSON
    cannot represent (dates, decimals) are serialised with ``str``.

    Args:
        data: Any JSON-serialisable value.
        algorithm: Any name accepted by ``hashlib.new``.

    Returns:
        Hex-encoded digest.
    """
    text = json.dumps(data, sort_keys=True, default=str)
    return hash_text(text, algorithm)

def short_hash(text: str, length: int = SHORT_HASH_LENGTH) -> str:
    """Compute a truncated SHA-256 of a string, for compact identifiers.

    Sixteen hex characters keep 64 bits. By the birthday bound that is
    a one-in-a-million collision chance at roughly six million items,
    which suits a per-dataset identifier and does not suit a
    verification hash. Use ``hash_text`` when the value must be checked
    against an external tool.

    Args:
        text: The string to hash.
        length: Hex characters to keep (1 to 64).

    Returns:
        The first ``length`` hex characters of the SHA-256 digest.

    Raises:
        ValueError: If ``length`` is outside 1 to 64.
    """
    if not 1 <= length <= 64:
        raise ValueError(f'length must be between 1 and 64, got {length!r}')
    return hash_text(text)[:length]

# ╔══════════════════════════════════════════════════════════════════╗
# ║ Message authentication                                           ║
# ╚══════════════════════════════════════════════════════════════════╝

def hmac_sha256(key: str, message: str) -> str:
    """Compute an HMAC-SHA256 message authentication code.

    Use an HMAC when a server-side secret must be bound into the
    digest, such as deriving the stored lookup code for an API key. Use
    ``hash_text`` for a plain content hash or a cache key.

    Args:
        key: The server-side secret.
        message: The message to authenticate.

    Returns:
        Hex-encoded HMAC.
    """
    return hmac.new(
        key.encode('utf-8'), message.encode('utf-8'), hashlib.sha256,
    ).hexdigest()

def sha256_hmac(secret: str, message: str) -> str:
    """Compute an HMAC-SHA256. The original name of ``hmac_sha256``.

    Kept because issued Cannlytics API keys are stored under this exact
    derivation; the output must never change.

    Args:
        secret: The server-side app secret.
        message: The client's secret, such as an API key.

    Returns:
        Hex-encoded HMAC.
    """
    return hmac_sha256(secret, message)

# ╔══════════════════════════════════════════════════════════════════╗
# ║ Inspection and migration                                         ║
# ╚══════════════════════════════════════════════════════════════════╝

def identify_hash(value: str | None) -> str:
    """Name the algorithm a hex digest most likely came from, by length.

    Length cannot distinguish a whole-file SHA-256 from the pre-1.0.0
    prefix SHA-256; both are 64 characters. Use ``build_hash_crosswalk``
    against the source files to tell those apart.

    Args:
        value: A candidate hex digest.

    Returns:
        ``'md5'``, ``'sha1'``, ``'sha256'``, ``'sha512'``, ``'empty'``
        (the SHA-256 of zero bytes), ``'short'`` (hex, but no standard
        length), or ``'unknown'``.
    """
    if not isinstance(value, str) or not value:
        return 'unknown'
    text = value.strip().lower()
    if any(char not in '0123456789abcdef' for char in text):
        return 'unknown'
    if text == EMPTY_SHA256:
        return 'empty'
    return _HEX_LENGTHS.get(len(text), 'short')

def legacy_file_hashes(
        path: PathLike,
        size: int = HASH_CHUNK_SIZE,
    ) -> dict[str, str]:
    """Compute every digest ``pdf_hash`` has carried, for one file.

    Args:
        path: Path to the file.
        size: Chunk size in bytes.

    Returns:
        A dictionary with ``sha256`` (canonical, whole file), ``sha1``
        (whole file; ``COAdoc.parse_all`` before 1.0.0), and
        ``sha256_prefix`` (first 64 KB only; ``COAdoc.parse`` before
        1.0.0). For a file of 64 KB or less, ``sha256_prefix`` equals
        ``sha256``.

    Raises:
        OSError: If the file cannot be read.
    """
    digests = hash_file_multi(path, ('sha256', 'sha1'), size=size)
    with open(path, 'rb') as file:
        digests['sha256_prefix'] = hash_bytes(file.read(LEGACY_PREFIX_BYTES))
    return digests

def build_hash_crosswalk(paths: Iterable[PathLike]) -> list[dict[str, Any]]:
    """Map every legacy ``pdf_hash`` of a set of files to the canonical one.

    Run this once over an archive of source PDFs, save the rows, and use
    them to re-key caches (``cannlytics.data.cache.rekey_cache``) and
    datasets. No document is re-parsed; only file bytes are read.

    Args:
        paths: Paths of the files to hash.

    Returns:
        One row per readable file with ``file_path``, ``file_size``,
        ``sha256``, ``sha1``, ``sha256_prefix``, and ``prefix_differs``
        (whether the pre-1.0.0 prefix hash differs from the canonical
        hash). An unreadable file yields a row with ``error`` set and
        the digests absent.
    """
    rows: list[dict[str, Any]] = []
    for path in paths:
        row: dict[str, Any] = {'file_path': os.fspath(path)}
        try:
            row['file_size'] = os.path.getsize(path)
            row.update(legacy_file_hashes(path))
            row['prefix_differs'] = row['sha256_prefix'] != row['sha256']
        except OSError as error:
            row['error'] = f'{type(error).__name__}: {error}'
        rows.append(row)
    return rows

def crosswalk_key_map(rows: Iterable[dict[str, Any]]) -> dict[str, str]:
    """Turn crosswalk rows into a ``legacy digest -> sha256`` lookup.

    A legacy digest shared by two different files (possible for the
    prefix hash, when two PDFs open with the same 64 KB) is ambiguous
    and is left out, so that a re-key can never merge two documents.

    Args:
        rows: Rows from ``build_hash_crosswalk``.

    Returns:
        Map from each unambiguous legacy digest to its canonical SHA-256.
    """
    targets: dict[str, set] = {}
    for row in rows:
        canonical = row.get('sha256')
        if not canonical:
            continue
        for field in ('sha1', 'sha256_prefix'):
            legacy = row.get(field)
            if legacy and legacy != canonical:
                targets.setdefault(legacy, set()).add(canonical)
    return {
        legacy: next(iter(found))
        for legacy, found in targets.items()
        if len(found) == 1
    }

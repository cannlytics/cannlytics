# Changelog

All notable changes to the `cannlytics` Python package will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.0.0] — Unreleased

> Set the date on the day the `v1.0.0` tag is pushed.

### Summary

The first release to PyPI since `0.0.17` (January 2024), and the first
with a stable public API. It includes everything in the three internal
milestones below (the rebuilt Firebase module, the COAdoc parsing
engine, `uuid4` document IDs) plus the release hardening listed here.
Requires Python 3.11 or later.

### Added

- **`cannlytics.utils.hashing`** — one definition of every hash in the
  ecosystem: `hash_file`, `hash_text`, `hash_bytes`, `hash_json`,
  `short_hash`, `hmac_sha256`, and `identify_hash`. SHA-256 over the
  whole input, reproducible with `sha256sum` / `Get-FileHash`.
  Standard library only. Re-exported from `cannlytics.utils`.
- **Hash migration tools** — `legacy_file_hashes`,
  `build_hash_crosswalk`, `crosswalk_key_map`, and
  `cannlytics.data.cache.rekey_cache`, to move caches and datasets to
  the canonical `pdf_hash` without re-parsing a single COA.
- **Gemini embeddings** — `gemini-embedding-001` and the multimodal
  `gemini-embedding-2`, selected by model name, with task hints
  (`task='clustering'`, `'search_query'`, ...). OpenAI models are
  unchanged.
- **File and document embeddings** — `create_file_embedding` (images,
  PDFs, audio, video) and `create_pdf_embedding`, which embeds a PDF of
  any length page by page in memory and returns one document vector
  keyed by `pdf_hash`, so embeddings join to lab results.
- **Vector helpers** — `create_embeddings` (batched), `find_similar`,
  `cosine_similarity`, `aggregate_embeddings`, `normalize_embedding`,
  `project_embeddings` (PCA to 2-D/3-D), and `score_outliers` (robust
  per-group outlier scores). NumPy only.
- **`calc_diversity_index(base=...)`**, and the `calc_colorfulness`
  spelling alias.
- **Metrc client**: `timeout` (60 s default, per client and per call),
  `close()`, context-manager support, and `log_file`.
- **`.env.example`** documenting every environment variable, and a
  `py.typed` marker.
- **Tests**: new suites for hashing, stats, Metrc, auth, embeddings
  providers, and package contracts (a core install imports nothing
  optional; every `__all__` resolves; one version number).

### Changed

- **`cannlytics.utils.hash_file` now returns SHA-256 (64 hex
  characters), not SHA-1 (40).** Pass `algorithm='sha1'` for the old
  digest. `size` remains the chunk size.
- **`pdf_hash` is one thing: the SHA-256 of the whole file.**
  Previously `COAdoc.parse()` hashed only the first 64 KB (two
  different COAs sharing a lab-logo prefix received the same
  `pdf_hash`), `COAdoc.parse_all()` used SHA-1, and the algorithms used
  whole-file SHA-256. `parse_all(legacy_keys=True)` still honours
  caches keyed by SHA-1, so upgrading never re-parses an archive.
- **Embedding cache keys are plain SHA-256** (`embedding_key`). Entries
  stored under the previous HMAC-derived key still hit
  (`legacy_keys=True`); new entries use the new key.
- **`sha256_hmac` moved to `cannlytics.utils.hashing`.** It is still
  importable from `cannlytics.auth`, and its output is byte-identical,
  so issued API keys keep working. `cannlytics.ai` no longer imports
  Firebase, and `cannlytics.ai` and `cannlytics.stats` are now core
  modules: they import with no extras installed.
- **`calc_diversity_index` returns `nan`, not `0.0`, for a sample with
  no detected compound.** Zero is the real score of a single-compound
  sample; "nothing detected" is a missing measurement. The function is
  vectorized and otherwise identical to 1e-15.
- **Metrc request logging is off by default** (`logs=False`). When on,
  it writes to an owner-only file and configures only the `metrc`
  logger; it no longer calls `logging.basicConfig`.
- **OpenAI's default COA model is `gpt-5-mini`.** `gpt-5-nano` is
  marked `quarantined` (it reports non-detects as `0.0`) and remains
  selectable by name.
- **Bogart caches** are read and written as UTF-8 on every platform,
  rewritten atomically, tolerate corrupt lines on merge, and accept a
  bare filename as the cache path.
- **`pip install "cannlytics[all]"`** no longer installs the test and
  lint tools or the `coa-legacy` system-dependent packages.
  `tzdata` is a core dependency and `pypdf` joins the `ai` extra.

### Deprecated

- `calculate_purpleness` and `calculate_colourfulness` — renamed
  `calc_purpleness` and `calc_colourfulness`. The old names warn and
  will be removed in 2.0.

### Removed

- The unused `xxhash` dependency.

### Fixed

- `COAdoc` no longer assigns every unreadable PDF the same `pdf_hash`
  (the SHA-256 of zero bytes); an unreadable file now raises `OSError`
  from `_hash_file`, reported by `parse()` as an `error`, and is
  skipped with a warning by `parse_all()`.
- `calc_colourfulness(metric='M3')` was silently wrong on 8-bit images
  (`R - G` wrapped around), and `calc_purpleness` raised
  `OverflowError` on an 8-bit pixel under NumPy 2. An unknown `how` or
  `metric` now raises `ValueError` instead of returning `None`.
- The Metrc client's reconnect never ran: it caught the built-in
  `ConnectionError`, which is unrelated to the one `requests` raises.
- Metrc models raised `KeyError` for a missing attribute, which broke
  `hasattr`, `getattr(..., default)`, and `copy.copy`.
- `from cannlytics.metrc import *` and
  `from cannlytics.data.cache import *` raised `TypeError`
  (`__all__` held objects, not strings).
- A shared mutable default in `Metrc.create_locations`.
- `poll_batch_job` could poll forever; it now has a `timeout`.

### Migration

1. Rename `calculate_purpleness` / `calculate_colourfulness` calls.
2. If you stored `pdf_hash` values or Bogart caches before 1.0.0, run
   `build_hash_crosswalk` over the source PDFs once, then
   `rekey_cache(cache_path, crosswalk_key_map(rows))`. A 40-character
   `pdf_hash` is a legacy SHA-1 (`identify_hash` tells you).
3. If you relied on Metrc request logs, pass `logs=True`.

---

## Internal milestone 1.0.2 — 2026-05-05 (never published; included in 1.0.0)
 
### Summary
 
Removed the abandoned `ulid-py` dependency. ID generation now uses the
Python standard library (`uuid.uuid4().hex`). This aligns with Firestore's
documented best practice of avoiding monotonically-increasing document
IDs, which create write hotspots on the most-recent index shard at scale.
 
### Changed
 
- **`create_id()`** now returns a 32-character lowercase hex UUIDv4
  (e.g. `'9852703aaba84d62a0a94f917d7b72c0'`) instead of a 26-character
  ULID. New IDs have 122 bits of entropy and contain no embedded
  timestamp — by design. Use a `created_at` field on the document for
  creation-time ordering, as Firestore docs recommend. ([core.py])
- **`firebase/core.py`** dropped the `import ulid` and the unused
  `from cannlytics.utils import get_random_string` import.
- **`tests/test_firebase/test_core.py`** updated `TestIdGeneration` to
  assert UUIDv4-hex format (32 chars, lowercase hex, no hyphens) and
  expanded uniqueness check to 1,000 IDs.
- **`pyproject.toml`** removed `ulid-py>=1.0` from the `firebase`,
  `utils`, and `all` optional dependency groups.
### Removed
 
- **`create_id_from_datetime(timestamp)`** — Removed. Encoding creation
  time into a Firestore document ID is an anti-pattern. Store
  `created_at` as a document field instead.
- **`get_id_timestamp(uid)`** — Removed. Use the `created_at` field.
- **`ulid-py`** dependency — abandoned (last release Sept 2020). The
  modern equivalent of the ULID concept is UUIDv7 (RFC 9562, May 2024),
  which is also unsuitable for Firestore primary keys for the same
  hotspot reason.
### Compatibility & migration
 
- **Existing ULID document IDs already in Firestore remain valid.**
  Firestore document IDs are opaque strings; mixing 26-char ULID
  legacy keys with 32-char UUIDv4 hex keys in the same collection is
  harmless. No data migration required.
- **Public API shape preserved.** `from cannlytics.firebase import
  create_id` continues to work. Only the *format* of the returned
  string changes (length 26 → 32; alphabet base32 → hex).
- **Caller audit.** No code in this repo reads, parses, or asserts on
  the format of `create_id()` output other than the test suite (now
  updated). The COA algorithm modules use `create_id` to mint random
  storage filenames — format-agnostic.
- **Firebase Auth UIDs:** `create_user()` passes `create_id()` as the
  Firebase Auth UID. Firebase Auth accepts any string up to 128 chars,
  so UUIDv4 hex is fine.
### Why not UUIDv7 / `python-ulid` / SHA256?
 
- **UUIDv7** is monotonically increasing — exactly what Firestore docs
  warn against. Also requires Python 3.14 stdlib (or a third-party
  package); package floor is Python 3.9.
- **`python-ulid`** (the maintained drop-in for `ulid-py`) preserves
  the same monotonic-key hotspot risk in Firestore.
- **SHA256 of content** is the wrong contract for a primary key: a
  content hash changes when content changes, breaking foreign-key
  relationships. SHA256 is correctly used elsewhere in this codebase
  (`sample_hash`, `results_hash`, `pdf_hash`) as separate verification
  fields, not as document IDs.
- **`uuid.uuid4()` (stdlib)** — random, no dependency, 122 bits of
  entropy, format-stable, supported on every Python the package
  targets, and aligned with Firestore's own auto-ID strategy.

## Internal milestone 1.0.1 — 2026-03-22 (never published; included in 1.0.0)

### Summary

Major package refactoring: the Firebase module was split into focused submodules,
21 unused utility functions and 5 deprecated Firebase functions were removed,
6 bugs were fixed (including a security issue), Firestore Enterprise support was
added, and a comprehensive 224-test suite was introduced. The package is 18% smaller
by line count with zero breaking changes to the public API.

### Added

- **Firestore Enterprise support.** New `database_id` parameter on `initialize_firebase()`
  enables multi-database configurations. A module-level `_get_client()` helper ensures
  all functions automatically route to the configured Enterprise database without
  requiring callers to pass a `database` parameter. ([core.py])
- **Firestore Pipeline operations.** New `pipelines.py` module with `execute_pipeline()`
  and `build_pipeline()` for Firestore Enterprise advanced queries (aggregations,
  string matching, ad-hoc filtering without pre-built indexes). Marked as experimental —
  Pipeline operations are in Preview (Pre-GA) as of March 2026. ([pipelines.py])
- **`start_after` pagination.** New parameter on `get_collection()` for cursor-based
  pagination alongside the existing `start_at`. ([core.py])
- **Signed URL generation.** `get_file_url()` now uses `generate_signed_url()` with
  configurable expiration (default 7 days) instead of permanently exposing files
  via `make_public()`. ([storage.py])
- **Test suite.** 224 tests across 16 files covering all 77 public functions. Tests
  use a mock infrastructure (`MockFirestoreClient`, `MockBucket`, `MockBlob`, etc.)
  that requires no credentials, emulators, or network access. ([tests/])
- **Updated `readme.md`** for the `firebase/` module documenting the new architecture,
  all submodules, Enterprise features, and the signed URL security change.

### Changed

- **Firebase module split.** The monolithic `firebase.py` (839 lines) was split into
  5 focused submodules:
  - `core.py` — Firestore initialization, CRUD, queries, batch writes, IDs, logging
  - `storage.py` — Firebase Storage file operations
  - `firebase_auth.py` — Firebase Auth user management
  - `secrets.py` — Google Cloud Secret Manager
  - `pipelines.py` — Firestore Enterprise Pipeline operations (new)

  All public functions are re-exported from `firebase/__init__.py` for full
  backward compatibility. `from cannlytics.firebase import get_document` continues
  to work unchanged.
- **`FieldFilter` migration.** `get_collection()` now uses the modern
  `.where(filter=FieldFilter(...))` syntax instead of the deprecated positional
  `.where(key, op, value)` syntax. ([core.py])
- **`delete_collection()` recursion fix.** The recursive call now correctly passes
  the `ref` string and `database` client instead of the `col` collection reference,
  which caused the recursion to fail on subsequent batches. ([core.py])
- **`initialize_firebase()` credential logic fix.** Changed from `if env_file ... elif key_path`
  (where env_file blocked key_path) to sequential `if env_file` sets key_path, then
  `if key_path` loads credential. Also uses `config.get()` instead of `config[]` to
  avoid `KeyError` on missing `GOOGLE_APPLICATION_CREDENTIALS`. ([core.py])
- **`download_files()` argument order fix.** Fixed a bug where `list_files(bucket_name, bucket_folder)`
  was passing arguments in the wrong order. Also added `os.makedirs(exist_ok=True)` for
  the local folder. ([storage.py])
- **Bare `except:` elimination.** All 9 bare `except:` clauses across `firebase.py`,
  `auth.py`, and `utils.py` were replaced with specific exception types (`except Exception`,
  `except AttributeError`, `except (json.JSONDecodeError, TypeError, ValueError)`, etc.).
- **Copyright headers updated** to `2021-2026` across all files.
- **`__all__` in `firebase/__init__.py`** now uses proper string names instead of
  object references.
- **`utils/constants.py` moisture mappings** standardized: all moisture-related keys
  now consistently map to `'moisture_content'` (3 conflicts fixed).
- **`utils/logs.py` default path** changed from Windows-specific `D:\\data\\.logs`
  to `None` (console-only by default).
- **`data/cache.py`** test block removed from module body (moved to test suite).
- **`settings.py`** updated to read `FIRESTORE_DATABASE_ID` from config and pass
  `database_id` to `initialize_firebase()`. The Firestore client is stored as
  `DATABASE` Django setting.
- **`pyproject.toml`** updated: `ulid-py` moved to `firebase` optional deps,
  `pytest-cov` added to test deps, version bumped to `1.0.1`.

### Deprecated

These functions were removed from the package. They remain accessible in git
history via the `v1.0.0` tag.

#### Firebase Functions (5 removed)

| Function | Reason |
|----------|--------|
| `create_document()` | Exact duplicate of `update_document()` |
| `import_data()` | Required Pandas at import time (caused Cloud Run circular import); replaced by dedicated upload scripts |
| `export_data()` | Required Pandas; never used in production |
| `create_doc_id()` | Unused; `create_id()` with ULID is superior |
| `create_short_url()` | Firebase Dynamic Links service deprecated by Google |

#### Utility Functions (21 removed)

| Function | Reason |
|----------|--------|
| `sentence_case()` | Unused |
| `format_billions()` | Matplotlib formatter; unused |
| `format_millions()` | Matplotlib formatter; unused |
| `format_thousands()` | Matplotlib formatter; unused |
| `decode_pdf()` | Unused; built-in `base64` suffices |
| `encode_pdf()` | Unused; built-in `base64` suffices |
| `unzip_files()` | Unused in production |
| `remove_duplicate_files()` | One-time utility |
| `get_number_of_lines()` | Rarely used |
| `get_blocks()` | Helper for `get_number_of_lines` only |
| `months_elapsed()` | Unused |
| `sandwich_list()` | Unused |
| `end_of_period_timeseries()` | Unused |
| `set_training_period()` | Unused |
| `convert_month_year_to_date()` | Unused |
| `end_of_month()` | Unused |
| `end_of_year()` | Unused |
| `combine_columns()` | Unused |
| `reverse_dataframe()` | Unused |
| `sum_columns()` | Unused |
| `reorder_columns()` | Unused |

#### Imports Removed

| Import | Reason |
|--------|--------|
| `import requests` (from firebase) | Only used by `create_short_url` |
| `from pandas import ...` (from firebase) | Only used by `import_data`/`export_data`; **fixes Cloud Run circular import bug** |
| `CollectionReference` (from firebase) | Only used by `import_data`/`export_data` |
| `snake_case` (from firebase) | Only used by `import_data` |
| `from os import listdir` (from firebase) | Replaced by `import os` |

#### Constants Cleaned

| Issue | Fix |
|-------|-----|
| 11 duplicate entries in `ANALYSES` | Removed (9 redundant + 2 conflicting) |
| 2 duplicate entries in `ANALYTES` | Removed (`abamectin`, `bile_tolerant_gram_negative_bacteria`) |
| 3 moisture mapping conflicts | All now map to `'moisture_content'` |

### Fixed

| # | Bug | Fix |
|---|-----|-----|
| 1 | Pandas circular import in Cloud Run | Removed Pandas from `firebase.py` imports entirely |
| 2 | Deprecated `.where()` positional syntax | Migrated to `FieldFilter` |
| 3 | `delete_collection` recursion bug | Passes `ref` string + `database` instead of `col` reference |
| 4 | `get_file_url` calls `make_public()` | **Security fix:** replaced with `generate_signed_url()` |
| 5 | `initialize_firebase` ignores `key_path` when `env_file` is passed | Fixed credential loading to sequential logic |
| 6 | 9 bare `except:` clauses | Replaced with specific exception types |
| 7 | `download_files` argument order | Fixed `list_files()` call to match function signature |
| 8 | `OPENAI_API_KEY` could be `None` in `os.environ` | Added default empty string |
| 9 | `get_embedding()` crashes when `use_db=False` | `text_ref` was defined inside `if use_db:` but used unconditionally; moved definition before conditional and guarded `update_document()` with `if use_db:` |

### Metrics

| Metric | Before | After | Change |
|--------|--------|-------|--------|
| `firebase.py` lines | 990 | 1,253 (split across 6 files) | Restructured |
| `utils.py` lines | 894 | 396 | −56% |
| `constants.py` duplicate entries | 11 | 0 | Fixed |
| Bare `except:` clauses | 9 | 0 | Fixed |
| Test count | 0 (package-level) | 224 | +224 |
| Public functions covered by tests | 0 | 77/77 | 100% |

---

## Internal milestone 1.0.0 — 2026-03-19 (never published; included in 1.0.0)

### Summary

Initial release of the modernized `cannlytics` package with the hybrid AI
COA parsing engine, multi-provider support, and modular architecture.

### Added

- Hybrid COA parsing engine with multi-provider AI fallback chain
  (Anthropic → OpenAI → Gemini → xAI).
- Lab identification registry with URL and text pattern matching.
- QR code scanning via `qrustie` (Rust) with Python fallback.
- Modular `pyproject.toml` with optional dependency groups.

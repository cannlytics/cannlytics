# Cannlytics Package — Test Suite

Comprehensive test suite for the `cannlytics` Python package, targeting **80%+ code coverage** across all retained modules.

## Quick Start

```bash
# Run all tests with coverage report.
pytest tests/ -v --cov=cannlytics --cov-report=term-missing

# Run a specific test module.
pytest tests/test_firebase/test_core.py -v

# Run a specific test class.
pytest tests/test_utils/test_strings.py::TestSnakeCase -v

# Run with short output.
pytest tests/ -q --cov=cannlytics
```

## Requirements

```bash
pip install pytest pytest-cov
```

All external services (Firebase, OpenAI, Google Cloud Secret Manager) are **fully mocked** — no credentials, emulators, or API keys are needed to run the test suite.

## Directory Structure

```
tests/
├── conftest.py                    # Shared fixtures: mock Firebase, Storage, Auth
├── test_firebase/
│   ├── test_core.py               # Firestore init, CRUD, queries, IDs, logging
│   ├── test_storage.py            # Storage upload/download/list/delete/rename
│   ├── test_auth.py               # Firebase Auth user management
│   ├── test_secrets.py            # Secret Manager (mocked)
│   └── test_pipelines.py          # Enterprise Pipeline operations (mocked)
├── test_auth/
│   ├── test_request_auth.py       # API request authentication middleware
│   └── test_api_keys.py           # API-key HMAC lookup, precedence, failure handling
├── test_metrc/
│   └── test_metrc_client.py       # Transport: auth, timeouts, reconnect, errors, logs, models
├── test_stats/
│   └── test_stats.py              # calc_* known answers, 8-bit overflow, deprecated names
├── test_package/
│   └── test_imports.py            # Core install imports nothing optional; __all__; version
├── test_coas/                     # COAdoc parser, AI client, config, schema, QR, registry
│   └── test_algorithms/           # Lab algorithms; need local PDF fixtures (marker: fixtures)
├── test_utils/
│   ├── test_hashing.py            # SHA-256 everywhere; HMAC; legacy hash crosswalk
│   ├── test_strings.py            # snake_case, camelcase, kebab_case, etc.
│   ├── test_numbers.py            # convert_to_numeric
│   ├── test_dates.py              # format_iso_date, get_date_range, get_timestamp
│   ├── test_files.py              # get_directory_files, find_latest_file, hash_file
│   ├── test_dicts.py              # Dictionary/list utilities
│   └── test_logs.py               # initialize_logs configurations
├── test_data/
│   ├── test_cache.py              # Bogart caching client
│   ├── test_compounds.py          # Cannabinoid/terpene/pesticide data integrity
│   └── test_constants.py          # ANALYSES, ANALYTES, state codes validation
└── test_ai/
    ├── test_embeddings.py         # Embedding creation/retrieval (mocked)
    └── test_embeddings_providers.py  # OpenAI + Gemini routing, files/PDFs, keys, vectors
```

## Coverage Targets by Module

| Module | Target | Key Validations |
|--------|--------|-----------------|
| `firebase/core.py` | 90%+ | `_get_client` Enterprise routing, `FieldFilter` usage, batch sharding, `create_reference` path parsing |
| `firebase/storage.py` | 85%+ | Signed URL generation (security fix), upload from file vs string |
| `firebase/firebase_auth.py` | 85%+ | User CRUD, claims merge logic, token/session verification |
| `firebase/secrets.py` | 95%+ | All 3 functions fully tested |
| `firebase/pipelines.py` | 90%+ | Both functions tested with mocked Enterprise API |
| `auth/auth.py` | 90%+ | All 3 auth paths (cookie, token, API key) + empty credentials |
| `utils/utils.py` | 80%+ | String conversions, Greek letters, date formatting, file ops |
| `utils/constants.py` | N/A | Data integrity validation (no executable code) |
| `compounds.py` | N/A | CAS number format, required fields, no duplicates |
| `data/cache.py` | 85%+ | CRUD, persistence, merge, JSONL read/organize |
| `ai/embeddings.py` | 70%+ | Core functions mocked; batch functions excluded |
| `utils/logs.py` | 90%+ | Console/file/temp configurations, Windows path fix |

## Test Design Principles

1. **No real credentials required.** Every external service is mocked via `unittest.mock`. The `conftest.py` provides `MockFirestoreClient`, `MockBucket`, `MockBlob`, `MockUserRecord`, and `MockBatch` classes that simulate Firebase behavior in memory.

2. **Every public function has at least one test.** The strategy guide mandates that every function exported from `__init__.py` is covered.

3. **Bug fixes are verified by specific tests.** Each of the 6 bugs identified in the strategy guide has a corresponding test that would fail if the fix regressed:
   - `TestGetCollection.test_query_with_filters_uses_field_filter` — verifies `FieldFilter` migration
   - `TestGetClient.test_enterprise_database_when_id_set` — verifies `database_id` routing
   - `TestGetFileUrl.test_does_not_call_make_public` — verifies signed URL security fix
   - `TestDeleteCollection` — recursion now passes `ref` string (not `col` reference)
   - `TestInitializeFirebase.test_init_with_env_file` — credential logic fix
   - All files pass `grep -c 'except:$'` = 0 — bare except elimination

4. **Data integrity tests catch regressions in reference data.** The `test_compounds.py` and `test_constants.py` modules validate CAS number formats, required fields, no duplicate keys, consistent moisture mappings, valid state codes, and IANA timezone formats.

5. **Fixtures are composable and reusable.** The mock infrastructure in `conftest.py` is designed to be extended as new modules are added.

## Adding Tests

When adding a new function to the package:

1. Add at least one test in the appropriate `test_*.py` file.
2. If the function calls Firebase/OpenAI/GCP, mock the external call.
3. If the function processes data, test with edge cases (empty input, None, Unicode).
4. Run `pytest --cov=cannlytics --cov-report=term-missing` to verify coverage did not decrease.

## CI Integration

Add to your GitHub Actions workflow:

```yaml
- name: Run tests
  run: |
    pip install pytest pytest-cov
    pip install -e ".[firebase]"
    pytest tests/ -v --cov=cannlytics --cov-report=xml
```

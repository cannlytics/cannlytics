# Cannlytics Package: Tests

## Quick start

    pip install -e ".[dev]"            # the package, every extra the tests use, pytest, and tools
    pytest tests -q                    # everything
    pytest tests/test_clean -v         # one area
    pytest tests --cov=cannlytics --cov-report=term-missing

No credentials, emulators, or API keys are needed: Firebase, Google
Cloud, and every AI provider are faked. Two kinds of skips are expected:

- **The lab-algorithm tests** need local COA PDFs
  (`tests/test_coas/test_algorithms/cb/` and `ky/`), which are kept out of
  the repository.
- **A few checks are POSIX-only.**

## Layout

    tests/
    ├── conftest.py                  # Shared fakes: Firestore, Storage, Auth
    ├── test_ai/                     # cannlytics.ai: embeddings; providers, files, keys, vectors
    ├── test_auth/                   # cannlytics.auth: request authentication, API keys
    ├── test_clean/                  # cannlytics.clean: dates (partial dates), ZIPs, phones, names
    ├── test_coas/                   # cannlytics.data.coas
    │   ├── test_ai_client.py        #   AI providers (streaming, costs, thinking tokens)
    │   ├── test_config.py           #   model registry, prices and schedules, provider names
    │   ├── test_identify_lab.py     #   lab identification
    │   ├── test_model_quarantine.py #   no quarantined model is a default
    │   ├── test_parser.py           #   COAdoc
    │   ├── test_pdf_utils.py        #   PDF reading
    │   ├── test_qr.py, test_qr_security.py  # QR codes; qrustie discovery security
    │   ├── test_schema.py           #   the COA schema
    │   └── test_algorithms/         #   lab algorithms (need local COA PDFs)
    ├── test_collect/                # cannlytics.collect: COACollector, polite sessions
    ├── test_constants/              # cannlytics.constants: analytes, aliases, states, units
    ├── test_data/                   # cache, compounds, the deprecated data.constants, GIS, web
    ├── test_datasets/               # cannlytics.datasets
    ├── test_firebase/               # Firestore, Storage, Auth, Secret Manager
    ├── test_licenses/               # cannlytics.licenses: numbers, keys, matching
    ├── test_metrc/                  # the Metrc client: transport and models
    ├── test_package/                # contracts (see below)
    ├── test_schema/                 # cannlytics.schema: LabResult
    ├── test_stats/                  # cannlytics.stats
    └── test_utils/                  # dates, dicts, files, frames, hashing, logs, numbers, strings

## Principles

1. **No credentials.** Every external service is faked; a test that
   needs a network is a bug.
2. **Known answers and invariants.** Reference data is tested by rules
   that hold however it grows: every canonical analyte key maps to
   itself, every CAS number passes its check digit, and none appears
   twice.
3. **A fixed defect keeps its test.** Each release plants its fixed
   defects back into the code (mutation testing) to confirm the suite
   catches each one.
4. **The package keeps its promises.** In `test_package/`:
   - a core install imports nothing optional;
   - the shipped readmes document only code that exists;
   - `.env.example` is complete both ways;
   - the names other Cannlytics repositories import still exist.

## Adding tests

1. Put the test in the folder named for the module (`tests/test_<module>/`).
2. Fake any external call, the way `conftest.py` does for Firebase.
3. Cover the edges: empty input, `None`, Unicode, and the values a
   source actually contains.
4. Run `pytest tests --cov=cannlytics --cov-report=term-missing` and
   check that coverage did not fall.

## Continuous integration

`.github/workflows/release.yml` runs the suite on Windows and Linux,
Python 3.11 to 3.14, for every release tag. Locally, the quick start
above runs the same suite.

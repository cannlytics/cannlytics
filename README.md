# Cannlytics

**Simple Cannabis Analytics** — The `cannlytics` Python package provides tools to wrangle, augment, archive, and analyze cannabis data. From COA parsing to lab results analytics to the Metrc API, Cannlytics puts cannabis data in your hands.

[![PyPI](https://img.shields.io/pypi/v/cannlytics)](https://pypi.org/project/cannlytics/)
[![Python](https://img.shields.io/pypi/pyversions/cannlytics)](https://pypi.org/project/cannlytics/)
[![License: MIT](https://img.shields.io/badge/License-MIT-orange.svg)](https://opensource.org/licenses/MIT)

---

## Installation

Install the core package from [PyPI](https://pypi.org/project/cannlytics/):

```bash
pip install cannlytics
```

Requires Python 3.11 or later. Install with optional features as needed:

```bash
# COA parsing (PDF extraction).
pip install "cannlytics[coa]"

# COA parsing with AI-powered multi-provider support, and embeddings.
pip install "cannlytics[coa,ai]"

# Firebase / Firestore integration.
pip install "cannlytics[firebase]"

# Every runtime extra.
pip install "cannlytics[all]"
```

Every API key is optional and read from the environment. Copy
[`.env.example`](./.env.example) to `.env` to see what each one switches on.

Or clone the repository:

```bash
git clone https://github.com/cannlytics/cannlytics.git
cd cannlytics
pip install -e ".[all]"
```

## Quick Start

### Parse a COA

Extract lab results from a Certificate of Analysis PDF:

```python
from cannlytics.data.coas import COAdoc

parser = COAdoc()
coa = parser.parse('blue-dream-coa.pdf')

if 'error' in coa:
    print(coa['error'])
else:
    # Sample details.
    metadata = coa['metadata']
    print(metadata['product_name'], metadata['lab'], metadata['total_thc'])

    # Results, grouped by analysis.
    for result in coa['analyses']['cannabinoids']['results']:
        print(result['key'], result['value'], result['units'])
```

### Work with the Published Results

Load the Cannlytics results product (Parquet; `pip install cannlytics[datasets]`):

```python
from cannlytics.datasets import load_samples, load_results, flatten_results

samples = load_samples('cannabis-results-2026-09-26', states=['ca', 'ky'], years=[2025])
results = load_results('cannabis-results-2026-09-26', states=['ky'], analytes=['Δ9-THC', 'THCA'])
wide = flatten_results(results)   # one row per sample (pdf_hash), one column per analyte
```

### Clean and Standardize

The same rules every Cannlytics dataset uses:

```python
from cannlytics.constants import normalize_analyte_key, state_code
from cannlytics.clean import parse_date, clean_zip_code
from cannlytics.licenses import normalize_license_number, license_key

normalize_analyte_key('Δ9-THC')           # 'delta_9_thc'
state_code('New Jersey')                  # 'NJ'
parse_date('1/5/24')                      # '2024-01-05'
clean_zip_code(2134)                      # '02134'
normalize_license_number(' c10-0000936-lic ')   # 'C10-0000936-LIC' (stored as issued)
license_key('C10-0000936-LIC')            # 'C10-936' (for matching only)
```

### Access Cannabis Data

Query Cannlytics data through the Firebase API:

```python
from cannlytics.firebase import initialize_firebase, get_collection

# Initialize with your credentials.
db = initialize_firebase('.env')

# Query lab results.
results = get_collection(
    'public/data/results',
    filters=[{'key': 'state', 'operation': '==', 'value': 'ca'}],
    order_by='total_thc',
    desc=True,
    limit=100,
)

for r in results:
    print(f"{r['product_name']}: {r['total_thc']}% THC")
```

### Use the Metrc API

Interface with the Metrc seed-to-sale tracking system:

```python
from cannlytics.metrc import Metrc

with Metrc(
    'your-vendor-api-key',
    'your-user-api-key',
    primary_license='123',
    state='ok',
    test=True,
) as track:

    # Get a plant by its ID.
    plant = track.get_plants(uid='123')

    # Harvest the plant.
    plant.harvest(harvest_name='Old-Time Moonshine', weight=420)
```

> **Metrc API version.** This client speaks version 1 of the Metrc API.
> Metrc has been retiring v1 state by state since the end of 2024 in
> favour of Metrc Connect (v2), so check your state before relying on
> it. Version 2 support is the next milestone for this module.

### Verify a file, embed a COA

Every hash in Cannlytics is a whole-input SHA-256 that you can reproduce
with `sha256sum` or `Get-FileHash`:

```python
from cannlytics.utils import hash_file

pdf_hash = hash_file('blue-dream-coa.pdf')
```

Embed text, images, and whole PDFs in one vector space, then search,
cluster, or look for outliers:

```python
from cannlytics.ai import create_pdf_embedding, find_similar, project_embeddings

coa = create_pdf_embedding('blue-dream-coa.pdf')   # keyed by pdf_hash
matches = find_similar(coa['embedding'], stored_embeddings, k=5)
coordinates, explained = project_embeddings(stored_embeddings, n_components=2)
```

## Package Overview

| Module | Description | Install |
|--------|-------------|---------|
| `cannlytics.data.coas` | COA parsing engine — AI-powered with multi-provider fallback | `pip install cannlytics[coa,ai]` |
| `cannlytics.firebase` | Firestore, Storage, Auth, Secret Manager wrapper | `pip install cannlytics[firebase]` |
| `cannlytics.auth` | API-key and session authentication for the Cannlytics API | `pip install cannlytics[firebase]` |
| `cannlytics.metrc` | Metrc API (v1) client for seed-to-sale compliance | Core |
| `cannlytics.constants` | States, analytes, analyses, product types, license taxonomy, units, compounds | Core |
| `cannlytics.schema` | `LabResult` and its validation: the canonical result record | Core |
| `cannlytics.clean` | Dates, ZIP codes, phone numbers, e-mails, URLs, names, numbers | Core |
| `cannlytics.licenses` | License numbers (stored as issued; matching keys), types, statuses | Core |
| `cannlytics.datasets` | Read the published results product | Core; `pip install cannlytics[datasets]` for Parquet |
| `cannlytics.collect` | `COACollector` base class, `PoliteSession`, one retry policy | Core; `pip install cannlytics[web]` for a browser |
| `cannlytics.stats` | Diversity index, colourfulness, purpleness, chemotype (`calc_*`) | Core |
| `cannlytics.utils` | String, date, file, and data utilities; `kebab_case` / `slugify` | Core |
| `cannlytics.utils.hashing` | SHA-256 for files, text, and JSON; HMAC; hash migration tools | Core |
| `cannlytics.data.cache` | JSONL-backed caching client (Bogart) | Core |
| `cannlytics.ai` | Text, image, and PDF embeddings (OpenAI, Gemini); vector search, PCA, outliers | Core to import; `pip install cannlytics[ai]` to call a provider |

## Firebase Module

The `cannlytics.firebase` module wraps `firebase_admin` with an ergonomic path-based API. Organized into focused submodules:

| Submodule | Contents |
|-----------|----------|
| `core.py` | Firestore init, CRUD, queries, batch writes, IDs, logging |
| `storage.py` | Upload, download, list, rename, delete files |
| `firebase_auth.py` | User management, custom claims, tokens, sessions |
| `secrets.py` | Google Cloud Secret Manager |

All functions are re-exported for convenience:

```python
from cannlytics.firebase import initialize_firebase, get_document, upload_file
```

### Firestore Enterprise

Supports multi-database configurations via the `database_id` parameter:

```python
db = initialize_firebase('.env', database_id='cannlytics-enterprise')
```

Once initialized, all subsequent calls (`get_document`, `get_collection`, etc.) automatically target the Enterprise database — no code changes needed in your API endpoints.

### Data Operations

```python
from cannlytics.firebase import (
    get_document,
    get_collection,
    update_document,
    update_documents,
)

# Get a single document.
strain = get_document('public/data/strains/blue-dream')

# Query with filters, ordering, and pagination.
results = get_collection(
    'public/data/results',
    filters=[
        {'key': 'state', 'operation': '==', 'value': 'wa'},
        {'key': 'total_thc', 'operation': '>=', 'value': 20.0},
    ],
    order_by='date_tested',
    desc=True,
    limit=50,
)

# Batch update (auto-shards at 420 docs per batch).
refs = [f'public/data/results/{r["id"]}' for r in results]
data = [{'reviewed': True} for _ in results]
update_documents(refs, data)
```

## COA Parsing

The `cannlytics.data.coas` module provides a hybrid COA parsing engine: lab-specific algorithms first, then AI with a multi-provider fallback chain (Anthropic → OpenAI → Gemini → xAI):

```python
from cannlytics.data.coas import COAdoc

parser = COAdoc()
coa = parser.parse('coa.pdf')          # a path, a URL, or a list of either
metadata, analyses = coa['metadata'], coa['analyses']
```

Each COA is identified by its `pdf_hash`, the SHA-256 of the whole file.

See the [COA documentation](./cannlytics/data/coas/readme.md) for full details.

## Data Assets

Cannlytics maintains comprehensive cannabis datasets:

| Dataset | Records | Coverage |
|---------|---------|----------|
| Cannabis Licenses | 41,000+ | 48 jurisdictions (37 U.S. + 11 Canada) |
| Lab Results | 995,000+ | 14+ U.S. states |
| Strains | 5,000+ | With terpene/cannabinoid statistics |
| Analytes | 200+ | Full reference data |

## Testing

Run the test suite:

```bash
pip install -e ".[test]"
pytest tests/ --cov=cannlytics --cov-report=term-missing
```

No credentials or network access are required: every external service is mocked. Tests that need real COA PDFs (marked `fixtures`) skip when the local-only fixture folders are absent, and live-sandbox tests are marked `integration`.

## Development

```bash
git clone https://github.com/cannlytics/cannlytics.git
cd cannlytics
pip install -e ".[dev]"
pytest tests/ -v
ruff check cannlytics/
```

## Contributing

Contributions are welcome. Please ensure:

1. All new functions have at least one test.
2. `pytest tests/` passes with no failures.
3. `ruff check cannlytics/` passes with no errors.

## License

```
Copyright (c) 2020-2026 Cannlytics

Permission is hereby granted, free of charge, to any person obtaining
a copy of this software and associated documentation files (the
"Software"), to deal in the Software without restriction, including
without limitation the rights to use, copy, modify, merge, publish,
distribute, sublicense, and/or sell copies of the Software, and to
permit persons to whom the Software is furnished to do so, subject to
the following conditions:

The above copyright notice and this permission notice shall be
included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
```

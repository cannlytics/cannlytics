# Cannlytics

**Simple Cannabis Analytics** — The `cannlytics` Python package provides tools to wrangle, augment, archive, and analyze cannabis data. From COA parsing to lab results analytics to the Metrc API, Cannlytics puts cannabis data in your hands.

[![PyPI](https://img.shields.io/pypi/v/cannlytics)](https://pypi.org/project/cannlytics/)
[![Python](https://img.shields.io/pypi/pyversions/cannlytics)](https://pypi.org/project/cannlytics/)
[![License: MIT](https://img.shields.io/badge/License-MIT-orange.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://img.shields.io/badge/tests-224%20passed-brightgreen)]()

---

## Installation

Install the core package from [PyPI](https://pypi.org/project/cannlytics/):

```bash
pip install cannlytics
```

Install with optional features as needed:

```bash
# COA parsing (PDF extraction).
pip install cannlytics[coa]

# COA parsing with AI-powered multi-provider support.
pip install cannlytics[coa,ai]

# Firebase / Firestore integration.
pip install cannlytics[firebase]

# Everything.
pip install cannlytics[all]
```

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
results = parser.parse('blue-dream-coa.pdf')
print(results['total_thc'])   # 24.5
print(results['strain_name']) # Blue Dream
print(results['status'])      # pass
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

track = Metrc(
    'your-vendor-api-key',
    'your-user-api-key',
    primary_license='123',
    state='ok',
    logs=True,
    test=False,
)

# Get a plant by its ID.
plant = track.get_plants(uid='123')

# Harvest the plant.
plant.harvest(harvest_name='Old-Time Moonshine', weight=420)
```

## Package Overview

| Module | Description | Install |
|--------|-------------|---------|
| `cannlytics.data.coas` | COA parsing engine — AI-powered with multi-provider fallback | `pip install cannlytics[coa,ai]` |
| `cannlytics.firebase` | Firestore, Storage, Auth, Secret Manager wrapper | `pip install cannlytics[firebase]` |
| `cannlytics.metrc` | Metrc API client for seed-to-sale compliance | Core |
| `cannlytics.utils` | String, date, file, and data utilities | Core |
| `cannlytics.data.compounds` | Cannabinoid, terpene, pesticide reference data | Core |
| `cannlytics.data.cache` | JSONL-backed caching client (Bogart) | Core |
| `cannlytics.ai` | Embedding creation and retrieval | `pip install cannlytics[ai]` |

## Firebase Module

The `cannlytics.firebase` module wraps `firebase_admin` with an ergonomic path-based API. Organized into focused submodules:

| Submodule | Contents |
|-----------|----------|
| `core.py` | Firestore init, CRUD, queries, batch writes, IDs, logging |
| `storage.py` | Upload, download, list, rename, delete files |
| `firebase_auth.py` | User management, custom claims, tokens, sessions |
| `secrets.py` | Google Cloud Secret Manager |
| `pipelines.py` | Firestore Enterprise Pipeline operations *(experimental)* |

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

The `cannlytics.data.coas` module provides a hybrid COA parsing engine that uses AI with a multi-provider fallback chain (Anthropic → OpenAI → Gemini → xAI):

<!-- FIXME: This example is broken -->

```python
from cannlytics.data.coas import COAdoc

parser = COAdoc()
results = parser.parse('coa.pdf')
```

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
pip install cannlytics[test]
pytest tests/ -v --cov=cannlytics --cov-report=term-missing
```

224 tests cover all 77 public functions. No credentials or network access required — all external services are fully mocked.

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

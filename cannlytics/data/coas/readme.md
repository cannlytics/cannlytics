# COA Parsing

`cannlytics.data.coas` reads certificates of analysis (COAs), the lab
reports that accompany cannabis products, and returns their data in one
standard form. `COAdoc` routes each COA to the best method: a
lab-specific **algorithm** when the lab is recognized (free, fast,
deterministic), otherwise an **AI model** (flexible, and billed per
token).

## Installation

```
pip install "cannlytics[coa]"        # algorithms only
pip install "cannlytics[coa,ai]"     # algorithms, with AI for unrecognized labs
```

AI parsing needs a key for at least one provider (see below). COA URLs
are recovered from QR codes by the `qrustie` binary when it is found
(`QRUSTIE_PATH`), else by the Python decoder of `pip install "cannlytics[qr]"`.

## Usage

```py
from cannlytics.data.coas import COAdoc

parser = COAdoc()                                    # method='auto', provider='anthropic'
result = parser.parse('coa.pdf')                     # a path, a URL, or bytes
result = parser.parse('https://example.com/coa.pdf')
result = parser.parse(pdf_bytes, filename='coa.pdf')

result['metadata'].get('coa_url')                    # found by QR code, if present
```

Useful options: `method='algorithm'` (never call an AI model) or
`method='ai'`; `provider` and `model` (see below); `analyses=[...]`
on `parse` to read only some analyses; `qrustie_path=False` to skip QR
scanning.

`parse` returns a dictionary with `metadata` and `analyses`; the
metadata includes `coa_url` when a QR code gave one. On failure it
returns `{'error': '...', 'metadata': {}}`.

## Pipeline mode

For collecting a state's COAs in bulk, give the parser a state and
directories, and call `parse_all`:

```py
from pathlib import Path
from cannlytics.data.coas import COAdoc

parser = COAdoc(state='ny', data_dir=Path('.datasets'), cache_dir=Path('.cache'), budget=25.0)
summary = parser.parse_all(source='prr')
```

Each COA is cached by the SHA-256 of its file (`pdf_hash`), so a run can
stop and resume without parsing, or paying for, anything twice.
`budget` caps AI spend in USD and `max_parses` the number of COAs.

## Algorithms

Recognized labs, from the routing table `LAB_REGISTRY`. A lab is
identified by the URLs and text on the first page of its COA (and, when
enabled, by its QR code). Tiers: 1 production, 2 beta, 3 alpha,
4 development.

| Lab or LIMS | Key | Algorithm | Tier | States |
|---|---|---|---|---|
| CannaBusiness Laboratories | `cannabusiness` | `parse_cannabusiness_coa` | 2 (beta) | KY |
| Encore Labs | `encore` | `parse_encore_coa` | 2 (beta) | CA, AZ |
| KCA Laboratories | `kca` | `parse_kca_coa` | 2 (beta) | KY |
| ACS Laboratory | `acs` | `parse_acs_coa` | 3 (alpha) | FL |
| Confident Cannabis (LIMS) | `confidentcannabis` | `parse_cc_coa` | 3 (alpha) | AZ, CA, CO, LA, MO, NY, OR, WA |
| Green Analytics | `green_analytics` | `parse_green_analytics_coa` | 3 (alpha) | NJ, MD, NY |
| Kaycha Labs | `kaycha` | `parse_kaycha_coa` | 3 (alpha) | AZ, FL, NY, OH, NJ |
| Phyto-Farma Labs | `phytofarma` | `parse_phyto_farma_coa` | 3 (alpha) | NY |
| SC Labs | `sclabs` | `parse_sc_labs_coa` | 3 (alpha) | AZ, CA, OR, CO, MI |
| Smithers CTS | `smithers` | `parse_smithers_coa` | 3 (alpha) | AZ, NY |
| TagLeaf LIMS | `tagleaf` | `parse_tagleaf_coa` | 3 (alpha) | CA, MO, NY, OR |
| TerpLife Labs | `terplife` | `parse_terplife_coa` | 3 (alpha) | FL |
| AcreLabs | `acrelabs` | `parse_acrelabs_coa` | 4 (development) | LA |

To add a lab: write `parse_<lab>_coa(parser=None, doc='', **kwargs)`
returning a dictionary of the COA's data, add an entry to
`LAB_REGISTRY` (its `urls`, `text_patterns`, `module`, and
`algorithm`), and validate it on real COAs. The parser adapts the
algorithm's dictionary to the standard form. To develop an algorithm
outside the package, put its module in a folder and pass
`local_algorithm_paths=[folder]`; local modules take priority.

## AI providers

When no algorithm applies, `COAdoc` uses one provider, falling back in
priority order if a provider fails or runs out of quota:

| Priority | Provider | Default model | Other models | Key |
|---|---|---|---|---|
| 1 | Anthropic Claude | `claude-haiku-4-5-20251001` | `claude-sonnet-5`, `claude-opus-5-5`, `claude-fable-5-1`, `claude-sonnet-4-5-20250929` | `ANTHROPIC_API_KEY` |
| 2 | OpenAI | `gpt-6-sol` | `gpt-6-luna`, `gpt-6-astra`, `gpt-5-mini`, `gpt-5` | `OPENAI_API_KEY` |
| 3 | Google Gemini | `gemini-3.8-flash` | `gemini-3.5-flash-lite`, `gemini-3.1-pro-preview`, `gemini-2.5-flash`, `gemini-2.5-pro` | `GOOGLE_API_KEY` |
| 4 | xAI Grok | `grok-4.7` | `grok-4.3` | `XAI_API_KEY` |

Prices and capabilities are in `cannlytics.data.coas.config`
(`AI_PROVIDERS`, checked against each provider's price page on
2026-09-28; `get_model_cost` prices a call on any date, since
some prices are scheduled to change). Models flagged `legacy` are
superseded but selectable; `quarantined` models failed a fidelity check
and are never a default. Before a large run, check every configured
provider with one live request each:

```
python tools/check_ai_providers.py
```

## The results

Each result is a `cannlytics.schema.LabResult` (111 fields).
The fields most analyses start from:

| Field | Meaning |
|---|---|
| `sample_id` | A stable ID for the sample. |
| `product_name` | The product as named on the COA. |
| `product_type` | Standardized product type. |
| `strain_name` | The strain, as named. |
| `batch_number` | The batch or lot. |
| `lab` | The testing laboratory. |
| `date_tested` | When the sample was tested (ISO date, at the precision given). |
| `total_thc` | Total THC, percent. |
| `total_cbd` | Total CBD, percent. |
| `coa_url` | The COA's own URL, from its QR code. |
| `results` | Every analyte reported: key, value, units, limits, status. |

Analyte keys follow `cannlytics.constants`: `normalize_analyte_key`
maps any label a lab uses (`'Δ9-THC'`, `'d9-THC'`) to one key
(`'delta_9_thc'`).

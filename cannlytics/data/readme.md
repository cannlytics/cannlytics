# Cannlytics Data Module

`cannlytics.data` holds the tools that gather and prepare cannabis data:
the COA parser, a JSONL cache for long collection runs, geographic
tools, and web tools. The building blocks those tools share live one
level up, and are where most data work starts:

| Module | What it does |
|--------|--------------|
| `cannlytics.constants` | States, analytes and their aliases, analyses, product types, license categories, units, and the compound reference (names and CAS numbers). |
| `cannlytics.clean` | Dates (keeping partial dates), ZIP codes, phone numbers, e-mail, URLs, names, and numbers. |
| `cannlytics.licenses` | License numbers as issued, matching keys, and license categories and statuses. |
| `cannlytics.schema` | `LabResult`, the standard record for one lab result, and its validation. |
| `cannlytics.datasets` | Reading the published results product (Parquet). |
| `cannlytics.collect` | `COACollector`, the base class for COA collectors, and a polite HTTP session. |

## COA parsing: `cannlytics.data.coas`

`COAdoc` reads a certificate of analysis (a PDF, a URL, or bytes) and
returns its metadata and results: by a lab-specific algorithm when the
lab is recognized, otherwise with an AI model. See the
[COA documentation](https://github.com/cannlytics/cannlytics/blob/main/cannlytics/data/coas/readme.md).

```py
from cannlytics.data.coas import COAdoc

parser = COAdoc()                      # Anthropic by default; reads ANTHROPIC_API_KEY
result = parser.parse('coa.pdf')
result['metadata'], result['analyses']
```

Requires `pip install "cannlytics[coa,ai]"`.

## Caching long runs: `cannlytics.data.cache`

`Bogart` is a JSONL cache keyed by hash (of a file or a URL), so that a
collection or parsing run can stop and resume without repeating work.

| Method | Description |
|--------|-------------|
| `append(key, value)` | Append a single entry to the .jsonl file. |
| `clear()` | Clear the cache. |
| `expire(key)` | Expire a key in the cache. |
| `get(key, default=None)` | Get a value from the cache. |
| `hash_file(file_path, block_size=65536)` | Hash a whole file (SHA-256) to use as a cache key. |
| `hash_url(url)` | Hash a URL (SHA-256) to use as a cache key. |
| `load(cache_path)` | Load the cache from a .jsonl file. |
| `merge(cache_path)` | Merge another .jsonl cache file into this cache, keeping unique hashes. |
| `save()` | Save the entire cache to a .jsonl file, atomically. |
| `set(key, value)` | Set a value in the cache. |
| `to_df()` | Return the cache as a DataFrame. |

## Geographic data: `cannlytics.data.gis`

State data and population from the Federal Reserve's FRED, geocoding
and place search with Google Maps, and distances and routes. The module
always imports; a function whose library is missing names the extra to
install, `pip install "cannlytics[utils]"`.

| Function | Description |
|----------|-------------|
| `get_state_data(state, code, fred_api_key=None, district='', obs_start=None, obs_end=None)` | A state's series from FRED, by series code. |
| `get_state_population(state, fred_api_key=None, district='', obs_start=None, obs_end=None, multiplier=1000.0)` | A state's resident population from FRED (series ``<STATE>POP``). |
| `get_google_maps_api_key(env_file='.env')` | Find a Google Maps API key. |
| `initialize_googlemaps(env_file='./.env')` | A Google Maps client, keyed from ``env_file`` or ``get_google_maps_api_key``. |
| `geocode_addresses(data, api_key=None, pause=0.0, address_field='')` | Geocode the addresses in a DataFrame, in place. |
| `search_for_address(query, api_key=None, fields=None)` | Find the address of a place by name with Google Places. |
| `parse_formatted_address(formatted_address)` | Split a Google formatted address into street, city, state, and ZIP code. |
| `get_transfer_distance(api_key, start, end, mode='driving')` | The distance and travel time between two places. |
| `get_transfer_route(api_key, start, end, departure_time=None, mode='driving')` | The route between two places. |

Keys: FRED reads `FRED_API_KEY` when none is passed. Google Maps keys
are found by `get_google_maps_api_key`: the environment, then `./.env`
(read, not loaded), then Google Secret Manager, then Firestore
(`admin/google`).

```py
from cannlytics.data.gis import parse_formatted_address

parse_formatted_address('1 Main St, Suite 5, Lacey, WA 98503, USA')
# {'state': 'WA', 'zipcode': '98503', 'city': 'Lacey', 'street': '1 Main St, Suite 5'}
```

## Web data: `cannlytics.data.web`

Page metadata, contact details, and downloads. Requires
`pip install "cannlytics[web]"`; Selenium is imported only when a
browser is started, and finds or downloads a matching driver itself.
Every request has a timeout (`TIMEOUT`), and downloads are written
atomically: a failed download leaves no partial file.

| Function | Description |
|----------|-------------|
| `get_page_metadata(url, timeout=(10, 60))` | Fetch a page and read its metadata. |
| `get_page_description(html)` | A page's description: its description meta tags, else its first paragraph. |
| `get_page_image(html, index=0, url='')` | A page's image: its sharing image, else its ``index``-th ``<img>``. |
| `get_page_favicon(html, url='')` | A page's favicon, absolute when ``url`` is given; else the site's ``/favicon.ico``. |
| `get_page_theme_color(html)` | A page's theme color (``<meta name="theme-color">``). |
| `get_page_phone_number(html, response=None, index=0)` | A phone number on a page: from ``tel:`` or ``callto:`` links, else the page text. |
| `get_page_email(html, response=None, index=-1)` | An e-mail address on a page: from ``mailto:`` links, else the page text. |
| `format_params(parameters, **kwargs)` | Map keyword arguments to an API's parameter names, dropping empty ones. |
| `download_file_from_url(url, destination='', ext='', file_name=None, timeout=(10, 60))` | Download a file to a folder. |
| `download_google_drive_file(drive_file, destination, timeout=(10, 60))` | Download a public Google Drive file. |
| `initialize_selenium(browser=None, headless=True, download_dir=None, arguments=())` | Start a Selenium WebDriver: Chrome, falling back to Edge. |
| `download_file_with_selenium(url, driver=None, persist=False, pause=3.33, wait=10, el_id='download', method='iframe', tag_name='iframe', filename=None, download_dir=None, headless=True)` | Download a file from a page that needs a browser. |

```py
from cannlytics.data.web import get_page_metadata

response, html, metadata = get_page_metadata('cannlytics.com')
metadata['description'], metadata['favicon']
```

## Moved: `cannlytics.data.constants` and `cannlytics.data.compounds`

Both now live in `cannlytics.constants`. The old paths still import
(`cannlytics.data.constants` with a `DeprecationWarning`) and will be
removed in 2.0.

```py
from cannlytics.constants import get_compound, normalize_analyte_key

normalize_analyte_key('Δ9-THC')        # 'delta_9_thc'
get_compound('Aflatoxin B1')           # {'name': 'Aflatoxin B1', 'cas': '1162-65-8', ...}
```

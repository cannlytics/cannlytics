##  Strain Data API <a name="strain-data"></a>

<div style="margin-top:1rem; margin-bottom: 1rem;">
  <img width="240px" alt="" src="https://firebasestorage.googleapis.com/v0/b/cannlytics.appspot.com/o/public%2Fimages%2Flogos%2Fskunkfx_logo.png?alt=media&token=1a75b3cc-3230-446c-be7d-5c06012c8e30">
</div>

You can get data about common cannabis strains with the `api/data/strains` endpoint. You can request data for a specific strain with the `api/data/strains/<strain_name>` endpoint.

## Parameters

Below are the parameters that you can pass and examples of how you can format a request body.

| Parameter | Options | Example |
|-----------|---------|---------|
| `limit` | The maximum number of strains to return, pass any positive integer. | `?limit=420` |
| `order` | The field to use to order the returned strains, `strain_name` by default. | `?order=total_thc` |
| `desc` | Whether or not to order in descending order, the default is `false`.  | `?desc=true` |
| `aromas` | The desired aromas as a comma-separated value. | `?aromas=lime,skunk` |
| `effects` | The desired effects as a comma-separated value. | `?effects=sleepy,dry+eyes` |
| `any` | Whether or not to return matches on any of the requested effects and aromas, the default is `false`. | `?any=true` |
| `{analyte}` | An analyte to filter by concentration. Prepend the concentration value by one of the operation prefixes in the table below. You can combine operations with a `+`. For example, `total_thc=g20+l25` is the logical equivalent of requesting `total_thc` greater than 20 and less than 25 percent. | `?beta_pinene=ge0.25` |

The operations that can be used as prefixes in `{analyte}` values include:

| Prefix | Operation |
|--------|-----------|
| `g` | Greater than X. |
| `ge` | Greater than or equal to X. |
| `l` | Less than X. |
| `le` | Less than or equal to X. |

Any of the analytes below can be used to query strains by their average concentrations.

```json
[
  "cbc",
  "cbd",
  "cbda",
  "cbg",
  "cbga",
  "cbn",
  "delta_8_thc",
  "delta_9_thc",
  "thca",
  "thcv",
  "alpha_bisabolol",
  "alpha_pinene",
  "alpha_terpinene",
  "beta_caryophyllene",
  "beta_myrcene",
  "beta_pinene",
  "camphene",
  "carene",
  "caryophyllene_oxide",
  "d_limonene",
  "eucalyptol",
  "gamma_terpinene",
  "geraniol",
  "guaiol",
  "humulene",
  "isopulegol",
  "linalool",
  "nerolidol",
  "ocimene",
  "p_cymene",
  "terpinene",
  "terpinolene",
  "total_cannabinoids",
  "total_cbd",
  "total_cbg",
  "total_terpenes",
  "total_thc",
  "terpinenes"
]
```

<!-- ### Variables -->

## Examples

Below are a handful of examples, written in Python, that can be generalized to your favorite programming language.

```py
import requests
import urllib.parse

# Define the URL.
url = 'https://cannlytics.com/api/data/strains'

# Get strains.
params = {'limit': 3}
response = requests.get(url, params=params)
data = response.json()['data']
print('Found %i strains.' % len(data))

# Get a specific strain.
strain_name = urllib.parse.quote_plus('Super Silver Haze')
response = requests.get(url + '/' + strain_name)
data = response.json()['data']
print('Found %s.' % data['strain_name'])

# Get strains by effects.
effects = json.dumps(['focused', 'creative'])
params = {'limit': 10, 'effects': effects}
response = requests.get(url, params=params)
data = response.json()['data']
print('Found %i strains.' % len(data))

# Get strains by aromas.
aromas = json.dumps(['skunk'])
params = {'limit': 5,'aromas': aromas}
response = requests.get(url, params=params)
data = response.json()['data']
print('Found %i strains.' % len(data))

# Get strain by compound concentration.
params = {'limit': 25, 'beta_pinene': 'g0.2'}
response = requests.get(url, params=params)
data = response.json()['data']
print('Found %i strains.' % len(data))
```

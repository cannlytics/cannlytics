# Predicting Effects and Aromas

> "It's been hard to breathe and the smell's been just horrendous... [It's] like you've literally been sprayed by a
**skunk**." - Resident of Prague, Oklahoma
[*'It's nasty': Prague neighbors push back on area cannabis facility*](https://kfor.com/news/local/its-nasty-prague-neighbors-push-back-on-area-cannabis-facility/), Oklahoma News 4 (2022)

## Objective

Can we build a model to **predict** if someone may *report* specific **effects** or **aromas** given a cannabis product’s **lab results**?

## Literature

[Over eight hundred cannabis strains characterized by the relationship between their psychoactive effects,
perceptual profiles, and chemical compositions](https://www.biorxiv.org/content/10.1101/759696v1.abstract) by Laura Alethia de la Fuente, Federico Zamberlan, Andres Sanchez, Facundo Carrillo, Enzo Tagliazucchi, Carla Pallavicini (2019)

* **Claim**: *"While cannabinoid content was variable even within individual strains, terpene profiles matched the perceptual characterizations made by the users and could be used to predict associations between different psychoactive effects."*

## Data

A panel of stain reviews was curated from the data of [Alethia, et. al. (2019)](https://data.mendeley.com/datasets/6zwcgrttkp/1). First, we downloaded the authors' strain review and lab result dataset. We then curated terpene and cannabinoid data from the raw text files in the dataset. Average cannabinoid and terpene concentrations were calculated for each of the 184 strains in the dataset from 431 lab results. Reviews are for purported strains and the lab results may or may not be representative of the concentration of the product that the reviewer is referencing. However, without the actual lab results of the product that the reviewer purchased, then the average concentrations for similarly named products can serve as an estimate. The following processing and assumptions were applied.

- Field names were transformed to `snake_case`.
- The fields `total_terpenes` and `total_cannabinoids` were calculated as the simple sum of all terpenes and cannabinoids respectively.
- The fields `total_thc` and `total_cbd` were calculated using the decarboxylation rate (87.7%) for THCA and CBDA.
- Observations with `total_cannabinoids` greater than 35% or `total_terpenes` greater than 6% were presumed to be outliers and were excluded.
- The field `classification` was determined by the original authors from natural language processing (NLP) and can take a value of `sativa`, `indica`, or `hybrid` depending on the language in the reviewer's description.
- Fields for each reported aroma and effect were created and assigned a value of 1 if the reviewer reported the aroma or effect and 0 otherwise.


| Datasets | URL |
|----------|-----|
| Raw data | <https://data.mendeley.com/datasets/6zwcgrttkp/1> |
| Curated panel data | <https://cannlytics.page.link/effects> |
| Potential strain effects data | <https://cannlytics.page.link/strain-effects> |

<!-- TODO: Add WA and CT (OH?) datasets :) -->
<!-- TODO: Explain methodology -->

## Results

An implementation of the prediction model can be found at <https://cannlytics.com/effects> and utilized through the API endpoint <https://cannlytics.com/api/stats/effects> with the following parameters. You can get an API key by signing up at <https://cannlytics.com/api>. You can substitute training and prediction data as you see fit.

| Parameter | Options | Example |
|-----------|-----------|-------|
| `model` | `full` (default), `cann`, `terp` | `?model=terp` |
| `train` | URL to training data | `?train=https://cannlytics.page.link/effects`  |
| `predict` | URL to prediction data | `?predict=https://cannlytics.page.link/effects`  |
| `pessimistic` | `true` (default), `false` | `?pessimistic=false` |
| `strain` | The name of a strain for which you're seeing reported effects and flavors. | `?strain=galactic-jack`

Here are a few quick examples in Python:

```py
import requests

# Safely pass your API key.
url = 'https://cannltics.com/api/stats/effects'
auth = {'Authorization': 'Bearer %s' % API_KEY}

# Get effects for a specific strain.
params = {'strain_name': 'Golden Goat'}
response = requests.get(url, params=params, auth=auth)
data = response.json()['data']

# Get effects given lab results.
params = {'total_cbd': 0.04, 'total_thc': 20}
response = requests.get(url, params=params, auth=auth)
data = response.json()['data']

# Post actual aromas and effects.
params = {
    'strain_name': 'Golden Goat',
    'effects': ['Bliss'],
    'aromas': ['Sweet', 'Sassy']
}
requests.post(url, params=params, auth=auth)
```

<!-- TODO: Return Type 1 or type 2 errors? -->

A typical response includes `potential_aromas`, `potential_effects`, and `model_stats` which contains summary statistics for each aroma and effect:

```json
[{
  "potential_aromas": [],
  "potential_effects": [],
  "model": "full",
  "model_stats": {}
}]
```

## Insights and future work

The more training data the better. If you want to [contribute lab results or reviews](https://cannlytics.com/stats/effects-and-flavors), then you are welcome! You can also use your own training data. Using the model to predict out-of-sample helps make the model robust. Please feel free to report your use of the model and its accuracy in the wild to <dev@cannlytics.com>. Thank you and good fortune!

## Disclaimer

```
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

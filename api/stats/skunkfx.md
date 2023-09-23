# `SkunkFx` - Effects and Aromas Prediction Model

<div align="center" style="text-align:center; margin-top:1rem; margin-bottom: 1rem;">
  <img width="240px" alt="" src="https://firebasestorage.googleapis.com/v0/b/cannlytics.appspot.com/o/public%2Fimages%2Flogos%2Fskunkfx_logo.png?alt=media&token=1a75b3cc-3230-446c-be7d-5c06012c8e30">
</div>

The `api/stats/effects` endpoint is used to predict effects and aromas that may be reported for a given product given its lab results. For technical details of the model, please see the AI documentation. In general, there are 3 main actions:

1. You can use the model to predict potentially reported effects and aromas for any cannabis flower for which you have lab results. Simply post your lab results to the `api/stats/effects` endpoint, specifying your model if you desire, and you will receive effect and aroma predictions.

2. You can get the model statistics by making a `GET` request to `api/stats/effects`. Currently, the model statistics include: `false_positive_rate`, `false_negative_rate`, `true_positive_rate`, `true_negative_rate`, `accuracy`, `informedness`.

3. Finally, you can post the actual effects and aromas that you may observe with the `api/stats/effects/actual` endpoint.

You can substitute training data, for strain reviews or lab results, as you see fit.

### Parameters

Below are the parameters that you can pass and examples of how you can format a request body.

<!-- FIXME: -->
| Parameter | Options | Example |
|-----------|---------|---------|
| `model` | `full` (default), `cannabinoid_only`, `terpene_only`, `totals`, `simple` | `?model=simple` |
<!-- | `train` | URL to training data | `?train=https://cannlytics.page.link/effects`  |
| `predict` | URL to prediction data | `?predict=https://cannlytics.page.link/effects`  |
| `pessimistic` | `true` (default), `false` | `?pessimistic=false` |
| `strain` | The name of a strain for which you're seeing reported effects and flavors. | `?strain=Super+Silver+Haze` -->

### Examples

Below are a handful of examples, written in Python, that can be generalized to your favorite programming language.

```py
import requests
import pandas as pd

BASE = 'https://cannlytics.com/api'

# Get statistics for the `full` model.
url = f'{BASE}/stats/effects'
params = {'model': 'full'}
response = requests.get(url, params=params)
model_stats = response.json()['data']

# Post lab results to get potential effects and aromas.
json = {
    'model': 'simple',
    'samples': [
        {'total_cbd': 1.0, 'total_thc': 18.0},
        {'total_cbd': 1.0, 'total_thc': 20.0},
        {'total_cbd': 1.0, 'total_thc': 30.0},
        {'total_cbd': 7.0, 'total_thc': 7.0},
    ]
}
url = f'{BASE}/stats/effects'
response = requests.post(url, json=json)
data = response.json()['data']

# Post actual aromas and effects, rating the usefulness of the prediction.
json = {
    'samples': [
        {
            'prediction_id': '01g4g8apexj1r426rbkcnfdjt9',
            'strain_name': 'Test Strain',
            'effects': ['happy', 'focused'],
            'aromas': ['citrus', 'pine'],
            'rating': 10,
        },
    ]
}
url = f'{BASE}/stats/effects/actual'
response = requests.post(url, json=json)
message = response.json()['message']
```

A typical response includes a list of `samples` with `predicted_aromas` and `predicted_effects`. There are also `model_stats`, summary statistics for each aroma and effect, and a `prediction_id` for each sample that can be used for reporting actual effects and aromas.

```json
[{
  "model": "full",
  "model_stats": {},
  "samples" [
    {
      "lab_results": {},
      "predicted_aromas": [],
      "predicted_effects": [],
      "predicted_at": "2022-06-03T04:20:00",
      "prediction_id": "01g4g8apexj1r426rbkcnfdjt9",
      "strain_name": "",
    }
  ]
}]
```

> At this time, the official Cannlytics effects model has only been trained on flower data and the model would not make sense for concentrates, edibles, etc..

### Variables

The variates for the models are:
```json
{
  "full": [
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
    "terpinolene"
  ],
  "terpene_only": [
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
    "terpinolene"
  ],
  "cannabinoid_only": [
    "cbc",
    "cbd",
    "cbda",
    "cbg",
    "cbga",
    "cbn",
    "delta_8_thc",
    "delta_9_thc",
    "thca",
    "thcv"
  ],
  "totals": ["total_cbd", "total_thc", "total_terpenes"],
  "simple": ["total_cbd", "total_thc"]
}
```

The possible effects and aromas are listed below. In general, the key is used for programmatic use and the name is the expected input from the user. E.g. a value of `effect_happy` may be returned from the API, but you can simply post `'Happy'` when reporting actual effects.

**Effects**

| Name | Key |
|------|-----|
| Anxiety | `effect_anxiety` |
| Anxious | `effect_anxious` |
| Aroused | `effect_aroused` |
| Arthritis | `effect_arthritis` |
| Creative | `effect_creative` |
| Depression | `effect_depression` |
| Dizzy | `effect_dizzy` |
| Dry Eyes | `effect_dry_eyes` |
| Dry Mouth | `effect_dry_mouth` |
| Energetic | `effect_energetic` |
| Epilepsy | `effect_epilepsy` |
| Euphoric | `effect_euphoric` |
| Eye Pressure | `effect_eye_pressure` |
| Fatigue | `effect_fatigue` |
| Focused | `effect_focused` |
| Giggly | `effect_giggly` |
| Happy | `effect_happy` |
| Headache | `effect_headache` |
| Hungry | `effect_hungry` |
| Migraines | `effect_migraines` |
| Pain | `effect_pain` |
| Paranoid | `effect_paranoid` |
| Relaxed | `effect_relaxed` |
| Seizures | `effect_seizures` |
| Sleepy | `effect_sleepy` |
| Spasticity | `effect_spasticity` |
| Stress | `effect_stress` |
| Talkative | `effect_talkative` |
| Tingly | `effect_tingly` |
| Uplifted | `effect_uplifted` |

**Aromas**

| Name | Key |
|------|-----|
| Ammonia | `aroma_ammonia` |
| Apple | `aroma_apple` |
| Apricot | `aroma_apricot` |
| Berry | `aroma_berry` |
| Blue Cheese | `aroma_blue_cheese` |
| Blueberry | `aroma_blueberry` |
| Butter | `aroma_butter` |
| Cheese | `aroma_cheese` |
| Chemical | `aroma_chemical` |
| Chestnut | `aroma_chestnut` |
| Citrus | `aroma_citrus` |
| Coffee | `aroma_coffee` |
| Diesel | `aroma_diesel` |
| Earthy | `aroma_earthy` |
| Flowery | `aroma_flowery` |
| Fruit | `aroma_fruit` |
| Grape | `aroma_grape` |
| Grapefruit | `aroma_grapefruit` |
| Honey | `aroma_honey` |
| Lavender | `aroma_lavender` |
| Lemon | `aroma_lemon` |
| Lime | `aroma_lime` |
| Mango | `aroma_mango` |
| Menthol | `aroma_menthol` |
| Mint | `aroma_mint` |
| Nutty | `aroma_nutty` |
| Orange | `aroma_orange` |
| Peach | `aroma_peach` |
| Pear | `aroma_pear` |
| Pepper | `aroma_pepper` |
| Pine | `aroma_pine` |
| Pineapple | `aroma_pineapple` |
| Plum | `aroma_plum` |
| Pungent | `aroma_pungent` |
| Rose | `aroma_rose` |
| Sage | `aroma_sage` |
| Skunk | `aroma_skunk` |
| Spicy to herbal | `aroma_spicytoherbal` |
| Strawberry | `aroma_strawberry` |
| Sweet | `aroma_sweet` |
| Tar | `aroma_tar` |
| Tea | `aroma_tea` |
| Tobacco | `aroma_tobacco` |
| Tree | `aroma_tree` |
| Tropical | `aroma_tropical` |
| Vanilla | `aroma_vanilla` |
| Violet | `aroma_violet` |
| Woody | `aroma_woody` |

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

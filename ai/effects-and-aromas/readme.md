# Predicting Effects and Aromas

<div align="center" style="text-align:center; margin-top:1rem; margin-bottom: 1rem;">
  <img width="240px" alt="" src="https://firebasestorage.googleapis.com/v0/b/cannlytics.appspot.com/o/public%2Fimages%2Flogos%2Fskunkfx_logo.png?alt=media&token=1a75b3cc-3230-446c-be7d-5c06012c8e30">
</div>

> "It's been hard to breathe and the smell's been just horrendous... [It's] like you've literally been sprayed by a
**skunk**." - Resident of Prague, Oklahoma in
[*'It's nasty': Prague neighbors push back on area cannabis facility*](https://kfor.com/news/local/its-nasty-prague-neighbors-push-back-on-area-cannabis-facility/), Oklahoma News 4 (2022).

## Objective

Can we build a model to **predict** if someone may *report* specific **effects** or **aromas** given a cannabis product’s **lab results**?

## Literature

[Over eight hundred cannabis strains characterized by the relationship between their psychoactive effects,
perceptual profiles, and chemical compositions](https://www.biorxiv.org/content/10.1101/759696v1.abstract) by Laura Alethia de la Fuente, Federico Zamberlan, Andres Sanchez, Facundo Carrillo, Enzo Tagliazucchi, Carla Pallavicini (2019).

* **Claim**: *"While cannabinoid content was variable even within individual strains, terpene profiles matched the perceptual characterizations made by the users and could be used to predict associations between different psychoactive effects."*

## Data

A panel of strain reviews was curated from the data published by [Alethia, et. al. (2019)](https://data.mendeley.com/datasets/6zwcgrttkp/1). First, we downloaded the authors' strain review and lab result datasets. We then curated terpene and cannabinoid data from the raw text files in the lab result dataset. Average cannabinoid and terpene concentrations were calculated for each of the 184 strains in the dataset from 431 lab results. Reviews are for purported strains and the lab results may or may not be representative of the concentration of the product that the reviewer is referencing. However, without the actual lab results of the product that the reviewer is referencing, the average concentrations for similarly named products can serve as an estimate. The following processing and assumptions were applied.

- Field names were transformed to `snake_case`.
- The fields `total_terpenes` and `total_cannabinoids` were calculated as the simple sum of all terpenes and cannabinoids respectively.
- The fields `total_thc`, `total_cbd`, and `total_cbg` were calculated using the decarboxylation rate (87.7%) for THCA, CBDA, and CBGA.
- Observations with `total_cannabinoids` greater than 35% or `total_terpenes` greater than 6% were presumed to be outliers and were excluded.
- The field `classification` was determined by the original authors from natural language processing (NLP) and can take a value of `sativa`, `indica`, or `hybrid` depending on the language in the reviewer's description.
- Fields for each reported aroma and effect were created and assigned a value of 1 if the reviewer reported the aroma or effect and 0 otherwise.
- Terpenes of similar names were combined on missing values: `p_cymene` with `pcymene`, `beta_caryophyllene` with `caryophyllene`, and `humulene` with `alpha_humulene`.
- Certain terpenes were summed into a encompassing field: `ocimene`, `beta_ocimene`, `trans_ocimene` to `ocimene` and `trans_nerolidol`, `cis_nerolidol`, `transnerolidol_1`, `transnerolidol_2` to `nerolidol`.
- A new field, `terpinenes`, was created as the sum of `alpha_terpinene`, `gamma_terpinene`, `terpinolene`, and `terpinene`.

| Datasets | URL |
|----------|-----|
| Raw data | <https://data.mendeley.com/datasets/6zwcgrttkp/1> |
| Curated panel data | <https://cannlytics.page.link/reported-effects> |
| Potential strain effects data | <https://cannlytics.page.link/strain-effects> |

<!-- TODO: Add WA and CT (OH?) datasets :) -->

## Methodology

A [multivariate probit model](https://en.wikipedia.org/wiki/Multivariate_probit_model) is used to predict the probability of all potential effects and aromas simultaneously given lab results for a sample or samples. Specific effects and aromas are predicted to be reported when the estimated probability of an effect or aroma crosses a threshold. The thresholds are set to best fit the observed occurrence of each effect and aroma. Below are the variates used in the models estimated.

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

## Results

An implementation of the prediction model can be found at <https://cannlytics.com/effects> and utilized through the API endpoint <https://cannlytics.com/api/stats/effects>. In general, there are 3 main actions:

1. You can use the model to predict potentially reported effects and aromas for any cannabis flower for which you have lab results. Simply post your lab results to the `/stats/effects` endpoint, specifying your model if you desire, and you will receive effect and aroma predictions.

2. You can get the model statistics by making a `GET` request to `/stats/effects`. Currently, the model statistics include `false_positive_rate`, `false_negative_rate`, `true_positive_rate`, `true_negative_rate`, `accuracy`, and `informedness`.

3. Finally, you can post the actual effects and aromas that you may observe with the `/stats/effects/actual` endpoint.

You can substitute training data, for strain reviews or lab results, as you see fit. Please see the API documentation for more information about using this API endpoint.

## Insights and future work

The more training data the better. If you want to [contribute lab results or reviews](https://cannlytics.com/stats/effects), then you are welcome! You can also use your own training data. Using the model to predict out-of-sample helps make the model robust. Please feel free to report your use of the model and its accuracy in the wild to <dev@cannlytics.com>. Lastly, but most importantly, remember that the predictions are for the probability of effects and aromas being reported by the observed sample given observed lab results. Extrapolations beyond the ranges of observed values aren't valid and all statistics should be taken at face value. Thank you and good fortune!

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

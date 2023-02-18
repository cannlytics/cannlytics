<div align="center" style="text-align:center; margin-top:1rem; margin-bottom: 1rem;">
  <img width="240px" alt="" src="https://firebasestorage.googleapis.com/v0/b/cannlytics.appspot.com/o/public%2Fimages%2Flogos%2Fcannlytics_ai_with_text.png?alt=media&token=78d19117-eff5-4f45-a8fa-3bbdabd6917d">
  <div style="margin-bottom:1rem;">
    <h3>Cannabis + Analytics + AI</h3>
  </div>

[![contributions welcome](https://img.shields.io/badge/contributions-welcome-brightgreen.svg?style=flat)](https://github.com/dwyl/esta/issues)

<https://cannlytics.com/ai>

> [Kreuzberger et. al](https://doi.org/10.48550/arXiv.2205.02302) stipulate, *"The final goal of all industrial machine learning (ML) projects is to develop ML products and rapidly bring them into production."* Cannlytics AI is no exception. The aim of Cannlytics AI is to develop and implement fully-functioning machine learning products for people in the cannabis space to use and interact with.

</div>

| Model | Description |
|-------|-------------|
| [Cultivar Prediction Model](./cultivar-prediction) | Given the lab results for two strains, the average of the results can be used as a predictor of the results of the child. |
| [Effects and Aromas Prediction Model](./effects-and-aromas) | A [multivariate probit model](https://en.wikipedia.org/wiki/Multivariate_probit_model) is used to predict the probability of all potential effects and aromas simultaneously given lab results for a sample or samples. |
| [Product Descriptions](./product-descriptions) | Create product descriptions given product details using NLP. |
| [Product Recommendations](./product-recommendations) | **Collaborative Filtering**: Recommend products similar to a given product and an inventory of products. Given a consumer's characteristics, recommend products that other consumers with similar characteristics enjoyed. **Content-Based**: Given a body of a consumer's reviews and lab results for those products, rank an inventory of products by the estimated consumer's preferences. |
| [Strain NFTs](./strain-nfts) | Programmatically create flower art given effects and aromas. |
| [Strain Statistics](./strain-statistics) | Cannabis strains, or cultivars, varieties, etc., are a focal point of the cannabis industry. The general understanding is that strain name usage is loose and the meaningfulness of strain names is hotly debated. Here, we simply attempt to identify and quantify common strain names that people use for the varieties that they cultivate and sell. We provide statistics about specific strain names and use the data and statistics to aid in prediction models. |

<!-- Possible models:
## Predicting consumption
## Predicting sales
## Predicting yield
## Predicting the likelihood of a sample failing QA
  Using a Bayesian model trained on Washington state data, we can provide the probability of failing various quality control tests given the parameters at hand and the limit in the state of interest.
-->

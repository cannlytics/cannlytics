# Cannlytics Statistics as a Service

<div align="center" style="text-align:center; margin-top:1rem; margin-bottom: 1rem;">
  <img width="150px" alt="" src="https://firebasestorage.googleapis.com/v0/b/cannlytics.appspot.com/o/public%2Fimages%2Flogos%2Fcannlytics_staas_logo.png?alt=media&token=fc71a230-90cf-4f72-b6e3-d1a6c52a726f">
</div>

| Function | Description |
|----------|-------------|
| `calculate_model_statistics(models, Y, X)` | Determine prediction thresholds for a given model. Calculate a confusion matrix and returns prediction statistics. |
| `estimate_discrete_model(X, Y, method=None)` | Estimate a prediction model(s) for discrete outcomes. The algorithm excludes all null columns, adds a constant, then fits probit model(s) for each effect variable. The user can specify their model, e.g. logit, probit, etc. |
| `get_stats_model(ref, data_dir='/tmp', name=None, bucket_name=None)` | Get a pre-built statistical model for use. First, gets the model data from Firebase Firestore. Second, downloads the pickle file and loads it into a model. |
| `predict_stats_model(models, X, thresholds=None)` | Predict outcomes for a given model and its thresholds. Add a constant column if necessary and only use model columns. |
| `upload_stats_model(models, ref, name=None, data_dir='/tmp', stats=None)` | Upload an statistical model for future use. Pickle each model, zip the model files, then upload the zipped file. Finally, record the file's data in Firebase Firestore. |

<!-- TODO: Examples -->

<!-- ## Models

- ARIMA
- Bayesian Regression
- Heckman
- Tobit
- VAR -->
<!-- TODO: Write documentation about statistical models!

  - OLS
  - IV (instrumental variables)
  - Logit
  - Conditional Logit
  - Multinomial Logit
  - Probit
  - Ordinal Probit
  - Multinomial Probit
  - Difference-in-differences
  - Fixed effects
  - Random effects
  - Interactions?
  - Dummy variables?

-->

<!-- TODO: Examples -->

<!-- ## Natural Language Processing (NLP) -->

<!-- TODO: Documentation for NLP tools -->


<!-- TODO: Examples -->

## Personality Test

This test is provided for educational and entertainment uses only. The test is not clinically administered and as such the results are not suitable for aiding important decisions. The test is also fallible, so, if the results say something about you that you don't think is true, then you are right and it is wrong. For more information, see [Administering IPIP Measures, with a 50-item Sample Questionnaire](https://ipip.ori.org/new_ipip-50-item-scale.htm). The prompt is as follows.

```
Describe yourself as you generally are now, not as you wish
to be in the future. Describe yourself as you honestly see
yourself, in relation to other people you know of the same
sex as you are, and roughly your same age. So that you can
describe yourself in an honest manner, your responses will
be kept in absolute confidence. Indicate for each statement
whether it is

1. Very Inaccurate,
2. Moderately Inaccurate,
3. Neither Accurate Nor Inaccurate,
4. Moderately Accurate, or
5. Very Accurate

as a description of you.
```

*Example*

```py
from cannlytics.stats.personality import score_personality_test

# Score a personality test.
test = {
    '1': 3,
    '2': 3,
    '3': 3,
    '4': 3,
    '5': 3,
    '6': 3,
    '7': 3,
    '8': 3,
    '9': 3,
    '10': 3,
    '11': 3,
    '12': 3,
    '13': 3,
    '14': 3,
    '15': 3,
    '16': 3,
    '17': 3,
    '18': 3,
    '19': 3,
    '20': 3,
    '21': 3,
    '22': 3,
    '23': 3,
    '24': 3,
    '25': 3,
    '26': 3,
    '27': 3,
    '28': 3,
    '29': 3,
    '30': 3,
    '31': 3,
    '32': 3,
    '33': 3,
    '34': 3,
    '35': 3,
    '36': 3,
    '37': 3,
    '38': 3,
    '39': 3,
    '40': 3,
    '41': 3,
    '42': 3,
    '43': 3,
    '44': 3,
    '45': 3,
    '46': 3,
    '47': 3,
    '48': 3,
    '49': 3,
    '50': 3,
}
score = score_personality_test(test)

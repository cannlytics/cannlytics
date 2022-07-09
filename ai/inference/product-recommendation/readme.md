# Product Recommendation


## Collaborative Filtering


## Content-Based Recommendations


## Statistics

term-frequency can be calculated by:

TF_{ij} = \frac{f_{ij}}{max_k f_{kj}}

where fij is the frequency of term(feature) i in document(item) j. 

inverse-document frequency can be calculated with:

```
IDF_{i} = log_e \frac{N}{n_i}
```

where, ni number of documents that mention term i. N is the total number of docs.

The total formula is:

TF-IDF score (w_{ij}) = TF_{ij} * IDF_i


# Product Recommendation

**Collaborative Filtering**: Recommend products similar to a given product and an inventory of products. Given a consumer's characteristics, recommend products that other consumers with similar characteristics enjoyed. **Content-Based**: Given a body of a consumer's reviews and lab results for those products, rank an inventory of products by the estimated consumer's preferences.


<!-- ## Collaborative Filtering -->


<!-- ## Content-Based Recommendations -->


## Statistics

The term-frequency can be calculated by:

```
TF_{ij} = \frac{f_{ij}}{max_k f_{kj}}
```

where `f_{ij}` is the frequency of term (feature) `i` in document (item) `j`.  The inverse-document frequency can be calculated with:

```
IDF_{i} = log_e \frac{N}{n_i}
```

where, `n_i` is number of documents that mention term `i` and `N` is the total number of docs. The total formula is:

```
TF-IDF score (w_{ij}) = TF_{ij} * IDF_i
```

## References

- [Machine Learning Operations (MLOps): Overview, Definition, and Architecture](https://doi.org/10.48550/arXiv.2205.02302)


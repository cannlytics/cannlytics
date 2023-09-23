<!-- | Cannlytics SOP-0007 |  |
|---------------------|--|
| Title | Documentation |
| Version | 1.0.0 |
| Created At | 2023-07-18 |
| Updated At | 2023-07-18 |
| Review Period | Annual |
| Last Review | 2023-07-18 |
| Author | Keegan Skeate, Founder |
| Approved by | Keegan Skeate, Founder |
| Status | Active | -->

# Testing

## End-to-end Testing

The Cannlytics Website and API can be built in a Docker container for testing:

```shell
docker build . --tag gcr.io/cannlytics/cannlytics
gcloud auth configure-docker
docker push gcr.io/cannlytics/cannlytics
```

The `cannlytics` package can be installed locally for testing with:

```shell
pip install .
```

Finally, the app can be run locally with:

```shell
npm run app:web
```

## Unit testing

Each algorithm has a suite of unit tests. In practice, you may not be able to test every case. Therefore, you may want to focus on

- Null cases;
- Range tests, e.g., positive/negative value tests;
- Edge cases;
- Failure cases;
- Testing the paths most likely to execute most of the time.

## Resources

- [Django Testing Tutorial](https://docs.djangoproject.com/en/3.1/intro/tutorial05/)
- [Build locally with Docker](https://cloud.google.com/run/docs/building/containers#building_locally_and_pushing_using_docker)

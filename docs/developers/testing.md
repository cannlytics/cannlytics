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

Run tests for an app with `python manage.py test survey`. See [testing](/testing) for more information.

## Local Testing

The Cannlytics Website can be built locally for testing:

```shell
docker build . --tag gcr.io/cannlytics/cannlytics-website
gcloud auth configure-docker
docker push gcr.io/cannlytics/cannlytics-website
```

## Unit testing

In practice, you may not be able to test every case. Therefore, you may want to focus on

- Null cases
- Range tests, e.g., positive/negative value tests
- Edge cases
- Failure cases
- Testing the paths most likely to execute most of the time

## Resources

- [Django Testing Tutorial](https://docs.djangoproject.com/en/3.1/intro/tutorial05/)
- [Build locally with Docker](https://cloud.google.com/run/docs/building/containers#building_locally_and_pushing_using_docker)

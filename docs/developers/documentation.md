<!-- | Cannlytics SOP-0006 |  |
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

# Documentation <a name="documentation"></a>

Documentation for Cannlytics is written in [Markdown](https://guides.github.com/features/mastering-markdown/) and lives in the `docs` folder. The configuration for the documentation is contained within `mkdocs.yml`. Building the documentation requires [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/) and [Docker](https://www.docker.com/get-started).

## Writing documentation

First, you will need to pull and build the Material for MKDocs Docker image:

```shell
docker pull squidfunk/mkdocs-material
docker build -t squidfunk/mkdocs-material docs
```

or

```shell
npm run docs:install
```

You will also need to install the Python dependencies for the documentation:

```shell
pip install -r docs/requirements.txt
```

Once you have a copy of the Docker image, you can preview the documentation as you write:

```shell
docker run --rm -it -p 8000:8000 -v "%cd%":/docs squidfunk/mkdocs-material
```

or

```shell
npm run docs:start
```

You can preview the documentation at <http://localhost:8000/> while you develop.

!!! note

    There is [a namespace conflict between `django-livereload-server` and `livereload`](https://gist.github.com/hangtwenty/f53b3867db1e33780505ccafd8d2eef0), so you need to be careful when and where you install Python requirements. If you run into a `django-livereload-server` import error, first check that `PRODUCTION=False` in your `.env` file and then follow [these instructions](https://gist.github.com/hangtwenty/f53b3867db1e33780505ccafd8d2eef0) to uninstall `livereload` and reinstall  `django-livereload-server`.

## Publishing documentation

When you are ready, you can build the documentation with:

```shell
npm run docs:build
```

Finally, you can publish the documentation with:

```shell
npm run docs:publish
```

Congratulations, you can now read the documentation at [https://docs.cannlytics.com](https://docs.cannlytics.com).

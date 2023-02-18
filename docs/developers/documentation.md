# 🐱‍👓 Documentation <a name="documentation"></a>

Documentation for the project is written in [Markdown](https://guides.github.com/features/mastering-markdown/). Building the documentation locally requires installing [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/) and [Docker](https://www.docker.com/get-started). The configuration for the documentation is contained within `mkdocs.yml`. You can serve the documentation locally by first pulling and building the Material for MKDocs image:

```shell
docker pull squidfunk/mkdocs-material
docker build -t squidfunk/mkdocs-material docs
```

Once setup, you can preview the documentation as you write:

```shell
docker run --rm -it -p 8000:8000 -v "%cd%":/docs squidfunk/mkdocs-material
```

or

```shell
npm run docs
```

> Note that there is [a namespace conflict between `django-livereload-server` and `livereload`](https://gist.github.com/hangtwenty/f53b3867db1e33780505ccafd8d2eef0), so you need to be careful when and where you install Python requirements. If you run into a `django-livereload-server` import error, first check that `PRODUCTION = False` in your `console/settings.py` and then follow [these instructions](https://gist.github.com/hangtwenty/f53b3867db1e33780505ccafd8d2eef0) to uninstall `livereload` and reinstall  `django-livereload-server`.

When you are ready, you can build the documentation:

```shell
npm run build-docs
```

And publish the documentation:

```shell
npm run publish-docs
```

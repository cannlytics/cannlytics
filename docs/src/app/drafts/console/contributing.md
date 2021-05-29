# Contributing

Thank you for your interest in contributing!

## Reporting Bugs and Ideas

Finding and reporting issues, bugs, and sub-optimal features and functionality is the first step in the development process. If you discover any bugs or have any ideas, then please contact [Keegan](mailto:keeganskeate@gmail.com).

## Pull Requests

Feel free to clone the repository and make any pull requests that you think would benefit the project.

## Writing documentation

Install Material for MkDocs with Docker.

```shell
docker pull squidfunk/mkdocs-material
```

Preview the documentation as you write.

```shell
docker run --rm -it -p 8000:8000 -v "%cd%":/docs squidfunk/mkdocs-material
```

or

```shell
npm run docs
```

* [Quick note - how to fix django-livereload-server import error](https://gist.github.com/hangtwenty/f53b3867db1e33780505ccafd8d2eef0)

Build the documentation

```shell
mkdocs build
```

or

```shell
npm run build-docs
```
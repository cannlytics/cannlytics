# My Personal Website

My (your) personal website.

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

My personal website is a modern portfolio website, built on the bleeding edge, to help you showcase your work. My personal website comes with **batteries included**, but you are always welcome to supercharge your setup with modifications and custom components. My personal website is:

* Free software.
* Freedom respecting.
* Community-driven.

> Currently, nonfree software is used in parts of my personal website. The mission of my personal website is to systematically migrate from any nonfree software to free software.

<!-- FIXME: [TOC] -->

## 🗺️ Road Map

TODO:

- Setup blog posts.
- Finish contact form.
- Clean up style.
- Integrate with Firestore.

Also, look into:

* [Customize Error Pages](https://docs.djangoproject.com/en/3.1/howto/deployment/checklist/#customize-the-default-error-views)
* [Experiment with App Engine](https://cloud.google.com/appengine/docs/flexible/python/quickstart#windows)
* [Add Google Cloud Armor](https://cloud.google.com/blog/products/identity-security/google-cloud-armor-features-to-protect-your-websites-and-applications?utm_source=release-notes&utm_medium=email&utm_campaign=2020-aug-release-notes-1-en)
* [Write custom Django commands](https://docs.djangoproject.com/en/3.1/howto/custom-management-commands/)

## 📖 Installation

My personal website is an open box and transparent. You do not have to guess about the software used in my personal website. My personal website is built and depends on the following software and services.

* [Python](https://www.python.org/psf/)
* [Django](https://www.djangoproject.com/foundation/)
* [Firebase](https://firebase.google.com/)
* [Google Cloud Platform](https://cloud.google.com/gcp)
* [Node.js](https://nodejs.org/en/about/)
* [Javascript, HTML, CSS](https://www.w3schools.com/)
* [Gimp](https://www.gimp.org/about/)
* [Inkscape](https://inkscape.org/about/)

The guiding philosophy of the project is that open source and [free solutions](http://www.gnu.org/philosophy/free-sw.html) are the best.

Developing my personal website requires installing the following tools:

* [Django](https://docs.djangoproject.com/en/3.1/intro/tutorial01)
* [Docker](https://docs.docker.com/get-docker/)
* [Firebase Tools](https://firebase.google.com/docs/cli)
* [Google Cloud SDK](https://dl.google.com/dl/cloudsdk/channels/rapid/GoogleCloudSDKInstaller.exe)
* [Node.js](https://nodejs.org/en/download/)

See [`docs/installation.md`](docs/installation.md) for complete installation instructions that guide you through:

* Cloning the repository.
* Setting your account credentials.
* Installing Python and Python dependencies.
* Installing development tools.

For a quick start, simply clone the repository:

```shell

git clone https://github.com/keeganskeate/personal-website.git

```

## 🏛️ Architecture

My personal website is built with [Python] using the [Django] framework. My personal website runs on [Cloud Run] and is hosted with [Firebase Hosting]. My personal website utilizes [Firebase Authentication], an optional SQL database, a [Firestore] NoSQL database for real-time data management, and [Firebase Storage] for file storage. You are free to swap out components for others. My personal website depends on several other Google Cloud services in the following ways:

  * Containerized using [Cloud Build].
  * Uploaded to [Cloud Registry].
  * Runs as a stateless container on [Cloud Run].
  * [Cloud Secret Manager](https://cloud.google.com/secret-manager/) is used for storing configurations and keeping secrets secret.
  * (*Optional*) [Cloud SQL](https://cloud.google.com/sql) can be utilized if desired.
  * (*Optional*) [Cloud Storage](https://cloud.google.com/storage) buckets can be used for file storage.

See [`docs/architecture.md`](docs/architecture.md) for information about the repository's architecture.

Helpful resources:

* [WSGI Servers](https://www.fullstackpython.com/wsgi-servers.html)

<!-- Architecture References: -->

  [Cloud Build]: https://cloud.google.com/cloud-build/docs
  [Cloud Registry]: https://cloud.google.com/container-registry
  [Cloud Run]: https://firebase.google.com/docs/hosting/cloud-run
  [Dart]: https://dart.dev/guides
  [Django]: https://www.djangoproject.com/
  [Firebase Authentication]: https://firebase.google.com/docs/auth
  [Firebase Hosting]: https://firebase.google.com/docs/hosting
  [Firebase Storage]: https://firebase.google.com/docs/storage
  [Firestore]: https://firebase.google.com/docs/firestore
  [Futter]: https://flutter.dev/docs
  [Python]: https://www.python.org/

## 🔨 Development

See [`docs/development.md`](docs/development.md) for a complete development guide. Development can happen in many avenues. Principally, clone the repository, begin working on an area, referring to documentation as needed, and commit your changes.

## 📡 Database

My personal website operates with a NoSQL database by default, however, can be configured with an SQL database.

You can perform a full database model build with:

```shell

python manage.py makemigrations
python manage.py migrate

```

Helpful resources:

* [Django Database API](https://docs.djangoproject.com/en/3.1/topics/db/queries/)

## 📁 Storage

You can gather all supporting files into the `static` folder with:

```shell

python manage.py collectstatic

```

> Add the `--noinput` tag to suppress the overwrite warning.

You can configure static files to be served from [Firebase Storage](https://firebase.google.com/docs/storage) instead of from [Firebase Hosting](https://firebase.google.com/docs/hosting) in `personal_website/settings.py`.

Helpful resources:

* [Serving static files on App Engine](https://cloud.google.com/appengine/docs/standard/python3/serving-static-files)

## 🐞 Bugs

See [`docs/bugs.md`](docs/bugs.md) for a full list of bugs and issues that you may encounter. To report a bug, please email <keeganskeate@gmail.com>.

## ⚗️ Testing

Please see [`docs/development.md`](docs/development.md) for full documentation on testing the website. Generally, you can run tests for a Django app with `python manage.py test app_name`.

My personal website can be built locally for testing with:

```shell

docker build . --tag gcr.io/${PROJECT_ID}/${APP_ID}
gcloud auth configure-docker
docker push gcr.io/${PROJECT_ID}/${APP_ID}

```

## 📚 Publishing

Publishing is done with one command:

```shell

npm run publish

```

> Both the development and production sites will be published with `npm run publish`. Specify `--only hosting:dev` or `--only hosting:production` to target a specific site.

The build process contains three steps:

1. Containerize the app and upload it to Container Registry.

Build your container image using Cloud Build by running the following command from the directory containing the Dockerfile:

```shell

gcloud builds submit --tag gcr.io/${PROJECT_ID}/${APP_ID}

```

2. Deploy the container image to Cloud Run.

```shell

gcloud beta run deploy ${APP_ID} --image gcr.io/${PROJECT_ID}/${APP_ID} --region ${REGION} --allow-unauthenticated --service-account=${GCS_SA}

```

3. Direct hosting requests to the containerized app.

This step provides access to this containerized app from a [Firebase Hosting](https://firebase.google.com/docs/hosting) URL, so that the app can generate dynamic content for the Firebase-hosted site.

```shell

firebase deploy --only hosting:production

```

## 🐕‍🦺 Resources

Below is a non-exhaustive list of helpful resources:

* [Django Philosophy](https://docs.djangoproject.com/en/3.1/misc/design-philosophies)
* [Django on Cloud Run](https://codelabs.developers.google.com/codelabs/cloud-run-django)
* [django-livereload](https://github.com/Fantomas42/django-livereload)
* [django-livereload-server](https://github.com/tjwalch/django-livereload-server)
* [Django Browser Sync with Docker](https://stackoverflow.com/questions/49482710/using-browser-sync-with-django-on-docker-compose)
* [Design Tips](https://dribbble.com/stories/2020/04/22/designing-for-conversions-7-ux-tips-ecommerce?utm_campaign=2020-05-05&utm_medium=email&utm_source=courtside-20200505)
* [Docker Tips](https://twg.io/blog/things-i-wish-i-knew-about-docker-before-i-started-using-it/)
* [Firebase Storage in Google Cloud Functions](https://hackersandslackers.com/manage-files-in-google-cloud-storage-with-python/)
* [How to reload Django?](https://stackoverflow.com/questions/19094720/how-to-automatically-reload-django-when-files-change)
* [Quickstart for Python in the App Engine Flexible Environment](https://cloud.google.com/appengine/docs/flexible/python/quickstart#windows)
* [Testing Docker Locally](https://cloud.google.com/run/docs/testing/local)
* [The Python Runtime for the App Engine Flexible Environment](https://cloud.google.com/appengine/docs/flexible/python/runtime)
* [VS Code Django Guide](https://code.visualstudio.com/docs/python/tutorial-django)

## 🤝 Contributing

Contributions are always welcome! You are encouraged to submit issues, functionality, and features that you want to be addressed. See [`docs/contributing.md`](docs/contributing.md) to get started.

Anyone is welcome to contribute anything. Currently, my personal website would love:

* Art.
* More code.
* More documentation.
* Ideas.

## 📜 License

Made with 💖 by Keegan Skeate.

Except where otherewise noted, copyright © 2020 Keegan Skeate.

[GNU General Public License](http://www.gnu.org/licenses/gpl-3.0.html)

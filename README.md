# <img height="32" alt="" src="https://cannlytics.com/static/cannlytics_website/images/logos/cannlytics_calyx_detailed.svg"> Cannlytics Console

![version](https://img.shields.io/badge/version-0.0.4-brightgreen)
[![contributions welcome](https://img.shields.io/badge/contributions-welcome-brightgreen.svg)](https://github.com/cannlytics/cannlytics-console/fork)

Cannlytics is simple, easy-to-use, **end-to-end** cannabis analytics software made with 💖. Cannlytics' mission is to make cannabis analysis **simple** and **easy**. We believe that everyone in the cannabis industry should be able to easily access rich, valuable data and that you will be better off for it. This documentation covers the Cannlytics architecture and how to build, develop, and publish Cannlytics software. You can view the platform live at <https://cannlytics.com> and the documentation at <https://docs.cannlytics.com>.

- [Introduction](#introduction)
- [Contributing](#contributing)
- [Installation](#installation)
- [Architecture](#architecture)
- [Authentication](#authentication)
- [Development](#development)
- [Testing](#testing)
- [Publishing](#publishing)
- [Administration](#administration)
- [Resources](#resources)
- [License](#license)

## 🏫 Introduction <a name="introduction"></a>

Cannlytics' website provides people with information about cannabis analytics. The `cannlytics` package is the core module implementing cannabis analytics logic. The `cannlytics` module handles database interactions, file management, authentication and authorization, traceability, data importing and exporting, and the logic for all workflows, such as certificate creation, item transfers, and publishing results. The `api` is the interface between the user's application and the cannabis analytics logic of `cannlytics`. The `console` is the user application where user's can interface with the infrastructure, such as the database, and utilize the cannabis analytics logic.

## 🤝 Contributing <a name="contributing"></a>

Contributions are always welcome! You are encouraged to submit issues, functionality, and features that you want to be addressed. See [the contributing guide](/docs/markdown/about/contributing.md) to get started. Anyone is welcome to contribute anything. Email <dev@cannlytics.com> for a quick onboarding. Currently, the Cannlytics Console would love:

* Art;
* More code;
* More documentation;
* Ideas.

## 📖 Installation <a name="installation"></a>

Cannlytics is an open box and transparent. You do not have to guess about the software used in the Cannlytics Engine. Our philosophy is that **open source** and **free** solutions are the best ([**free** as in **free** speech, not as in *free beer*](http://www.gnu.org/philosophy/free-sw.html)). See the [installation guide](/installation) for complete instructions. The installation instructions will guide you through:

1. Cloning the Cannlytics Engine.
2. Setting your account credentials.
3. Installing Python, Python dependencies, and all development tools.

A good place to begin is to clone the repository and get a lay of the architecture.

```shell
git clone https://github.com/cannlytics/cannlytics_website.git
```

Cannlytics is built and depends on the following software and services, so you will need to install or be setup each service.

* [Python](https://www.python.org/psf/)
* [Django](https://www.djangoproject.com/foundation/)
* [Docker](https://docs.docker.com/get-docker/)
* [Firebase](https://firebase.google.com/)
* [Firebase Tools](https://firebase.google.com/docs/cli)
* [Google Cloud Platform](https://cloud.google.com/gcp)
* [Google Cloud SDK](https://dl.google.com/dl/cloudsdk/channels/rapid/GoogleCloudSDKInstaller.exe)
* [Node.js](https://nodejs.org/en/about/)
* [Javascript, HTML, CSS](https://www.w3schools.com/)
* [Gimp](https://www.gimp.org/about/)
* [Inkscape](https://inkscape.org/about/)

## 🏛️ Architecture <a name="architecture"></a>

The Cannlytics Website is built with [Python] using the [Django] framework. The Cannlytics Website runs on [Cloud Run](https://firebase.google.com/docs/hosting/cloud-run) and is hosted with [Firebase Hosting]. The Cannlytics Website utilizes [Firebase Authentication], an optional SQL database, a [Firestore] NoSQL database for real-time data management, and [Firebase Storage] for file storage. The Cannlytics Engine has a user interface that is built with [Flutter] and [Dart] with a backend powered by [Python].

<!-- FIXME: Leaf and Metrc links -->
Cannlytics users can swap out components for others. For example, Cannlytics users can swap out [Leaf] integration for [METRC] integration. Separating your choice of each component from another, Cannlytics frees users to choose combinations that suits them, freeing adminstrators and developers to focus on their preferred area of specialization.

For backing services, the Cannlytics Website utilizes several Google Cloud service, including:

  * Containerized using [Cloud Build](https://cloud.google.com/build).
  * Uploaded to [Cloud Registry](https://cloud.google.com/container-registry).
  * Runs as a stateless container on [Cloud Run](https://firebase.google.com/docs/hosting/cloud-run).
  * *Optional* [Cloud SQL](https://cloud.google.com/sql) can be utilized if desired.
  * Additional [Cloud Storage](https://cloud.google.com/storage) buckets can be used for file storage.
  * [Cloud Secret Manager](https://cloud.google.com/secret-manager/) is used for storing configurations and keeping secrets secret.

Resources:

* [WSGI Servers](https://www.fullstackpython.com/wsgi-servers.html)

  [Dart]: https://dart.dev/guides
  [Django]: https://www.djangoproject.com/
  [Firebase Authentication]: https://firebase.google.com/docs/auth
  [Firebase Hosting]: https://firebase.google.com/docs/hosting
  [Firebase Storage]: https://firebase.google.com/docs/storage
  [Firestore]: https://firebase.google.com/docs/firestore
  [Futter]: https://flutter.dev/docs
  [Python]: https://www.python.org/

## 🛡️ Authentication <a name="authentication"></a>

When you are ready to begin working, then you will need to setup your authorization.

Resources:

* [Firebase Custom Authentication System with Django](https://medium.com/@gabriel_gamil/firebase-custom-authentication-system-with-django-c411009ddb44)
* [Django with Google Firebase](https://hackanons.com/2018/03/python-django-with-google-firebase-getting-started-intro-basic-configuration-firebase-authentication-part1.html)

## 🔨 Development <a name="development"></a>

See [the development guide](https://cannlytics.com/dev) for a full-guide. Development can happen in many avenues. Principally, clone the repository, create a fork, work on your desired problem, and finally create a pull request for your changes.

### Documentation

In brief, you can run the docs locally with:

```shell
npm run docs
```

Building the documentation locally requires installing [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/) with [Docker](https://www.docker.com/get-started).

```shell
docker pull squidfunk/mkdocs-material
```

You will need to build the documentation's container:

```shell
docker build -t squidfunk/mkdocs-material docs
```

So you can preview the documentation as you write:

```shell
docker run --rm -it -p 8000:8000 -v "%cd%":/docs squidfunk/mkdocs-material
```

* [Quick note - how to fix django-livereload-server import error](https://gist.github.com/hangtwenty/f53b3867db1e33780505ccafd8d2eef0)

Finally, you can build the documentation:

```shell
npm run build-docs
```

And publish the documentation:

```shell
npm run publish-docs
```

### 📡 Data <a name="data"></a>

Cannlytics operates with a NoSQL database, Firebase by default, however, can be configured with any SQL database.

Resources:

* [Django Database API](https://docs.djangoproject.com/en/3.1/topics/db/queries/)

### 📁 Storage <a name="storage"></a>

Cannlytics utilizes Firebase Storage / Google Cloud Storage for most storage solutions.

* [Serving static files on App Engine](https://cloud.google.com/appengine/docs/standard/python3/serving-static-files)

### 🐞 Bugs <a name="bugs"></a>

See [bugs](https://cannlytics.com/bugs) for a full list of bugs and issues that you may encounter. Below are noteworthy bugs that you may encounter and their solutions.

- [Error: Can't Use Google Cloud Storage in Google Cloud Functions](https://stackoverflow.com/questions/52249978/write-to-google-cloud-storage-from-cloud-function-python/52250030)

  > **Solution** - If you are using Firebase Storage in a Google Cloud Function, then you need to specify `google-cloud-storage` in your `requirements.txt`.

* [Error: Firebase Hosting Base Rewrite Not Working](https://stackoverflow.com/questions/44871075/redirect-firebase-hosting-root-to-a-cloud-function-is-not-working)

  > **Solution** - In order to use a rewrite at the root in Firebase Hosting, you must not include an `index.html` file in the public folder.

## ⚗️ Testing <a name="testing"></a>

Please see [the testing guide](https://cannlyitcs.com/docs/testing) for full documentation on Cannlytics software testing. Generally, you can run tests for an app, e.g. `app_name` as follows.

```
python manage.py test app_name
```

The Cannlytics Website can be built locally for testing:

```shell
docker build . --tag gcr.io/cannlytics/cannlytics-website
gcloud auth configure-docker
docker push gcr.io/cannlytics/cannlytics-website
```

## 📚 Publishing <a name="publishing"></a>

See [the publishing guide](https://cannlytics.com/publishing) for complete instructions on how to publish the Cannlytics Engine for use. Publishing is done with one command:

```shell
npm run publish
```

The build process contains three steps:

1. Containerize the app and upload it to Container Registry.

Build your container image using Cloud Build by running the following command from the directory containing the Dockerfile:

`gcloud builds submit --tag gcr.io/cannlytics/cannlytics-website`

2. Deploy the container image to Cloud Run.

`gcloud beta run deploy cannlytics-website --image gcr.io/cannlytics/cannlytics-website --region us-central1 --allow-unauthenticated --service-account=${GCS_SA}`

3. Direct hosting requests to the containerized app.

This step provides access to this containerized app from a [Firebase Hosting](https://firebase.google.com/docs/hosting) URL, so the app can generate dynamic content for the Firebase-hosted site.

`firebase deploy --only hosting:production`

## 🕵️ Administration <a name="administration"></a>

*Admin Site*

* Get an admin password with `gcloud secrets versions access latest --secret admin_password && echo ""`

*User Authentication*

Helpful resources:

* [Django Admin Tutorial](https://docs.djangoproject.com/en/3.1/intro/tutorial07/)
* [Authenticating end users](https://cloud.google.com/run/docs/authenticating/end-users)
* [Authentication](https://cloud.google.com/run/docs/authenticating/public)
* [Google Cloud Authentication](https://google-auth.readthedocs.io/en/latest/user-guide.html)

## 🐕‍🦺 Resources <a name="resources"></a>

* [Django Philosophy](https://docs.djangoproject.com/en/3.1/misc/design-philosophies)
* [Django on Cloud Run](https://codelabs.developers.google.com/codelabs/cloud-run-django)
* [Firebase Storage in GCF](https://hackersandslackers.com/manage-files-in-google-cloud-storage-with-python/)
* [Design Tips](https://dribbble.com/stories/2020/04/22/designing-for-conversions-7-ux-tips-ecommerce?utm_campaign=2020-05-05&utm_medium=email&utm_source=courtside-20200505)
* [Docker Tips](https://twg.io/blog/things-i-wish-i-knew-about-docker-before-i-started-using-it/)
* [Testing Docker Locally](https://cloud.google.com/run/docs/testing/local)
* [The Python Runtime for the App Engine Flexible Environment](https://cloud.google.com/appengine/docs/flexible/python/runtime)
* [Quick start for Python in the App Engine Flexible Environment](https://cloud.google.com/appengine/docs/flexible/python/quickstart#windows)


## 📜 License <a name="license"></a>

**Cannlytics** Copyright (C) 2020-2021 Cannlytics and Cannlytics Contributors.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

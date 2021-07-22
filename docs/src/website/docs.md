# Cannlytics Website

<h1 align="center"><img align="center" width="300" alt="Cannlytics" src="https://cannlytics.com/static/cannlytics_website/images/logos/cannlytics_calyx_detailed.svg"></h1>

> Cannlytics is a modern cannabis testing engine, built and battle-tested on the bleeding 🩸 edge, to help you power your laboratory.

The Cannlytics engine comes with **batteries included**, but you are always welcome to supercharge your setup with modifications and custom components.

The Cannlytics Engine is:

* Free software;
* Freedom respecting;
* Community-driven;

> Currently, nonfree software is used in parts of the Cannlytics Engine. Cannlytics' mission is to systematically migrate all nonfree software to free software.

[TOC]

## 🏫 Introduction

Cannlytics is a healthy mix of user friendly interfaces and software that you can use in your cannabis-testing lab. Users do not have to have any advanced knowledge and can jump in at any point. There are many advanced features that people with background in the web stack, Python, or your favorite programming language can jump right into.

The Cannlytics Website provides people with information about Cannlytics. The Cannlytics Engine is a mobile, desktop, and web app that provides administrators, laboratory staff, laboratory clients, and client integrators to interact with laboratory information.

[![Generic badge](https://img.shields.io/badge/release-v1.0.0-blue.svg)](https://shields.io/)

* Features
* Road Map
* Development
* Testing
* Building
* Publishing
* Administration

## 🚀 Features

* [Cannlytics App](https://cannlytics.com/app)
* [Cannlytics Assistant](https://cannlytics.com/assistant)
* [Cannlytics Beanstalk](https://cannlytics.com/beanstalk)
* [Cannlytics Command Line Interface](https://cannlytics.com/cli)
  -Resource: [Codeburst](https://codeburst.io/building-beautiful-command-line-interfaces-with-python-26c7e1bb54df)
* [Cannlytics OakHeart Authentication](https://cannlytics.com/authentication)
* [Cannlytics Portal](https://cannlytics.com/portal)
* [Cannlytics Website](https://cannlytics.com/website)

## 🗺️ Road Map

TODO: Add features. Also;

* [Customize Error Pages](https://docs.djangoproject.com/en/3.1/howto/deployment/checklist/#customize-the-default-error-views)
* [Experiment with App Engine](https://cloud.google.com/appengine/docs/flexible/python/quickstart#windows)
* [Add Google Cloud Armor](https://cloud.google.com/blog/products/identity-security/google-cloud-armor-features-to-protect-your-websites-and-applications?utm_source=release-notes&utm_medium=email&utm_campaign=2020-aug-release-notes-1-en)
* [Write custom Django commands](https://docs.djangoproject.com/en/3.1/howto/custom-management-commands/)
* Cannlytics Assistant (bot)
* Users can chose their own UTC time.

## 📖 Installation

Cannlytics is an open box and transparent. You do not have to guess about the software used in the Cannlytics Engine. Cannlytics is built and depends on the following software and services.

* [Python](https://www.python.org/psf/)
* [Django](https://www.djangoproject.com/foundation/)
* [Firebase](https://firebase.google.com/)
* [Google Cloud Platform](https://cloud.google.com/gcp)
* [Node.js](https://nodejs.org/en/about/)
* [Javascript, HTML, CSS](https://www.w3schools.com/)
* [Gimp](https://www.gimp.org/about/)
* [Inkscape](https://inkscape.org/about/)

Our philosophy is that open source and free solutions are the best.

> ["'Free' as in 'free speech,' not as in 'free beer.'"](http://www.gnu.org/philosophy/free-sw.html)

Developing the Cannlytics Engine requires installing the following tools:

* [Django](https://docs.djangoproject.com/en/3.1/intro/tutorial01)
* [Docker](https://docs.docker.com/get-docker/)
* [Firebase Tools](https://firebase.google.com/docs/cli)
* [Google Cloud SDK](https://dl.google.com/dl/cloudsdk/channels/rapid/GoogleCloudSDKInstaller.exe)
* [Node.js](https://nodejs.org/en/download/)

See [installation](/installation) for complete instructions. The installation instructions will guide you through:

* Cloning the Cannlytics Engine.
* Setting your account credentials.
* Installing Python and Python dependencies.
* Installing development tools.

For a quick start, simply clone the repository:

```

git clone https://github.com/cannlytics/cannlytics_website.git

```

## 🛡️ Authentication

In Django, you can authenticate your Firebase app with [Pyrebase](https://github.com/thisbejim/Pyrebase) or in a custom manner.

Resources:

* [Firebase Custom Authentication System with Django](https://medium.com/@gabriel_gamil/firebase-custom-authentication-system-with-django-c411009ddb44)
* [Django with Google Firebase](https://hackanons.com/2018/03/python-django-with-google-firebase-getting-started-intro-basic-configuration-firebase-authentication-part1.html)

## 🏛️ Architecture

The Cannlytics Website is built with [Python] using the [Django] framework. The Cannlytics Website runs on [Cloud Run] and is hosted with [Firebase Hosting]. The Cannlytics Website utilizes [Firebase Authentication], an optional SQL database, a [Firestore] NoSQL database for real-time data management, and [Firebase Storage] for file storage. The Cannlytics Engine has a user interface that is built with [Flutter] and [Dart] with a backend powered by [Python].

Cannlytics users can swap out components for others. For example, Cannlytics users can swap out [Leaf] integration for [METRC] integration. Separating your choice of each component from another, Cannlytics frees users to choose combinations that suits them, freeing adminstrators and developers to focus on their preferred area of specialization.

For backing services, the Cannlytics Website utilizes several Google Cloud service, including:

  * Containerized using [Cloud Build]
  * Uploaded to [Cloud Registry]
  * Runs as a stateless container on [Cloud Run]
  * *Optional* [Cloud SQL](https://cloud.google.com/sql) can be utilized if desired.
  * Additional [Cloud Storage](https://cloud.google.com/storage) buckets can be used for file storage.
  * [Cloud Secret Manager](https://cloud.google.com/secret-manager/) is used for storing configurations and keeping secrets secret.

Resources:

* [WSGI Servers](https://www.fullstackpython.com/wsgi-servers.html)

<!-- Architecture References: -->

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

See [the development guide](https://cannlytics.com/dev) for a full-guide. Development can happen in many avenues. Principally, clone the repository, begin working on an area, referring to documentation as needed, and commit your changes.

## 📡 Database

Cannlytics operates with a NoSQL database by default, however, can be configured with an SQL database.

Full database model build:

```shell

python manage.py makemigrations
python manage.py migrate

```

Resources:

* [Django Database API](https://docs.djangoproject.com/en/3.1/topics/db/queries/)

## 📁 Storage

* [Serving static files on App Engine](https://cloud.google.com/appengine/docs/standard/python3/serving-static-files)

## 🐞 Bugs

See [bugs](https://cannlytics.com/bugs) for a full list of bugs and issues that you may encounte. Below are some prominant bugs that you may encounter:

* [*Using Google Cloud Storage in Google Cloud Functions*](https://stackoverflow.com/questions/52249978/write-to-google-cloud-storage-from-cloud-function-python/52250030)

  > If you are using Firebase Storage in a Google Cloud Function, then you need to specify `google-cloud-storage` in your `requirements.txt`.

* [Firebase Hosting Base Rewrite Not Working](https://stackoverflow.com/questions/44871075/redirect-firebase-hosting-root-to-a-cloud-function-is-not-working)

  > In order to use a rewrite at the root in Firebase Hosting, you must not include an `index.html` file in the public folder.

## ⚗️ Testing

Please see [the testing guide](https://cannlyitcs.com/docs/testing) for full documentation on Cannlytics software testing. Generally, you can run tests for an app with `python manage.py test app_name`.

The Cannlytics Website can be built locally for testing:

```shell

docker build . --tag gcr.io/cannlytics/cannlytics-website
gcloud auth configure-docker
docker push gcr.io/cannlytics/cannlytics-website

```

## 📚 Publishing

See [the publishing guide](https://cannlytics.com/publishing) for complete instructions on how to publish the Cannlytics Engine for use.

Publishing is done with one command:

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

## 🕵️ Administration

*Admin Site*

* Get an admin password with `gcloud secrets versions access latest --secret admin_password && echo ""`

*User Authentication*

Resources:

* [Django Admin Tutorial](https://docs.djangoproject.com/en/3.1/intro/tutorial07/)
* [Authenticating end users](https://cloud.google.com/run/docs/authenticating/end-users)
* [Authentication](https://cloud.google.com/run/docs/authenticating/public)
* [Google Cloud Authentication](https://google-auth.readthedocs.io/en/latest/user-guide.html)

## 🐕‍🦺 Resources

* [Django Philosophy](https://docs.djangoproject.com/en/3.1/misc/design-philosophies)
* [Django on Cloud Run](https://codelabs.developers.google.com/codelabs/cloud-run-django)
* [Firebase Storage in GCF](https://hackersandslackers.com/manage-files-in-google-cloud-storage-with-python/)
* [Design Tips](https://dribbble.com/stories/2020/04/22/designing-for-conversions-7-ux-tips-ecommerce?utm_campaign=2020-05-05&utm_medium=email&utm_source=courtside-20200505)
* [Docker Tips](https://twg.io/blog/things-i-wish-i-knew-about-docker-before-i-started-using-it/)
* [Testing Docker Locally](https://cloud.google.com/run/docs/testing/local)
* [The Python Runtime for the App Engine Flexible Environment](https://cloud.google.com/appengine/docs/flexible/python/runtime)
* [Quickstart for Python in the App Engine Flexible Environment](https://cloud.google.com/appengine/docs/flexible/python/quickstart#windows)

## 🤝 Contributing

Contributions are always welcome! You are encouraged to submit issues, functionality, and features that you want to be addressed. See [the contributing guide](https://github.com/cannlytics/cannlytics/blob/master/contributing.md) to get started.

Anyone is welcome to contribute anything. Currently, Cannlytics would love:

* Art;
* More code;
* More documentation;
* Ideas.

## 📜 License

Made with 💖 by Cannlytics.

Except where otherewise noted, copyright © 2020 Cannlytics.

[GNU General Public License](http://www.gnu.org/licenses/gpl-3.0.html)

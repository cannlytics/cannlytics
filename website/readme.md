<div align="center" style="text-align:center; margin-top:1rem; margin-bottom: 1rem;">
  <img style="max-width:420px" width="420px" alt="" src="https://firebasestorage.googleapis.com/v0/b/cannlytics.appspot.com/o/public%2Fimages%2Flogos%2Fcannlytics-website-logo.png?alt=media&token=3dc8ee8c-77ed-4ac2-b42e-b24c416911d3">
  <div style="margin-top:0.5rem;">
    <h3>Simple, easy, cannabis analytics.</h3>
  </div>

  <https://cannlytics.com>

[![License: MIT](https://img.shields.io/badge/License-MIT-darkgreen.svg)](https://opensource.org/licenses/MIT)
[![Version](https://img.shields.io/pypi/v/cannlytics.svg)](https://pypi.org/project/cannlytics)
[![PyPI download month](https://img.shields.io/pypi/dm/cannlytics.svg)](https://pypi.python.org/pypi/cannlytics/)

</div>

The 🔥 Cannlytics Website provides an aesthetic user interface for users to learn about Cannlytics and get set up with everything that they need to utilize Cannlytics to its fullest extent. This documentation explains the Cannlytics Website architecture and how to build, develop, and publish the website.

- [👩‍🏫 Introduction](#introduction)
- [🌱 Installation](#installation)
- [🏗️ Architecture](#architecture)
- [🪛 Development](#development)
- [🚀 Publishing](#publishing)
- [❤️ Support](#support)
- [🏛️ License](#license)

## 👩‍🏫 Introduction <a name="introduction"></a>

Cannlytics is a healthy mix of user friendly interfaces and software that you can use in your cannabis-testing lab. Users do not have to have any advanced knowledge and can jump in at any point. There are many advanced features that people with background in the web stack, Python, or your favorite programming language can jump right into. The objective of the Cannlytics Website is to provide people with information about Cannlytics and give everyone in the cannabis industry access to simple, easy, and end-to-end cannabis analytics. You can find all Cannlytics products below.

| Product | Status | Live URL |
|---------|--------|----------|
| [Cannlytics AI](https://github.com/cannlytics/cannlytics-ai) | 🟡 | In progress |
| [Cannlytics API](https://github.com/cannlytics/cannlytics-api) | 🟡 | In progress |
| [Cannlytics App](https://cannlytics.com/cannlytics-app) | 🟡  | In progress |
| [Cannlytics Console](https://github.com/cannlytics/cannlytics) | 🟢 | <https://console.cannlytics.com> |
| [Cannlytics Documentation](https://github.com/cannlytics/cannlytics-docs) | 🟢 | <https://docs.cannlytics.com> |
| [Cannlytics Python SDK](https://github.com/cannlytics/cannlytics-engine) | 🟢 | <https://pypi.org/project/cannlytics/>|
| [Cannlytics Website](https://github.com/cannlytics/cannlytics-website) | 🟢 | <https://cannlytics.com> |

## 🌱 Installation <a name="installation"></a>

In brief, installation entails:

1. [Cloning the repository.](#cloning-the-repository)
2. [Setting your Firebase account credentials.](#setting-your-account-credentials)
3. [Installing project dependencies and development tools.](#installing-dependencies)

### 1. Cloning the repository <a name="cloning-the-repository"></a>

The best place to begin is to clone the repository and get a lay of the architecture. You can open a command prompt, navigate to where you wish for the source code to live, and clone the repository.

```bash
git clone https://github.com/cannlytics/cannlytics-website.git
```

### 2. Setting your account credentials <a name="setting-your-account-credentials"></a>

Creating your credentials is often the most time consuming, yet important, part of installation. Once you have appropriately set all of your credentials, then you will be off to the races, safely and securely. Currently, Cannlytics expects a [Firebase account](https://console.firebase.google.com/) and a Firebase project, so [creating a Firebase project](https://firebase.google.com/docs/projects/learn-more) is often a good place to begin.

2.1. First, create an `.env` file at the project's root.

2.2. Next, create a Django secret key and save it in your `.env` file as follows.

```py
# tools/quickstart.py
from django.utils.crypto import get_random_string

# Generate a secret key for your project.
chars = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'
generated_secret_key = get_random_string(50, chars)
print(generated_secret_key)
```

```bash
# .env
SECRET_KEY=xyz
```

2.3 Next, [add a Firebase web app](https://firebase.google.com/docs/web/setup). We recommend using the same namespace you chose for your project, for example `your-lims`, and setting up [Firebase Hosting](https://firebase.google.com/docs/hosting) with your app. We recommend choosing a project name that is in kebab-case so that you can safely use the project name for many namespaces throughout the project. Once you have created a web app, navigate to your Firebase project settings, find your Firebase app Config, and set your Firebase configuration in your `.env` file.

```bash
# .env
FIREBASE_API_KEY=xyz
FIREBASE_AUTH_DOMAIN=your-lims.firebaseapp.com
FIREBASE_DATABASE_URL=https://your-lims.firebaseio.com
FIREBASE_PROJECT_ID=your-lims
FIREBASE_STORAGE_BUCKET=your-lims.appspot.com
FIREBASE_MESSAGING_SENDER_ID=123
FIREBASE_APP_ID=123
FIREBASE_MEASUREMENT_ID=G-abc
```

2.4. If you wish to leverage Cannlytics' email capabilities, then set `EMAIL_HOST_USER` and `EMAIL_HOST_PASSWORD` environment variables in your `.env` file. If you are using Gmail, then it is recommended that you [create a new app password](https://support.google.com/accounts/answer/185833/sign-in-with-app-passwords?hl=en).

```bash
# .env
EMAIL_HOST_USER=admin@your-company.com
EMAIL_HOST_PASSWORD=your-app-password
```

2.5. Finally, to facilitate development and administration of your app and Firebase account, you can create and download a service account and save the path to your service account as a `GOOGLE_APPLICATION_CREDENTIALS` environment variable. These credentials will only be used for development and administrative functionality. For your security, this configuration file needs to be kept in a safe place and should be treated as a password to your account.

```bash
# .env
GOOGLE_APPLICATION_CREDENTIALS=path/to/your/service/account.json
```

If you are leveraging Secret Manager, which is the default, then you will need to grant your service key *Secret Manager Admin* permissions in [Cloud IAM Admin](https://console.cloud.google.com/iam-admin/iam).

2.6. Finish by creating a `.firebasesrc` in the root directory with your Firebase Hosting references. For example:

```json
{
  "projects": {
    "default": "your-lims"
  },
  "targets": {
    "your-project": {
      "hosting": {
        "docs": [
          "your-lims-docs"
        ],
        "dev": [
          "your-lims-dev"
        ],
        "production": [
          "your-lims"
        ]
      }
    }
  }
}
```

### 3. Installing project dependencies and development tools <a name="installing-dependencies"></a>

Cannlytics is built and tested with Python 3.9 and above. We recommend using [Anaconda](https://docs.anaconda.com/anaconda/install/index.html) if you are developing Cannlytics. You can then create a virtual environment to test, develop, and use the Cannlytics Website in isolation and in a reproducible manner. After installing Anaconda, you can open a terminal in the console directory and run the following commands to create a ready-to-go environment.

```bash
conda create --name website python=3.9
conda activate website
pip install -r requirements.txt
python manage.py migrate
npm install
```

You are now ready to develop. Note that `python manage.py migrate` creates a new `db.sqlite3` file if you do not have one already.

## 🏗️ Architecture <a name="architecture"></a>

Cannlytics is an open, transparent box and you do not have to guess about the software used and how it is implemented. The Cannlytics Website is built with [Python](https://www.python.org/) using the [Django](https://www.djangoproject.com/) framework. The Cannlytics Website runs on [Cloud Run](https://firebase.google.com/docs/hosting/cloud-run) and is hosted with [Firebase Hosting](https://firebase.google.com/docs/hosting). The Cannlytics Website utilizes [Firebase Authentication](https://firebase.google.com/docs/auth), an optional SQL database, a [Firestore](https://firebase.google.com/docs/firestore) NoSQL database for real-time data management, and [Firebase Storage](https://firebase.google.com/docs/storage) for file storage. For publishing, the Cannlytics Website utilizes several Google Cloud services, including:

- [Cloud Build](https://cloud.google.com/build/docs) is used for containerizing the app;
- [Cloud Registry](https://cloud.google.com/container-registry) is used for uploading the app;
- [Cloud Run](https://firebase.google.com/docs/hosting/cloud-run) is used to run the stateless container.
- *Optional* [Cloud SQL](https://cloud.google.com/sql) can be utilized if desired.
- [Cloud Storage](https://cloud.google.com/storage) is used for file storage.
- [Cloud Secret Manager](https://cloud.google.com/secret-manager/) is used for storing configurations and keeping secrets secret.

> See [Django on Cloud Run](https://codelabs.developers.google.com/codelabs/cloud-run-django) for a good tutorial on how to run Django projects on Cloud Run.

The Cannlytics Website generally follows a model-template-view (MTV) architectural pattern, where:

- The **model** is Django, `cannlytics`, and all engine components, such as JavaScript and CSS, that contain the logic of the application, which is provided to the views.
- The **templates** are Django HTML files that describe the display and how data are presented.
- The **views** are Python functions that control the model's logic, specify and provide data to templates, and manage user requests.

Below is an overview of the project's directory.

```shell
├── .admin
│   └── tokens
│       └── your-firebase-service-account.json
├── .firebase
│   ├── firestore.indexes # Available database queries.
│   ├── firestore.rules # Database access control and data validation.
|   └── storage.rules # File storage access control and validation.
├── api
│   ├── {endpoint}
│   |   └── {endpoint}.py # Implementation of specific API endpoints.
│   ├── api.py # Implementation of general API endpoints.
|   └── urls.py # Defined API endpoints.
├── node_modules
├── public
|   └── static # Files hosted with Firebase hosting. Populated programmatically.
├── tests # Tests of all features and functionality.
├── tools # Development tools.
├── website
│   ├── assets
│   |   ├── css # StyleSheets.
│   |   └── js # JavaScript to be bundled into a `cannlytics` module.
│   ├── core # Required Django configuration.
│   ├── static/website # Static files, including images and Webpack bundles.
│   ├── templates/website # User interface templates.
│   ├── templatetags # Custom template helpers.
│   ├── views # Controls templates, context, user requests, and application logic.
│   ├── settings.py # Django configuration.
│   ├── state.py # Static text for certain pages and sections.
│   └── urls.py # Console navigation.
├── .env # Your secrets for development.
├── .firebasesrc # Firebase hosting sources.
├── db.sqlite3 # Unused SQL database.
├── Dockerfile # Docker container configuration.
├── firebase.json # Firebase configuration file.
├── LICENSE
├── manage.py # Django development utility script.
├── package.json # Node.js dependencies and scripts.
├── README.md
├── requirements.txt # Python requirements.
└── webpack.config.js # JavaScript and CSS Webpack bundle configuration.
```

## 🪛 Development <a name="development"></a>

Development can happen in many avenues. Frequent, small scope pull requests are encouraged. Any contribution, even if it needs future polishing, helps build the project and advance the field of cannabis analytics. In general;

1. [Create a fork](https://docs.github.com/en/github/getting-started-with-github/quickstart/fork-a-repo) of the repository and set up your development environment.
2. Work on a solution for your most-pressing problem. Be creative. 
3. [Create a pull request](https://docs.github.com/en/github/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/creating-a-pull-request) for your changes to be reviewed and merged into the project upon approval or for you to receive feedback on how your changes can be approved.

The simplest way to run the app is to open a command line from the project's root directory and run:

```bash
python manage.py runserver
```

You can leverage [django-livereload-server](https://github.com/tjwalch/django-livereload-server) for hot-reloading while you develop, simply with:

```bash
npm run start
```

> If you encounter problems with livereload, then try `pip uninstall django-livereload-server livereload` followed by `pip install django-livereload-server`. Also ensure that `PRODUCTION=False` in your `.env` file.

### Running the project for development with hot-reload <a name="running"></a>

Hot-reloading is an important tool of development. You can use `django-livereload-server`, which uses both [python-livereload](https://github.com/lepture/python-livereload) and [django-livereload](https://github.com/Fantomas42/django-livereload), for smooth reloading. You can install [django-live-reload-server](https://github.com/tjwalch/django-livereload-server) with:

```bash
pip install django-livereload-server
```

You can start hot-reloading by starting the `livereload` server:

```bash
python manage.py livereload
```

In another console, you start the Django development server as usual:

```bash
python manage.py runserver
```

You can compile JavaScript ([ES6](https://developers.google.com/web/shows/ttt/series-2/es2015)) and SCSS, utilizing [Webpack](https://webpack.js.org/). The output JavaScript bundle is a module and is callable from the user interface with the `cannlytics` namespace, handy for use in templates. You can run the build for development with:

```bash
webpack-dev-server --env production=False
```

It is an inconvenience to run multiple consoles, but a major convenience to have smooth hot-reloading. So, [`npm-run-all`](https://www.npmjs.com/package/npm-run-all) is used to run multiple servers in the same console for smooth development. When you are setup, you can run the project for development simply with:

```bash
npm run start
```

## 🚀 Publishing <a name="publishing"></a>

See [the publishing guide](https://docs.cannlytics.com/developers/publishing/) for complete instructions on how to publish Cannlytics for production. The guide is based on the [Running Django on Cloud Run guide](https://cloud.google.com/python/django/run#windows). After setup, publishing is done with one command:

```bash
npm run publish
```

If you need to change accounts or projects, then you can use:

```bash
gcloud config set account `ACCOUNT`
gcloud config set project `PROJECT ID`
```

The build process contains three steps:

1. Containerize the app and upload it to Container Registry.

Build your container image using [Cloud Build](https://cloud.google.com/build) by running the following command from the directory containing the Dockerfile:

```bash
gcloud builds submit --tag gcr.io/your-lims/cannlytics
```

2. Deploy the container image to Cloud Run.

```bash
gcloud beta run deploy your-lims --image gcr.io/your-lims/cannlytics --region us-central1 --allow-unauthenticated --service-account=${GCS_SA}
```

3. Direct hosting requests to the containerized app.

This step provides access to this containerized app from a [Firebase Hosting](https://firebase.google.com/docs/hosting) URL, so that the app can generate dynamic content for the Firebase-hosted site.

```bash
firebase deploy --only hosting:production
```

## ❤️ Support <a name="support"></a>

Cannlytics is made available with ❤️ and <a href="https://opencollective.com/cannlytics-company">your good will</a>. Please consider making a contribution to keep the good work coming. Thank you 🙏

🥞 Bitcoin donation address: 34CoUcAFprRnLnDTHt6FKMjZyvKvQHb6c6

## 🏛️ License <a name="license"></a>

```
Copyright (c) 2020-2021 Cannlytics

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

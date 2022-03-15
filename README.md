<div align="center" style="text-align:center; margin-top:1rem; margin-bottom: 1rem;">
  <img style="height:180px" alt="" src="https://firebasestorage.googleapis.com/v0/b/cannlytics.appspot.com/o/public%2Fimages%2Flogos%2Fcannlytics-space-logo.png?alt=media&token=87727d92-bfb1-43df-bb9e-e2308dfa9b08">
  <div style="margin-top:0.5rem;">
    <h3>Simple, easy, cannabis analytics.</h3>
  </div>

<https://cannlytics.com>

[![License: MIT](https://img.shields.io/badge/License-MIT-lightgreen.svg)](https://opensource.org/licenses/MIT)
[![Version](https://img.shields.io/pypi/v/cannlytics.svg)](https://pypi.org/project/cannlytics)
[![PyPI download month](https://img.shields.io/pypi/dm/cannlytics.svg)](https://pypi.python.org/pypi/cannlytics/)

</div>

Cannlytics is simple, easy-to-use, **end-to-end** cannabis analytics software designed to make your data and information accessible. Cannlytics makes cannabis analysis **simple** and **easy** through data accessibility. We believe that everyone in the cannabis industry should be able to access rich, valuable data quickly and easily and that you will be better off for it. This documentation covers the Cannlytics architecture and how to build, develop, and publish each Cannlytics component. You can refer to <https://docs.cannlytics.com> for using Cannlytics.

- [🔥 Introduction](#introduction)
- [🌱 Installation](#installation)
- [🏗️ Architecture](#architecture)
- [🪛 Development](#development)
  * [Compiling](#compiling)
  * [Serving](#serving)
- [👩‍🔬 Testing](#testing)
- [🚀 Publishing](#publishing)
- [🤝 Contributing](#contributing)
- [❤️ Support](#support)
- [🏛️ License](#license)

You can find a repository for each component if you are only interested in using part of Cannlytics.

| Component | Status | Live URL |
|---------|--------|----------|
| [Cannlytics AI](https://github.com/cannlytics/cannlytics-ai) | 🟡 | Under Development |
| [Cannlytics API](https://github.com/cannlytics/cannlytics-api) | 🟢 | <https://cannlytics.com/api> |
| [Cannlytics App](https://cannlytics.com/cannlytics-app) | 🟡  | In Planning |
| [Cannlytics Console](https://github.com/cannlytics/cannlytics-console) | 🟢 | <https://console.cannlytics.com> |
| [Cannlytics Documentation](https://github.com/cannlytics/cannlytics-docs) | 🟢 | <https://docs.cannlytics.com> |
| [Cannlytics Python SDK](https://github.com/cannlytics/cannlytics-engine) | 🟢 | <https://pypi.org/project/cannlytics/>|
| [Cannlytics Website](https://github.com/cannlytics/cannlytics-website) | 🟢 | <https://cannlytics.com> |

## 🔥 Introduction <a name="introduction"></a>

The `cannlytics` package is the core module implementing cannabis analytics logic. The `cannlytics` module handles [database interactions](#data), [file management](#storage), [authentication and authorization](#authentication), traceability, data importing and exporting, and the logic for all workflows, such as certificate creation, item transfers, and publishing results. The `api` is the interface between the user application and the cannabis analytics logic of `cannlytics`. The `console` is the user application where user's can interface with the infrastructure, such as the database, and utilize the cannabis analytics logic. The `docs` provide information about the project and the `website` provides people with information about cannabis analytics. You can also use the `ai` to automatically collect, augment, and make inferences from data.

## 🌱 Installation <a name="installation"></a>

In brief, installation entails:

1. [Cloning the repository.](#cloning-the-repository)
2. [Setting your Firebase account credentials.](#setting-your-account-credentials)
3. [Installing project dependencies and development tools.](#installing-dependencies)

### 1. Cloning the repository <a name="cloning-the-repository"></a>

The best place to begin is to clone the repository and get a lay of the architecture.

```shell
git clone https://github.com/cannlytics/cannlytics.git
```

### 2. Setting your account credentials <a name="setting-your-account-credentials"></a>

When you are ready to begin development or publish the Cannlytics web app, then you will need to setup your credentials. You will need to [create a Firebase account](https://console.firebase.google.com/) and start a project before you begin. We recommend choosing a project name that is in kebab-case so that you can safely use the project name for many namespaces throughout the project, for example `your-lims`. Below is a diagram that depicts how Cannlytics leverages [Firebase Authentication to authorize user requests](https://cloud.google.com/blog/products/gcp/how-to-authenticate-users-on-google-app-engine-using-firebase).

![Authentication on Google App Engine using Firebase](https://firebasestorage.googleapis.com/v0/b/cannlytics.appspot.com/o/public%2Fimages%2Fdiagrams%2Ffirebase_auth_diagram.png?alt=media&token=ca0afc16-4829-4785-abb0-695304de802c)

2.1. First, create an `.env` file at the project's root.

2.2. Next, create a Django secret key and save it your `.env` file as follows.

```py
# tools/quickstart.py
from django.utils.crypto import get_random_string

# Generate a secret key for your project.
chars = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'
generated_secret_key = get_random_string(50, chars)
print(generated_secret_key)
```

```shell
# .env
SECRET_KEY=xyz
```

2.3 Next, [add a Firebase web app](https://firebase.google.com/docs/web/setup). We recommend using the same namespace you chose for your project, for example `your-lims`, and setting up [Firebase Hosting] with your app. Once you have created a web app, navigate to your Firebase project settings, find your Firebase app Config, and set your Firebase configuration in your `.env` file.

```shell
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

2.4. If you wish to leverage Cannlytics' email capabilities, then set `EMAIL_HOST_USER` and `EMAIL_HOST_PASSWORD` environment variables in your `.env` file. It is recommended that you [create an app password](https://support.google.com/accounts/answer/185833/sign-in-with-app-passwords?hl=en) if you are using Gmail. After you have created your app password, set your Gmail email and app password as environment variables, `EMAIL_HOST_USER` and `EMAIL_HOST_PASSWORD` respectively.

```shell
echo EMAIL_HOST_USER=\"youremail@gmail.com\" >> .env
echo EMAIL_HOST_PASSWORD=\"your-app-password\" >> .env
gcloud secrets versions add cannlytics_settings --data-file .env
```

```shell
# .env
EMAIL_HOST_USER=admin@your-company.com
EMAIL_HOST_PASSWORD=your-app-password
```

2.5. Finally, to facilitate communication between your app and Firebase, create and download a service account and save the path to your service account as a `GOOGLE_APPLICATION_CREDENTIALS` environment variable. For your security, this configuration file needs to be kept in a safe place.

```shell
# .env
GOOGLE_APPLICATION_CREDENTIALS=path/to/your/service/account.json
```

You will need to grant your service key *Secret Manager Admin* permissions in [Cloud IAM Admin](https://console.cloud.google.com/iam-admin/iam).

2.6. Finish by creating a `.firebasesrc` in the root directory with your [Firebase Hosting] references. For example

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
        ],
        "website": [
          "your-website"
        ]
      }
    }
  }
}
```

### 3. Installing project dependencies and development tools <a name="installing-dependencies"></a>

<!-- npm install webpack-dev-server --save-dev -->

Cannlytics is built and depends on the following software and services, so you will need to install or setup each service. We recommend using the latest stable version of each piece of software whenever possible.

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

Cannlytics is built and tested with Python 3.9 and above. We recommend using [Anaconda](https://docs.anaconda.com/anaconda/install/index.html) if you are developing Cannlytics. You can then create a virtual environment to test, develop, and use the Cannlytics Console in isolation and in a reproducible manner. After installing Anaconda, you can open a terminal and run the following commands to create a ready-to-go environment.

```bash
conda create --name cannlytics python=3.9
conda activate cannlytics
pip install -r requirements.txt
python manage.py migrate
npm install
```

You are now ready to develop. Note that `python manage.py migrate` creates a new `db.sqlite3` file if you do not have one already.

## 🏗️ Architecture <a name="architecture"></a>

Cannlytics is built with [Python](https://www.python.org/) and leverages the [Django](https://www.djangoproject.com/) framework. Cannlytics utilizes [Firebase](https://firebase.google.com/) for user authentication with [Firebase Authentication](https://firebase.google.com/docs/auth), a [Firestore](https://firebase.google.com/docs/firestore) NoSQL database for real-time data management, [Firebase Storage](https://firebase.google.com/docs/storage) for file storage, and is hosted with [Firebase Hosting](https://firebase.google.com/docs/hosting). Cannlytics also uses a number of other [Google Cloud](https://console.cloud.google.com/) backend services for hosting, including:

| Service | Purpose |
|---------|---------|
| [Cloud Build](https://cloud.google.com/build) | Used to containerize the app. |
| [Cloud Registry](https://cloud.google.com/container-registry) | Used to upload the app to storage. |
| [Cloud Run](https://cloud.google.com/run) | Used to run the app as a stateless container. |
| [Cloud Storage](https://cloud.google.com/storage) | Used for file storage. |
| [Cloud Secret Manager](https://cloud.google.com/secret-manager) | Used for storing configurations and keeping secrets secret. |

Cannlytics generally follows a model-template-view (MTV) architectural pattern, where:

| | |
|-|-|
| **model** | Django, `cannlytics`, and all engine components, such as JavaScript and CSS, that contain the core logic, which is provided to the views.|
| **template** | Django HTML files that describe the display and how data are presented. |
| **view** | Python functions that control the model's logic, specify and provide data to templates, and manage user requests. [Django describes views](https://docs.djangoproject.com/en/3.1/intro/tutorial03/#write-views-that-actually-do-something) as follows: *"Your view can read records from a database, or not. It can use a template system such as Django's – or a third-party Python template system – or not. It can generate a PDF file, output XML, create a ZIP file on the fly, anything you want, using whatever Python libraries you want."* |

The architecture of the Cannlytics codebase is as follows.
<!-- TODO: Talk about `Dockerfile` and `webpack.config.js` in each folder -->
<!-- TODO: Talk about remaining cannlytics modules -->

```bash
├── .admin
│   └── tokens
│       └── your-firebase-service-account.json
├── .firebase
│   ├── firestore.indexes # Available database queries.
│   ├── firestore.rules # Database access control and data validation.
|   └── storage.rules # File storage access control and validation.
├── ai
│   ├── augmentation # Tools for automatically augmenting data.
│   ├── collection # Tools for automatically collecting data.
|   └── inference # Tools for automatically making inferences from data.
├── api
│   ├── {endpoint}
│   |   └── {endpoint}.py # Implementation of specific API endpoints.
│   ├── urls.py # Defined API endpoints.
|   └── views.py # Implementation of general API endpoints.
├── cannlytics
│   ├── auth # Core authentication logic.
│   ├── lims # All LIMS logic.
│   ├── metrc # Metrc API module.
│   ├── models # Main data entities.
│   ├── utils # General utility functions.
│   ├── firebase.py # Firebase module.
│   ├── paypal.py # PayPal module.
|   └── quickbooks.py # QuickBooks module.
├── console
│   ├── assets
│   |   ├── css # Core style, minified and bundled.
│   |   └── js # JavaScript bundled into a `cannlytics` module.
│   ├── core # Required Django configuration.
│   ├── static/console # Static files, like images.
│   ├── templates/console # User interface templates.
│   ├── settings.py # Django configuration.
│   ├── state.py # Static text for certain pages and sections.
│   ├── urls.py # Console navigation.
│   ├── utils.py # General console utility functions.
|   └── views.py # Implementation of user interfaces and their context.
├── docs
│   ├── src # The documentation text.
│   ├── theme # The style of the documentation.
|   └── Dockerfile # Documentation container configuration.
├── node_modules
├── public
|   └── static # Files hosted with Firebase hosting.
├── tests # Tests for all features and functionality.
├── tools # Development tools.
├── website # A company website.
├── .env # Your secrets.
├── .firebasesrc # Firebase hosting sources.
├── db.sqlite3 # Unused SQL database.
├── firebase.json # Firebase configuration file.
├── LICENSE
├── manage.py # Django utility script.
├── mkdocs.yaml # Documentation configuration.
├── package.json # Node.js dependencies and scripts.
├── README.md
└── requirements.txt # All Python requirements.
```

All text material is either stored in JSON in `state.py` or written in Markdown in `docs` directories. See [`python-markdown` Extensions](https://python-markdown.github.io/extensions/) for more information on rendering Markdown. For help with storing static files, see [serving static files on App Engine](https://cloud.google.com/appengine/docs/standard/python3/serving-static-files). If you modify assets, then you can gather all supporting files, located in each app's `static` directory, into the `public/static` directory with:

```shell
set PROJECT=website
python manage.py collectstatic --noinput
```

or

```shell
npm run console:collectstatic
npm run website:collectstatic
```

You can configure static files to be served from [Firebase Storage](https://firebase.google.com/docs/storage) instead of from [Firebase Hosting](https://firebase.google.com/docs/hosting) in `console/settings.py`.

### Data

Cannlytics operates with a NoSQL database, [Firestore](https://firebase.google.com/docs/firestore) by default. You can conceptualize every entity as a JSON object called a document. A group of documents is a collection. Every document is required to be a member of a collection. Below is a [diagram of the Cannlytics LIMS standard data models](https://firebasestorage.googleapis.com/v0/b/cannlytics.appspot.com/o/public%2Flims%2Fdiagrams%2Fcannlytics_standard_data_models_0_0_8.svg?alt=media&token=de8e81a9-6250-4aac-857e-3936d26b4f1b).

<img width="100%" alt="" src="https://firebasestorage.googleapis.com/v0/b/cannlytics.appspot.com/o/public%2Flims%2Fdiagrams%2Fcannlytics_standard_data_models_0_0_8.svg?alt=media&token=de8e81a9-6250-4aac-857e-3936d26b4f1b">

## 🪛 Development <a name="development"></a>

Development can happen in many avenues. Frequent, small scope pull requests are encouraged. Any contribution, even if it needs future polishing, helps build the project and advance the field of cannabis analytics. In general;

1. [Create a fork](https://docs.github.com/en/github/getting-started-with-github/quickstart/fork-a-repo) of the repository.
2. Work on a solution for your most-pressing problem. Be creative.
3. [Create a pull request](https://docs.github.com/en/github/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/creating-a-pull-request) for your changes to be reviewed and merged into the project upon approval or for you to receive feedback on how your changes can be approved.

The simplest way to run the app is to open a command line from the project's root directory, set a `PROJECT` environment variable, and run:

```shell
set PROJECT=website
python manage.py runserver
```

or

```shell
npm run console:dev
npm run website:dev
```

You can also leverage [django-livereload-server](https://github.com/tjwalch/django-livereload-server) for hot-reloading while you develop.

```shell
npm run console:start
npm run website:start
```

See the table below for a complete list of available development commands.

| Command | Purpose |
|---------|---------|
| `ai:deploy-cannabis-data-daily` | Deploy the routine that collects daily cannabis data. |
| `console:start` | Start the complete console development environment. |
| `console:serve` | Serve the assets with `webpack-dev-server`. |
| `console:livereload` | Serve Django with `django-livereload-server`. |
| `console:dev` | Serve Django with `runserver`. |
| `console:build` | Build the assets for production with `webpack`. |
| `console:collectstatic` | Gather all of the Django static files into the `public` directory. |
| `console:container` | Build a container image for the app. |
| `console:cloud` | Run the container image in the cloud. |
| `console:deploy` | Direct requests to the running container image. |
| `console:publish` | Perform all publishing steps: `build`, `container`, `cloud`, and `deploy`.
| `docs:install` | Install the documentation requirements and dependencies. |
| `docs:build` | Build the documentation. |
| `docs:publish` | Publish the documentation as a static site. |
| `docs:serve` | Serve the documentation locally for development. |
| `website:start` | Start the complete website development environment. |
| `website:serve` | Serve the assets with `webpack-dev-server`. |
| `website:livereload` | Serve Django with `django-livereload-server`. |
| `website:dev` | Serve Django with `runserver`. |
| `website:build` | Build the assets for production with `webpack`. |
| `website:collectstatic` | Gather all of the Django static files into the `public` directory. |
| `website:container` | Build a container image for the app. |
| `website:cloud` | Run the container image in the cloud. |
| `website:deploy` | Direct requests to the running container image. |
| `website:publish` | Perform all publishing steps: `build`, `container`, `cloud`, and `deploy`.

### Compiling the project <a name="compiling"></a>

Hot-reloading is an important tool of development. You can use `django-livereload-server`, which uses both [python-livereload](https://github.com/lepture/python-livereload) and [django-livereload](https://github.com/Fantomas42/django-livereload), for smooth reloading. You can install [django-live-reload-server](https://github.com/tjwalch/django-livereload-server) with:

```shell
pip install django-livereload-server
```

You can start hot-reloading by starting the `livereload` server:

```shell
set PROJECT=website
python manage.py livereload
```

In another console, you start the Django development server as usual:

```shell
set PROJECT=website
python manage.py runserver
```

You can build the static assets, JavaScript and CSS, utilizing [Webpack](https://webpack.js.org/). The JavaScript bundle is a JavaScript module and is callable from the user interface with the `cannlytics` namespace. You can run the build for development with:

```shell
webpack-dev-server --env production=False
```

or

```shell
npm run console:serve
npm run website:serve
```

It is an inconvenience to run multiple consoles, but a major convenience to have smooth hot-reloading. So, [`npm-run-all`](https://www.npmjs.com/package/npm-run-all) is used to run multiple servers in the same console for smooth development. When you are setup, you can run the project for development simply with:

```shell
npm run console:start
npm run website:start
```

### Serving the project <a name="serving"></a>

You can serve the built project from anywhere you desire. The default option is to serve the project from Google App Engine, outlined below in [publishing](#publishing). Below are general instructions for building and serving the project in a [Docker container image](https://docs.docker.com/get-started/02_our_app/#build-the-apps-container-image).

First, build the Docker container image:

```shell
# build docker image
docker build -t cannlytics .
```

You can register the container with:

```shell
# docker push to container registry. 
docker push cannlytics 
```

You can [run the application container](https://docs.docker.com/get-started/02_our_app/#start-an-app-container) locally with:

```shell
# run docker
docker run -dp 8080:8080 --env-file docker.env cannlytics
```

Finally, you can quickly run the container, or multiple containers, with:

```shell
# bring up containers
docker-compose up -d --build

# bring down
docker-compose down

# logs
docker-compose logs
```

Congratulations, you can now build and run Cannlytics just about anywhere! The sky is the limit.

## 👩‍🔬 Testing <a name="testing"></a>

You can check for errors detectable by Django with:

```shell
python manage.py check
```

You can run tests for a specific app with.

```shell
python manage.py test your_app_name
```

You can also build the platform in a docker container for your specific purposes:

```shell
docker build . --tag gcr.io/your-lims/cannlytics
gcloud auth configure-docker
docker push gcr.io/your-lims/cannlytics
```

Perusing the `tests` directory is actually a good place to find examples on how to use Cannlytics and can be a good place to begin your explorations.

## 🚀 Publishing <a name="publishing"></a>

See [the publishing guide](https://docs.cannlytics.com/developers/publishing/) for complete instructions on how to publish Cannlytics for production. The guide is based on the [Running Django on Cloud Run guide](https://cloud.google.com/python/django/run#windows). After setup, publishing is done with one command:

```shell
npm run console:publish
npm run website:publish
```

If you need to change accounts or projects, then you can use:

```shell
gcloud config set account `ACCOUNT`
gcloud config set project `PROJECT ID`
```

The build process contains three steps:

1. Containerize the app and upload it to Container Registry.

Build your container image using [Cloud Build](https://cloud.google.com/build) by running the following command from the directory containing the Dockerfile:

```shell
gcloud builds submit --tag gcr.io/your-lims/cannlytics
```

2. Deploy the container image to Cloud Run.

```shell
gcloud beta run deploy your-lims --image gcr.io/your-lims/cannlytics --region us-central1 --allow-unauthenticated --service-account=${GCS_SA}
```

3. Direct hosting requests to the containerized app.

This step provides access to this containerized app from a [Firebase Hosting] URL, so the app can generate dynamic content for the Firebase-hosted site.

```shell
firebase deploy --only hosting:production
```

## 🤝 Contributing <a name="contributing"></a>

Contributions are always welcome! You are encouraged to submit issues, functionality, and features that you want to be addressed. See [the contributing guide](https://docs.cannlytics.com/developers/contributing/) to get started. Anyone is welcome to contribute anything. Email <dev@cannlytics.com> for a quick onboarding. Currently, the codebase could greatly benefit from:

* Art;
* More code;
* More documentation;
* Ideas;
* Tests;
* Examples.

## ❤️ Support <a name="support"></a>

Cannlytics is made available with ❤️ and your good will. Please consider making a contribution to help us continue crafting useful tools and data pipelines for you.

| | |
|-|-|
| 💸 PayPal Donation | <form action="https://www.paypal.com/donate" method="post" target="_top"><input type="hidden" name="hosted_button_id" value="SSB85GMSZB6UG" /><input type="image" src="https://www.paypalobjects.com/en_US/i/btn/btn_donate_SM.gif" border="0" name="submit" title="PayPal - The safer, easier way to pay online!" alt="Donate with PayPal button" /><img alt="" border="0" src="https://www.paypal.com/en_US/i/scr/pixel.gif" width="1" height="1" /></form> |
| 🪙 Bitcoin donation address| 34CoUcAFprRnLnDTHt6FKMjZyvKvQHb6c6 |
| ⚡ Ethereum donation address | 0x8997cA09B3FAe2ce4039E295A5269cf4ae7a0BA5 |

## 🏛️ License <a name="license"></a>

```
Copyright (c) 2020-2022 Cannlytics

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

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

- [🔥 Introduction](#introduction)
- [🪴 Installation](#installation)
- [🏗️ Architecture](#architecture)
- [🚜 Development](#development)
  * [Editing](#editing)
  * [Running](#running)
  * [Serving](#serving)
- [🧪 Testing](#testing)
- [🚀 Publishing](#publishing)

## 🔥 Introduction <a name="introduction"></a>

The `cannlytics` package is the core module implementing cannabis analytics logic. The `cannlytics` module handles [database interactions](#data), [file management](#storage), [authentication and authorization](#authentication), traceability, data importing and exporting, and the logic for all workflows, such as certificate creation, item transfers, and publishing results. The `api` is the interface between the user application and the cannabis analytics logic of `cannlytics`. The `console` is the user application where user's can interface with the infrastructure, such as the database, and utilize the cannabis analytics logic. The `docs` provide information about the project and the `website` provides people with information about cannabis analytics. You can also use the `ai` to automatically collect, augment, and make inferences from data.

## 🪴 Installation <a name="installation"></a>

In brief, installation entails:

1. [Cloning the repository.](#cloning-the-repository)
2. [Setting your Firebase account credentials.](#setting-your-account-credentials)
3. [Installing project dependencies and development tools.](#installing-dependencies)

### 1. Cloning the repository <a name="cloning-the-repository"></a>

The best place to begin is to clone the repository and get a lay of the architecture.

```shell
git clone https://github.com/cannlytics/cannlytics.git
```

The architecture of the Cannlytics codebase is as follows.

```bash
├── .admin
│   └── tokens
│       └── your-firebase-service-account.json
├── .firebase
│   ├── firestore.indexes # Available database queries.
│   ├── firestore.rules # Database access control and data validation.
|   └── storage.rules # File storage access control and validation.
├── ai
│   ├── curation # Tools for automatically cleaning and augmenting data.
│   ├── functions # Tools for automatically collecting data.
|   └── inference # Tools for automatically making inferences from data.
├── api
│   ├── {endpoint}
│   |   └── {endpoint}.py # Implementation of specific API endpoints.
│   ├── urls.py # Defined API endpoints.
|   └── views.py # Implementation of general API endpoints.
├── cannlytics
│   ├── auth # Core authentication logic.
│   ├── ccrs # Interface to Washington State's traceability system.
│   ├── charts # Crispy, ready-to-use charts.
│   ├── data # Data logic, from wrangling to market.
│   ├── firebase # Interface to Firebase.
│   ├── lims # All laboratory information management (LIMS) logic.
│   ├── metrc # Interface to the Metrc traceability system.
│   ├── models # Defined models.
│   ├── paypal # Interface to PayPal.
│   ├── quickbooks # Interface to QuickBooks.
│   ├── stats # Nifty, ready-to-use statistical models.
│   ├── utils # General utility functions.
│   ├── cannlytics.py # Core Cannlytics interface.
|   └── requirements.txt # Package-specific requirements.
├── console
│   ├── assets
│   |   ├── css # Stylesheets that will be minified and bundled.
│   |   └── js # JavaScript that will be bundled into a `cannlytics.min.js` module.
│   ├── core # Required Django configuration.
│   ├── static/console # Static files, such as images and Excel templates.
│   ├── templates/console # User interface templates.
│   ├── templatetags # Custom Django template utility functions.
│   ├── views # Implementation of user interfaces and their context.
│   |   └── {view}.py # Views for specific purposes.
│   ├── db.sqlite3 # Unused SQL database.
│   ├── Dockerfile # Production configuration.
│   ├── requirements.txt # Console-specific requirements.
│   ├── settings.py # Django configuration.
│   ├── state.py # Static text for certain pages and sections.
│   ├── urls.py # Console navigation.
|   └── webpack.config.js # Build configuration.
├── docs
│   ├── {src} # Specific documentation.
│   ├── theme # The style of the documentation site.
|   └── Dockerfile # Documentation container configuration.
├── node_modules
├── public # Files hosted with Firebase hosting.
├── tests # Tests for all features and functionality.
├── tools # Administrative, developer, and data management tools.
├── website # A company website with the same structure as the `console`.
├── .env # Your secrets.
├── .firebasesrc # Firebase hosting sources.
├── .gitignore # Files not committed to GitHub.
├── firebase.json # Firebase configuration file.
├── manage.py # Django utility script.
├── mkdocs.yaml # Documentation configuration.
├── package.json # Node.js dependencies and scripts.
├── requirements.txt # All Python requirements.
└── setup.py # Python SDK configuration.
```

### 2. Installing project dependencies and development tools <a name="installing-dependencies"></a>

You will need to install the following technologies when developing or creating an installation of Cannlytics. We recommend using the latest stable version of each piece of software whenever possible. Cannlytics has been tested with Python 3.9.

* [Python](https://www.python.org/psf/)
* [Docker](https://docs.docker.com/get-docker/)
* [Node.js](https://nodejs.org/en/about/)

The standard installation requires that you have an account with:

* [Firebase](https://firebase.google.com/)
* [Google Cloud Platform](https://cloud.google.com/gcp)

If you are developing Cannlytics, then you will need a couple extra tools:

* [Firebase Tools](https://firebase.google.com/docs/cli)
* [Google Cloud SDK](https://dl.google.com/dl/cloudsdk/channels/rapid/GoogleCloudSDKInstaller.exe)

We recommend using [Anaconda](https://docs.anaconda.com/anaconda/install/index.html) if you are developing Cannlytics so that you can create a virtual environment to test, develop, and use the Cannlytics Console in isolation and in a reproducible manner. After installing Anaconda, you can open a terminal and run the following commands to create a ready-to-go environment.

<!-- Is this needed? npm install webpack-dev-server --save-dev -->
```bash
conda create --name cannlytics python=3.9
conda activate cannlytics
pip install -r requirements.txt
python manage.py migrate
npm install
```

> Note that `python manage.py migrate` creates a new `db.sqlite3` file if you do not have one already.

### 3. Setting your account credentials <a name="setting-your-account-credentials"></a>

For a standard setup, you will need to [create a Firebase account and a project](https://console.firebase.google.com/). We recommend choosing a project name that is in kebab-case, e.g. `your-lims`, so that you can safely use the project name in many places. Now, follow these steps to fill in your environment variables. When publishing, you will need to copy pertinent environment variables to a [Google Cloud Secret](https://codelabs.developers.google.com/codelabs/cloud-run-django/index.html?index=..%2F..index#4).

1. Create an `.env` file in your project's root directory. See `.env.example` for an example with all credentials.
2. Create a Django secret key:
    ```py
    # tools/quickstart.py
    from django.utils.crypto import get_random_string

    # Generate a secret key for your project.
    chars = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'
    generated_secret_key = get_random_string(50, chars)
    print(generated_secret_key)
    ```

    And save it in your `.env` file:

    ```bash
    # .env
    SECRET_KEY=xyz
    ```
3. [Create a Firebase web app](https://firebase.google.com/docs/web/setup). We recommend using the same namespace you chose for your project, e.g. `your-lims` or `your-lims-dev`, and setting up [Firebase Hosting](https://firebase.google.com/docs/hosting) with your app. Once you have created a Firebase web app, navigate to your Firebase project settings, find your Firebase App Config, and set your Firebase configuration in your `.env` file.
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
4. If you wish to leverage Cannlytics' email capabilities, then set `EMAIL_HOST_USER` and `EMAIL_HOST_PASSWORD` environment variables in your `.env` file. It is recommended that you [create an app password](https://support.google.com/accounts/answer/185833/sign-in-with-app-passwords?hl=en) if you are using Gmail. After you have created your app password, set your email and app password as environment variables, `EMAIL_HOST_USER` and `EMAIL_HOST_PASSWORD` respectively.
    ```bash
    # .env
    EMAIL_HOST_USER=admin@your-company.com
    EMAIL_HOST_PASSWORD=your-app-password
    ```
5. Finally, to facilitate Firebase management, create and download a service account and save the path to your service account as a `GOOGLE_APPLICATION_CREDENTIALS` environment variable. For accessing [secrets](https://cloud.google.com/secret-manager), you will need to grant your service key *Secret Manager Admin* permissions in [Cloud IAM Admin](https://console.cloud.google.com/iam-admin/iam). For your security, this configuration file needs to be kept in a safe place.
    ```bash
    # .env
    GOOGLE_APPLICATION_CREDENTIALS=path/to/your/service/account.json
    ```
6. Finish by creating a `.firebaserc` in the root directory with your [Firebase Hosting](https://firebase.google.com/docs/hosting) references. See `example.firebaserc` for an example.

You are now ready to develop!

## 🏗️ Architecture <a name="architecture"></a>

The Cannlytics Console and Cannlytics Website are built with the [Django](https://www.djangoproject.com/) framework and generally follow a model-template-view (MTV) architectural pattern, where:

| Abstraction | Description |
|-|-|
| **Model** | The `cannlytics` package, Django, and all `assets`, such as JavaScript and CSS, that contain the core logic, which is provided to the views.|
| **Template** | Django HTML files that describe the display and how data are presented. |
| **View** | Python functions that control the model's logic, specify and provide data to templates, and manage user requests. [Django describes views](https://docs.djangoproject.com/en/3.1/intro/tutorial03/#write-views-that-actually-do-something) as follows: *"Your view can read records from a database, or not. It can use a template system such as Django's – or a third-party Python template system – or not. It can generate a PDF file, output XML, create a ZIP file on the fly, anything you want, using whatever Python libraries you want."* |

Cannlytics utilizes a number of [Google Cloud](https://console.cloud.google.com/) services, including:

| Service | Purpose |
|---------|---------|
| [Firebase](https://firebase.google.com/) | Cloud services, such as [dynamic links](https://firebase.google.com/docs/dynamic-links). |
| [Firebase Authentication](https://firebase.google.com/docs/auth) | User authentication. |
| [Firebase Firestore](https://firebase.google.com/docs/firestore) | NoSQL database for real-time data management. |
| [Firebase Storage](https://firebase.google.com/docs/storage) | File storage. |
| [Firebase Hosting](https://firebase.google.com/docs/hosting) | Console, website, and documentation hosting. |
| [Cloud Build](https://cloud.google.com/build) | Used to containerize the app. |
| [Cloud Registry](https://cloud.google.com/container-registry) | Used to upload the app to storage. |
| [Cloud Run](https://cloud.google.com/run) | Used to run the app as a stateless container. |
| [Cloud Storage](https://cloud.google.com/storage) | Used for console and website file storage. |
| [Cloud Secret Manager](https://cloud.google.com/secret-manager) | Used for storing configurations and keeping secrets secret. |

The [standard Cannlytics data models](https://firebasestorage.googleapis.com/v0/b/cannlytics.appspot.com/o/public%2Flims%2Fdiagrams%2Fcannlytics_standard_data_models_0_0_8.svg?alt=media&token=de8e81a9-6250-4aac-857e-3936d26b4f1b) and their default fields are shown below. Cannlytics data models are highly flexible and can contain fewer, different, or additional fields.

<img width="100%" alt="" src="https://firebasestorage.googleapis.com/v0/b/cannlytics.appspot.com/o/public%2Flims%2Fdiagrams%2Fcannlytics_standard_data_models_0_0_8.svg?alt=media&token=de8e81a9-6250-4aac-857e-3936d26b4f1b">

## 🚜 Development <a name="development"></a>

Development can happen in many avenues. Frequent, small scope pull requests are encouraged. Any contribution, even if it needs future polishing, helps build the project and advance cannabis science. In general;

1. [Create a fork](https://docs.github.com/en/github/getting-started-with-github/quickstart/fork-a-repo) of the repository.
2. [Edit the project](#edit) by improving the codebase in some manner. Be creative.
3. [Create a pull request](https://docs.github.com/en/github/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/creating-a-pull-request) for your changes to be reviewed and merged into the project upon approval or for you to receive feedback on how your changes can be approved.

The table below lists available development commands.

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

### Editing the project <a name="editing"></a>

All text material is either stored in JSON in `state.py` or written in Markdown in `docs` directories. See [`python-markdown` Extensions](https://python-markdown.github.io/extensions/) for more information on rendering Markdown. For help with storing static files, see [serving static files on App Engine](https://cloud.google.com/appengine/docs/standard/python3/serving-static-files). You can configure static files to be served from [Firebase Storage](https://firebase.google.com/docs/storage) instead of from [Firebase Hosting](https://firebase.google.com/docs/hosting) in `console/settings.py` or `website/settings.py`. If you modify assets, then you can gather all supporting files, located in each app's `static` directory, into the `public/static` directory with:

```shell
set PROJECT=website
python manage.py collectstatic --noinput
```

or

```shell
npm run console:collectstatic
# or
npm run website:collectstatic
```

### Running the project <a name="running"></a>

The simplest way to run the app is to open a command line from the project's root directory, set a `PROJECT` environment variable, and run:

```shell
set PROJECT=website
python manage.py runserver
```

or

```shell
npm run console:dev
# or
npm run website:dev
```

You can also leverage [django-livereload-server](https://github.com/tjwalch/django-livereload-server) for hot-reloading while you develop.

```shell
npm run console:start
# or
npm run website:start
```

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
# or
npm run website:serve
```

It is an inconvenience to run multiple consoles, but a major convenience to have smooth hot-reloading. So, [`npm-run-all`](https://www.npmjs.com/package/npm-run-all) is used to run multiple servers in the same console for smooth development. When you are setup, you can run the project for development simply with:

```shell
npm run console:start
# or
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

## 🧪 Testing <a name="testing"></a>

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
# or
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

<div align="center" style="text-align:center; margin-top:1rem; margin-bottom: 1rem;">
  <img style="max-width:420px" width="420px" alt="" src="https://firebasestorage.googleapis.com/v0/b/cannlytics.appspot.com/o/public%2Fimages%2Flogos%2Fcannlytics-console-logo.png?alt=media&token=0c017a89-6752-4a14-98d5-2476393e3127">
  <div style="margin-top:0.5rem;">
    <h3>Simple, easy, cannabis analytics.</h3>
  </div>

  <https://console.cannlytics.com>

[![License: MIT](https://img.shields.io/badge/License-MIT-darkgreen.svg)](https://opensource.org/licenses/MIT)

</div>

🔥 Cannlytics is simple, easy-to-use, **end-to-end** cannabis analytics software designed to make your data and information accessible. We believe that everyone in the cannabis industry should be able to access their rich, valuable data quickly and easily and that you will be better off for it. This documentation covers how to build, develop, and publish the Cannlytics Console, your user interface to wield the power of Cannlytics.

- [👩‍🏫 Introduction](#introduction)
- [🌱 Installation](#installation)
- [🏗️ Architecture](#architecture)
- [🔨 Development](#development)
  * [Authentication](#authentication)
  * [Running the project for development](#running)
  * [Data](#data)
  * [File Storage](#storage)
  * [Email](#email)
  * [Views](#views)
  * [Templates](#templates)
  * [Style](#style)
  * [Text](#text)
  * [Building and running the project with Docker](#docker)
- [👩‍🔬 Testing](#testing)
- [🚀 Publishing](#publishing)

## 👩‍🏫 Introduction <a name="introduction"></a>

The Cannlytics Console is a user interface for `cannlytics`, the core module implementing cannabis analytics, [database interactions](#data), [file management](#storage), [authentication and authorization](#authentication), traceability, data importing and exporting, and the logic for all workflows, such as certificate creation, item transfers, and publishing results. The `api` is the interface between the user application and `cannlytics`. The `console` is the user application where user's can interface with `cannlytics`.

## 🌱 Installation <a name="installation"></a>

In brief, installation entails:

1. [Cloning the repository.](#cloning-the-repository)
2. [Setting your Firebase account credentials.](#setting-your-account-credentials)
3. [Installing project dependencies and development tools.](#installing-dependencies)

### 1. Cloning the repository <a name="cloning-the-repository"></a>

The best place to begin is to clone the repository and get a lay of the architecture. You can open a command prompt, navigate to where you wish for the source code to live, and clone the repository.

```bash
git clone https://github.com/cannlytics/cannlytics-console.git
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

<!-- npm install webpack-dev-server --save-dev -->

Cannlytics is built and tested with Python 3.9 and above. We recommend using [Anaconda](https://docs.anaconda.com/anaconda/install/index.html) if you are developing Cannlytics. You can then create a virtual environment to test, develop, and use the Cannlytics Console in isolation and in a reproducible manner. After installing Anaconda, you can open a terminal in the console directory and run the following commands to create a ready-to-go environment.

```bash
conda create --name console python=3.9
conda activate console
pip install -r requirements.txt
python manage.py migrate
npm install
```

You are now ready to develop. Note that `python manage.py migrate` creates a new `db.sqlite3` file if you do not have one already.

## 🏗️ Architecture <a name="architecture"></a>

Cannlytics is built with [Python](https://www.python.org/) and leverages the [Django](https://www.djangoproject.com/) framework. Cannlytics utilizes [Firebase](https://firebase.google.com/) for user authentication with [Firebase Authentication](https://firebase.google.com/docs/auth), a [Firestore](https://firebase.google.com/docs/firestore) NoSQL database for real-time data management, [Firebase Storage](https://firebase.google.com/docs/storage) for file storage, and is hosted with [Firebase Hosting](https://firebase.google.com/docs/hosting). Cannlytics uses a number of [Google Cloud](https://console.cloud.google.com/) backend services, including:

  - [Cloud Build](https://cloud.google.com/build) to containerize the app.
  - [Cloud Registry](https://cloud.google.com/container-registry) to upload the app to storage.
  - [Cloud Run](https://cloud.google.com/run) to run the app as a stateless container.
  - [Cloud Storage](https://cloud.google.com/storage) for additional file storage.
  - [Cloud Secret Manager](https://cloud.google.com/secret-manager) for storing configurations and keeping secrets secret.
    <!-- * *Optional* [Cloud SQL](https://cloud.google.com/sql) can be utilized if desired. -->

Cannlytics generally follows a model-template-view (MTV) architectural pattern, where:

- The **model** is Django, `cannlytics`, and all engine components, such as JavaScript and CSS, that contain the logic of the application, which is provided to the views.
- The **templates** are Django HTML files that describe the display and how data are presented.
- The **views** are Python functions that control the model's logic, specify and provide data to templates, and manage user requests.

Cannlytics favors a [domain-style code structure](https://stackoverflow.com/questions/40233657/ddd-what-is-proper-code-structure) for apps and material that will be edited frequently, separating Python views, HTML templates, and Javascript/CSS assets, and a [ducks-style code structure](https://www.etatvasoft.com/insights/react-design-patterns-and-structures-of-redux-and-flux/) for concepts within the apps, grouping dependencies required for a specific feature. 🦆 Ducks can inherit properties if needed, but are encouraged to be individualized and as self-contained as possible. The architecture of the Cannlytics app is as follows.

```bash
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
├── console
│   ├── assets
│   |   ├── css # StyleSheets.
│   |   └── js # JavaScript to be bundled into a `cannlytics` module.
│   ├── core # Required Django configuration.
│   ├── static/console # Static files, including images and Webpack bundles.
│   ├── templates/console # User interface templates.
│   ├── templatetags # Custom template helpers.
│   ├── views # Controls templates, context, user requests, and application logic.
│   ├── settings.py # Django configuration.
│   ├── state.py # Static text for certain pages and sections.
│   └── urls.py # Console navigation.
├── node_modules
├── public
|   └── static # Files hosted with Firebase hosting. Populated programmatically.
├── tests # Tests of all features and functionality.
├── tools # Development tools.
├── .env # Your secrets.
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

## 🔨 Development <a name="development"></a>

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

> If you encounter problems with livereload, then try `pip uninstall django-livereload-server livereload` followed by `pip install django-livereload-server`.

### Authentication <a name="authentication"></a>

Below is a diagram that depicts how Cannlytics leverages [Firebase Authentication](https://firebase.google.com/docs/auth) to authorize user requests.

![Authentication on Google App Engine using Firebase](https://firebasestorage.googleapis.com/v0/b/cannlytics.appspot.com/o/public%2Fimages%2Fdiagrams%2Ffirebase_auth_diagram.png?alt=media&token=ca0afc16-4829-4785-abb0-695304de802c)

Original image: [How to authenticate users on Google App Engine using Firebase](https://cloud.google.com/blog/products/gcp/how-to-authenticate-users-on-google-app-engine-using-firebase)

### Running the project for development <a name="running"></a>

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

### Data <a name="data"></a>

Cannlytics operates with a NoSQL database, [Firestore](https://firebase.google.com/docs/firestore) by default. You can conceptualize every entity as a JSON object called a document. A group of documents is a collection. Every document is required to be a member of a collection. Below is a [diagram of the Cannlytics LIMS standard data models](https://firebasestorage.googleapis.com/v0/b/cannlytics.appspot.com/o/public%2Flims%2Fdiagrams%2Fcannlytics_standard_data_models_0_0_8.svg?alt=media&token=de8e81a9-6250-4aac-857e-3936d26b4f1b).

<img width="100%" style="max-width:1300px;" alt="" src="https://firebasestorage.googleapis.com/v0/b/cannlytics.appspot.com/o/public%2Flims%2Fdiagrams%2Fcannlytics_standard_data_models_0_0_8.svg?alt=media&token=de8e81a9-6250-4aac-857e-3936d26b4f1b">

### File Storage <a name="storage"></a>

Cannlytics utilizes [Firebase Storage](https://firebase.google.com/docs/storage) ( a.k.a Google Cloud Storage) for most storage solutions. For help with storing static files, see [serving static files on App Engine](https://cloud.google.com/appengine/docs/standard/python3/serving-static-files). You can gather all supporting files, located in each app's `static` directory, into the `public/static` directory with:

```bash
python manage.py collectstatic --noinput
```

You can configure static files to be served from [Firebase Storage](https://firebase.google.com/docs/storage) instead of from [Firebase Hosting](https://firebase.google.com/docs/hosting) in `console/settings.py`.

### Email <a name="email"></a>

If you are sending email with Gmail, then you can follow these steps.

- Navigate to [Gmail](https://mail.google.com), click your profile, and click manage your google account.
- Navigate to the [security tab](https://myaccount.google.com/security).
- Enable 2-step verification and then click on App passwords.
- Select Mail for app and enter a custom name for device.
- Click generate and Gmail will generate an app password. Copy this app password to a text file and save it where it is secure and will not be uploaded to a public repository, for example save the password in the `.admin` directory.

After you have created your app password, set your Gmail email and app password as environment variables, `EMAIL_HOST_USER` and `EMAIL_HOST_PASSWORD` respectively.

```bash
echo EMAIL_HOST_USER=\"youremail@gmail.com\" >> .env
echo EMAIL_HOST_PASSWORD=\"your-app-password\" >> .env
gcloud secrets versions add cannlytics_settings --data-file .env
```

### Views <a name="views"></a>

Views are Python functions that describe the data to be presented. [Django describes views](https://docs.djangoproject.com/en/3.1/intro/tutorial03/#write-views-that-actually-do-something) in the following quote.

> "Your view can read records from a database, or not. It can use a template system such as Django's – or a third-party Python template system – or not. It can generate a PDF file, output XML, create a ZIP file on the fly, anything you want, using whatever Python libraries you want."

## Templates <a name="templates"></a>

Templates are Django HTML files that describe how the data is presented. Default Django templates can be found in your Anaconda/Python directory in `Lib\site-packages\django\contrib\admin\templates\admin`.

### Style <a name="style"></a>

[Bootstrap 5](https://getbootstrap.com/docs/5.0/getting-started/introduction/) is used for styling templates. Style distinguishes one site from another. You are free and encouraged to modify the style to create a site that is uniquely yours.

### Text Material <a name="text"></a>

All text material is either stored in JSON in `state.py` or written in Markdown in the `console/assets/docs` directory. There are many ways that you can extend the markdown functionality with [`python-markdown` Extensions](https://python-markdown.github.io/extensions/).

### Building and running the project with Docker <a name="docker"></a>

You can [build the application in a Docker container image](https://docs.docker.com/get-started/02_our_app/#build-the-apps-container-image) with:

```bash
# build docker image
docker build -t cannlytics .
```

You can register the container with:

```bash
# docker push to container registry. 
docker push cannlytics 
```

You can [run the application container](https://docs.docker.com/get-started/02_our_app/#start-an-app-container) locally with:

```bash
# run docker
docker run -dp 8080:8080 --env-file docker.env cannlytics
```

Finally, you can quickly run the container, or multiple containers, with:

```bash
# bring up containers
docker-compose up -d --build

# bring down
docker-compose down

# logs
docker-compose logs
```

## 👩‍🔬 Testing <a name="testing"></a>

You can check for errors detectable by Django with:

```bash
python manage.py check
```

You can run tests for a specific app with.

```bash
python manage.py test your_app_name
```

You can also build the platform in a docker container for your specific purposes:

```bash
docker build . --tag gcr.io/your-lims/cannlytics
gcloud auth configure-docker
docker push gcr.io/your-lims/cannlytics
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

This step provides access to this containerized app from a [Firebase Hosting] URL, so the app can generate dynamic content for the Firebase-hosted site.

```bash
firebase deploy --only hosting:production
```

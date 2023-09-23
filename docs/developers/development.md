<!-- | Cannlytics SOP-0005 |  |
|---------------------|--|
| Title | Development |
| Version | 1.0.0 |
| Created At | 2023-07-18 |
| Updated At | 2023-07-18 |
| Review Period | Annual |
| Last Review | 2023-07-18 |
| Author | Keegan Skeate, Founder |
| Approved by | Keegan Skeate, Founder |
| Status | Active | -->

# Development

This SOP covers the Cannlytics architecture and how to build, develop, and publish the Cannlytics platform. You can view the platform live at <https://cannlytics.com> and read the documentation at <https://docs.cannlytics.com>.

- [Introduction](#introduction)
- [Installation](#installation)
- [Architecture](#architecture)
- [Development](#development)
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
- [Testing](#testing)
- [Publishing](#publishing)
- [Conclusion](#conclusion)
- [Resources](#resources)

## Introduction <a name="introduction"></a>

The `cannlytics` package is the core module implementing cannabis analytics logic. The `cannlytics` module handles [database interactions](#data), [file management](#storage), [authentication and authorization](#authentication), traceability, data importing and exporting, and the logic for all workflows, such as certificate creation, item transfers, and publishing results. The `api` is the interface between the user application and the cannabis analytics logic of `cannlytics`. The `console` is the user application where user's can interface with the infrastructure, such as the database, and utilize the cannabis analytics logic. The `docs` provide information about the project and the `website` provides people with information about cannabis analytics. You can test the [app](https://app.cannlytics.com), [console](https://console.cannlytics.com), and [data UI](https://data.cannlytics.com).

## Installation <a name="installation"></a>

In brief, installing Cannlytics entails:

1. [Cloning the repository.](#cloning-the-repository)
2. [Setting your Firebase account credentials.](#setting-your-account-credentials)
3. [Installing project dependencies and development tools.](#installing-dependencies)

### 1. Cloning the repository <a name="cloning-the-repository"></a>

The best place to begin is to clone the repository and get a lay of the architecture.

```shell
git clone https://github.com/cannlytics/cannlytics.git
```

### 2. Setting your account credentials <a name="setting-your-account-credentials"></a>

When you are ready to begin development or publish the Cannlytics web app, then you will need to setup your credentials. You will need to [create a Firebase account](https://console.firebase.google.com/) and start a project before you begin. We recommend choosing a project name that is in kebab-case so that you can safely use the project name for many namespaces throughout the project, for example `your-lims`.

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

2.4. If you wish to leverage Cannlytics' email capabilities, then set `EMAIL_HOST_USER` and `EMAIL_HOST_PASSWORD` environment variables in your `.env` file. It is recommended that you [create an app password](https://support.google.com/accounts/answer/185833/sign-in-with-app-passwords?hl=en) if you are using Gmail.

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
        ]
      }
    }
  }
}
```

For downloading files from Firebase Storage, you should set your CORS rules. If you don't want any domain-based restrictions (the most common scenario), then copy the following JSON to a file named `cors.json`:

```json
[
  {
    "origin": ["*"],
    "method": ["GET"],
    "maxAgeSeconds": 3600
  }
]
```

Then deploy the rules with:

```shell
gsutil cors set cors.json gs://<your-cloud-storage-bucket>
```

> Note: Your service account will need `gcloud.builds.submit` and `storage.objects.get` permissions to deploy the rules.

2.7 Create your production secret environment variables

Now, you will need to set your environment variables for production.

Open [Google Cloud Shell](https://console.cloud.google.com/) and run the following command to ensure that you are working under the correct email and with the correct project:

```shell
gcloud init
```

Next, ensure that your project has billing enabled, then enable the Cloud APIs that are used:

```shell
gcloud services enable \
  run.googleapis.com \
  sql-component.googleapis.com \
  sqladmin.googleapis.com \
  compute.googleapis.com \
  cloudbuild.googleapis.com \
  secretmanager.googleapis.com
```

Create a secret with:

```shell
gcloud secrets create \
  cannlytics_lims_settings \
  --replication-policy automatic
```

Allow Cloud Run access to access this secret:

```shell
PROJECT_ID=$(gcloud config get-value project)
PROJECTNUM=$(gcloud projects describe ${PROJECT_ID} --format 'value(projectNumber)')
CLOUDRUN=${PROJECTNUM}-compute@developer.gserviceaccount.com

gcloud secrets add-iam-policy-binding \
  cannlytics_settings \
  --member serviceAccount:${CLOUDRUN} \
  --role roles/secretmanager.secretAccessor
```


Cloud Build will run Django commands, so Cloud Build will also need access to this secret:

```shell
PROJECT_ID=$(gcloud config get-value project)
PROJECTNUM=$(gcloud projects describe ${PROJECT_ID} --format 'value(projectNumber)')
CLOUDBUILD=${PROJECTNUM}@cloudbuild.gserviceaccount.com

gcloud secrets add-iam-policy-binding \
  cannlytics_settings \
  --member serviceAccount:${CLOUDBUILD} \
  --role roles/secretmanager.secretAccessor
```

Create a Cloud Storage bucket with a globally unique name:

```shell
REGION=us-central1
GS_BUCKET_NAME=${PROJECT_ID}-media
gsutil mb -l ${REGION} gs://${GS_BUCKET_NAME}
```

Then create your environment variables and save them to the secret:

```shell
APP_ID=cannlytics
REGION=us-central1
DJPASS="$(cat /dev/urandom | LC_ALL=C tr -dc 'a-zA-Z0-9' | fold -w 30 | head -n 1)"
echo DATABASE_URL=\"postgres://djuser:${DJPASS}@//cloudsql/${APP_ID}:${REGION}:cannlytics-sql/cannlytics-sql-database\" > .env
echo GS_BUCKET_NAME=\"${GS_BUCKET_NAME}\" >> .env
echo SECRET_KEY=\"$(cat /dev/urandom | LC_ALL=C tr -dc 'a-zA-Z0-9' | fold -w 50 | head -n 1)\" >> .env
echo DEBUG=\"False\" >> .env
echo EMAIL_HOST_USER=\"your-email\" >> .env
echo EMAIL_HOST_PASSWORD=\"your-email-password\" >> .env
gcloud secrets versions add cannlytics_settings --data-file .env
rm .env
```

> Set `EMAIL_HOST_USER` and `EMAIL_HOST_PASSWORD` with your email and [app password](https://dev.to/abderrahmanemustapha/how-to-send-email-with-django-and-gmail-in-production-the-right-way-24ab). If you do not plan to use Django's email interface, then you exclude `EMAIL_HOST_USER` and `EMAIL_HOST_PASSWORD`.

Update your IAM policy:

```shell
gcloud beta run services add-iam-policy-binding --region=us-central1 --member=allUsers --role=roles/run.invoker your-lims
```

You can confirm that the secret was created or updated with:

```shell
gcloud secrets versions list cannlytics_settings
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

## Architecture <a name="architecture"></a>

Cannlytics is built with [Python](https://www.python.org/) and leverages the [Django](https://www.djangoproject.com/) framework. Cannlytics utilizes [Firebase](https://firebase.google.com/) for user authentication with [Firebase Authentication](https://firebase.google.com/docs/auth), a [Firestore](https://firebase.google.com/docs/firestore) NoSQL database for real-time data management, [Firebase Storage](https://firebase.google.com/docs/storage) for file storage, and hosted with [Firebase Hosting](https://firebase.google.com/docs/hosting). Cannlytics uses a number of [Google Cloud](https://console.cloud.google.com/) backend services, including:

  * [Cloud Build](https://cloud.google.com/build) to containerize the app.
  * [Cloud Registry](https://cloud.google.com/container-registry) to upload the app to storage.
  * [Cloud Run](https://cloud.google.com/run) to run the app as a stateless container.
  * [Cloud Storage](https://cloud.google.com/storage) for file storage.
  * [Cloud Secret Manager](https://cloud.google.com/secret-manager) for storing configurations and keeping secrets secret.
    <!-- * *Optional* [Cloud SQL](https://cloud.google.com/sql) can be utilized if desired. -->

Cannlytics generally follows a model-template-view (MTV) architectural pattern, where:

* The **model** is Django, the engine that sends requests to views.
* The **views** are Python functions that describe the data to be presented.
* The **templates** are Django HTML files that describe how the data is presented.

Cannlytics favors a [domain-style code structure](https://stackoverflow.com/questions/40233657/ddd-what-is-proper-code-structure) for apps and material that will be edited frequently and a [ducks-style code structure](https://www.etatvasoft.com/insights/react-design-patterns-and-structures-of-redux-and-flux/) for concepts within the apps. Ducks 🦆 can inherit properties if needed and are encouraged to be individualized and self-contained as possible. The architecture of the Cannlytics app is as follows.

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
│   ├── urls.py # Defined API endpoints.
|   └── views.py # Implementation of general API endpoints.
├── cannlytics
│   ├── lims # All LIMS logic.
│   ├── traceability
│   |   ├── leaf # Leaf Data Systems API module.
|   |   └── metrc # Metrc API module.
│   ├── utils # General utility functions.
│   ├── firebase.py # Firebase module.
|   └── models.py # Main data entities.
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
├── Dockerfile # Docker container configuration.
├── firebase.json # Firebase configuration file.
├── LICENSE
├── manage.py # Django utility script.
├── mkdocs.yaml # Documentation configuration.
├── package.json # Node.js dependencies and scripts.
├── README.md
├── requirements.txt # Python requirements.
└── webpack.config.js # JavaScript and CSS bundle configuration.
```

## Development <a name="development"></a>

Development can happen in many avenues. Frequent, small scope pull requests are encouraged. Any contribution, even if it needs future polishing, helps build the project and advance the field of cannabis analytics. In general;

1. [Create a fork](https://docs.github.com/en/github/getting-started-with-github/quickstart/fork-a-repo) of the repository.
2. Work on a solution for your most-pressing problem.
3. [Create a pull request](https://docs.github.com/en/github/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/creating-a-pull-request) for your changes to be reviewed and merged into the project upon approval or for you to receive feedback on how your changes can be approved.

The simplest way to run the app is to open a command line from the project's root directory and run:

```shell
python manage.py runserver
```

You can also leverage [django-livereload-server](https://github.com/tjwalch/django-livereload-server) for hot-reloading while you develop.

```shell
npm run start
```

### Authentication <a name="authentication"></a>

Below is a diagram that depicts how Cannlytics leverages [Firebase Authentication] to authorize user requests.

![Authentication on Google App Engine using Firebase](https://firebasestorage.googleapis.com/v0/b/cannlytics.appspot.com/o/public%2Fimages%2Fdiagrams%2Ffirebase_auth_diagram.png?alt=media&token=ca0afc16-4829-4785-abb0-695304de802c)

Original image: [How to authenticate users on Google App Engine using Firebase](https://cloud.google.com/blog/products/gcp/how-to-authenticate-users-on-google-app-engine-using-firebase)

### Running the project for development <a name="running"></a>

Hot-reloading is an important tool of development. You can use `django-livereload-server`, which uses both [python-livereload](https://github.com/lepture/python-livereload) and [django-livereload](https://github.com/Fantomas42/django-livereload), for smooth reloading. You can install [django-live-reload-server](https://github.com/tjwalch/django-livereload-server) with:

```shell
pip install django-livereload-server
```

You can start hot-reloading by starting the `livereload` server:

```shell
python manage.py livereload
```

In another console, you start the Django development server as usual:

```shell
python manage.py runserver
```

You can build the static assets, JavaScript and CSS, utilizing [Webpack](https://webpack.js.org/). The JavaScript bundle is a JavaScript module and is callable from the user interface with the `cannlytics` namespace. You can run the build for development with:

```shell
webpack-dev-server --env production=False
```

or

```shell
npm run webpack
```

It is an inconvenience to run multiple consoles, but a major convenience to have smooth hot-reloading. So, [`npm-run-all`](https://www.npmjs.com/package/npm-run-all) is used to run multiple servers in the same console for smooth development. When you are setup, you can run the project for development simply with:

```shell
npm run start
```

### Data <a name="data"></a>

Cannlytics operates with a NoSQL database, [Firestore](https://firebase.google.com/docs/firestore) by default. You can conceptualize every entity as a JSON object called a document. A group of documents is a collection. Every document is required to be a member of a collection. Below is a [diagram of the Cannlytics LIMS standard data models](https://firebasestorage.googleapis.com/v0/b/cannlytics.appspot.com/o/public%2Flims%2Fdiagrams%2Fcannlytics_standard_data_models_0_0_8.svg?alt=media&token=de8e81a9-6250-4aac-857e-3936d26b4f1b).

<img width="100%" alt="" src="https://firebasestorage.googleapis.com/v0/b/cannlytics.appspot.com/o/public%2Flims%2Fdiagrams%2Fcannlytics_standard_data_models_0_0_8.svg?alt=media&token=de8e81a9-6250-4aac-857e-3936d26b4f1b">

<!-- Resources:

* [Django Database API](https://docs.djangoproject.com/en/3.1/topics/db/queries/) -->

### File Storage <a name="storage"></a>

Cannlytics utilizes [Firebase Storage] ( a.k.a Google Cloud Storage) for most storage solutions. For help with storing static files, see [serving static files on App Engine](https://cloud.google.com/appengine/docs/standard/python3/serving-static-files). You can gather all supporting files, located in each app's `static` directory, into the `public/static` directory with:

```shell
python manage.py collectstatic --noinput
```

or

```shell
npm run collectstatic
```

You can configure static files to be served from [Firebase Storage] instead of from [Firebase Hosting] in `console/settings.py`.

### Email <a name="email"></a>

If you are sending email with Gmail, then you can follow these steps.

- Navigate to [Gmail](https://mail.google.com), click your profile, and click manage your google account.
- Navigate to the [security tab](https://myaccount.google.com/security).
- Enable 2-step verification and then click on App passwords.
- Select Mail for app and enter a custom name for device.
- Click generate and Gmail will generate an app password. Copy this app password to a text file and save it where it is secure and will not be uploaded to a public repository, for example save the password in the `.admin` directory.

After you have created your app password, set your Gmail email and app password as environment variables, `EMAIL_HOST_USER` and `EMAIL_HOST_PASSWORD` respectively.

```shell
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

Style distinguishes one site from another. You are free and encouraged to modify the style to create a site that is uniquely yours. [Bootstrap](https://getbootstrap.com/docs/4.5/getting-started/introduction/) is used for styling templates. You can install Bootstrap with:

```shell
npm install bootstrap
npm install style-loader --save
```

The main Cannlytics colors are:

* Cannlytics Orange: #ff5733
* Cannlytics Light Orange: #ffa600
* Cannlytics Dark Orange: #e53a23
* Cannlytics Green: #45B649
* Cannlytics Light Green: #96e6a1
* Cannlytics Dark Green: #3f7f34
* Cannlytics Darkest Green: #104607

The main Cannlytics fonts are:

* [Libre Franklin (Headlines)](https://fonts.google.com/specimen/Libre+Franklin)
* [Libre Baskerville (Body)](https://fonts.google.com/specimen/Libre+Baskerville)
* [Montserrat](https://fonts.google.com/specimen/Montserrat?query=Montserrat)

Useful open source icon sets include:

- [Feather Icons](https://feathericons.com/)
- [Material Icons](https://fonts.google.com/icons)


### Text Material <a name="text"></a>

All text material is either stored in JSON in `state.py` or written in Markdown in `docs` directories.

Resources:

* [`python-markdown` Extensions](https://python-markdown.github.io/extensions/)

### Building and running the project with Docker <a name="docker"></a>

You can [build the application in a Docker container image](https://docs.docker.com/get-started/02_our_app/#build-the-apps-container-image) with:

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

## Documentation <a name="documentation"></a>

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

## Testing <a name="testing"></a>

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

## Publishing <a name="publishing"></a>

See [the publishing guide](https://docs.cannlytics.com/developers/publishing/) for complete instructions on how to publish Cannlytics for production. The guide is based on the [Running Django on Cloud Run guide](https://cloud.google.com/python/django/run#windows). After setup, publishing is done with one command:

```shell
npm run publish
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

> Note: You can setup a custom domain. You can register a domain with [Google Domains](https://domains.google.com/registrar/). You can then add a custom domain in the Firebase Hosting console. If you are using Google Domains, then use '@' for your root domain name and 'www' or 'www.domain.com' for your subdomains when registering your DNS A records.

### Security rules

You can deploy a new set of security rules with the Firebase CLI.

```shell
firebase deploy --only firestore:rules
```

### Monitoring

You can now monitor your app with the following tools.

| Resource | Description |
| ---------- | ------------ |
| [Cloud Run Console](https://console.cloud.google.com/run) | Manage your app's container. |
| [Logs Explorer](https://console.cloud.google.com/logs) | Realtime logs for your app. |
| [Error Reporting](https://console.cloud.google.com/errors) | Provides detailed historic errors that occurred when running your app. |

## Conclusion

Congratulations, you have developed, built, and published Cannlytics! You now have a simple, yet complex, website running on Cloud Run, which will automatically scale to handle your website's traffic, optimizing CPU and memory so that your website runs with the smallest footprint possible, saving you money. If you desire, you can now seamlessly integrate services such as Cloud Storage into your Django website. You can now plug and play and tinker to your heart's content while your users enjoy your well-organized cannabis data and analytics!

## Resources

- [Running Django on Cloud Run](https://cloud.google.com/python/django/run#gcloud)
- [Django on Cloud Run Code Lab](https://codelabs.developers.google.com/codelabs/cloud-run-django/index.html#7)
- [Generating Django Secret Keys](https://stackoverflow.com/questions/4664724/distributing-django-projects-with-unique-secret-keys)
- [Granting permissions](https://cloud.google.com/container-registry/docs/access-control#grant)
- [Permission Denied - GCP Cloud Resource Manager setIamPolicy](https://stackoverflow.com/questions/53163115/permission-denied-gcp-cloud-resource-manager-setiampolicy)
- [Secret manager access denied despite correct roles for service account](https://stackoverflow.com/questions/62444867/secret-manager-access-denied-despite-correct-roles-for-service-account)
- [Troubleshooting group membership](https://cloud.google.com/iam/docs/troubleshooting-access#troubleshooting_group_membership)

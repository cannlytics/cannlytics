# 📖 Installation

Cannlytics works right out of the box, however, we recommended to setup your own credentials. Cannlytics uses Firebase by default for many back-end services. As you are free to modify anything, you are welcome to modify Cannlytics to use the back-end services of your choice.

## Getting Started

First things first, you will need to install the Cannlytics Engine. Below are several useful resources:

* [Django on Cloud Run](https://codelabs.developers.google.com/codelabs/cloud-run-django/index.html)

First, install [Git](https://git-scm.com/downloads), open a command prompt, navigate to the directory of your choice, and clone the repository:

```shell

git clone <repo>

```

## Credentials

If you want to utilize the default backing services, then you will need a [Gmail or G Suite account](https://accounts.google.com/SignUp). The following documentation will assume that you are managing your own account.


### Creating Environmental Variables

Once you have an account, download the [Cloud SDK installer](https://dl.google.com/dl/cloudsdk/channels/rapid/GoogleCloudSDKInstaller.exe) and run:

```shell

gcloud init

```

Next, enable the Cloud APIs that are used:

```shell

gcloud services enable run.googleapis.com sql-component.googleapis.com sqladmin.googleapis.com compute.googleapis.com cloudbuild.googleapis.com secretmanager.googleapis.com

```

> You will need to [accept the Gcloud terms of service](https://console.developers.google.com/terms/cloud).

Second, store the configurations as a secret.

1. Open Google Cloud Shell.

2. Set project: `gcloud config set project cannlytics`

3. Set the following environment variables:

```shell

echo DATABASE_URL=\"postgres://djuser:${DJPASS}@//cloudsql/${PROJECT_ID}:${REGION}:myinstance/mydatabase\" > .env
echo GS_BUCKET_NAME=\"${GS_BUCKET_NAME}\" >> .env
echo SECRET_KEY=\"$(cat /dev/urandom | LC_ALL=C tr -dc 'a-zA-Z0-9' | fold -w 50 | head -n 1)\" >> .env
echo DEBUG=\"True\" >> .env
gcloud secrets versions add application_settings --data-file .env
rm .env

```

You can create a secret if you haven't already with:

```shell

gcloud secrets create application_settings --replication-policy automatic

```

You can confirm the secret was created or updated with:

```
gcloud secrets versions list application_settings

```

Finally, you can [create a Google Cloud service account](https://cloud.google.com/docs/authentication/getting-started) and set the `GOOGLE_APPLICATION_CREDENTIALS` environmental variable to the full path to your credentials.

When you are finished, you should have a `.env` file stored in your root directory and a Gcloud service account and a Firebase service account stored in `admin/tokens`.

> Keep your `.env` file and service accounts safe and do not upload them to a public repository.

## Python

Cannlytics leverages the power of Python. The recommended way to install Python is "using conda. Anaconda Python is a self-contained Python environment that is particularly useful for scientific applications. If you don’t already have it, start by installing Miniconda, which includes a complete Python distribution and the conda package manager. Choose the Python 3 version, unless you have a particular reason why you must use Python 2."

https://docs.conda.io/en/latest/miniconda.html

Install a [distribution of Python](https://docs.conda.io/en/latest/miniconda.html), open the Anaconda Prompt, navigate to the Cannlytics repository, and install Python dependencies:

```shell

pip install -r requirements.txt

```

You may also need to install other project and development dependencies, including:

  * Install [Psycopg2](https://www.psycopg.org/install/): `pip install psycopg2`
  * [Python Decouple](https://pypi.org/project/python-decouple/): `pip install python-decouple`

<!-- ### Live (Hot) Reloading

Hot-reloading is an important tool of development, so, you may want to use [livereload](https://github.com/lepture/python-livereload):

```shell

conda install livereload

```

[dj-static](https://github.com/heroku-python/dj-static) is required to automatically serve static files:

```shell

pip install dj-static

```

[dj-static] is enabled in `wsgi.py`:

```py

from dj_static import Cling

application = Cling(get_wsgi_application())

```

Then run:

  1. `python manage.py livereload`

Resources:

* [How to reload Django?](https://stackoverflow.com/questions/19094720/how-to-automatically-reload-django-when-files-change)
* [django-livereload](https://github.com/Fantomas42/django-livereload)
* [django-livereload-server](https://github.com/tjwalch/django-livereload-server)
* [Browser Sync with Django and Docker](https://stackoverflow.com/questions/49482710/using-browser-sync-with-django-on-docker-compose) -->

### ChemSpider API

All ChemSpider API operations require an API key. To obtain one, [create a RSC Developers account](https://developer.rsc.org/accounts/create) and then [add a new key](https://developer.rsc.org/create-an-api-key).

"The Royal Society of Chemistry web services are currently available as an Open Developer Preview. During the preview you can make 1000 calls per month."


## Node.js

Cannlytics utilizes Node.js for web development. [Download Node.js](https://nodejs.org/en/download/) and install Node.js dependencies in the command prompt:

```shell

npm install

```

## Wrap-Up

Great! You now have Cannlytics installed and are ready to start developing. Make sure to document any [bugs](/bugs) and your development process.

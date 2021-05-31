<h1>Installation</h1>

The Cannlytics website works right out of the box, however, it is recommended to setup your own credentials for deploying to production. The website uses [Firebase](https://firebase.google.com) by default for many back-end services. As you are free to modify anything, you are welcome to modify the website to use the back-end services of your choice. You can walk through these short sections to install the website on your own computer.

<!-- * [Getting started](#getting-started)
* [Credentials](#credentials)
  - [Creating environment variables](#creating-environment-variables)
* [Python](#python)
* [Node.js](#node-js)
* [Wrap-up](#wrap-up)
* [Helpful resources](#helpful-resources) -->
[TOC]

## Getting started

First things first, clone the repository.


```shell
git clone https://github.com/cannlytics/cannlytics-website.git
```
## Credentials

If you want to utilize the default backing services, then you will need a [Gmail or G Suite account](https://accounts.google.com/SignUp). The following documentation will assume that you are managing your own account. For development, you can [create a Google Cloud service account](https://cloud.google.com/docs/authentication/getting-started) and set the `GOOGLE_APPLICATION_CREDENTIALS` environmental variable to the full path to your credentials. When you are finished, you should have a `.env` file stored in your root directory. You can optionally store a Gcloud service account and/or a Firebase service account stored in `admin/tokens` if you need any Google Cloud or Firebase utilities.

> Keep your `.env` file and service accounts safe and do not upload them to a public repository.

## Python

This website leverages the power of Python. The recommended way to install Python is with [Anaconda](https://www.anaconda.com/products/individual/get-started-commercial-edition-1). Anaconda Python is a self-contained Python environment that is particularly useful for scientific applications.

After you have installed a [distribution of Python](https://docs.conda.io/en/latest/miniconda.html), open the Anaconda Prompt, navigate to this website's repository, and install Python dependencies:

```shell
pip install -r requirements.txt
```

You may also need to install other project and development dependencies, including:

* [dj-static](https://github.com/heroku-python/dj-static): `pip install dj-static`
* [django-livereload-server](https://github.com/tjwalch/django-livereload-server): `pip install django-livereload-server`
* [Psycopg2](https://www.psycopg.org/install/): `pip install psycopg2`
* [Python Decouple](https://pypi.org/project/python-decouple/): `pip install python-decouple`

## Node.js

The website utilizes Node.js for web development. You can[download Node.js](https://nodejs.org/en/download/) and install Node.js dependencies in the command prompt:

```shell
npm install
```

## Wrap-Up

Great! You now have the website installed and are ready to start [developing](development.md). Make sure to document any bugs and your development process if you want to [contribute](contributing.md) to the project.

## Helpful resources

* [Django on Cloud Run](https://codelabs.developers.google.com/codelabs/cloud-run-django/index.html)

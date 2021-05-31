# Development

Developing this website is intended to be fun, easy, and productive.

[TOC]


## Installation

You can begin by cloning the repository.

```shell

git clone https://github.com/keeganskeate/personal-website.git

```

See [architecture.md](docs/architecture.md) for information about the repository's architecture.

Next, follow [installation.md](docs/architecture.md) to create your credentials and install all of the project's dependencies.

Resources:

* [Django on Cloud Run](https://codelabs.developers.google.com/codelabs/cloud-run-django/index.html)


## Supporting Files

You can gather all supporting files into the `static` folder with:

```shell

python manage.py collectstatic

```

> Add the `--noinput` tag to suppress the overwrite warning.

You can configure static files to be served from [Firebase Storage](https://firebase.google.com/docs/storage) instead of from [Firebase Hosting](https://firebase.google.com/docs/hosting) in `personal_website/settings.py`.


## Running

You can then serve the site locally with:

```shell

python manage.py runserver

```


### Hot-Reloading (Livereload)

Hot-reloading is an important tool of development, so, you may want to install [django-live-reload-server](https://github.com/tjwalch/django-livereload-server):

```shell

pip install django-livereload-server

```

> django-livereload-server uses both [python-livereload](https://github.com/lepture/python-livereload) and [django-livereload](https://github.com/Fantomas42/django-livereload) for smooth reloading. Either project can be substituted if bugs are encountered.

In a console, start the livereload server:

```shell

python manage.py livereload

```

In another console, start the Django development server:

```shell

python manage.py runserver

```

It is an inconvinience to run 2 consoles, but a major convinience to have smooth hot-reloading. If you are using Node.js, then you can use the `npm run dev` command. If you are using [VS Code](https://code.visualstudio.com/download), then you can use the [NPM-Scripts](https://github.com/Duroktar/vscode-npm-scripts) extension to open the first terminal in VS Code.

> If you encounter a [django-livereload-server NotImplementedError](https://stackoverflow.com/questions/58422817/jupyter-notebook-with-python-3-8-notimplementederror), then it is likely that you are using Python 3.8+ and need to add the following code to `Lib\site-packages\tornado\platform\asyncio.py`.

  ```py

  import sys

  if sys.platform == 'win32':
      asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

  ```

Resources:

* [Livereload Chrome Extension](https://chrome.google.com/webstore/detail/livereload)
* [Django Livereload with Grunt](https://github.com/sinnwerkstatt/sinnwerkstatt-web/blob/master/Django/Django-livereload.md)


### Webpack

<!-- Webpack goodies like hot reloading and dynamic imports! -->

<https://pascalw.me/blog/2020/04/19/webpack-django.html>

## Views

Views are Python functions that describe the data to be presented. [Django describes views](https://docs.djangoproject.com/en/3.1/intro/tutorial03/#write-views-that-actually-do-something) in the following quote.

> "Your view can read records from a database, or not. It can use a template system such as Django's – or a third-party Python template system – or not. It can generate a PDF file, output XML, create a ZIP file on the fly, anything you want, using whatever Python libraries you want."


## Templates

Tempaltes are Django HTML files that describe how the data is presented.

Default Django templates can be found in your Anaconda/Python directory in `Lib\site-packages\django\contrib\admin\templates\admin`.


### Text Material

All text material is either stored in JSON in `state.py` or written in Markdown in `docs` directories.

Resources:

* [`python-markdown` Extensions](https://python-markdown.github.io/extensions/)


## Data

This website has opted for a NoSQL approach for data management with Firebase's [Firestore](https://firebase.google.com/docs/firestore).


## Style

Style distinguishes one site from another. You are free and encouraged to modify the style to create a site that is uniquely yours. See [style.md](style.md) for a guide on the personal website's style.


## Email

If you are sending email with Gmail, then you can follow these steps.

- Navigate to [Gmail](mail.google.com), click your profile, and click manage your google account.
- Navigate to the [security tab](https://myaccount.google.com/security).
- Enable 2-step verification and then click on App passwords.
- Select Mail for app and enter a custom name for device.
- Click generate and Gmail will generate an app password. Copy this app password to a text file and save it where it is secure and will not be uploaded to a public repository, for example save the password in the `.admin` directory.

After you have created your app password, set your Gmail email and app password as environment variables, `EMAIL_HOST_USER` and `EMAIL_HOST_PASSWORD` respectively.

```shell

echo EMAIL_HOST_USER=\"youremail@gmail.com\" >> .env
echo EMAIL_HOST_PASSWORD=\"your-app-password\" >> .env
gcloud secrets versions add etch_mobility_settings --data-file .env

```

* [Email Self-Defense](https://emailselfdefense.fsf.org/en/)
* [GnuPG](https://www.gnupg.org/)
* [Django Email Templates](https://github.com/vintasoftware/django-templated-email)


## Forms

Django makes creating stock forms easy.

* [django-crispy-forms](https://django-crispy-forms.readthedocs.io/en/latest/crispy_tag_forms.html)
* [How to use Bootstrap 4 Forms with Django](https://simpleisbetterthancomplex.com/tutorial/2018/08/13/how-to-use-bootstrap-4-forms-with-django.html)
* [Django Forms and Bootstrap](https://stackoverflow.com/questions/8474409/django-forms-and-bootstrap-css-classes-and-divs)


## Testing and Debugging

You can check for errors with:

```shell

python manage.py check

```

You can run tests for an app with:

```shell

python manage.py test personal_website

```

See [testing](/testing) for more information.

## Writing documentation

Install Material for MkDocs with Docker.

```shell
docker pull squidfunk/mkdocs-material
```

Build the documentation:

```shell
docker build -t squidfunk/mkdocs-material docs
```

Preview the documentation as you write.

```shell
docker run --rm -it -p 8000:8000 -v "%cd%":/docs squidfunk/mkdocs-material
```

or

```shell
npm run docs
```

* [Quick note - how to fix django-livereload-server import error](https://gist.github.com/hangtwenty/f53b3867db1e33780505ccafd8d2eef0)

Build the documentation

```shell
mkdocs build
```

or

```shell
npm run build-docs
```


## Helpful Resources

* [VS Code Django Guide](https://code.visualstudio.com/docs/python/tutorial-django)
* [How to reload Django?](https://stackoverflow.com/questions/19094720/how-to-automatically-reload-django-when-files-change)
* [django-livereload](https://github.com/Fantomas42/django-livereload)
* [django-livereload-server](https://github.com/tjwalch/django-livereload-server)
* [Browser Sync with Django and Docker](https://stackoverflow.com/questions/49482710/using-browser-sync-with-django-on-docker-compose)

# Development

Before you begin developing, read up on [Django] and the principles employed in development.

- [The Zen of Python](https://www.python.org/dev/peps/pep-0020/)
- [Django Style Guide](https://github.com/HackSoftware/Django-Styleguide)
- [Python Style Guide](https://google.github.io/styleguide/pyguide.html)
- [Typography Checklist](https://www.typewolf.com/checklist)
* [GNU Standards](https://www.gnu.org/prep/standards/standards.html)

## Architecture

Cannlytics generally follows a model-template-view (MTV) architectural pattern, where:

* The **model** is Django, the engine that sends requests to views.
* The **views** are Python functions that describe the data to be presented.
* The **templates** are Django HTML files that describe how the data is presented.


<!-- [Ducks file structure](https://github.com/erikras/ducks-modular-redux) is useful for modules and components. -->
Cannlytics favors a domain-style code structure for apps and material that will be edited frequently and a ducks-style code structure for concepts within the apps. Ducks 🦆 can inherit properties if needed and are encouraged to be individualized and self-contained as possible.

File directory:

* `.admin` - Project secrets (Keep secure. Do NOT upload to a public repository.)
* `apps` - Supporting Django apps.
* `assets` - All original assets; images, PDFs, etc.
* `cannlytics_website` - Main app.
* `node_modules` - Node.js packages.
* `static` - Where static files are served, uploaded to hosting.
* `templates` - Django HTML templates for all apps.
* `.env` - Locally save secrets (Keep secure. Do NOT upload to a public repository.)
* `firebase.json` - Firebase hosting configuration.
* `LICENSE`- GNU General Public License.
* `manage.py` - Django utility.
* `package.json` - Node.js configuration.
* `readme.md` - General introduction and installation guide.
* `requirements.txt` - Python dependencies.
* `webpack.config.js` - Webpack configuration.

A Duck's 🦆 (an app's) directory usually contains:

* `static\${app_name}` - All app-specific supporting files.
  - `docs` - Text documents.
  - `js` - App-related Javascript.
  - `css` - App-related CSS
* `templates\${app_name}` - App-specific tempaltes.
* `apps.py` - App configuration file.
* `urls.py` - App URL patterns.
* `views.py` - App view functions.

A Duck may also have:

* `forms.py` - Forms used in the app.
* `settings.py` - For the core app.

Resources:

* [React design patterns and structures of Redux and Flux](https://www.etatvasoft.com/insights/react-design-patterns-and-structures-of-redux-and-flux/)

## Supporting Files

You can gather all supporting files into the `static` folder with:

```shell

python manage.py collectstatic

```

## Running

Hot-reloading is an important tool of development, so, you may want to install the [django-live-reload-server](https://github.com/tjwalch/django-livereload-server):

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

## Reactivity

TODO: Explore adding reactivity to webpages.

* [django-rest-framework-reactive](https://github.com/genialis/django-rest-framework-reactive)

## Views

"Your view can read records from a database, or not. It can use a template system such as Django's – or a third-party Python template system – or not. It can generate PDF files, output XML, create ZIP files, anything you want, all on the fly, using all of the Python libraries that you want."

You can create a starter app with:

```shell

python manage.py startapp example

```

Helpful resources:

* [Cool URIs don't change](https://www.w3.org/Provider/Style/URI)


## SQL Database

If you choose to implement a SQL database, then you can follow these steps to get started.

Build the database in full:

```shell

python manage.py makemigrations
python manage.py migrate

```

Make migrations with:

```shell

python manage.py makemigrations ${app_name}

```

Get SQL for migrations with:

```shell

python manage.py sqlmigrate ${app_name} 0001

```

Check for errors with:

```shell

python manage.py check

```

Apply all migrations to the database with:

```shell

python manage.py migrate

```

This synchronizes models with the database schema.

SQL Resources:

* [Django Database API](https://docs.djangoproject.com/en/3.1/topics/db/queries/)

## Administration

The Cannlytics admin site exists for you, your staff, or your clients to create, edit, and delete published material. The admin site isn't intended to be used by site visitors.

You can create an admin user with:

```shell

python manage.py createsuperuser

```

You can login to the Django admin site at [http://127.0.0.1:8000/admin](http://127.0.0.1:8000/admin) with your user name and password.

Resources:

* [Django Admin Tutorial](https://docs.djangoproject.com/en/3.1/intro/tutorial07/)

## Style

Style is a distinguishing characteristic between sites. Therefore, the style of the Cannlytics Website is what makes it distinctly Cannlytics. You are free to modify the style to create a site that is distinctly for you.

[Bootswatch](https://bootswatch.com/help/) provides many great themes. Cannlytics uses the [pulse theme](https://bootswatch.com/pulse/).

### CSS

[Bootstrap](https://getbootstrap.com/docs/4.5/getting-started/introduction/) is used for styling templates. You can install Bootstrap with:

```shell

npm install bootstrap
npm install style-loader --save

```

[Material Components](https://github.com/material-components/material-components-web) are used for certain widgets. Material components provide beautiful animations and useful Google-style widgets.

You can install material components with:

```shell

npm i material-components-web

```

You can install material components dependencies with:

```shell

npm install --save-dev webpack webpack-cli webpack-dev-server css-loader sass-loader sass extract-loader file-loader autoprefixer postcss-loader @babel/core babel-loader @babel/preset-env

```

### Colors

* Cannlytics Orange: #ff5733
* Cannlytics Light Orange: #ffa600
* Cannlytics Dark Orange: #e53a23
* Cannlytics Green: #45B649
* Cannlytics Light Green: #96e6a1
* Cannlytics Dark Green: #3f7f34
* Cannlytics Darkest Green: #104607

Color resources:

* [Gradients (UI)](https://uigradients.com/#KyooTah)
* [Gradients (Web)](https://webgradients.com/)
* [CSS Transparency](https://stackoverflow.com/questions/23201134/transparent-argb-hex-value)

### Fonts

Main fonts:

* [Libre Franklin (Headlines)](https://fonts.google.com/specimen/Libre+Franklin)
* [Libre Baskerville (Body)](https://fonts.google.com/specimen/Libre+Baskerville)

Serif fonts:

* [Cinzel Decorative (Brand Title)](https://fonts.google.com/specimen/Cinzel+Decorative)
* [Cinzel (Special Titles)](https://fonts.google.com/specimen/Cinzel)

Sans-serif fonts:

* [Montserrat](https://fonts.google.com/specimen/Montserrat?query=Montserrat)

### Icons

Useful open source icon sets include:

* [Feather Icons](https://feathericons.com/)

### Templates

Default Django templates can be found in your Anaconda/Python directory `Lib\site-packages\django\contrib\admin\templates\admin`.

### Django Templates

Default Django templates can be found in your Anaconda library: `..\Anaconda\Lib\site-packages\django\contrib\admin\templates`

Resources:

* [Django Style Tutorial](https://docs.djangoproject.com/en/3.1/intro/tutorial06/)
* [Material Components](https://github.com/material-components/material-components-web/tree/master/packages)
* [Bootstrap Theming](https://getbootstrap.com/docs/4.5/getting-started/theming/)
* [Bootstrap Repo](https://github.com/twbs/bootstrap)
* [Bootstrap Examples](https://getbootstrap.com/docs/4.5/examples/)

## Debugging

You can check for errors with:

```shell

python manage.py check

```

## Testing

Run tests for an app with:

```shell

python manage.py test ${app_name}

```

See [testing](/testing) for more information.

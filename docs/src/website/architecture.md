# Architecture

The Cannlytics website generally follows a model-template-view (MTV) architectural pattern, where:

* The **model** is Django and Firebase, the engine that sends requests to views.
* The **templates** are Django HTML files that describe how the data is presented.
* The **views** are Python functions that retrieve data utilizing Django and Firebase to be presented in the templates.

The website favors a domain-style code structure for apps and material that will be edited frequently and a [ducks-style code structure](https://github.com/erikras/ducks-modular-redux) for modules and components within the apps. Ducks can inherit properties if needed and are encouraged to be individualized and self-contained as possible.

Directories:

* `.admin` - Project secrets (Keep secure. Do NOT upload to a public repository.)
* `assets` - All original assets; images, PDFs, etc.
* `personal_website` - Main app.
* `node_modules` - Node.js packages.
* `static` - Where static files are served, uploaded to hosting.
* `templates` - Django HTML templates for all apps.
* `utils` - Python utility (helper) functions.

Root folder files:

* `.env` - Locally save secrets (Keep secure. Do NOT upload to a public repository.)
* `.dockerignore` - Files to ignore when building a Docker container image.
* `.gitignore` - Files to ignore when committing to a Git repository.
* `cloudmigrate.yaml` - Cloud Run configuration.
* `db.sqlite3` - Default SQLite database for development or  low-volume web apps.
* `Dockerfile` - Configuration for Docker container image.
* `firebase.json` - Firebase hosting configuration.
* `LICENSE`- GNU General Public License.
* `manage.py` - Django utility.
* `package.json` - Node.js configuration.
* `readme.md` - General introduction and installation guide.
* `requirements.txt` - Python dependencies.
<!-- * `webpack.config.js` - Webpack configuration. -->

A Duck's 🦆 (an app's) directory usually contains:

* `static\${app_name}` - All app-specific supporting files.
  - `docs` - Text documents.
  - `images` - Supporting images.
  - `js` - App-related Javascript.
  - `css` - App-related CSS
* `templates\${app_name}` - App-specific tempaltes.
* `apps.py` - App configuration file.
* `state.py` - A file for storing state (a database is preferred).
* `urls.py` - App URL patterns.
* `views.py` - App view functions.

The main project app contains:

* `settings.py` - Django project settings.
* `asgi.py` - ASGI configuration.
* `wsgi.py` - WSGI configuration, enhanced with `dj-static`.

A Duck may also have:

* `forms.py` - Forms used in the app.

Resources:

* [React design patterns and structures of Redux and Flux](https://www.etatvasoft.com/insights/react-design-patterns-and-structures-of-redux-and-flux/)

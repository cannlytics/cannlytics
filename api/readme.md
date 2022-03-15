# <img height="32" alt="" src="https://cannlytics.com/static/cannlytics_website/images/logos/cannlytics_calyx_detailed.svg"> Cannlytics API

[![license](https://img.shields.io/badge/License-MIT-brightgreen.svg)](https://opensource.org/licenses/MIT)
[![contributions welcome](https://img.shields.io/badge/contributions-welcome-brightgreen.svg)](https://github.com/cannlytics/cannlytics-api/fork)


The Cannlytics API provides an interface to quickly receive samples, perform analyses, collect and review results, and publish certificates of analysis (CoAs). There are also logistics, CRM (client relationship management), inventory management, and invoicing tools. The Cannlytics API comes with [**batteries included**](https://cannlytics.com/support/), but you are always welcome to supercharge your setup with custom modifications.

- [Installation](#installation)
- [Development](#development)
- [Testing](#testing)
- [Publishing](#publishing)
- [License](#license)

## Installation<a name="installation"></a>

Installing the Cannlytics API is simple.

```shell
git clone https://github.com/cannlytics.com/cannlytics-api
```

## Development<a name="development"></a>

Running the Cannlytics API locally for development is easy.

```shell
python manage.py runserver 4200
```

or

```shell
npm run dev
```

> Note that the API is run on port 4200 to allow for simultaneous development with other pieces of the Cannlytics engine.

## Testing<a name="testing"></a>

Tests are performed with [`pytest`](https://docs.pytest.org/en/stable/). You can perform the tests by executing the `pytest` command from the `tests` directory.

```shell
cd tests
pytest
```

## Publishing<a name="publishing"></a>

See [`docs/publishing.md`](docs/publishing.md) for instructions on how to publish the API. Publishing entails containerizing the API, deploying the container to Cloud Run, and directing hosting requests to the containerized app from Firebase Hosting. You can publish using Node.js with one quick command:

```shell
npm run publish
```

## License <a name="license"></a>

This application is released under the [MIT license](LICENSE.md). You can use the code for any purpose, including commercial projects.

[![license](https://img.shields.io/badge/License-MIT-brightgreen.svg)](https://opensource.org/licenses/MIT)

Made with 💖 by Cannlytics.

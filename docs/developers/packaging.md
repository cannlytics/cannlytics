| Cannlytics SOP-0010 |  |
|---------------------|--|
| Title | Packaging |
| Version | 1.0.0 |
| Created At | 2023-07-18 |
| Updated At | 2023-07-18 |
| Review Period | Annual |
| Last Review | 2023-07-18 |
| Author | Keegan Skeate, Founder |
| Approved by | Keegan Skeate, Founder |
| Status | Active |

# Packaging

This SOP guides you through packaging the `cannlytics` Python package and deploying the package to [PyPI](https://pypi.org).

## Testing

First, ensure that all tests are passed.

```shell
cd ./tests
pytest --disable-pytest-warnings
cd ../
```

## Installation

Make sure you have the latest versions of setuptools and wheel installed:

```shell
pip install --user --upgrade setuptools wheel
```

You will also need to install Twine:

```shell
pip install --user --upgrade twine
```

## Deploying

First, build the package from the same directory where setup.py is located:

```shell
python setup.py sdist bdist_wheel
```

Next, run Twine to upload all of the archives under dist:

DEV:

 ```shell
python -m twine upload --repository testpypi dist/*
 ```

 PRODUCTION

```shell
python -m twine upload dist/*
 ```

You will be prompted for a username and password. For the username, use `__token__`. For the password, use your API key issued on PyPi, including the pypi- prefix. On Windows, when entering your password, right click the taskbar, then select `Edit` > `Paste`, because other pasting methods do not work for this password field.

## Resources

- [Real Python Packaging Tutorial](https://realpython.com/pypi-publish-python-package/)

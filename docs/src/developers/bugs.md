# 🐞 Bugs

A non-exhaustive list of encountered bugs and their solutions.

- [Visual Studio Code - Target of URI doesn't exist 'package:flutter/material.dart'](https://stackoverflow.com/questions/44909653/visual-studio-code-target-of-uri-doesnt-exist-packageflutter-material-dart) - This error usually is not an actual error and is shown when 2 different projects are open.

- [FlatButton - This class is deprecated, please use TextButton instead.](https://api.flutter.dev/flutter/material/TextButton-class.html)

- [The parameter can't have a value of 'null' because of its type in Dart](https://stackoverflow.com/questions/64560461/the-parameter-cant-have-a-value-of-null-because-of-its-type-in-dart) - [Solution](https://dart.dev/null-safety): Set an initial value when declaring variables.

- `Could not find a file named "pubspec.yaml" in ...` - [Solution](https://stackoverflow.com/questions/27217278/could-not-find-a-file-named-pubspec-yaml-in): Make sure your that your `path` in `pubspec.yaml` points to a valid Flutter package with a `pubspec.yaml`.

- If you encounter a [django-livereload-server NotImplementedError](https://stackoverflow.com/questions/58422817/jupyter-notebook-with-python-3-8-notimplementederror), then it is likely that you are using Python 3.8+ and need to add the following code to `Lib\site-packages\tornado\platform\asyncio.py`.

  ```py

  import sys

  if sys.platform == 'win32':
      asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
  ```

- [`HTTPError: 400 Client Error: File already exists.` when publishing to PyPi](https://github.com/pypa/warehouse/issues/6872)

- [Error: Can't Use Google Cloud Storage in Google Cloud Functions](https://stackoverflow.com/questions/52249978/write-to-google-cloud-storage-from-cloud-function-python/52250030)

  > **Solution** - If you are using Firebase Storage in a Google Cloud Function, then you need to specify `google-cloud-storage` in your `requirements.txt`.

- [Error: Firebase Hosting Base Rewrite Not Working](https://stackoverflow.com/questions/44871075/redirect-firebase-hosting-root-to-a-cloud-function-is-not-working)

  > **Solution** - In order to use a rewrite at the root in Firebase Hosting, you must not include an `index.html` file in the public folder.

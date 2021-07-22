# 🐞 Bugs

A non-exhaustive list of encountered bugs and their solutions.

- When running `npm run docs` you get an error message including: `docker: error during connect: This error may indicate that the docker daemon is not running`. Simply start [Docker](https://docs.docker.com/engine/reference/commandline/start/).

- [No 'Access-Control-Allow-Origin' header is present on the requested resource—when trying to get data from a REST API](https://stackoverflow.com/questions/43871637/no-access-control-allow-origin-header-is-present-on-the-requested-resource-whe). Solution: Create a file
  ```json
  [
    {
      "origin": ["*"],
      "method": ["GET"],
      "maxAgeSeconds": 3600
    }
  ]
  ```
  and deploy the rules with:
  ```shell
  gsutil cors set cors.json gs://<your-cloud-storage-bucket>
  ```

- [Error: PostCSS plugin autoprefixer requires PostCSS 8. Update PostCSS or downgrade this plugin](https://stackoverflow.com/questions/64057023/error-postcss-plugin-autoprefixer-requires-postcss-8-update-postcss-or-downgra). Solution: `npm i postcss`.

- Access to fetch at `<pdf-url>` from origin 'http://127.0.0.1:8000' has been blocked by CORS policy: No 'Access-Control-Allow-Origin' header is present on the requested resource. If an opaque response serves your needs, set the request's mode to 'no-cors' to fetch the resource with CORS disabled.

  * Potential solution: <https://stackoverflow.com/a/58153018/5021266>

- **Current** [InsufficientPermissionError] after initializing Firebase in a production environment. Leads:

  * Possible solution: <https://github.com/firebase/firebase-functions/issues/679>
  * Proposed workaround: <https://github.com/firebase/firebase-js-sdk/issues/1958>
  * Helpful reading: <https://stackoverflow.com/questions/55016899/appengine-warning-openblas-warning-could-not-determine-the-l2-cache-size-on>
  * Promising: <https://stackoverflow.com/questions/24488891/gunicorn-errors-haltserver-haltserver-worker-failed-to-boot-3-django>
  * Long shot: <https://stackoverflow.com/questions/64585380/firebase-authentication-unknown-error-while-making-a-remote-service-call>
  * Similar issue: <https://github.com/jotes/django-cookies-samesite/issues/19>
  * Potential fix: <https://github.com/jotes/django-cookies-samesite>
  * **Solution**: Assign permissions in IAM console (see the installation guide).

- [Firebase Hosting strip all cookies except for `__session`.](https://stackoverflow.com/a/58719953/5021266) Also see [this issue](https://stackoverflow.com/questions/57450648/how-to-use-multiple-cookies-in-firebase-hosting-cloud-run?noredirect=1&lq=1). Simple fix: use `__session` cookie instead of `session` cookie.

- [AppEngine warning - OpenBLAS WARNING - could not determine the L2 cache size on this system](https://stackoverflow.com/questions/55016899/appengine-warning-openblas-warning-could-not-determine-the-l2-cache-size-on)

- [Firebase hosting deployment failing](https://stackoverflow.com/questions/57911225/firebase-hosting-deployment-failing) at `hosting: uploading new files [5/128]` with error `Error: Task xyz failed: retries exhausted after 6 attempts`. Quick solution: Delete the hidden folder in you project root directory `.firebase/hosting.*.cache`.

- When running `npm run publish` to create the container for Cloud Run, the program keeps retying, for example `Retrying in 12 seconds`. In this case, there is a container naming issue. Ensure `gcloud run deploy APP-NAME` matches the image tag `gcr.io/PROJECT/APP-NAME`.

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

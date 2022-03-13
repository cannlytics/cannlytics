# 🐞 Bugs

A non-exhaustive list of encountered bugs and their solutions.

18. 400 Bad Request after publishing to Cloud Run.
  > **Solution**: Ensure `ALLOWED_HOSTS` in your `settings.py` has all the permitted domains or is set to `['*']`.

17. When running `npm run docs` you get an error message including: `docker: error during connect: This error may indicate that the docker daemon is not running`.
  > **Solution**: Simply start [Docker](https://docs.docker.com/engine/reference/commandline/start/).

16. [No 'Access-Control-Allow-Origin' header is present on the requested resource—when trying to get data from a REST API](https://stackoverflow.com/questions/43871637/no-access-control-allow-origin-header-is-present-on-the-requested-resource-whe).
  > **Solution**: Create a `cors.json` file:
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

15. [Error: PostCSS plugin autoprefixer requires PostCSS 8. Update PostCSS or downgrade this plugin](https://stackoverflow.com/questions/64057023/error-postcss-plugin-autoprefixer-requires-postcss-8-update-postcss-or-downgra).
  > **Solution**: `npm i postcss`.

14. Access to fetch at `<pdf-url>` from origin 'http://127.0.0.1:8000' has been blocked by CORS policy: No 'Access-Control-Allow-Origin' header is present on the requested resource. If an opaque response serves your needs, set the request's mode to 'no-cors' to fetch the resource with CORS disabled.
  > *Potential solution*: <https://stackoverflow.com/a/58153018/5021266>

13. [InsufficientPermissionError] after initializing Firebase in a production environment.
  > **Solution**: Assign permissions in IAM console (see the installation guide).

12. [Firebase Hosting strip all cookies except for `__session`.](https://stackoverflow.com/a/58719953/5021266) Also see [this issue](https://stackoverflow.com/questions/57450648/how-to-use-multiple-cookies-in-firebase-hosting-cloud-run?noredirect=1&lq=1).
  > **Solution**: use `__session` cookie instead of `session` cookie. Also see [Django cookies and headers](https://stackoverflow.com/questions/15124308/django-cookies-and-headers). Furthermore, set the `__session cookie` as follows to ensure the cookie is passed in production.
  ```py
  
  ```


11. [AppEngine warning - OpenBLAS WARNING - could not determine the L2 cache size on this system](https://stackoverflow.com/questions/55016899/appengine-warning-openblas-warning-could-not-determine-the-l2-cache-size-on)

10. [Firebase hosting deployment failing](https://stackoverflow.com/questions/57911225/firebase-hosting-deployment-failing) at `hosting: uploading new files [5/128]` with error `Error: Task xyz failed: retries exhausted after 6 attempts`.
  > **Solution**: Delete the hidden folder in you project root directory `.firebase/hosting.*.cache`.

9. When running `npm run publish` to create the container for Cloud Run, the program keeps retying, for example `Retrying in 12 seconds`.
  > **Solution**: In this case, there is a container naming issue. Ensure `gcloud run deploy APP-NAME` matches the image tag `gcr.io/PROJECT/APP-NAME`.

4. If you encounter a [django-livereload-server NotImplementedError](https://stackoverflow.com/questions/58422817/jupyter-notebook-with-python-3-8-notimplementederror), then it is likely that you are using Python 3.8+ and need to add the following code to `Lib\site-packages\tornado\platform\asyncio.py`.
  ```py

  import sys

  if sys.platform == 'win32':
      asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
  ```

3. [`HTTPError: 400 Client Error: File already exists.` when publishing to PyPi](https://github.com/pypa/warehouse/issues/6872)

2. [Error: Can't Use Google Cloud Storage in Google Cloud Functions](https://stackoverflow.com/questions/52249978/write-to-google-cloud-storage-from-cloud-function-python/52250030)
  > **Solution** - If you are using Firebase Storage in a Google Cloud Function, then you need to specify `google-cloud-storage` in your `requirements.txt`.

1. [Error: Firebase Hosting Base Rewrite Not Working](https://stackoverflow.com/questions/44871075/redirect-firebase-hosting-root-to-a-cloud-function-is-not-working)
  > **Solution** - In order to use a rewrite at the root in Firebase Hosting, you must not include an `index.html` file in the public folder.

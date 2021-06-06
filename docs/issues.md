# Issues

### Discovered Bugs <a name="bugs"></a>

Below is a running list of existing and solved issues. See [bugs](https://cannlytics.com/bugs) for a full list of bugs and issues that you may encounter. Below are noteworthy bugs that you may encounter and their solutions.

- [Error: Can't Use Google Cloud Storage in Google Cloud Functions](https://stackoverflow.com/questions/52249978/write-to-google-cloud-storage-from-cloud-function-python/52250030)

  > **Solution** - If you are using Firebase Storage in a Google Cloud Function, then you need to specify `google-cloud-storage` in your `requirements.txt`.

* [Error: Firebase Hosting Base Rewrite Not Working](https://stackoverflow.com/questions/44871075/redirect-firebase-hosting-root-to-a-cloud-function-is-not-working)

  > **Solution** - In order to use a rewrite at the root in Firebase Hosting, you must not include an `index.html` file in the public folder.
# Firebase

The personal site leverages Firebase for many back-end services. If you wish to create a Firebase project similar to this one, then you can follow these steps.

First, create a [Firebase account](https://www.google.com/aclk?sa=l&ai=DChcSEwjAhp2UsL_sAhX-GK0GHZDMBWcYABAAGgJwdg&sig=AOD64_3PgoXNGg4h4EkZJ8nByAn5x8xSLg&q&adurl&ved=2ahUKEwifm5eUsL_sAhUE7J4KHffyAOUQ0Qx6BAgnEAE) with a [Blaze payment plan](https://console.firebase.google.com/project/_/overview?purchaseBillingPlan=metered). Once you have an account, sign into the [Firebase Console](https://console.firebase.google.com/) and create or open a project.

You will need your Firebase project ID, database region, and storage bucket name when deploying<sup>[*](#storage-bucket)</sup> the personal website to Firebase hosting.

> <a name="storage-bucket">*</a> A storage bucket is used by the Secret Manager. The same or a different storage bucket can optionally be used to serve static files for your deployed site.

## Potential use cases

- Sending Email with Firestore and Firebase Cloud Functions.
- Storing template data in Firestore.
- Storing files for user's to download in Firebase Storage.

## Cloud Functions

Here are the important snippets from the [quick start to Python Cloud Functions](https://cloud.google.com/functions/docs/quickstart).

1. Deploy a Python cloud function from the command line:

```shell
gcloud functions deploy hello_get \
--runtime python38 --trigger-http --allow-unauthenticated
```

2. Describe the function:

```shell
gcloud functions describe hello_get
```

3. Delete a function:

```shell
gcloud functions delete hello_get
```

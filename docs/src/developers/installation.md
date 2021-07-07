# Installation

First things first, you can clone the repository:

```shell
git clone https://github.com/cannlytics/cannlytics
```

Next, you can install the Node.js dependencies:

```shell
npm install
```

## Credentials

1. The project expects an `.env` file at the project's root.

2. You can create a Django secret key and save it your `.env` file as follows.

```py
from django.utils.crypto import get_random_string

chars = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'
generated_secret_key = get_random_string(50, chars)
print(generated_secret_key)
```

```
SECRET_KEY=xyz
```

3. Next, navigate to your Firebase project settings and set your Firebase configuration in your `.env` file.

```
FIREBASE_API_KEY=xyz
FIREBASE_AUTH_DOMAIN=cannlytics.firebaseapp.com
FIREBASE_DATABASE_URL=https://cannlytics.firebaseio.com
FIREBASE_PROJECT_ID=cannlytics
FIREBASE_STORAGE_BUCKET=cannlytics.appspot.com
FIREBASE_MESSAGING_SENDER_ID=123
FIREBASE_APP_ID=123
FIREBASE_MEASUREMENT_ID=G-abc
```

4. You can also setup email by setting the `EMAIL_HOST_USER` and `EMAIL_HOST_PASSWORD` environment variables. It is recommended that you [create an app password](https://support.google.com/accounts/answer/185833/sign-in-with-app-passwords?hl=en) if you are using Gmail.


5. Finally, create and download a service account and save the path to your service account as a `GOOGLE_APPLICATION_CREDENTIALS` environment variable.

```
GOOGLE_APPLICATION_CREDENTIALS=path/to/your/service/account.json
```

## Firebase Hosting

Create a `.firebasesrc` in the root directory with your Firebase hosting reference. For example

```json
{
  "projects": {
    "default": "your-lims"
  },
  "targets": {
    "your-lims": {
      "hosting": {
        "docs": [
          "your-docs"
        ],
        "dev": [
          "your-dev"
        ],
        "production": [
          "your-lims"
        ]
      }
    }
  }
}
```

For downloading files from Firebase Storage, you should set your CORS rules. If you don't want any domain-based restrictions (the most common scenario), then copy the following JSON to a file named `cors.json`:

```json
[
  {
    "origin": ["*"],
    "method": ["GET"],
    "maxAgeSeconds": 3600
  }
]
```

Then deploy the rules with:

```shell
gsutil cors set cors.json gs://<your-cloud-storage-bucket>
```

### Required Google permissions

* gcloud.builds.submit
* storage.objects.get

-compute@developer.gserviceaccount.com needs Storage Object Admin

## Create your secret environment variables

Open [Google Cloud Shell](https://console.cloud.google.com/) and run the following command to ensure that you are working under the correct email and with the correct project:

```shell
gcloud init
```

Next, ensure that your project has billing enabled, then enable the Cloud APIs that are used:

```shell
gcloud services enable \
  run.googleapis.com \
  sql-component.googleapis.com \
  sqladmin.googleapis.com \
  compute.googleapis.com \
  cloudbuild.googleapis.com \
  secretmanager.googleapis.com
```

Create a secret with:

```shell
gcloud secrets create \
  cannlytics_lims_settings \
  --replication-policy automatic
```

Allow Cloud Run access to access this secret:

```shell
PROJECT_ID=$(gcloud config get-value project)
PROJECTNUM=$(gcloud projects describe ${PROJECT_ID} --format 'value(projectNumber)')
CLOUDRUN=${PROJECTNUM}-compute@developer.gserviceaccount.com

gcloud secrets add-iam-policy-binding \
  cannlytics_settings \
  --member serviceAccount:${CLOUDRUN} \
  --role roles/secretmanager.secretAccessor
```


Cloud Build will run Django commands, so Cloud Build will also need access to this secret:

```shell
PROJECT_ID=$(gcloud config get-value project)
PROJECTNUM=$(gcloud projects describe ${PROJECT_ID} --format 'value(projectNumber)')
CLOUDBUILD=${PROJECTNUM}@cloudbuild.gserviceaccount.com

gcloud secrets add-iam-policy-binding \
  cannlytics_settings \
  --member serviceAccount:${CLOUDBUILD} \
  --role roles/secretmanager.secretAccessor
```

Create a Cloud Storage bucket with a globally unique name:

```shell
REGION=us-central1
GS_BUCKET_NAME=${PROJECT_ID}-media
gsutil mb -l ${REGION} gs://${GS_BUCKET_NAME}
```

Then create your environment variables and save them to the secret:

```shell
APP_ID=cannlytics
REGION=us-central1
DJPASS="$(cat /dev/urandom | LC_ALL=C tr -dc 'a-zA-Z0-9' | fold -w 30 | head -n 1)"
echo DATABASE_URL=\"postgres://djuser:${DJPASS}@//cloudsql/${APP_ID}:${REGION}:cannlytics-sql/cannlytics-sql-database\" > .env
echo GS_BUCKET_NAME=\"${GS_BUCKET_NAME}\" >> .env
echo SECRET_KEY=\"$(cat /dev/urandom | LC_ALL=C tr -dc 'a-zA-Z0-9' | fold -w 50 | head -n 1)\" >> .env
echo DEBUG=\"False\" >> .env
echo EMAIL_HOST_USER=\"your-email\" >> .env
echo EMAIL_HOST_PASSWORD=\"your-email-password\" >> .env
gcloud secrets versions add cannlytics_settings --data-file .env
rm .env
```

> Set `EMAIL_HOST_USER` and `EMAIL_HOST_PASSWORD` with your email and [app password](https://dev.to/abderrahmanemustapha/how-to-send-email-with-django-and-gmail-in-production-the-right-way-24ab). If you do not plan to use Django's email interface, then you exclude `EMAIL_HOST_USER` and `EMAIL_HOST_PASSWORD`.

Update your IAM policy:

```shell
gcloud beta run services add-iam-policy-binding --region=us-central1 --member=allUsers --role=roles/run.invoker your-lims
```

You can confirm that the secret was created or updated with:

```shell
gcloud secrets versions list cannlytics_settings
```

Helpful resources:

* [Generating Django Secret Keys](https://stackoverflow.com/questions/4664724/distributing-django-projects-with-unique-secret-keys)

## Deploying

The deployment contains three steps:

### 1. The app is containerized and uploaded to Container Registry.

First, set the project you want to work with:

```shell
gcloud config set project your-lims
```

You can build your container image using Cloud Build by running the following command from the directory containing the Dockerfile:

```shell
set PROJECT_ID=your-lims
set APP_ID=cannlytics
gcloud config set project %PROJECT_ID%
gcloud builds submit --tag gcr.io/%PROJECT_ID%/%APP_ID%
```

<!-- python manage.py collectstatic --noinput -->

> Note that your `APP_ID` must be in snake case.

You can list all the container images associated with your current project using this command:

```shell
gcloud container images list
```

### 2. The container image is deployed to Cloud Run.

Cannlytics uses a fully managed Cloud Run platform. Deploy the container to Cloud Run with:

```shell
set REGION=us-central1
gcloud run deploy %PROJECT_ID% --image gcr.io/%PROJECT_ID%/%APP_ID% --region %REGION% --allow-unauthenticated --platform managed
```

You can retrieve the service URL with:

```shell
gcloud run services describe your-lims \
  --platform managed \
  --region $REGION  \
  --format "value(status.url)"
```

### 3. Hosting requests are directed to the containerized app.

This step provides access to this containerized app from a [Firebase Hosting](https://firebase.google.com/docs/hosting) URL, so that the app can generate dynamic content for the Firebase-hosted site. You will need to have Firebase's command line tool installed:

```shell
npm install -g firebase-tools
```

Afterwards, you can login to Firebase in the command line with:

```shell
firebase login --reauth
```

Then, you can deploy the site with:

```shell
firebase deploy --project %PROJECT_ID% --only hosting:production
```

or

```shell
npm run deploy
```

### Security rules

You can deploy a new set of security rules with the Firebase CLI.

```shell
firebase deploy --only firestore:rules
```

## Monitoring

You can now monitor your app with the following tools.

| Resource | Description |
| ---------- | ------------ |
| [Cloud Run Console](https://console.cloud.google.com/run) | Manage your app's container. |
| [Logs Explorer](https://console.cloud.google.com/logs) | Realtime logs for your app. |
| [Error Reporting](https://console.cloud.google.com/errors) | Provides detailed historic errors that occurred when running your app. |

## (Optional) Setup a Custom Domain

You can register a domain with [Google Domains](https://domains.google.com/registrar/). You can then add a custom domain in the Firebase Hosting console.

> If you are using Google Domains, then use '@' for your root domain name and 'www' or 'www.domain.com' for your subdomains when registering your DNS A records.

## Conclusion

You now have a simple, yet complex, website running on Cloud Run, which will automatically scale to handle your website's traffic, optimizing CPU and memory so that your website runs with the smallest footprint possible, saving you money. If you desire, you can now seamlessly integrate services such as Cloud Storage into your Django website. You can now plug and play and tinker to your heart's content while your users enjoy your beautiful material!


## Helpful Resources

- [Running Django on Cloud Run](https://cloud.google.com/python/django/run#gcloud)
- [Django on Cloud Run Code Lab](https://codelabs.developers.google.com/codelabs/cloud-run-django/index.html#7)
- [Granting permissions](https://cloud.google.com/container-registry/docs/access-control#grant)
- [Permission Denied - GCP Cloud Resource Manager setIamPolicy](https://stackoverflow.com/questions/53163115/permission-denied-gcp-cloud-resource-manager-setiampolicy)
- [Secret manager access denied despite correct roles for service account](https://stackoverflow.com/questions/62444867/secret-manager-access-denied-despite-correct-roles-for-service-account)
- [Troubleshooting group membership](https://cloud.google.com/iam/docs/troubleshooting-access#troubleshooting_group_membership)

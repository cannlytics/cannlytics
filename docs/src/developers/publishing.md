# Publishing

First, you will need to save your environment variables as a secret. Then, you may want to walk through the build process one time manually. Afterwards, publishing the website is done with one command:

```shell
npm run publish
```

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
  cannlytics_lims_settings \
  --member serviceAccount:${CLOUDRUN} \
  --role roles/secretmanager.secretAccessor
```


Cloud Build will run Django commands, so Cloud Build will also need access to this secret:

```shell
PROJECT_ID=$(gcloud config get-value project)
PROJECTNUM=$(gcloud projects describe ${PROJECT_ID} --format 'value(projectNumber)')
CLOUDBUILD=${PROJECTNUM}@cloudbuild.gserviceaccount.com

gcloud secrets add-iam-policy-binding \
  cannlytics_lims_settings \
  --member serviceAccount:${CLOUDBUILD} \
  --role roles/secretmanager.secretAccessor
```

Create a Cloud Storage bucket with a globally unique name:

```shell
REGION=us-central1
GS_BUCKET_NAME=${PROJECT_ID}-media
gsutil mb -l ${REGION} gs://${GS_BUCKET_NAME}
```

Then create your environment variables and save them to the secret in the [Secret Manager console](https://console.cloud.google.com/security/secret-manager) or with:

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

You can confirm that the secret was created or updated with:

```shell
gcloud secrets versions list cannlytics_lims_settings
```

Finally, update your IAM policy for all project users to invoke cloud run:

```shell
gcloud beta run services add-iam-policy-binding --region=us-central1 --member=allUsers --role=roles/run.invoker your-lims
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

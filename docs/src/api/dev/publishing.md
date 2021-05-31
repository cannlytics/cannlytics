# Publishing

First, you will need to save your environment variables as a secret. Then, you may want to walk through the build process one time manually. Before publishing, change `DEBUG=False` to `DEBUG=True` in your `.env` file. Afterwards, publishing the website is done with one command:

```shell
npm run publish
```

## Create secret environment variables

Before you can publish, you will need to set your environment variables. Open [Google Cloud Shell](https://console.cloud.google.com/) and run the following command:

```shell
gcloud init
```

Next, enable the Cloud APIs that are used:

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
  cannlytics_api_settings \
  --replication-policy automatic
```

Allow Cloud Run to access this secret:

```shell
PROJECT_ID=cannlytics
PROJECTNUM=$(gcloud projects describe ${PROJECT_ID} --format 'value(projectNumber)')
CLOUDRUN=${PROJECTNUM}-compute@developer.gserviceaccount.com

gcloud secrets add-iam-policy-binding \
  cannlytics_api_settings \
  --member serviceAccount:${CLOUDRUN} \
  --role roles/secretmanager.secretAccessor
```

Then create your environment variables and save them to the secret:

```shell
REGION=us-central1
DJPASS="$(cat /dev/urandom | LC_ALL=C tr -dc 'a-zA-Z0-9' | fold -w 30 | head -n 1)"
echo DATABASE_URL=\"postgres://djuser:${DJPASS}@//cloudsql/${PROJECT_ID}:${REGION}:cannlytics-sql/cannlytics-sql-database\" > .env
echo GS_BUCKET_NAME=\"${GS_BUCKET_NAME}\" >> .env
echo GCS_SA=\"${PROJECT_NUM}-compute@developer.gserviceaccount.com\" >> .env
echo SECRET_KEY=\"$(cat /dev/urandom | LC_ALL=C tr -dc 'a-zA-Z0-9' | fold -w 50 | head -n 1)\" >> .env
echo DEBUG=\"False\" >> .env
gcloud secrets versions add cannlytics_api_settings --data-file .env
rm .env
```

Update your IAM policy:

```shell
gcloud beta run services add-iam-policy-binding --region=us-central1 --member=allUsers --role=roles/run.invoker cannlytics
```

You can confirm that the secret was created or updated with:

```shell
gcloud secrets versions list cannlytics_api_settings
```

Helpful resources:

* [Generating Django Secret Keys](https://stackoverflow.com/questions/4664724/distributing-django-projects-with-unique-secret-keys)

## Publishing process

The publishing process contains three steps:

### 1. The app is containerized and uploaded to Container Registry.

You can build your container image using Cloud Build by running the following command from the directory containing the Dockerfile:

```shell
set PROJECT_ID=cannlytics
set APP_ID=cannlytics_api
gcloud builds submit --tag gcr.io/%PROJECT_ID%/%APP_ID%
```

> Note that your `APP_ID` must be in snake case.

### 2. The container image is deployed to Cloud Run.

This project uses a fully managed Cloud Run platform. [Cloud Run for Anthos](https://cloud.google.com/anthos/run) can be used as an alternative. Deploy the container to Cloud Run with:

```shell
set REGION=us-central1
gcloud run deploy %PROJECT_ID% --image gcr.io/%PROJECT_ID%/%APP_ID% --region %REGION% --allow-unauthenticated --platform managed
```

You can retrieve the service URL with:

```shell
gcloud run services describe cannlytics-website \
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
firebase login
```

Then, you can deploy the site with:

```shell
firebase deploy
```

## Monitoring

You can then view logs for your deployment in the Cloud run console.

## Conclusion

You now have a simple, yet powerful, API running on Cloud Run, which will automatically scale to handle your API's traffic, optimizing CPU and memory so that your API runs with the smallest footprint possible, saving you money and letting society breathe easier. If you desire, then you can now seamlessly integrate services such as Cloud Storage into your Django API. You can now plug and play and tinker to your heart's content while your users enjoy your beautiful material!

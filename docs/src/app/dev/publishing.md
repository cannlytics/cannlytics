# Publishing

First, you will need to save your environment variables as a secret. Then, you may want to walk through the build process one time manually. Afterwards, publishing the website is done with one command:

```shell
npm run publish
```

## Create secret environment variables

Open [Google Cloud Shell](https://console.cloud.google.com/) and run the following command:

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
  cannlytics_console_settings \
  --replication-policy automatic
```

Allow Cloud Run to access this secret:

```shell
PROJECT_ID=cannlytics
PROJECTNUM=$(gcloud projects describe ${PROJECT_ID} --format 'value(projectNumber)')
CLOUDRUN=${PROJECTNUM}-compute@developer.gserviceaccount.com

gcloud secrets add-iam-policy-binding \
  cannlytics_console_settings \
  --member serviceAccount:${CLOUDRUN} \
  --role roles/secretmanager.secretAccessor
```

Then create your environment variables and save them to the secret:

```shell
APP_ID=cannlytics-console
REGION=us-central1
DJPASS="$(cat /dev/urandom | LC_ALL=C tr -dc 'a-zA-Z0-9' | fold -w 30 | head -n 1)"
GS_BUCKET_NAME=cannlytics-console.appspot.com
echo DATABASE_URL=\"postgres://djuser:${DJPASS}@//cloudsql/${APP_ID}:${REGION}:cannlytics-sql/cannlytics-sql-database\" > .env
echo GS_BUCKET_NAME=\"${GS_BUCKET_NAME}\" >> .env
echo SECRET_KEY=\"$(cat /dev/urandom | LC_ALL=C tr -dc 'a-zA-Z0-9' | fold -w 50 | head -n 1)\" >> .env
echo DEBUG=\"True\" >> .env
echo EMAIL_HOST_USER=\"email\" >> .env
echo EMAIL_HOST_PASSWORD=\"password\" >> .env
gcloud secrets versions add cannlytics_console_settings --data-file .env
rm .env

```

> Set `EMAIL_HOST_USER` and `EMAIL_HOST_PASSWORD` with your email and [app password](https://dev.to/abderrahmanemustapha/how-to-send-email-with-django-and-gmail-in-production-the-right-way-24ab). If you do not plan to use Django's email interface, then you exclude `EMAIL_HOST_USER` and `EMAIL_HOST_PASSWORD`.

Update your IAM policy:

```shell
 gcloud beta run services add-iam-policy-binding --region=us-central1 --member=allUsers --role=roles/run.invoker cannlytics
```

You can confirm that the secret was created or updated with:

```shell
gcloud secrets versions list cannlytics_console_settings
```

Helpful resources:

* [Generating Django Secret Keys](https://stackoverflow.com/questions/4664724/distributing-django-projects-with-unique-secret-keys)

## Publishing process

The publishing process contains three steps:

### 1. The app is containerized and uploaded to Container Registry.

You can build your container image using Cloud Build by running the following command from the directory containing the Dockerfile:

```shell
set PROJECT_ID=cannlytics
set APP_ID=cannlytics-console
python manage.py collectstatic --noinput
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
gcloud run services describe cannltics-console \
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
firebase deploy --project ${PROJECT_ID} --only hosting:production
```

> If you are using an SQL database, then you will also need to run:
  ```shell
  gcloud builds submit --config cloudmigrate.yaml \
    --substitutions _REGION=$REGION
  ```

### Security rules

You can deploy a new set of security rules with the Firebase CLI.

```shell
firebase deploy --only firestore:rules
```

## Monitoring

You can view logs for your deployment in the Cloud run console at https://console.cloud.google.com/run/detail/us-central1/your-project/logs?project=your-project

## (Optional) Setup a Custom Domain

You can register a domain with [Google Domains](https://domains.google.com/registrar/). You can then add a custom domain in the Firebase Hosting console.

> If you are using Google Domains, then use '@' for your root domain name and 'www' or 'www.domain.com' for your subdomains when registering your DNS A records.

## Conclusion

You now have a simple, yet complex, website running on Cloud Run, which will automatically scale to handle your website's traffic, optimizing CPU and memory so that your website runs with the smallest footprint possible, saving you money. If you desire, you can now seamlessly integrate services such as Cloud Storage into your Django website. You can now plug and play and tinker to your heart's content while your users enjoy your beautiful material!

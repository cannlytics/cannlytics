# Cloud Functions

Cloud Functions provide a mechanism to run code in the cloud based on certain events. You will need to [enable billing for your project](http://console.cloud.google.com/billing/), [enable the Cloud Scheduler API](http://console.cloud.google.com/apis/library/cloudscheduler.googleapis.com), and [enable the Pub/Sub API](http://console.cloud.google.com/apis/library/pubsub.googleapis.com) to allow all functionality.

```shell
gcloud services enable cloudfunctions.googleapis.com cloudscheduler.googleapis.com pubsub.googleapis.com --project=<your-project-id>
```

*Functions*

- [Auth Sign Up](#auth-sign-up)
- [Metrc Sync](#metrc-sync)
- [Get YouTube Video Views](#get-youtube-video-views)

## Auth Sign Up

The `auth_signup` cloud function is designed to create any new user data in Firestore when a new user is created in Firebase Authentication. Specifically, it populates the user's subscription with 10 trial tokens.

You can deploy the `auth_signup` cloud function with:

```shell
gcloud functions deploy auth_signup --source auth_signup --entry-point auth_signup  --trigger-event providers/firebase.auth/eventTypes/user.create  --trigger-resource cannlytics --runtime python39
```



## Calculate Strains Statistics

Triggered by changes to `public/data/lab_results/{lab_result_id}`. The function calculates the following statistics for each strain:

The data is saved to `public/data/strains/{strain_id}`.


You can deploy the `calc_strains_stats` cloud function with:

```shell
gcloud functions deploy calc_strains_stats --source calc_strains_stats --entry-point calc_strains_stats  --trigger-event providers/firebase.auth/eventTypes/user.create  --trigger-resource cannlytics --runtime python310
```

## Metrc Sync

You can deploy the `metrc_sync` cloud function with:

```shell
gcloud functions deploy metrc_sync \
  --entry-point metrc_sync \
  --runtime python39 \
  --trigger-event "providers/cloud.firestore/eventTypes/document.write" \
  --trigger-resource "projects/cannlytics/databases/(default)/documents/organizations/{org_id}/metrc_user_api_keys/{key_id}"
```

The `metrc_sync` cloud function is designed to synchronize a user's Metrc data with their data saved in Firestore. Specifically, it watches for changes to documents located at `organizations/{org_id}/metrc_user_api_keys/{metrc_hash}`. These documents contain API key data used for authenticating with the Metrc. The 3 actions the function performs are:

1. If a document is added, the function will perform an initial synchronization of the Metrc data. 
2. If a document is changed and the sync field is set to `True`, the function will perform a synchronization of the Metrc data.
3. If an API key is deleted, the function will delete the associated data from Firestore.

The function initializes both Metrc and Firebase, retrieves all Metrc data by category, and calculates Metrc usage statistics, such as totals. The data and statistics are saved to Firestore. Once syncing is complete, the API key data is updated to set sync to `False` with the timestamp for when the data was last synced, `synced_at`. Finally, the administrator is emailed if a key was added, a key was deleted, or there is an error.


## Get YouTube Video Views

You will need to create an `env.yaml` file in the `get_youtube_video_views` folder with the following environment variable.

```yaml
YOUTUBE_API_KEY: your-youtube-api-key
```

Automating the collection of YouTube video views can be done with the following 3 steps.

1. Create a Pub/Sub topic:

    ```shell
    gcloud pubsub topics create get_youtube_video_views
    ```

2. Deploy the function:

    ```shell
    gcloud functions deploy get_youtube_video_views --source get_youtube_video_views --entry-point get_youtube_video_views --runtime python39 --trigger-topic get_youtube_video_views --memory 512MB --timeout 120 --env-vars-file get_youtube_video_views/env.yaml
    ```

3. Finally, create a [Cloud Scheduler](https://cloud.google.com/scheduler/docs/creating#gcloud) cron job:

    ```shell
    gcloud scheduler jobs create pubsub get_youtube_video_views --schedule "15 * * * *" --topic get_youtube_video_views --message-body "success"
    ```

Your function should now run nicely every 15 minutes. You can read the logs for your function with:

```shell
gcloud functions logs read get_youtube_video_views
```

You can substitute `create` in step 3 with `update` to update your scheduled job.

> Note: If you encounter a `PERMISSION_DENIED` error, then make sure that [the service account being used has sufficient permissions](https://stackoverflow.com/a/58646481/5021266).

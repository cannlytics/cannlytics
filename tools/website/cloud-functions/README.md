# Cloud Functions

Cloud Functions provide a mechanism to run code in the cloud based on certain events. You will need to [enable billing for your project](http://console.cloud.google.com/billing/), [enable the Cloud Scheduler API](http://console.cloud.google.com/apis/library/cloudscheduler.googleapis.com), and [enable the Pub/Sub API](http://console.cloud.google.com/apis/library/pubsub.googleapis.com) to allow all functionality.

```shell
gcloud services enable cloudfunctions.googleapis.com cloudscheduler.googleapis.com pubsub.googleapis.com --project=<your-project-id>
```

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

# Cloud Functions

Cloud Functions provide a mechanism to run code in the cloud based on certain events. You will need to [enable billing for your project](http://console.cloud.google.com/billing/), [enable the Cloud Scheduler API](http://console.cloud.google.com/apis/library/cloudscheduler.googleapis.com), and [enable the Pub/Sub API](http://console.cloud.google.com/apis/library/pubsub.googleapis.com) to allow all functionality.

```shell
gcloud services enable cloudfunctions.googleapis.com cloudscheduler.googleapis.com pubsub.googleapis.com --project=<your-project-id>
```

Publishing a cloud function (e.g. `get_data_ma`) can be done with the following 3 steps.

1. Create a Pub/Sub topic:

    ```shell
    gcloud pubsub topics create get_data_ma
    ```

2. Deploy the function:

    ```shell
    gcloud functions deploy get_data_ma --source get_data_ma --entry-point get_data_ma --runtime python39 --trigger-topic get_data_ma --memory 512MB --timeout 120 --env-vars-file get_data_ma/env.yaml
    ```

3. If you want your function to run periodically, then you can create a [Cloud Scheduler](https://cloud.google.com/scheduler/docs/creating#gcloud) cron job:

    ```shell
    gcloud scheduler jobs create pubsub get_data_ma --schedule "20 4,16 * * *" --topic get_data_ma --message-body "success"
    ```

    > Note: You can substitute `create` in step 3 with `update` to update your scheduled job.

Your function is now published. You can read the logs for your function with:

```shell
gcloud functions logs read get_data_ma
```

> Note: If your function encounters a `PERMISSION_DENIED` error, then make sure that [the service account being used has sufficient permissions](https://stackoverflow.com/a/58646481/5021266).

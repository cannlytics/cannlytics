# CannBot


## Schedule CannBot

You will need to create an `env.yaml` file in the `get_youtube_video_views` folder with the following environment variable.

```yaml
OPENAI_API_KEY: your-openai-api-key
```

Automating the CannBot research agent can be done with the following 3 steps.

1. Create a Pub/Sub topic:

    ```shell
    gcloud pubsub topics create cannbot
    ```

2. Deploy the function:

    ```shell
    gcloud functions deploy cannbot --source cannbot --entry-point cannbot --runtime python39 --trigger-topic cannbot --memory 512MB --timeout 120 --env-vars-file cannbot/env.yaml
    ```

3. Finally, create a [Cloud Scheduler](https://cloud.google.com/scheduler/docs/creating#gcloud) cron job:

    ```shell
    gcloud scheduler jobs create pubsub cannbot --schedule "15 * * * *" --topic cannbot --message-body "success"
    ```

CannBot should now run every 15 minutes. You can read the logs for your function with:

```shell
gcloud functions logs read cannbot
```

You can substitute `create` in step 3 with `update` to update your scheduled job.

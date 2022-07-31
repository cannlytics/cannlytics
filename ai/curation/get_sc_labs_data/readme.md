# Get SC Labs Data

Archive SC Labs test results.

## Automation

Automating the collection of lab results can be done with the following 3 steps.

1. Create a Pub/Sub topic:

    ```shell
    gcloud pubsub topics create get_sc_labs_data
    ```

2. Deploy the function (from the `ai/curation` directory):

    ```shell
    gcloud functions deploy get_sc_labs_data --source get_sc_labs_data --entry-point get_sc_labs_data --runtime python39 --trigger-topic get_sc_labs_data --memory 512MB --timeout 120
    ```

3. Finally, create a [Cloud Scheduler](https://cloud.google.com/scheduler/docs/creating#gcloud) cron job:

    ```shell
    gcloud scheduler jobs create pubsub get_sc_labs_data --schedule "20 16 * * *" --topic get_sc_labs_data --message-body "success"
    ```

Your function should now run periodically. You can read the logs for your function with:

```shell
gcloud functions logs read get_sc_labs_data
```

You can substitute `create` in step 3 with `update` to update your scheduled job.

> Note: If you encounter a `PERMISSION_DENIED` error, then make sure that [the service account being used has sufficient permissions](https://stackoverflow.com/a/58646481/5021266).

## Resources

- [SC Labs Test Results](https://client.sclabs.com/)
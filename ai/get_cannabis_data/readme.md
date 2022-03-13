# Get Cannabis Data - Daily

This routine gets cannabis data that needs to be collected daily. Currently, the routine collects the following data:

- [Connecticut product data](#ct)
- [Oklahoma licensee data](#ok)

## Deployment

1. Create a Pub/Sub topic:

    ```
    gcloud pubsub topics create get_cannabis_data_daily
    ```

2. Deploy the function:

    ```
    gcloud functions deploy get_cannabis_data_daily --entry-point get_cannabis_data_daily --runtime python39 --trigger-topic get_cannabis_data_daily --memory 1024MB --timeout 300 --env-vars-file env.yaml
    ```

3. Finally, create a [Cloud Scheduler](https://cloud.google.com/scheduler/docs/creating#gcloud) cron job:

    ```
    gcloud scheduler jobs create pubsub get_cannabis_data_daily --schedule "20 4 * * *" --topic get_cannabis_data_daily --message-body "success"
    ```

Your function should now run nicely everyday at 4:20am EDT. You can read the logs for your function with:

```
gcloud functions logs read get_cannabis_data_daily
```

## Connecticut product data <a name="ct"></a>


## Oklahoma licensee data <a name="ok"></a>

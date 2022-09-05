# Get Raw Garden Lab Result Data

Archive Raw Garden test result data.

## Historic Data Curation

If you wish to populate your database with all of Raw Garden's historic lab results, then you can run the full archival routine. The routine will create datafiles for archiving and upload the data to Firestore.

```shell
python ai/curation/get_rawgarden_data/get_all_rawgarden_data.py
```

## Automation

Automating the collection of lab results can be done with the following 3 steps.

1. Create a Pub/Sub topic:

    ```shell
    gcloud pubsub topics create get_rawgarden_data
    ```

2. Deploy the function (from the root directory):

    ```shell
    gcloud functions deploy get_rawgarden_data --source ai/curation/get_rawgarden_data --entry-point get_rawgarden_data --runtime python39 --trigger-topic get_rawgarden_data --memory 1024MB --timeout 252
    ```

3. Finally, create a [Cloud Scheduler](https://cloud.google.com/scheduler/docs/creating#gcloud) cron job:

    ```shell
    gcloud scheduler jobs create pubsub get_rawgarden_data --schedule "20 16 * * *" --topic get_rawgarden_data --message-body "success"
    ```

Your function should now run periodically. You can read the logs for your function with:

```shell
gcloud functions logs read get_rawgarden_data
```

You can substitute `create` in step 3 with `update` to update your scheduled job.

> Note: If you encounter a `PERMISSION_DENIED` error, then make sure that [the service account being used has sufficient permissions](https://stackoverflow.com/a/58646481/5021266).

## References

**Data Sources**

- [Raw Garden Lab Results](https://rawgarden.farm/lab-results/)

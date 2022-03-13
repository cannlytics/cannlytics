# Data Collection | Public State Data

Cannlytics strives to be the go-to source of public cannabis data. Cannlytics wishes to use our comparative advantage in aggregating data from disparate resources and provide you with a simple, standardized interface to consume the data.

| State | Abbreviation | Cannabis Data | Data Collection Routine |
|-------|--------------|---------------|-------------------------|
|  Alabama |  AL  | No |  |
|  [Alaska](./data-collection-ak.md) |  AK  | Yes | In progress |
|  [Arizona](./data-collection-az.md) |  AZ  | Yes | In progress |
|  Arkansas |  AR  | No |  |
|  [California](./data-collection-ca.md) |  CA  | Yes | In progress |
|  [Colorado](./data-collection-co.md) |  CO  | Yes | In progress |
|  [Connecticut](./data-collection-ct.md) |  CT  | Yes | In progress |
|  Delaware |  DE  | ? |  |
|  District of Columbia |  DC  | Maybe |  |
|  [Florida](./data-collection-fl.md) |  FL  | ? |  |
|  Georgia |  GA  | Maybe |  |
|  Hawaii |  HI  | Maybe |  |
|  Idaho |  ID  | No |  |
|  [Illinois](./data-collection-il.md) |  IL  | Yes | In progress |
|  Indiana |  IN  | No |  |
|  Iowa |  IA  | No |  |
|  Kansas |  KS  | No |  |
|  Kentucky |  KY  | Maybe |  |
|  [Louisiana](./data-collection-la.md) |  LA  | Maybe |  |
|  [Maine](./data-collection-me.md) |  ME  | Yes | In progress |
|  [Maryland](./data-collection-md.md) |  MD  | Yes | In progress |
|  [Massachusetts](./data-collection-ma.md) |  MA  | Yes | In progress |
|  [Michigan](./data-collection-mi.md) |  MI  | Yes | In progress |
|  Minnesota |  MN  | No |  |
|  Mississippi |  MS  | No |  |
|  Missouri |  MO  | No |  |
|  [Montana](./data-collection-mt.md) |  MT  | Yes | In progress |
|  Nebraska |  NE  | No |  |
|  [Nevada](./data-collection-nv.md) |  NV  | Yes | In progress |
|  New Hampshire |  NH  | Maybe |  |
|  New Jersey |  NJ  | Maybe |  |
|  New Mexico |  NM  | Maybe |  |
|  New York |  NY  | Maybe |  |
|  North Carolina |  NC  | No |  |
|  North Dakota |  ND  | No |  |
|  [Ohio](./data-collection-oh.md) |  OH  | Maybe |  |
|  [Oklahoma](./data-collection-ok.md) |  OK  | Yes | In progress |
|  [Oregon](./data-collection-or.md) |  OR  | Yes | In progress |
|  Pennsylvania |  PA  | No |  |
|  Puerto Rico |  PR  | Maybe |  |
|  Rhode Island |  RI  | Maybe |  |
|  South Carolina |  SC  | No |  |
|  South Dakota |  SD  | No |  |
|  Tennessee |  TN  | No |  |
|  Texas |  TX  | No |  |
|  Utah |  UT  | No |  |
|  Vermont |  VT  | Maybe |  |
|  Virginia |  VA  | Maybe |  |
|  [Washington](./data-collection-wa.md) |  WA  | Maybe | In progress |
|  West Virginia |  WV  | Maybe |  |
|  Wisconsin |  WI  | No |  |
|  Wyoming |  WY  | No |  |

## Get Cannabis Data - Daily

This routine gets cannabis data that needs to be collected daily. Currently, the routine collects the following data:

- [Connecticut product data](#ct)
- [Oklahoma licensee data](#ok)

### Deployment

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

<!-- ## Connecticut product data <a name="ct"></a>


## Oklahoma licensee data <a name="ok"></a> -->


<div align="center" style="text-align:center; margin-top:1rem; margin-bottom: 1rem;">
  <img width="240px" alt="" src="https://firebasestorage.googleapis.com/v0/b/cannlytics.appspot.com/o/public%2Fimages%2Flogos%2Fcannlytics_ai_with_text.png?alt=media&token=78d19117-eff5-4f45-a8fa-3bbdabd6917d">
  <div style="margin-bottom:1rem;">
    <h3>Cannabis + Analytics + AI</h3>
  </div>

[![contributions welcome](https://img.shields.io/badge/contributions-welcome-brightgreen.svg?style=flat)](https://github.com/dwyl/esta/issues)

<https://cannlytics.com/ai>

> [Kreuzberger et. al](https://doi.org/10.48550/arXiv.2205.02302) stipulate, *"The final goal of all industrial machine learning (ML) projects is to develop ML products and rapidly bring them into production."* Cannlytics AI is no exception. The aim of Cannlytics AI is to develop and implement fully-functioning machine learning products for people in the cannabis space to use and interact with.

</div>

<!-- 1. Properly version and share AI models, code, and datasets. -->
<!-- 2. Data should be readily sharable through the Cannlytics API. -->
<!-- 3. Processes should be pluggable, so AI pipelines can be crafted by users. -->
<!-- 4. Models should be able to handle large, very large, datasets. -->

🔥 Cannlytics AI is an artificial intelligence that strives to be the go-to source of **cannabis data**. Cannlytics AI leverages her comparative advantage in aggregating cannabis data from disparate resources to provide you with clean, standardized, readily-accessible cannabis data. Cannlytics AI, without mistake, flaw, or complaint, provides you with a rich buffet of cannabis data. Bon appétit!

- [🧑‍💻 Data](#data)
- [🏃‍♀️ Quickstart](#quickstart)
- [🪛 Development](#development)
- [🦾 Automation](#automation)

## 🧑‍💻 Data <a name="name"></a>

The status for data and statistics by state is as follows.

| Status |  |
|--------|--|
| Priority | 🔴 |
| Started | 🟡 |
| Live | 🟢 |
| No Data | ⚪ |

| State | Adult Use / Medical | Cannabis Data | Data Collection |
|-------|--------------|---------------|-------------------------|
|  Alabama (AL) |  No / No  | No | ⚪ |
|  [Alaska](./functions/get_data_ak/readme.md) (AK) |   | Yes | 🟡 |
|  [Arizona](./functions/get_data_az/readme.md) (AZ) |    | Yes | 🟡 |
|  Arkansas (AR) | No / Yes | No | ⚪ |
|  [California](./functions/get_data_ca/readme.md) (CA) |   | Yes | 🟡 |
|  [Colorado](./functions/get_data_co/readme.md) (CO) |   | Yes | 🟡 |
|  [Connecticut](./functions/get_data_ct/readme.md) (CT) |   | Yes | 🟡 |
|  Delaware (DE) | No / Yes | No | ⚪ |
|  District of Columbia (DC) |    | Maybe | 🔴 |
|  [Florida](./functions/get_data_fl/readme.md) (FL) |   | ? | 🔴 |
|  Georgia (GA) |   | Maybe | 🔴 |
|  Hawaii (HI) |   | Maybe | 🔴 |
|  Idaho (ID) |   | No | ⚪ |
|  [Illinois](./functions/get_data_il/readme.md) (IL) |   | Yes | 🟡 |
|  Indiana (IN) |   | No | ⚪ |
|  Iowa (IA) |   | No | ⚪ |
|  Kansas (KS) |   | No | ⚪ |
|  Kentucky (KY) |   | Maybe | 🔴 |
|  [Louisiana](./functions/get_data_la/readme.md) (LA) |   | Maybe | 🔴 |
|  [Maine](./functions/get_data_me/readme.md) (ME) |   | Yes | 🟡 |
|  [Maryland](./functions/get_data_md/readme.md) (MD) |   | Yes | 🟡 |
|  [Massachusetts](./functions/get_data_ma/readme.md) (MA) |   | Yes | 🟡 |
|  [Michigan](./functions/get_data_mi/readme.md) (MI) |   | Yes | 🟡 |
|  Minnesota (MN) |   | No | ⚪ |
|  Mississippi (MS) |   | No | ⚪ |
|  Missouri (MO) |   | No | ⚪ |
|  [Montana](./functions/get_data_mt/readme.md) (MT) |   | Yes | 🟡 |
|  Nebraska (NE) |   | No | ⚪ |
|  [Nevada](./functions/get_data_nv/readme.md) (NV) |   | Yes | 🟡 |
|  New Hampshire (NH) |    | Maybe | 🔴 |
|  New Jersey (NJ) |   | Maybe | 🔴 |
|  New Mexico (NM) |   | Maybe | 🔴 |
|  New York (NY) |   | Maybe | 🔴 |
|  North Carolina (NC) |   | No | ⚪ |
|  North Dakota (ND) |   | No | ⚪ |
|  [Ohio](./functions/get_data_oh/readme.md) (OH) |  | Maybe | 🔴 |
|  [Oklahoma](./functions/get_data_ok/readme.md) (OK) |   | Yes | 🟡 |
|  [Oregon](./functions/get_data_or/readme.md) (OR) |   | Yes | 🟡 |
|  Pennsylvania (PA) |   | No | ⚪ |
|  Puerto Rico (PR) |   | Maybe | 🔴 |
|  Rhode Island (RI) |   | Maybe | 🔴 |
|  South Carolina (SC) |   | No | ⚪ |
|  South Dakota (SD) |   | No | ⚪ |
|  Tennessee (TN) |   | No | ⚪ |
|  Texas (TX) |   | No | ⚪ |
|  Utah (UT) |   | No | ⚪ |
|  Vermont (VT) |   | Maybe | 🔴 |
|  Virginia (VA) |   | Maybe | 🔴 |
|  [Washington](./functions/get_data_wa/readme.md) (WA) |   | Maybe | 🟡 |
|  West Virginia (WV) |   | Maybe | 🔴 |
|  Wisconsin (WI) |   | No | ⚪ |
|  Wyoming (WY) |   | No | ⚪ |

National statistics are also available.

| State | Adult Use / Medical | Cannabis Data | Data Collection |
|-------|--------------|---------------|-------------------------|
| USA |  No / No  | Yes | 🟡 |
| Canada |  Yes / Yes  | Yes | 🟡 |


## 🏃‍♀️ Quickstart <a name="quickstart"></a>

You can simply clone the repository to get your hands on the AI source code.

```shell
git clone https://github.com/cannlytics/cannlytics.git
```

For various functions, you will need to create an `env.yaml` in the functions folder and include environment variables as needed:

| Environment Variable | Credential Source |
|----------------------|-------------------|
| `FRED_API_KEY` | <http://research.stlouisfed.org/fred2/> |
| `SOCRATA_APP_TOKEN` | [Socrata Application Token](https://dev.socrata.com/docs/app-tokens.html) |

You can also use each function through the command line. For example, you can collect data for Massachusetts with:

```shell
python ai/functions/get_data_ma/main.py
```

## 🪛 Development <a name="development"></a>

Contributions are strongly encouraged. If you know how a new data source can be collected, then please feel free to contribute your knowledge. Please see the data collection [functions](./functions/readme.md) for information on how public data is collected. You can jump right in developing a data collection routine for your favorite state, a state where there is a high demand for data, a state that needs a data collection routine, or a data collection routine that needs improvement. Thank you a million for your contributions!

## 🦾 Automation <a name="automation"></a>

Now for the fun part, automation. Automation is needed for machine learning programs to be reliably operationalized and brought into production.

These automation routines leverage the [Google Cloud Platform](https://cloud.google.com/) and require enabling [billing](http://console.cloud.google.com/billing/?_ga=2.91797530.1059044588.1636848277-147951098.1631325967), [the Cloud Scheduler API](http://console.cloud.google.com/apis/library/cloudscheduler.googleapis.com?_ga=2.121230088.1059044588.1636848277-147951098.1631325967), and [the Pub/Sub API](http://console.cloud.google.com/apis/library/pubsub.googleapis.com?_ga=2.121230088.1059044588.1636848277-147951098.1631325967). The 3 steps to publish a function, e.g. `get_data_ma`, are:

1. Create a Pub/Sub topic:

    ```
    gcloud pubsub topics create get_data_ma
    ```

2. Deploy the function:

    ```
    gcloud functions deploy get_data_ma --entry-point get_data_ma --runtime python39 --trigger-topic get_data_ma --memory 1024MB --timeout 300 --env-vars-file env.yaml
    ```

3. Finally, create a [Cloud Scheduler](https://cloud.google.com/scheduler/docs/creating#gcloud) cron job. Here the function runs at 4:20am and 4:20pm, but you can pick any [schedule](https://cloud.google.com/scheduler/docs/configuring/cron-job-schedules):

    ```
    gcloud scheduler jobs create pubsub get_data_ma --schedule "20 4/16 * * *" --topic get_data_ma --message-body "success"
    ```

Your function should now run nicely for perpetuity. You can read the logs for your function with:

```
gcloud functions logs read get_data_ma
```

<!-- ## 👩‍🔬 Testing <a name="testing"></a>

You can run tests with code coverage with `pytest`.

```
pytest --cov=ai tests/
``` -->

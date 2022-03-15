<div align="center" style="text-align:center; margin-top:1rem; margin-bottom: 1rem;">
  <img style="max-width:420px" width="420px" alt="" src="https://firebasestorage.googleapis.com/v0/b/cannlytics.appspot.com/o/public%2Fimages%2Flogos%2Fcannlytics_ai_with_text.png?alt=media&token=78d19117-eff5-4f45-a8fa-3bbdabd6917d">
  <div style="margin-top:0.5rem; margin-bottom:1rem;">
    <h3>Simple, easy, cannabis analytics.</h3>
  </div>

[![License: MIT](https://img.shields.io/badge/License-MIT-brightgreen.svg)](https://opensource.org/licenses/MIT)
[![Coverage Status](https://coveralls.io/repos/github/cannlytics/cannlytics-ai/badge.svg?branch=main)](https://coveralls.io/github/cannlytics/cannlytics-ai?branch=main)
[![contributions welcome](https://img.shields.io/badge/contributions-welcome-brightgreen.svg?style=flat)](https://github.com/dwyl/esta/issues)
[![Maintainability](https://api.codeclimate.com/v1/badges/26b6ae8411a22b373639/maintainability)](https://codeclimate.com/github/cannlytics/cannlytics-ai/maintainability)

<https://cannlytics.com/ai>

</div>

<!-- 1. Properly version and share AI models, code, and datasets. -->
<!-- 2. Data should be readily sharable through the Cannlytics API. -->
<!-- 3. Processes should be pluggable, so AI pipelines can be crafted by users. -->
<!-- 4. Models should be able to handle large, very large, datasets. -->

🔥 Cannlytics AI is artificial intelligence, powered by Cannlytics, that strives to be the go-to source of public cannabis data. Cannlytics AI leverages the comparative advantage of Cannlytics in aggregating cannabis data from disparate resources to provide you with clean, standardized data. Cannlytics AI provides you with a rich buffet of cannabis data, automatically, without mistakes, flaws, or complaint.

- [🌱 Installation](#installation)
- [🏃‍♀️ Quickstart](#quickstart)
- [🔨 Development](#development)
- [🦾 Automation](#automation)
- [👩‍🔬 Testing](#testing)
- [❤️ Support](#support)
- [🏛️ License](#license)

Currently, data is available in the following states. Contributions are greatly welcome. If you know how a new data source can be collected, then please feel free to contribute your knowledge.

| State | Abbreviation | Cannabis Data | Data Collection Routine |
|-------|--------------|---------------|-------------------------|
|  Alabama |  AL  | No |  |
|  [Alaska](./guides/data-collection-ak.md) |  AK  | Yes | In progress |
|  [Arizona](./guides/data-collection-az.md) |  AZ  | Yes | In progress |
|  Arkansas |  AR  | No |  |
|  [California](./guides/data-collection-ca.md) |  CA  | Yes | In progress |
|  [Colorado](./guides/data-collection-co.md) |  CO  | Yes | In progress |
|  [Connecticut](./guides/data-collection-ct.md) |  CT  | Yes | In progress |
|  Delaware |  DE  | ? |  |
|  District of Columbia |  DC  | Maybe |  |
|  [Florida](./guides/data-collection-fl.md) |  FL  | ? |  |
|  Georgia |  GA  | Maybe |  |
|  Hawaii |  HI  | Maybe |  |
|  Idaho |  ID  | No |  |
|  [Illinois](./guides/data-collection-il.md) |  IL  | Yes | In progress |
|  Indiana |  IN  | No |  |
|  Iowa |  IA  | No |  |
|  Kansas |  KS  | No |  |
|  Kentucky |  KY  | Maybe |  |
|  [Louisiana](./guides/data-collection-la.md) |  LA  | Maybe |  |
|  [Maine](./guides/data-collection-me.md) |  ME  | Yes | In progress |
|  [Maryland](./guides/data-collection-md.md) |  MD  | Yes | In progress |
|  [Massachusetts](./guides/data-collection-ma.md) |  MA  | Yes | In progress |
|  [Michigan](./guides/data-collection-mi.md) |  MI  | Yes | In progress |
|  Minnesota |  MN  | No |  |
|  Mississippi |  MS  | No |  |
|  Missouri |  MO  | No |  |
|  [Montana](./guides/data-collection-mt.md) |  MT  | Yes | In progress |
|  Nebraska |  NE  | No |  |
|  [Nevada](./guides/data-collection-nv.md) |  NV  | Yes | In progress |
|  New Hampshire |  NH  | Maybe |  |
|  New Jersey |  NJ  | Maybe |  |
|  New Mexico |  NM  | Maybe |  |
|  New York |  NY  | Maybe |  |
|  North Carolina |  NC  | No |  |
|  North Dakota |  ND  | No |  |
|  [Ohio](./guides/data-collection-oh.md) |  OH  | Maybe |  |
|  [Oklahoma](./guides/data-collection-ok.md) |  OK  | Yes | In progress |
|  [Oregon](./guides/data-collection-or.md) |  OR  | Yes | In progress |
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
|  [Washington](./guides/data-collection-wa.md) |  WA  | Maybe | In progress |
|  West Virginia |  WV  | Maybe |  |
|  Wisconsin |  WI  | No |  |
|  Wyoming |  WY  | No |  |

## 🌱 Installation <a name="installation"></a>

You can simply clone the repository to get your hands on the AI source code.

```shell
git clone https://github.com/cannlytics/cannlytics-ai.git
```

You will also need to create and save the following credentials in your `env.yaml`.

- `FRED_API_KEY`: You can sign up for a free API key at <http://research.stlouisfed.org/fred2/>.
- `SOCRATA_APP_TOKEN`: You will need a [Socrata Application Token](https://dev.socrata.com/docs/app-tokens.html) to collect data from certain states, such as Massachusetts and Connecticut.

## 🏃‍♀️ Quickstart <a name="quickstart"></a>

You can run each data collection routine through the command line. For example:

```shell
python ai/get_cannabis_data/get_data_ma.py
```

## 🔨 Development <a name="development"></a>

Please see the [data collection guides](guides/data/data-collection.md) for information on how public data is collected.

## 🦾 Automation <a name="automation"></a>

Now for the fun part, automation.

> Note that you will need to [enable billing for your project](http://console.cloud.google.com/billing/?_ga=2.91797530.1059044588.1636848277-147951098.1631325967), [enable the Cloud Scheduler API](http://console.cloud.google.com/apis/library/cloudscheduler.googleapis.com?_ga=2.121230088.1059044588.1636848277-147951098.1631325967), and [enable the Pub/Sub API](http://console.cloud.google.com/apis/library/pubsub.googleapis.com?_ga=2.121230088.1059044588.1636848277-147951098.1631325967).

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

Your function should now run nicely everyday at 4:20am. You can read the logs for your function with:

```
gcloud functions logs read get_cannabis_data_daily
```

## 👩‍🔬 Testing <a name="testing"></a>

You can run tests with code coverage with `pytest`.

```
pytest --cov=ai tests/
```

## ❤️ Support <a name="support"></a>

Cannlytics is made available with ❤️ and <a href="https://opencollective.com/cannlytics-company">your good will</a>. Please consider making a contribution to keep the good work coming 🚢 Thank you 🙏

🥞 Bitcoin donation address: 34CoUcAFprRnLnDTHt6FKMjZyvKvQHb6c6

## 🏛️ License <a name="license"></a>

```
Copyright (c) 2021 Cannlytics and Cannlytics Contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

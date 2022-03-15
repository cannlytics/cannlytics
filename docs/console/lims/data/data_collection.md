# Data Collection

Below are example steps of how you could begin uploading your instrument data automatically.

1. First, create a directory, e.g. `C:\Cannlytics\data`, where all of your instrument data will live.

2. Next, download the sample data files into your directory, in this case `C:\Cannlytics\data`, so you have analysis plus instrument specific directories, such as `C:\Cannlytics\data\agilent_gc_residual_solvents`.

3. Open a command prompt and cd to where you want your Cannlytics code to live. Download the latest version of Cannlytics with Git:

```shell
git clone https://github.com/cannlytics/cannlytics.git
```

4. Create a `.env` file in the root of your cannlytics directory with the following variables:

```
CANNLYTICS_ORGANIZATION_ID=test-company
CANNLYTICS_API_KEY=DsXzsDbbp2RpEJWUErgnxuXk-lb1tU-pXc4IFkzzsRQuqvN9bqM7Bd9MuQGntIfO
```

Note that this is an API key for the following account. It is not the best practice to share an API key in this manner, so, please just use this key for development and consider creating a new account and getting a new API key for production.

5. Run the following command and reap your results.

```shell
python cannlytics/lims/instruments.py
```

You can also pass arguments to specify the organization, minutes ago restriction, and .env file location. A complete example is:

```shell
python cannlytics/lims/instruments.py --org=test-company --modifed=60 --env=prod.env
```

6. You can then use the user interface to manage your results, measurements, and instruments. You can also manage the analyses and analytes too.

Email: test@cannlytics.com

Password: dontpanic

**Bonus**) You could also accomplish this by installing the Cannlytics Python module:

```shell
pip install cannlytics==0.0.8
```

And creating your own Python script:

```py
from cannlytics import lims
measurements = lims.instruments.automatic_collection(
        org_id='test-company,
        env_file='../../../.env',
        minutes_ago=None
    )
```

Once you have run the import routine, then you can create a CRON job in a number of ways. Here are several good guides that can get you up and running (without hands).

- StackOverflow
- Tutorial
- Linux Guide

This is simply a proof of concept that your results can be automatically imported into clean JSON. The data is then ripe for creating CoAs.

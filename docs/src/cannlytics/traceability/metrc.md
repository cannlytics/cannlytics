# Metrc

## Permissions

Employee permissions include:

Administration – Provides the capability to perform all administrative functions,
including ordering tags, setting up strains, locations, and items, and adding
employees (it is recommended that the number of users granted administrative
permissions be limited).

Plants – Provides the capability to create plantings, move plants, change growth
phase, log waste, and create harvests in Metrc.

Packages – Provides the capability to create, adjust, and re-package packages into
smaller or larger quantities, as well as create packages of production batches.

Transfers – Provides the capability to create, modify, void, and receive/reject
transfers.

Transfer Hub – Provides the capability to view a manifest, edit transporter
information, and record actual departure, arrival, layover check-in, and layover
check-out dates/times.

Sales – Provides the capability to input sales data or initiate sales uploads.

Reports – Provides the capability to generate pre-defined reports.

## Initializing the Metrc Client

Here is an example of how to initialize a Metrc API client with the `dotenv` module.

```py
from dotenv import dotenv_values

# Initialize Metrc client.
config = dotenv_values('.env')
vendor_api_key = config['METRC_TEST_VENDOR_API_KEY']
user_api_key = config['METRC_TEST_USER_API_KEY']
track = metrc.authorize(vendor_api_key, user_api_key)
```

The client is powerful and capable of performing all actions. Models with certain convenience actions implemented are returned by `GET` requests or are initialized from JSON as an argument to the class or with a `create_from_json` method. The `create_from_json` method also creates a record in Metrc. 

::: cannlytics.traceability.metrc
    rendering:
      show_root_toc_entry: true
      show_root_heading: true
      show_source: true
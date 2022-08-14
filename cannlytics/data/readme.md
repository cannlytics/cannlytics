# Cannlytics Data Module

The `cannlytics.data` module is a large toolbox for accessing, collecting, cleaning, augmenting, standardizing, saving, and analyzing cannabis data.

## Core Data Functions

The core data manipulation tools are found in `cannlytics.data.data`.

*Data Aggregation*

| Function | Description |
|----------|-------------|
| `aggregate_datasets(directory, on='sample_id', how='left', replace='right', reverse=True, concat=False)` | Aggregate datasets. Leverages `rmerge` to combine each dataset in the given directory. |

*Data Cleaning*

| Function | Description |
|----------|-------------|
| `find_first_value(string, breakpoints=None)` | Find the first value of a string, be it a digit, a 'ND', '<', or other specified breakpoints.  |
| `parse_data_block(div, tag='span')` | Parse an HTML data block into a dictionary. |

*Data Augmentation*

| Function | Description |
|----------|-------------|
| `create_sample_id(private_key, public_key, salt='')` | Create a hash to be used as a sample ID. The standard is to use: 1. `private_key = producer` 2. `public_key = product_name` 3. `salt = date_tested` |

*Data Saving*

| Function | Description |
|----------|-------------|
| `write_to_worksheet(ws, values)` | Write data to an Excel Worksheet. |

<!-- TODO: Examples -->

## Figures

| Function | Description |
|----------|-------------|
| `crispy_barchart(df, annotations=False, key=0, fig_size=(5, 3.5), font_family='serif', font_style='Times NEw Roman', text_color='#333F4B', notes='', notes_offset=.15, palette=None, percentage=False, title='', save='', x_label=None, y_label=None, y_ticks=None, zero_bound=False,)` | Create a beautiful bar chart given data. |
| `crispy_scatterplot(data, x, y, category_key, categories, colors, label_size=20, legend_loc='upper left', notes='', notes_offset=.15, note_size=14, percentage=False, save='', title='', title_size=24, font_size=18, fig_size=(15, 7.5), font_family='serif', font_style='Times New Roman', text_color='#333F4B',)` | Create a beautiful scatter plot given data. |

<!-- TODO: Examples -->

## Flower Art

You can programmatically create cannabis flower art using image data with the `cannlytics.data.flower_art` submodule.

```py
# Import Flower Art
from cannlytics.data.flower_art import FlowerArt

# Create an art AI client.
art = FlowerArt(
    line_size=7,
    blur_value=7,
    number_of_filters=10,
    total_colors=50,
    sigmaColor=50,
    sigmaSpace=50,
)

# Create a strain NFT.
art.cartoonize_image('model.jpg', 'strain-nft.jpg')
```

## GIS Data

There are a number of geographic information system tools in `cannlytics.data.gis`. The tools primarily leverage Google Maps and expect a [Google Maps API Key](https://developers.google.com/maps/documentation/javascript/get-api-key).

| Function | Description |
|----------|-------------|
| `get_state_population(state, api_key, district='', obs_start=None, obs_end=None, multiplier=1000)` | Get a given state's latest population from the Fed Fred API, getting the number in 1000's and returning the absolute value. |
| `geocode_addresses(data, api_key=None, pause=0.0, address_field='')` | Geocode addresses in a dataframe. |
| `search_for_address(query, api_key=None, fields=None)` | Search for the address of a given name. |
|

<!-- TODO: Examples -->

## Cannabis OpenData

The `cannlytics.data.opendata` submodule contains a `OpenData` class. An instance of the `OpenData` class communicates with the [Cannabis Control Commission of the Commonwealth of Massachusetts' Open Data catalog](https://masscannabiscontrol.com/open-data/data-catalog/).

| Method | Description |
|----------|-------------|
| `get_agents(dataset='gender-stats')` | Get agent statistics. Datasets: `gender-stats`, `ethnicity-stats` |
| `get_licensees(dataset='', limit=10_000, order_by='app_create_date', ascending=False)` | Get Massachusetts licensee data and statistics. Datasets: `approved`, `pending`, `demographics`, `under-review-stats`, `application-stats` |
| `get_retail(dataset='sales-stats', limit=10_000, order_by='date', ascending=False)` | Get Massachusetts retail data and statistics. Datasets: `sales-stats`, `sales-weekly`, `price-per-ounce` |
| `get_medical(dataset='stats')` | Get Massachusetts medical stats. |
| `get_plants(limit=10_000, order_by='activitysummarydate', ascending=False)` | Get Massachusetts cultivation data and statistics. |
| `get_sales(limit=10_000, order_by='activitysummarydate', ascending=False)` | Get Massachusetts sales data. |

*Examples*

```py
from cannlytics.data.opendata import OpenData

# Create an OpenData instance.
ccc = OpenData()

# Get data!
licensees = ccc.get_licensees()
retail = ccc.get_retail()
plants = ccc.get_plants()
sales = ccc.get_sales()
```

<!--
- TODO: Create a data guide.
- FIXME: SQL queries do not appear to work.
-->

## Cannabis Patent Data

With the `cannlytics.data.patents` submodule you can find and curate data for cannabis patents.

| Function | Description |
|----------|-------------|
| `search_patents(query, limit=50, details=False, pause=None, term='')` | Search for patents. |
| `get_patent_details(data=None, patent_number=None, patent_url=None, user_agent=None, fields=None, search_field='patentNumber', search_fields='patentNumber', query='patentNumber',)` | Get details for a given patent, given it's patent number and URL. |

*Example*

```py
from cannlytics.data.patents import (
  get_patent_details,
  search_patents,
)

# Search for cannabis plant patents.
patents = search_patents('cannabis cultivar', limit=1000, term='TTL%2F')

# Get patent details.
patent = get_patent_details(
    patent_number='PP34051',
    patent_url='https://patft.uspto.gov/netacgi/nph-Parser?Sect1=PTO2&Sect2=HITOFF&u=%2Fnetahtml%2FPTO%2Fsearch-adv.htm&r=7&f=G&l=50&d=PTXT&p=1&S1=%22marijuana+plant%22&OS=%22marijuana+plant%22&RS=%22marijuana+plant%22',
)
```

## Web Data

There are a number of web data tools in `cannlytics.data.web`.

| Function | Description |
|----------|-------------|
| `format_params(parameters, **kwargs)` | Format given keyword arguments HTTP request parameters. |
| `get_page_metadata(url)` | Get the metadata of a web page |
| `get_page_description(html)` | Get the description of a web page. |
| `get_page_image(html, index=0)` | Get an image on a web page, the first image by default. |
| `get_page_favicon(html, url='')` | Get the favicon from a web page. |
| `get_page_theme_color(html)` | Get the theme color of a web page. |
| `get_page_phone_number(html, response, index=0)` | Get the first phone number on a web page. |
| `get_page_email(html, response)` | Get an email on a web page, the last email by default. |

<!-- TODO: Examples -->

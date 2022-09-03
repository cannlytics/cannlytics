# 🥸 CoADoC | CoA Data Parser

<div align="center" style="text-align:center; margin-top:1rem; margin-bottom: 1rem;">
  <img width="150px" alt="" src="https://firebasestorage.googleapis.com/v0/b/cannlytics.appspot.com/o/public%2Fimages%2Flogos%2Fcannlytics_coa_doc.png?alt=media&token=1871dde9-82db-4342-a29d-d373671491b3">
</div>

Certificates of analysis (CoAs) are abundant for cultivators, processors, retailers, and consumers too, but the data is often locked away. Rich, valuable laboratory data so close, yet so far away! CoADoc puts these vital data points in your hands by parsing PDFs and URLs, finding all the data, standardizing the data, and cleanly returning the data to you.

## Usage

Initialize a `CoADoc` parsing client.

```py
from cannlytics.data.coas import CoADoc

# Initialize a CoA parser.
parser = CoADoc()
```

Parse a PDF.

```py
# Parse a PDF.
filename = 'Classic Jack.pdf'
data = parser.parse_pdf(filename)
```

Parse a URL.

```py
# Parse a URL.
url = 'https://lims.tagleaf.com/coa_/F6LHqs9rk9'
data = parser.parse_url(url)
```

Parse a list or URLs or PDFs, a mix of both is okay.
```py
# Parse a list of CoAs.
data = parser.parse([filename, url])
```

Close the client when you are finished to perform garbage cleaning.

```py
# Close the parser.
parser.quit()
```

## Algorithms

Getting data from CoAs is inevitable and with modern tools, plus a little human ingenuity, we can methodically parse CoAs produced by various labs that test cannabis. All CoAs that are extracted through manually written routines are quite useful because these can then be used for training natural language processing (NLP) models to further extract data!

| Status | | |
|---|---|---|
| 🟠 Development | 🟡 Operational | 🟢 Live |

| Lab / LIMS | Algorithm | Status |
|------------|-----------|--------|
| Anresco Laboratories | `parse_anresco_coa` | 🟢 |
| Cannalysis | `parse_cannalysis_coa` | 🟢 |
| Confident Cannabis | `parse_cc_coa` | 🟢 |
| Green Leaf Lab | `parse_green_leaf_lab_coa` | 🟢 |
| MCR Labs | `parse_mcr_labs_coa` | 🟡 |
| SC Labs | `parse_sc_labs_coa` | 🟢 |
| Sonoma Lab Works | `parse_sonoma_coa` | 🟢 |
| TagLeaf LIMS | `parse_tagleaf_coa` | 🟢 |
| Veda Scientific | `parse_veda_coa` | 🟠 |

## Core Methods

CoADoc comes ready to rumble, but to unleash CoADoc's true power, ensure that you have installed [ChromeDriver](https://chromedriver.chromium.org/downloads) and that CoADoc can find your ChromeDriver in your PATH.

| Function | Description |
|----------|-------------|
| `identify_lims(doc, lims=None)` | Identify if a CoA was created by a common LIMS. Search all of the text of the LIMS name or URL. If no LIMS is identified from the text, then the images are attempted to be decoded, searching for a QR code URL.|
| `parse(data, headers={}, kind='url', lims=None, max_delay=7, persist=True)` | Parse all CoAs given a directory, a list of files, or a list of URLs. |
| `parse_pdf(pdf, headers={}, kind='url', lims=None, max_delay=7, persist=True)` | Parse a CoA PDF. The method searches PDF images, alternating from the first then the last to the middle, for a QR code that decodes to a URL. If a URL is found, then results are attempted to be collected from the web. If no QR code is found or results can't be found on the web, then data is extracted from the PDF. |
| `parse_url(url, headers={}, kind='url', lims=None, max_delay=7, persist=True)` | Parse a CoA URL using web data collection methods. |
| `pdf_ocr(filename, outfile, temp_path='/tmp', resolution=300, cleanup=True)` | Pass a PDF through OCR to recognize its text. Outputs a new PDF. A temporary directory is used, because the algorithm is to: 1. Convert all PDF pages to images. 2. Convert each image to PDF with text. 3. Compile the PDFs with text to a single PDF. The rendered images and individual PDF files are removed by default. |
| `save(data, outfile, codings=None, column_order=None, nuisance_columns=None, numeric_columns=None, standard_analyses=None, standard_analytes=None, standard_fields=None, google_maps_api_key=None)` | Save all CoA data, elongating results and widening values. That is, a Workbook is created with a "Details" worksheet that has all of the raw data, a "Results" worksheet with long-form data where each row is a result for an analyte, and a "Values" worksheet with wide-form data where each row is an observation and each column is the `value` field for each of the `results`. |
| `standardize(data, codings=None, column_order=None, nuisance_columns=None, numeric_columns=None, how='details', details_data=None, results_data=None, standard_analyses=None, standard_analytes=None, standard_fields=None, google_maps_api_key=None)` | Standardize (and normalize) given data. Pass A `google_maps_api_key` to supplement addresses with latitude and longitude. Specify `column_order` as a list of columns in desired order. Specify `nuisance_columns` as a list of column suffixes to remove. Specify `numeric_columns` as a list of columns to apply codings and convert to numeric values. Specify `how` for a simple clean of the data `details` by default. Alternatively specify `wide` for a wide-form DataFrame of values or `long` for a long-form DataFrame of results. Specify `standard_analyses`, `standard_analytes`, `standard_fields` to use custom standardization mappings.|
| `quit()` | Close any driver, end any session, and reset the parameters. |

## Common CoA Data Points

Below is a non-exhaustive list of fields, used to standardize the various data that are encountered, that you may expect to be returned from the parsing of a CoA.

| Field | Example| Description |
|-------|-----|-------------|
| `analyses` | ["cannabinoids"] | A list of analyses performed on a given sample. |
| `{analysis}_method` | "HPLC" | The method used for each analysis. |
| `{analysis}_status` | "pass" | The pass, fail, or N/A status for pass / fail analyses.   |
| `coa_urls` | [{"url": "", "filename": ""}] | A list of certificate of analysis (CoA) URLs. |
| `date_collected` | 2022-04-20T04:20 | An ISO-formatted time when the sample was collected. |
| `date_tested` | 2022-04-20T16:20 | An ISO-formatted time when the sample was tested. |
| `date_received` | 2022-04-20T12:20 | An ISO-formatted time when the sample was received. |
| `distributor` | "Your Favorite Dispo" | The name of the product distributor, if applicable. |
| `distributor_address` | "Under the Bridge, SF, CA 55555" | The distributor address, if applicable. |
| `distributor_street` | "Under the Bridge" | The distributor street, if applicable. |
| `distributor_city` | "SF" | The distributor city, if applicable. |
| `distributor_state` | "CA" | The distributor state, if applicable. |
| `distributor_zipcode` | "55555" | The distributor zip code, if applicable. |
| `distributor_license_number` | "L2Stat" | The distributor license number, if applicable. |
| `images` | [{"url": "", "filename": ""}] | A list of image URLs for the sample. |
| `lab_results_url` | "https://cannlytics.com/results" | A URL to the sample results online. |
| `producer` | "Grow Tent" | The producer of the sampled product. |
| `producer_address` | "3rd & Army, SF, CA 55555" | The producer's address. |
| `producer_street` | "3rd & Army" | The producer's street. |
| `producer_city` | "SF" | The producer's city. |
| `producer_state` | "CA" | The producer's state. |
| `producer_zipcode` | "55555" | The producer's zipcode. |
| `producer_license_number` | "L2Calc" | The producer's license number. |
| `product_name` | "Blue Rhino Pre-Roll" | The name of the product. |
| `lab_id` | "Sample-0001" | A lab-specific ID for the sample. |
| `product_type` | "flower" | The type of product. |
| `batch_number` | "Order-0001" | A batch number for the sample or product. |
| `metrc_ids` | ["1A4060300002199000003445"] | A list of relevant Metrc IDs. |
| `metrc_lab_id` | "1A4060300002199000003445" | The Metrc ID associated with the lab sample. |
| `metrc_source_id` | "1A4060300002199000003445" | The Metrc ID associated with the sampled product. |
| `product_size` | 2000 | The size of the product in milligrams. |
| `serving_size` | 1000 | An estimated serving size in milligrams. |
| `servings_per_package` | 2 | The number of servings per package. |
| `sample_weight` | 1 | The weight of the product sample in grams. |
| `results` | [{...},...] | A list of results, see below for result-specific fields. |
| `status` | "pass" | The overall pass / fail status for all contaminant screening analyses. |
| `total_cannabinoids` | 14.20 | The analytical total of all cannabinoids measured. |
| `total_thc` | 14.00 | The analytical total of THC and THCA. |
| `total_cbd` | 0.20 | The analytical total of CBD and CBDA. |
| `total_terpenes` | 0.42 | The sum of all terpenes measured. |
| `sample_id` | "{sha256-hash}" | A generated ID to uniquely identify the `producer`, `product_name`, and `date_tested`. |
| `strain_name` | "Blue Rhino" | A strain name, if specified. Otherwise, can be attempted to be parsed from the `product_name`. |

Each result can contain the following fields.

| Field | Example| Description |
|-------|--------|-------------|
| `analysis` | "pesticides" | The analysis used to obtain the result. |
| `key` | "pyrethrins" | A standardized key for the result analyte. |
| `name` | "Pyrethrins" | The lab's internal name for the result analyte |
| `value` | 0.42 | The value of the result. |
| `mg_g` | 0.00000042 | The value of the result in milligrams per gram. |
| `units` | "ug/g" | The units for the result `value`, `limit`, `lod`, and `loq`. |
| `limit` | 0.5 | A pass / fail threshold for contaminant screening analyses. |
| `lod` | 0.01 | The limit of detection for the result analyte. Values below the `lod` are typically reported as `ND`. |
| `loq` | 0.1 | The limit of quantification for the result analyte. Values above the `lod` but below the `loq` are typically reported as `<LOQ`. |
| `status` | "pass" | The pass / fail status for contaminant screening analyses. |


## Advanced Usage

If you are developing a new parsing routine for a lab or LIMS, then you will need to follow these steps.
1. Implement a `parse_{lab}_coa`, `parse_{lab}_pdf` and/or a `parse_{lab}_url` function to parse results from a given CoA. If there is a QR code on the CoA containing the sample's `lab_results_url`, then the PDF parsing routine can be as simple as follows. If not, then you can implement your own PDF parsing logic.
    ```py
    def parse_cc_pdf(
            self,
            doc: Any,
            max_delay: Optional[float] = 7,
            persist: Optional[bool] = False,
        ) -> dict:
        """Parse a Confident Cannabis CoA PDF.
        Args:
            doc (str or PDF): A file path to a PDF or a pdfplumber PDF.
            max_delay (float): The maximum number of seconds to wait
                for the page to load.
            persist (bool): Whether to persist the driver.
                The default is `False`. If you do persist
                the driver, then make sure to call `quit`
                when you are finished.
        Returns:
            (dict): The sample data.
        """
        # TODO: Implement any custom PDF parsing here....

        return self.parse_pdf(
            self,
            doc,
            lims='Confident Cannabis',
            max_delay=max_delay,
            persist=persist,
        )
    ```
    Your algorithm to parse from a lab or LIMS CoA URL can be as simple or as complex as necessary. If the lab or LIMS has implemented an API, then the algorithm can simply be a function to make a request to the lab's API. Be sure to create a unique `sample_id` before returning the observation (`obs`) data.
    ```py
    from cannlytics.data.data import create_sample_id

    def parse_cc_url(
            self,
            url: str,
            headers: Optional[Any] = None,
            max_delay: Optional[float] = 7,
            persist: Optional[bool] = False,
        ) -> dict:
        """Parse a Confident Cannabis CoA URL.
        Args:
            url (str): The CoA URL.
            headers (Any): Optional headers for standardization.
            max_delay (float): The maximum number of seconds to wait
                for the page to load.
            persist (bool): Whether to persist the driver.
                The default is `False`. If you do persist
                the driver, then make sure to call `quit`
                when you are finished.
        Returns:
            (dict): The sample data.
        """
        # TODO: Implement API request and parsing here....

        # Return the sample with a freshly minted sample ID.
        obs['sample_id'] = create_sample_id(
            private_key=producer,
            public_key=product_name,
            salt=date_tested,
        )
        return obs
    ```
    Finally, you can create a `parse_{lab}_coa` function to parse either a PDF or a URL.
    ```py
    def parse_cc_coa(
        parser,
        doc: Any,
        **kwargs,
    ) -> dict:
    """Parse a Confident Cannabis CoA PDF or URL.
    Args:
        doc (str or PDF): A PDF file path or pdfplumber PDF.
    Returns:
        (dict): The sample data.
    """
    if isinstance(doc, str):
        if doc.startswith('http'):
            return parse_cc_url(parser, doc, **kwargs)
        elif doc.endswith('.pdf'):
            return parse_cc_pdf(parser, doc, **kwargs)
        else:
            return parse_cc_pdf(parser, doc, **kwargs)
    else:
        return parse_cc_pdf(parser, doc, **kwargs)
    ```
2. Import the details for your lab / LIMS in `coas.py`, where your lab or LIMS details contain the following fields:
    ```py
    YOUR_FAVORITE_LIMS = {
        'coa_algorithm': 'favorite.py',
        'coa_algorithm_entry_point': 'parse_favorite_coa',
        'lims': 'Your Favorite LIMS',
        'url': 'https://cannlytics.com',
    }
    ```
3. Add the lab details to the `LIMS` dictionary with the preferred name of your lab / LIMS as the key. For Example:
    ```py
    LIMS = {
      'Your Favorite LIMS': YOUR_FAVORITE_LIMS,
    }
    ```

You can use `CoADoc`'s built-in helper functions in your parsing algorithms.

| Function | Description |
|----------|-------------|
| `decode_pdf_qr_code(page, img, resolution=300)` | Decode a PDF QR Code from a given image. |
| `find_pdf_qr_code_url(pdf, image_index=None)` | Find the QR code given a CoA PDF or page. If no `image_index` is provided, then all images are tried to be decoded until a QR code is found. If no QR code is found, then a `IndexError` is raised. |
| `find_metrc_id(pdf)` | *Under Development* |
| `get_metrc_results` | *Under Development* |
| `get_pdf_creation_date(pdf)` | Get the creation date of a PDF in ISO format. |
| `identify_lims(doc)` | Identify if a CoA was created by a common LIMS. |

Once you have created a function or functions to parse CoAs for a new lab or LIMS, then you can create a pull request to have your algorithm reviewed and included in the main Cannlytics repository upon approval. Once published, your algorithm and the knowledge that it generates can be used to help parse CoAs all around the world. As more and more CoAs are parsed, the knowledge base will grow and grow. Now you have rich CoA data, cleverly unlocked, continuously being polished, and ripe for your plundering.

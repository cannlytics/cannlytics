# 🥸 CoADoC | Cannlytics CoA Data Parser

<div align="center" style="text-align:center; margin-top:1rem; margin-bottom: 1rem;">
  <img width="150px" alt="" src="https://firebasestorage.googleapis.com/v0/b/cannlytics.appspot.com/o/public%2Fimages%2Flogos%2Fcannlytics_coa_doc.png?alt=media&token=1871dde9-82db-4342-a29d-d373671491b3">
</div>

Certificates of analysis (CoAs) are abundant for cultivators, processors, retailers, and consumers too, but the data is often locked away. Rich, valuable laboratory data so close, yet so far away! CoADoc puts these vital data points in your hands by parsing PDFs and URLs, finding all the data, standardizing the data, and cleanly returning the data to you.

| Algorithm | Lab / LIMS | Status |
|-----------|------------|--------|
| `parse_cc_coa` | Confident Cannabis | 🟢 |
| `parse_tagleaf_coa` | TagLeaf LIMS | 🟢 |
| `parse_green_leaf_lab_coa` | Green Leaf Lab | 🟢 |
| `parse_veda_coa` | Veda Scientific | 🔴 |
| `parse_mcr_labs_coa` | MCR Labs | 🔴 |
| `parse_sc_labs_coa` | SC Labs | 🔴 |

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

## Advanced Usage

If you are developing a new parsing routine for a lab or LIMS, then you will need to follow these steps.
1. Implement a `parse_{lab}_pdf` and/or a `parse_{lab}_url` function to parse results from a given CoA.
2. Import your functions in `coas.py` and
3. Add the lab details to the `LIMS` constant.
3. Add your function to the `CoADoc` class `__init__` function.

If there is a QR code on the CoA containing the sample's `lab_results_url`, then the PDF parsing routine can be as simple as follows. If not, then you can implement your own PDF parsing logic.

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

You can use `CoADoc`'s built-in helper functions in your parsing algorithms.

| Function | Description |
|----------|-------------|
| `decode_pdf_qr_code(page, img, resolution=300)` | Decode a PDF QR Code from a given image. |
| `find_pdf_qr_code_url(pdf, image_index=None)` | Find the QR code given a CoA PDF or page. If no `image_index` is provided, then all images are tried to be decoded until a QR code is found. If no QR code is found, then a `IndexError` is raised. |
| `find_metrc_id(pdf)` | *Under Development* |
| `get_metrc_results` | *Under Development* |
| `get_pdf_creation_date(pdf)` | Get the creation date of a PDF in ISO format. |
| `identify_lims(doc)` | Identify if a CoA was created by a common LIMS. |

Once you have created a function or functions to parse CoAs for a new lab or LIMS, then you can create a pull request to have your algorithm reviewed and included in the main Cannlytics repository upon approval. Then your algorithm can be used to parse CoAs for anyone in the world who needs your service.

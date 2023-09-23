# COA Data Extraction API

The `api/data/coas` API endpoint allows users to extract lab results from certificates of analysis (COAs) through PDFs, images that contain QR codes of the COA URL, or directly from the COA URLs. The endpoint also provides functionality to get, query, and delete parsed lab results. Users can pass the COA data in the request body using the following formats:

- **PDFs**: Users can upload COA PDF files directly as part of the request using the file field. The API supports a maximum of 100 files per request, and each file should not exceed 5 MB in size.
- **Images**: Users can upload images that contain QR codes of the COA URLs using the file field. The API accepts PNG, JPG, and JPEG image formats.
- **URLs**: Users can provide COA URLs in the request body using the urls field as an array.

!!! example

    Post COA URLS and files to have the data extracted and returned.
    ```bash
    POST /api/data/coas
    Content-Type: multipart/form-data
    Authorization: Bearer <token>

    {
      "urls": ["https://coa-url-1", "https://coa-url-2"],
      "file": [PDF_FILE_1, PDF_FILE_2, IMAGE_FILE_1, IMAGE_FILE_2]
    }
    ```

    Upon successful extraction, the API will return a JSON response with the extracted COA data.

    ```bash
    HTTP/1.1 200 OK
    Content-Type: application/json

    {
      "success": true,
      "data": [
        {
          "coa_pdf": "Pineapple-XX-5-13-2129146.pdf",
          "coa_hash": "9501acee692a29f309b618ac994179d274753de3c4131837af2d8e552920ec95",
          "analyses": "[\"terpenes\", \"pesticide\", \"microbiological\", \"water_activity\", \"mycotoxin\", \"residual_solvents\", \"potency\", \"heavy_metals\"]",
          "potency_status": "pass",
          "terpenes_status": "pass",
          "microbiological_status": "pass",
          "mycotoxin_status": "NT",
          "residual_solvents_status": "NT",
          "heavy_metals_status": "pass",
          "pesticide_status": "pass",
          "water_activity_status": "pass",
          "methods": null,
          "date_collected": null,
          "date_tested": null,
          "date_received": "2021-05-13T00:00:00",
          "lab": "Genesis Testing Labs",
          "lab_address": "1620 South Main St, Unit A, Grove, OK 74344",
          "lab_street": "1620 South Main St",
          "lab_city": "Grove",
          "lab_state": "OK",
          "lab_zipcode": "74344",
          "distributor": null,
          "distributor_address": null,
          "distributor_street": null,
          "distributor_city": null,
          "distributor_state": null,
          "distributor_zipcode": null,
          "distributor_license_number": null,
          "producer": "On The Hill",
          "producer_address": "7703 W 7st Street, Tulsa, OK 74127",
          "producer_street": "7703 W 7st Street",
          "producer_city": "Tulsa",
          "producer_state": "OK",
          "producer_zipcode": "74127",
          "producer_license_number": "GAAA-4JCT-WABI",
          "product_name": "Pineapple XX",
          "lab_id": "SA-051321-8070",
          "product_type": "flower",
          "batch_number": null,
          "traceability_ids": null,
          "product_size": null,
          "serving_size": null,
          "servings_per_package": null,
          "sample_weight": null,
          "status": "pass",
          "total_cannabinoids": null,
          "total_thc": 18.2281,
          "total_cbd": null,
          "total_terpenes": 1.7241,
          "sample_id": "ae39227764932d53abbfe37ceb0e5f88c84ef9fce8e545a0135cdeedd3e41e04",
          "strain_name": "Pineapple XX",
          "coa_algorithm": "coa_ai.py",
          "coa_algorithm_entry_point": "parse_coa_with_ai",
          "coa_algorithm_version": "0.0.15",
          "coa_parsed_at": "2023-06-12T18:22:33.816071",
          "images": "[]",
          "results": "[]",
          "results_hash": "0dac0a24ba0545e6812b172c25d78eecd449f6d2e3463357c8051c693dcfe1f2",
          "sample_hash": "559540bbcf278a11efdacebde76fc9305eaf54b22199b0b3648f2837a009ae0b",
          "warning": "This data was extracted by AI. Please verify it before using it. You can submit feedback to dev@cannlytics.com"
        }
      ]
    }
    ```

## COA Metadata

| Field | Example | Description |
|-------|---------|-------------|
| `analyses` | ["cannabinoids"] | A list of analyses performed on a given sample. |
| `{analysis}_status` | "pass" | The pass, fail, or N/A status for pass / fail analyses.   |
| `methods` | [{"analysis: "cannabinoids", "method": "HPLC"}] | The methods used for each analysis. |
| `date_collected` | 2022-04-20T04:20 | An ISO-formatted time when the sample was collected. |
| `date_tested` | 2022-04-20T16:20 | An ISO-formatted time when the sample was tested. |
| `date_received` | 2022-04-20T12:20 | An ISO-formatted time when the sample was received. |
| `lab` | "MCR Labs" | The lab that tested the sample. |
| `lab_address` | "85 Speen St, Framingham, MA 01701" | The lab's address. |
| `lab_street` | "85 Speen St" | The lab's street. |
| `lab_city` | "Framingham" | The lab's city. |
| `lab_state` | "MA" | The lab's state. |
| `lab_zipcode` | "01701" | The lab's zipcode. |
| `distributor` | "Fred's Dispensary" | The name of the product distributor, if applicable. |
| `distributor_address` | "420 State Ave, Olympia, WA 98506" | The distributor address, if applicable. |
| `distributor_street` | "420 State Ave" | The distributor street, if applicable. |
| `distributor_city` | "Olympia" | The distributor city, if applicable. |
| `distributor_state` | "WA" | The distributor state, if applicable. |
| `distributor_zipcode` | "98506" | The distributor zip code, if applicable. |
| `distributor_license_number` | "L-123" | The distributor license number, if applicable. |
| `producer` | "Grow House" | The producer of the sampled product. |
| `producer_address` | "3rd & Army, San Francisco, CA 55555" | The producer's address. |
| `producer_street` | "3rd & Army" | The producer's street. |
| `producer_city` | "San Francisco" | The producer's city. |
| `producer_state` | "CA" | The producer's state. |
| `producer_zipcode` | "55555" | The producer's zipcode. |
| `producer_license_number` | "L2Calc" | The producer's license number. |
| `product_name` | "Blue Rhino Pre-Roll" | The name of the product. |
| `lab_id` | "Sample-0001" | A lab-specific ID for the sample. |
| `product_type` | "flower" | The type of product. |
| `batch_number` | "Order-0001" | A batch number for the sample or product. |
| `traceability_ids` | ["1A4060300002199000003445"] | A list of relevant traceability IDs. |
| `product_size` | 2000 | The size of the product in milligrams. |
| `serving_size` | 1000 | An estimated serving size in milligrams. |
| `servings_per_package` | 2 | The number of servings per package. |
| `sample_weight` | 1 | The weight of the product sample in grams. |
| `status` | "pass" | The overall pass / fail status for all contaminant screening analyses. |
| `total_cannabinoids` | 14.20 | The analytical total of all cannabinoids measured. |
| `total_thc` | 14.00 | The analytical total of THC and THCA. |
| `total_cbd` | 0.20 | The analytical total of CBD and CBDA. |
| `total_terpenes` | 0.42 | The sum of all terpenes measured. |
| `sample_id` | "{sha256-hash}" | A generated ID to uniquely identify the `producer`, `product_name`, and `date_tested`. |
| `strain_name` | "Blue Rhino" | A strain name, if specified. Otherwise, can be attempted to be parsed from the `product_name`. |

## COA Results

The results are a JSON string representation, for example:

```bash
[
  {
    "analysis": "cannabinoids",
    "key": "thca",
    "name": "THC-A",
    "value": 14.20,
    "mg_g": 142,
    "units": "percent",
    "limit": null,
    "lod": null,
    "loq": null,
    "status": null
  }
]
```

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

## Limitations

- Maximum number of files that can be parsed in one request: 10
- Maximum file size for a single file: 100 MB
- Supported file types: PDF, PNG, JPG, JPEG
- Maximum number of observations that can be downloaded at once: 200,000

## Examples

```py
import requests

# Define the API URL.
api_url = "https://cannlytics.com/api/data/coas"

# Define a COA URL to parse.
coa_url = "https://cannlytics.page.link/test-coa"
headers = {"Authorization": "Bearer <token>"}
data = {"urls": [coa_url]}

# Parse a COA URL with the API.
response = requests.post(api_url, headers=headers, json=data)
extracted = response.json()
print(extracted["data"])

# Parse a COA PDF with the API.
doc = 'coa.pdf'
with open(doc, 'rb') as pdf:
    files = {'file': pdf}
    response = requests.post(url, files=files, headers=headers)
    extracted = response.json()
    print(extracted["data"])
```

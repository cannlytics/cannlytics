# AI API Endpoints

Here you can find a brief introduction to the `/ai` endpoints.


## COA Data Extraction API

The `api/data/coas` API endpoint allows users to extract lab results from certificates of analysis (COAs) through PDFs, images that contain QR codes of the COA URL, or directly from the COA URLs. The endpoint also provides functionality to get, query, and delete parsed lab results. Users can pass the COA data in the request body using the following formats:

- PDFs: Users can upload COA PDF files directly as part of the request using the file field. The API supports a maximum of 10 files per request, and each file should not exceed 100 MB in size.
- Images: Users can upload images that contain QR codes of the COA URLs using the file field. The API accepts PNG, JPG, and JPEG image formats.
- URLs: Users can provide COA URLs in the request body using the urls field as an array.

Example request:

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

Where:

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

Where:

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

### Limitations

- Maximum number of files that can be parsed in one request: 10
- Maximum file size for a single file: 100 MB
- Supported file types: PDF, PNG, JPG, JPEG
- Maximum number of observations that can be downloaded at once: 200,000

### Example Usage

```py
import requests

# Make a request to the API.
url = "https://api.example.com/api/data/coas"
headers = {
    "Authorization": "Bearer <token>"
}
data = {
    "urls": [
        "https://coa-url-1",
        "https://coa-url-2"
    ],
    "file": [
        open("coa_file_1.pdf", "rb"),
        open("coa_file_2.png", "rb")
    ]
}

# Parse the response.
response = requests.post(url, headers=headers, files=data)
parsed_data = response.json()["data"]
```

## Receipt Data Extraction API

The `api/data/receipts` endpoint allows users to extract their receipt data from images of receipts. It also provides functionality to get, query, and delete parsed receipts.

| Parameter | Options | Example |
|-----------|---------|---------|
| `limit` | The maximum number of receipts to return, pass any positive integer. | `?limit=420` |
| `order` | The field to use to order the returned receipts, `date_sold` by default. | `?order=total_price` |
| `desc` | Whether or not to order in descending order, the default is `false`.  | `?desc=true` |
| `product_name` | The desired product name. | `?product_name=skunk` |
| `product_type` | The desired product type. | `?product_type=flower` |
| `date` | The desired date sold. | `?date=2023-04-20` |
| `price` | The desired total price. | `?price=42` |
| `license` | The desired retailer license number. | `?license=123456789012345678901234` |
| `number` | The desired invoice number. | `?number=123456789012345678901234` |

### Example

```bash
GET /api/data/receipts
```

```bash
[{
  "hash": "04f2df46212aa2ae9ac2804059d074ab3f75be6e7714ddb208f5ac63d91d754d",
  "date_sold": "2022-08-21",
  "invoice_number": "EWFZVP",
  "product_names": ["GARCIA HAND PICKED DARK KARMA [3.5G]"],
  "product_types": null,
  "product_quantities": [1],
  "product_prices": [60.07],
  "product_ids": null,
  "total_amount": 75.0,
  "subtotal": 60.07,
  "total_discount": 0.0,
  "total_paid": 80.0,
  "change_due": 5.0,
  "rewards_earned": null,
  "rewards_spent": null,
  "total_rewards": null,
  "city_tax": 3.3,
  "county_tax": null,
  "state_tax": 6.03,
  "excise_tax": 4.99,
  "retailer": "Embarc Tahoe",
  "retailer_license_number": "C10-00006896-LIC",
  "retailer_address": "4035 Lake Tahoe Blvd, South Lake Tahoe, California 96150",
  "budtender": "BROOKE",
  "total_price": 60.07,
  "total_tax": 28.64,
  "total_transactions": 1,
  "algorithm": "receipts_ai.py",
  "algorithm_entry_point": "parse_receipt_with_ai",
  "algorithm_version": "0.0.15",
  "parsed_at": "2023-06-16T06:45:48.774879",
  "warning": "This data was parsed from text using OpenAI's GPT models. Please verify the data before using it. You can submit feedback and report issues to dev@cannlytics.com, thank you."
}]
```

<!-- MAX_NUMBER_OF_FILES: Maximum number of files that can be parsed in a single request. The default value is 10. -->

## BudderBaker - Recipe Generator

<!-- ```py
# Get a user's recipes.

``` -->

```py
# Create a recipe.
data = {
  'creativity': 0.420,
  'doses': [{'name': 'Terpinolene', 'value': 2.5, 'units': 'mg'}],
  'image_type': 'Water painting',
  'ingredients': ['coffee', 'milk', 'butter'],
  'product_name': 'Infused cannabis coffee',
  'public': True,
  'special_instructions': 'Morning coffee',
  'total_thc': 400,
  'total_cbd': 5,
  'units': 'mg',
}
url = 'https://cannlytics.com/api/ai/recipes'
response = session.post(url, json=data)
```

<!-- ## AI Utilities

```py
# Generate a color from text.

```

```py
# Generate an emoji from text.

``` -->

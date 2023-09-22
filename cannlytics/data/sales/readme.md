# `BudSpender` | Cannabis Receipt Parser

<div align="center" style="text-align:center; margin-top:1rem; margin-bottom: 1rem;">
  <img width="150px" alt="" src="https://firebasestorage.googleapis.com/v0/b/cannlytics.appspot.com/o/public%2Fimages%2Flogos%2Fbud_spender.png?alt=media&token=e0de707b-9c18-44b9-9944-b36fcffd9fd3">
</div>

Your cannabis receipts hold a lot of data, put that data to work with `BudSpender`. This [OpenAI](https://platform.openai.com/docs/api-reference/introduction)-powered tool parses cannabis receipts into well-structured data that can be used for trending, analytics, and however you please.

## Usage

Initialize a `ReceiptsParser` parsing client:

```py
from cannlytics.data.sales import ReceiptsParser

# Initialize a COA parser.
parser = ReceiptsParser(openai_api_key=openai_api_key)
```

Parse a cannabis receipt:

```py
# Parse a receipt.
filename = 'receipt-2023-04-20.jpeg'
data = parser.parse(filename)
```

## Extracted Data

`BudSpender` is designed to extract structured data from unstructured text commonly found in cannabis receipts. Below is a breakdown of the extracted fields

| Field | Example | Description |
|-------|---------|-------------|
| `date_sold` | "2020-04-20" | The date the receipt was sold. |
| `invoice_number` | "123456789" | The receipt number. |
| `product_names` | ["Blue Rhino Pre-Roll"] | The names of the product purchased. |
| `strain_names` | ["Blue Rhino"] | The strain names of the products purchased. |
| `product_types` | ["flower"] | The types of the products purchased. |
| `product_quantities` | [1] | The quantities of the products purchased. |
| `product_weights` | [3.5g] | The weights of the products purchased. |
| `product_prices` | [5.0] | The prices of the products purchased. |
| `product_ids` | ["5f8b9c4b0f5c4b0008d1b2b0"] | The IDs of the products purchased. |
| `total_amount` | 5.0 | The total amount of all product prices. |
| `subtotal` | 5.0 | The subtotal of the receipt. |
| `total_discount` | 0.0 | The amount of discount applied to the transaction, if applicable. |
| `total_paid` | 5.0 | The total amount paid. |
| `change_due` | 0.0 | The amount of change due. |
| `rewards_earned` | 0.0 | The amount of rewards earned. |
| `rewards_spent` | 0.0 | The amount of rewards spent. |
| `total_rewards` | 0.0 | The total amount of rewards. |
| `city_tax` | 0.0 | The amount of city tax applied to the transaction, if applicable. |
| `county_tax` | 0.0 | The amount of county tax applied to the transaction, if applicable. |
| `state_tax` | 0.0 | The amount of state tax applied to the transaction, if applicable. |
| `excise_tax` | 0.0 | The amount of excise tax applied to the transaction, if applicable. |
| `retailer` | "BudHouse" | The name of the retailer. |
| `retailer_license_number` | "C11-0000001-LIC" | The license number of the retailer. |
| `retailer_address` | "1234 Main St, San Diego, CA 92101" | The address of the retailer. |
| `retailer_street` | "420 State Ave" | The retailer street, if applicable. |
| `retailer_city` | "Olympia" | The retailer city, if applicable. |
| `retailer_state` | "CA" | The state of the retailer, if applicable. |
| `retailer_zipcode` | "98506" | The zip code of the retailer, if applicable. |
| `budtender` | "John Doe" | The name of the budtender. |

## Methods

| Method Name  | Return Type | Description   | Parameters  |
|-----|--------|--------------|----------------|
| `parse` | `dict`  | Parses a receipt with OpenAI's GPT model and returns the structured data as a JSON. | `doc`: Path to the document.<br>Other parameters to fine-tune the parsing such as `model`, `openai_api_key`, `max_tokens`, etc. |
| `image_to_pdf_to_text`| `str`  | Extracts the text from an image by converting it to a PDF.| `image_file`: Path to the image file. |
| `image_to_text` | `str`  | Directly extracts the text from an image. | `image_file`: Path to the image file.<br>`median_blur`: (Optional) Removes noise. Must be a positive odd integer. |
| `save` | -  | Saves the extracted data to a specified file. | `obs`: The parsed observation.<br>`filename`: Destination file name. |
| `quit` | -  | Resets the parser and performs garbage cleaning. | -   |

# Receipt Data Extraction API

The `api/data/receipts` endpoint allows users to extract their receipt data from images of receipts. It also provides functionality to get, query, and delete parsed receipts.

!!! example

    Post receipt files to have the data extracted and returned.
    ```bash
    POST /api/data/receipts
    Content-Type: multipart/form-data
    Authorization: Bearer <token>

    {
      "file": [YOUR_RECEIPT_IMAGE]
    }
    ```

    You can then get parsed receipt data.
    ```bash
    GET /api/data/receipts
    ```

    The data is returned as JSON: 
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

## Query parameters

You can use `GET` requests with the following parameters to the `api/data/receipts` endpoint to query the parsed receipts.

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

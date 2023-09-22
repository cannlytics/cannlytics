# Sales Data <a name="sales-data"></a>

You can use use the Cannlytics `ReceiptParser` through the `api/data/receipts` endpoint. The `ReceiptParser` is a tool that can parse receipts from a variety of point-of-sale (POS) systems using OpenAI's GPT-4 model.

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

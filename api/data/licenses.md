# Licensee Data <a name="licensee-data"></a>

The `api/data/licenses` API endpoint allows users to retrieve data about cannabis licenses. Users can query the license data using various parameters such as license number, type, name, county, and zip code. The endpoint also provides options to sort the results and limit the number of records returned.

```bash
GET /api/data/licenses
```
| Parameter       | Description                                              | Example                         |
|-----------------|------------------------------------------------------|---------------------------------|
| `license_number`| Filter licenses by a specific license number (optional).  | `?license_number=1234567890`       |
| `type`          | Filter licenses by license type (optional).              | `?type=ABC`                         |
| `name`          | Search licenses by business legal name or DBA name (optional). | `?name=Example%20Business`             |
| `county`        | Filter licenses by county (optional).                   | `?county=XYZ%20County`                 |
| `state`         | Filter licenses by state (optional).                   | `?state=ma`                 |
| `zipcode`       | Filter licenses by ZIP code (optional).                 | `?zipcode=12345`                     |
| `order_by`      | Sort the results by a specific field (optional). By default, sorted by DBA name. | `?order_by=date_sold`       |
| `limit`         | Limit the number of results returned (optional). Default limit is 100. | `?limit=50`          |
| `product_name`  | The desired product name.                              | `?product_name=Example%20Product`      |
| `product_type`  | The desired product type.                              | `?product_type=Type%20A`                |
| `date`          | The desired date sold.                                 | `?date=2023-06-16`                   |
| `price`         | The desired total price.                               | `?price=100`                         |
| `license`       | The desired retailer license number.                    | `?license=ABC123`                    |
| `number`        | The desired invoice number.                            | `?number=INV123`                     |

### Example

```bash
GET /api/data/licenses?license_number=ABC123
```

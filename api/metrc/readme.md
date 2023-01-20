# Metrc API Endpoints `/api/metrc`

Why use the Cannlytics API to interface with the Metrc API? Hopefully, to make your life easier. This is why Cannlytics built and uses the following endpoints to interface with Metrc. Hopefully you will also find these tools easy to use. Furthermore, you can employ Cannlytics services as a [verified Metrc integrator](https://cannlytics.com#metrc) to interface with Metrc for your compliance needs.

| Object | Endpoint | Methods |
|-------|----------|---------|
| [Authentication](#authentication) | `/api/metrc/admin/create-license` | `POST` |
| [Authentication](#authentication) | `/api/metrc/admin/delete-license` | `POST` |
| [Facilities](#facilities-and-employees) | `/api/metrc/facilities/<license_number>` | `GET` |
| [Employees](#facilities-and-employees) | `/api/metrc/employees/<license_number>` | `GET` |
| [Locations](#locations) | `/api/metrc/locations/<area_id>` | `GET`, `POST`, `DELETE` |
| [Strains](#strains) | `/api/metrc/strains/<strain_id>` | `GET`, `POST`, `DELETE` |
| [Plants](#plants) | `/api/metrc/plants/<plant_id>` | `GET`, `POST`, `DELETE` |
| [Plant batches](#plant-batches) | `/api/metrc/batches/<batch_id>` | `GET`, `POST`, `DELETE` |
| [Harvests](#harvests) | `/api/metrc/harvests/<harvest_id>` | `GET`, `POST`, `DELETE` |
| [Packages](#packages) | `/api/metrc/packages/<package_id>` | `GET`, `POST`, `DELETE` |
| [Items](#items) | `/api/metrc/items/<item_id>` | `GET`, `POST`, `DELETE` |
| [Transfers](#transfers) | `/api/metrc/transfers/<transfer_id>` | `GET`, `POST`, `DELETE` |
| [Results](#results) | `/api/metrc/results/<test_id>` | `GET`, `POST`, `DELETE` |
| [Patients](#patients) | `/api/metrc/patients/<patient_id>` | `GET`, `POST`, `DELETE` |
| [Sales](#sales) | `/api/metrc/sales/<sale_id>` | `GET`, `POST`, `DELETE` |
| [Deliveries](#deliveries) | `/api/metrc/deliveries/<delivery_id>` | `GET`, `POST`, `DELETE` |
| [Drivers](#drivers-and-vehicles) | `/api/metrc/drivers/<driver_id>` | `GET` |
| [Vehicles](#vehicles-and-vehicles) | `/api/metrc/vehicles/<vehicle_id>` | `GET` |
| [Types](#types) | `/api/metrc/types/<type>` | `GET` |

## Authentication

First, you will need to register your Metrc user API key with Cannlytics to authorize your use of the services. Your Metrc user API key will be stored in Google Cloud Secret Manager and will only be accessed to make secure requests directly to the Metrc API. Once your Metrc user API key is registered, you can make requests by passing your Cannlytics API key in the `Authorization: Bearer <token>` header along with an optional `license` query parameter or key in the body of your request.

| Endpoint | Description |
|----------|-------------|
| `/api/metrc/admin/create-license` | Allows users to register their Metrc user API keys for a given organization. The endpoint checks that the user is authenticated, the owner of the organization, and retrieves the necessary information from the request. Then it saves the key in a secure manner in Google Cloud Secret Manager and the key metadata in Firestore for users to manage. It also creates a log of the activity and returns a success or failure message. |
| `/api/metrc/admin/delete-license` | Allows users to delete a license from a given organization's licenses on request. The endpoint first authenticates the user and retrieves the necessary information from the request such as the license number, organization ID, and the reason for deletion. Then it deletes the license data and redacts the secret from Google Cloud Secret Manager. It also creates a log of the activity and returns a success or failure message. |

Here is an example showing how to create and delete a license.

```py
import os
import requests

# Define the API.
base = 'https://cannlytics.com/api'

# Pass your Cannlytics API Key.
api_key = os.getenv('CANNLYTICS_API_KEY')
headers = {
    'Authorization': 'Bearer %s' % API_KEY,
    'Content-type': 'application/json',
}

# Create a license.
url = f'{base}/metrc/admin/create-license'
data = {
  'metrc_user_api_key': 'redacted',
  'license_number': 'redacted',
  'license_type': 'Grower',
  'org_id': 'your-organization',
  'state': 'ok',
}
response = requests.post(url data=data, headers=headers)
assert response.data['success']

# Delete a license.
url = f'{base}/metrc/admin/delete-license'
data = {
  'license_number': 'redacted',
  'org_id': 'your-organization',
  'deletion_reason': 'Test deletion.',
}
response = requests.post(url data=data, headers=headers)
assert response.data['success']
```

## Facilities and Employees

```py
# Get facilities.

# Get facility.

# Get employees.

# Get an employee.

```

## Locations

The following example shows how to interface with locations in the Metrc API.

```py
# Create a location.
data = {
  'name': 'Flower Room',
  'location_type_name': 'Default'
}
url = f'{base}/metrc/locations'
response = requests.post(url, data=data headers=headers)
assert response.status_code == 200

# Get a location.
url = f'{base}/metrc/locations/420'
response = requests.get(url, headers=headers)
assert response.status_code == 200

# Update the name of a location.
data = {
  'id': 420,
  'name': 'Flower Room A',
  'location_type_name': 'Default'
}
url = f'{base}/metrc/locations'
response = requests.post(url, data=data headers=headers)
assert response.status_code == 200

# Delete a location.
url = f'{base}/metrc/locations/420'
response = requests.delete(url, headers=headers)
assert response.status_code == 200
```

## Strains

You can interface with strains in the Metrc API as follows.

```py
# Create a location.

# Get a location.
url = f'{base}/metrc/locations/redacted'
response = requests.get(url, headers=headers)
assert response.status_code == 200

# Update the name of a location.

# Delete a location.
url = f'{base}/metrc/locations/redacted'
response = requests.delete(url, headers=headers)
assert response.status_code == 200
```

## Plants

You can interface with plants in the Metrc API as follows.

```py

```

## Plant batches

You can interface with plant batches in the Metrc API as follows.

```py

```

## Harvests

You can interface with harvests in the Metrc API as follows.

```py

```

## Packages

You can interface with packages in the Metrc API as follows.

```py

```

## Items

You can interface with package items in the Metrc API as follows.

```py

```

## Transfers

You can interface with transfers in the Metrc API as follows.

```py

```

## Results

You can interface with lab results in the Metrc API as follows.

```py

```

## Patients

You can interface with patients in the Metrc API as follows.

```py

```

## Sales

You can interface with sales in the Metrc API as follows.

```py

```

## Deliveries

You can interface with deliveries in the Metrc API as follows.

```py

```

## Drivers and Vehicles

You can get drivers and vehicles from the Metrc API as follows.

```py

```

## Types

You can get various types of data from the Metrc API as follows.

```py
# Get adjustment reasons.
url = f'{base}/metrc/types/adjustments'
response = requests.get(url, headers=headers)
assert response.status_code == 200

# Get batch types.
url = f'{base}/metrc/types/batches'
response = requests.get(url, headers=headers)
assert response.status_code == 200

# Get categories.
url = f'{base}/metrc/types/categories'
response = requests.get(url, headers=headers)
assert response.status_code == 200

# Get customer types.
url = f'{base}/metrc/types/customers'
response = requests.get(url, headers=headers)
assert response.status_code == 200

# Get location types.
url = f'{base}/metrc/types/locations'
response = requests.get(url, headers=headers)
assert response.status_code == 200

# Get package types.
url = f'{base}/metrc/types/packages'
response = requests.get(url, headers=headers)
assert response.status_code == 200

# Get package statuses.
url = f'{base}/metrc/types/package-statuses'
response = requests.get(url, headers=headers)
assert response.status_code == 200

# Get return reasons.
url = f'{base}/metrc/types/return-reasons'
response = requests.get(url, headers=headers)
assert response.status_code == 200

# Get test statuses.
url = f'{base}/metrc/types/test-statuses'
response = requests.get(url, headers=headers)
assert response.status_code == 200

# Get test types.
url = f'{base}/metrc/types/tests'
response = requests.get(url, headers=headers)
assert response.status_code == 200

# Get transfer types.
url = f'{base}/metrc/types/transfers'
response = requests.get(url, headers=headers)
assert response.status_code == 200

# Get units of measure.
url = f'{base}/metrc/types/units'
response = requests.get(url, headers=headers)
assert response.status_code == 200

# Get waste types.
url = f'{base}/metrc/types/waste'
response = requests.get(url, headers=headers)
assert response.status_code == 200

# Get waste methods.
url = f'{base}/metrc/types/waste-methods'
response = requests.get(url, headers=headers)
assert response.status_code == 200

# Get waste reasons.
url = f'{base}/metrc/types/waste-reasons'
response = requests.get(url, headers=headers)
assert response.status_code == 200
```

For further assistance using the Cannlytics API to interface with Metrc, [contact support](https://cannlytics.com/contact).

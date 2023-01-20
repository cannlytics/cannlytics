"""
Metrc API Endpoint Tests | Cannlytics API
Copyright (c) 2023 Cannlytics

Authors: Keegan Skeate <https://github.com/keeganskeate>
Created: 1/12/2023
Updated: 1/19/2023
License: MIT License <https://opensource.org/licenses/MIT>
"""
import os
import requests
from dotenv import dotenv_values

# Define the endpoint.
ENDPOINT = 'metrc'

# Dev: Test with the development server.
BASE = 'http://127.0.0.1:8000/api'

# Production: Uncomment to test with the production server once published.
# BASE = 'https://console.cannlytics.com/api'

# Load your API key to pass in the authorization header as a bearer token.
config = dotenv_values('../../.env')
API_KEY = config['CANNLYTICS_API_KEY']


# === Tests ===
if __name__ == '__main__':

    # Authentication a session.
    session = requests.Session()
    session.headers.update({'Authorization': f'Bearer {API_KEY}'})  


    #------------------------------------------------------------------
    # [ ] License management.
    #------------------------------------------------------------------

    # [✓] Test adding a Metrc user API key.
    # print('Adding a license...')
    # url = f'{BASE}/metrc/admin/create-license'
    # data = {
    #   'metrc_user_api_key': os.getenv('METRC_TEST_USER_API_KEY'),
    #   'license_number': '',
    #   'license_type': 'Processor',
    #   'org_id': 'test-processor',
    #   'state': 'ok',
    # }
    # response = requests.post(url, json=data, headers=HEADERS)
    # assert response.json()['success']
    # print('Added Metrc user API key.')

    # TODO: Delete a license.
    # print('Deleting a license...')
    # url = f'{BASE}/metrc/admin/delete-license'
    # data = {
    #   'license_number': '',
    #   'org_id': 'test-processor',
    #   'deletion_reason': 'Test deletion.',
    # }
    # response = requests.post(url, json=data, headers=HEADERS)
    # assert response.data['success']
    # print('Delete Metrc user API key.')


    #------------------------------------------------------------------
    # [✓] Facilities
    #------------------------------------------------------------------

    # [✓] Test facilities.
    response = session.get(f'{BASE}/metrc/facilities')
    assert response.status_code == 200
    facilities = response.json()['data']
    print('Found %i facilities' % len(facilities))


    #------------------------------------------------------------------
    # [ ] Locations
    #------------------------------------------------------------------

    # [ ] Test getting a location.
    params = {'license': facilities[0]['license']['number']}
    response = session.get(f'{BASE}/metrc/locations', params=params)
    assert response.status_code == 200

    # [ ] Test creating a location.


    # [ ] Test update the name of the location.


    # [ ] Test deleting a location.


#------------------------------------------------------------------
# TODO: [ ] Strains
#------------------------------------------------------------------

# Create a new strain.


# Get strains.


# Update a strain.


# Delete strains?


#------------------------------------------------------------------
# TODO: [ ] Items
#------------------------------------------------------------------

# Create an item.


# Create multiple items.


# Get an item.


# Query items.


# Update an item.


# Update items.


# Delete items?


#------------------------------------------------------------------
# TODO: [ ] Batches
#------------------------------------------------------------------

# Create a new plant batch.


# Get a plant batch.


# Create a package.


# Update a batch.


# Destroy a batch.


#------------------------------------------------------------------
# TODO: [ ] Plants
#------------------------------------------------------------------

# Get a plant created in a plant batch.


# Change the growth phase of a plant from `Vegetative` to `Flowering`.


# Move a plant to a different room.


# Destroy a plant.


# Manicure a plant.


# Harvest a plant.


# Delete a harvest?


#------------------------------------------------------------------
# TODO: [ ] Harvests
#------------------------------------------------------------------

# Get a harvest.


# Create a package.


# Remove waste weight from a harvest.


# Finish a harvest.


# Unfinish the harvest.


# Delete a harvest?


#------------------------------------------------------------------
# TODO: [ ] Packages
#------------------------------------------------------------------

# Get a package.


# Create a package from another package.


# Change the item of a package.


# Adjust the weight of a package.


# Finish a package.


# Unfinish a package.


# Delete a package?


#------------------------------------------------------------------
# TODO: [ ] Transfers and transfer templates
#------------------------------------------------------------------

# Get a licensed courier.


# Create a testing package.


# Get the tested package.


# Set up an external transfer.


# Get external transfers.


# Update an external transfer.


# Create a transfer template.


# Get transfer templates.


# Update a transfer template.


# Delete a transfer template.


#------------------------------------------------------------------
# TODO: [ ] Lab results
#------------------------------------------------------------------

# Record a lab test result.


# Create the lab result record.


# Get a package's lab results.


# Get lab results for multiple packages.



#------------------------------------------------------------------
# TODO: [ ] Sales
#------------------------------------------------------------------

# Create a sales receipt for a package.


# Get a sale.


# Get sales.


# Update a sales receipt.


# Void a sales receipt.



# # === Tests ===
# if __name__ == '__main__':

#     # Initialize a client.
#     session = requests.Session()
#     session.headers.update({'Authorization': f'Bearer {API_KEY}'})  

#     # [✓] Test facilities.
#     response = session.get(f'{BASE}/metrc/facilities/')
#     assert response.status_code == 200
#     facilities = len(response.json()['data'])
#     print('Retrieved facilities.')

    # [ ] Test employees.

    # [ ] Test locations.
    # test_get_locations(client)
    # test_create_locations(client)
    # test_update_locations(client)
    # test_delete_locations(client)

    # [ ] Test packages.

    # [ ] Test items.

    # [ ] Test lab results.

    # [ ] Test strains.

    # [ ] Test batches.

    # [ ] Test plants.

    # [ ] Test harvests.

    # [ ] Test transfers and transfer templates.

    # [ ] Test patients.

    # [ ] Test sales and transactions.

    # [ ] Test deliveries.

    # [ ] Test miscellaneous endpoints
    # - additives
    # - categories
    # - customer types
    # - Test statuses
    # - Test types
    # - units of measure
    # - waste

    # [ ] Test removing a Metrc user API key.

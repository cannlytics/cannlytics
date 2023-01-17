"""
Metrc API Endpoint Tests | Cannlytics API
Copyright (c) 2023 Cannlytics

Authors: Keegan Skeate <https://github.com/keeganskeate>
Created: 1/12/2023
Updated: 1/17/2023
License: MIT License <https://opensource.org/licenses/MIT>
"""
import os
import requests
from dotenv import load_dotenv

# Define the endpoint.
ENDPOINT = 'metrc'

# Dev: Test with the development server.
BASE = 'http://127.0.0.1:8000/api'

# Production: Uncomment to test with the production server once published.
# BASE = 'https://console.cannlytics.com/api'

# Load your API key.
load_dotenv('../../.env')
API_KEY = os.getenv('CANNLYTICS_API_KEY')

# Pass your API key through the authorization header as a bearer token.
HEADERS = {
    'Authorization': 'Bearer %s' % API_KEY,
    'Content-type': 'application/json',
}


# === Test ===
if __name__ == '__main__':
    pass

#------------------------------------------------------------------
# TODO: [ ] Facilities
#------------------------------------------------------------------

def test_get_facilities(client):
    """Test getting facilities from the Metrc API,
    through the Cannlytics API.
    """
    response = client.get('/facilities/')
    assert response.status_code == 200
    # assert response.data['data'] == [{'id': 1, 'name': 'Facility 1'}, {'id': 2, 'name': 'Facility 2'}]



#------------------------------------------------------------------
# TODO: [ ] Locations
#------------------------------------------------------------------

def test_get_locations(client):
    """Test getting a location."""
    response = client.get('/locations/')
    assert response.status_code == 200
    assert response.data['data'] == [{'id': 1, 'name': 'Location 1'}, {'id': 2, 'name': 'Location 2'}]

def test_create_locations(client):
    """Test creating a location."""
    data = [{'name': 'Location 1', 'location_type': 'Room'}, {'name': 'Location 2', 'location_type': 'Room'}]
    response = client.post('/locations/', data={'data': data})
    assert response.status_code == 201
    assert response.data['data'] == data

def test_update_locations(client):
    """Test update the name of the location."""
    data = [{'id': 1, 'name': 'Location 1 Updated', 'location_type': 'Room'}, {'id': 2, 'name': 'Location 2 Updated', 'location_type': 'Room'}]
    response = client.post('/locations/', data={'data': data})
    assert response.status_code == 200
    assert response.data['data'] == data

def test_delete_locations(client):
    """Test deleting a location."""
    data = [{'id': 1}, {'id': 2}]
    response = client.delete('/locations/', data={'data': data})
    assert response.status_code == 200
    assert response.data == {'success': True, 'data': []}


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



# === Tests ===
if __name__ == '__main__':

    # TODO: Initialize a client.
    client = None

    # [ ] Test adding a Metrc user API key.

    # [ ] Test facilities.

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

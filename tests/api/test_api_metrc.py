"""
Metrc API Endpoint Tests | Cannlytics API
Copyright (c) 2023 Cannlytics

Authors: Keegan Skeate <https://github.com/keeganskeate>
Created: 1/12/2023
Updated: 1/12/2023
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

# Get facilities.


#------------------------------------------------------------------
# TODO: [ ] Locations
#------------------------------------------------------------------
# Create a new location.


# Get created location.


# Update the name of the location.


# View the location.


# Delete locations?


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


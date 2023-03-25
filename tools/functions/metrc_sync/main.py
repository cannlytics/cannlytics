"""
Export Metrc Data
Copyright (c) 2023 Cannlytics

Authors: Keegan Skeate <https://github.com/keeganskeate>
Created: 3/24/2023
Updated: 3/24/2023
License: MIT License <https://github.com/cannlytics/cannlytics-website/blob/main/LICENSE>
"""
# Internal imports.
import base64
import os
import requests

# External imports.
from cannlytics.firebase import (
    get_collection,
    update_documents,
)
from firebase_admin import initialize_app, firestore

# TODO: Watch 
# organizations/{org_id}/metrc_user_api_keys/{metrc_hash}

# Note: These are double entered.
# The doc with `user` == True can be disregarded.


# TODO: If the document is deleted, delete Metrc data.


# TODO: If the document is added, perform initial Metrc sync.


# TODO: If the document is changed, if `sync`, then perform sync.


# TODO: Initialize Metrc.


# TODO: Initialize Firebase.


# TODO: Get all Metrc data, category by category.
# - facilities
# - employees
# - locations
# - strains
# - plants
# - plants-batches
# - harvests
# - packages
# - items
# - transfers
# - lab results
# - receipts
# - transactions
# - deliveries
# - patients


# TODO: Calculate Metrc data statistics.
# - totals


# TODO: Save Metrc data and statistics to Firestore.


# TODO: Update the API key data to `sync` = False.
# And include the `synced_at` timestamp.


# TODO: Email admin with results.


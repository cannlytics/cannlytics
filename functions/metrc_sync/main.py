"""
Export Metrc Data
Copyright (c) 2023 Cannlytics

Authors: Keegan Skeate <https://github.com/keeganskeate>
Created: 3/24/2023
Updated: 3/26/2023
License: MIT License <https://github.com/cannlytics/cannlytics-website/blob/main/LICENSE>
"""
# Internal imports.
from datetime import datetime, timedelta
from typing import Optional

# External imports.
from cannlytics.firebase import (
    access_secret_version,
    get_collection,
    update_documents,
    update_document,
)
from cannlytics.metrc import Metrc, MetrcAPIError
from cannlytics.utils import get_timestamp
from firebase_admin import initialize_app, firestore
import google.auth


# Initialize Firebase globally for persistence.
try:
    initialize_app()
except ValueError:
    pass
db = firestore.client()
_, project_id = google.auth.default()


def get_vendor_api_key(
        state: str,
        test: Optional[bool] = True,
        project_id: Optional[str] = None,
    ) -> str:
    """Get the Metrc vendor API key from Google Secret Manager."""
    if project_id is None:
        _, project_id = google.auth.default()
    if test:
        secret_id = f'metrc_test_vendor_api_key_{state.lower()}'
    else:
        secret_id = f'metrc_vendor_api_key_{state.lower()}'
    try:
        return access_secret_version(project_id, secret_id)
    except:
        return None


def initialize_metrc_from_key_data(
        data: dict,
        logs: Optional[bool] = False,
    ) -> Metrc:
    """Initialize Metrc from API key data stored in Firestore."""
    secret_id = data['value']['fields']['secret_id']['stringValue']
    state = data['value']['fields']['state']['stringValue']
    test = data['value']['fields']['test']['booleanValue']
    metrc_user_api_key = access_secret_version(project_id, secret_id)
    metrc_vendor_api_key = get_vendor_api_key(state, test, project_id)
    return Metrc(
        metrc_vendor_api_key,
        metrc_user_api_key,
        logs=logs,
        state=state,
        test=test,
    )


def sync_metrc_facilities(track: Metrc, org_id: str):
    """Sync Metrc facilities with Firestore."""
    # Get all facilities.
    docs, refs = [], []
    col = f'organizations/{org_id}/facilities'
    facilities = track.get_facilities()
    licenses = [x.license['number'] for x in facilities]
    for i, obj in enumerate(facilities):
        data = obj.to_dict()
        data['synced_at'] = get_timestamp(zone=track.state)
        docs.append(data)
        license_number = licenses[i]
        refs.append(f'{col}/{license_number}')

    # Save facilities to Firestore.
    update_documents(refs, docs, database=db)
    return licenses


def sync_metrc_employees(track: Metrc, org_id: str, licenses: list):
    """Sync Metrc employees with Firestore."""
    # Get all employees from each license.
    docs, refs = [], []
    org_col = f'organizations/{org_id}/metrc'
    for license_number in licenses:
        col = f'{org_col}/{license_number}/employees'
        try:
            objs = track.get_employees(license_number=license_number)
        except MetrcAPIError as e:
            print(f'ERROR GETTING EMPLOYEES ({license_number})', e)
            continue
        for obj in objs:
            data = obj.to_dict()
            data['synced_at'] = get_timestamp(zone=track.state)
            docs.append(data)
            employee_id = objs[0].license['number']
            refs.append(f'{col}/{employee_id}')

    # Save employees to Firestore.
    update_documents(refs, docs, database=db)
    return docs


def sync_metrc_locations(track: Metrc, org_id: str, licenses: list):
    """Sync Metrc locations with Firestore."""
    # Get all locations from each license.
    docs, refs = [], []
    org_col = f'organizations/{org_id}/metrc'
    for license_number in licenses:
        col = f'{org_col}/{license_number}/locations'
        try:
            objs = track.get_locations(license_number=license_number)
        except MetrcAPIError as e:
            print(f'ERROR GETTING LOCATIONS ({license_number})', e)
            continue
        for obj in objs:
            data = obj.to_dict()
            data['synced_at'] = get_timestamp(zone=track.state)
            docs.append(data)
            doc_id = obj.id
            refs.append(f'{col}/{doc_id}')

    # Save employees to Firestore.
    update_documents(refs, docs, database=db)
    return docs


def sync_metrc_strains(track: Metrc, org_id: str, licenses: list):
    """Sync Metrc strains with Firestore."""
    # Get all strains from each license.
    docs, refs = [], []
    org_col = f'organizations/{org_id}/metrc'
    for license_number in licenses:
        col = f'{org_col}/{license_number}/strains'
        try:
            objs = track.get_strains(license_number=license_number)
        except MetrcAPIError as e:
            print(f'ERROR GETTING STRAINS ({license_number})', e)
            continue
        for obj in objs:
            data = obj.to_dict()
            data['synced_at'] = get_timestamp(zone=track.state)
            docs.append(data)
            doc_id = obj.id
            refs.append(f'{col}/{doc_id}')

    # Save employees to Firestore.
    update_documents(refs, docs, database=db)
    return docs


# FIXME:
# def sync_metrc_patients(track: Metrc, org_id: str, licenses: list):
#     """Sync Metrc patients with Firestore."""
#     # Get all patients from each license.
#     docs, refs = [], []
#     org_col = f'organizations/{org_id}/metrc'
#     for license_number in licenses:
#         col = f'{org_col}/{license_number}/patients'
#         try:
#             objs = track.get_patients(license_number=license_number)
#         except MetrcAPIError as e:
#             print(f'ERROR GETTING PATIENTS ({license_number})', e)
#             continue
#         for obj in objs:
#             data = obj.to_dict()
#             data['synced_at'] = get_timestamp(zone=track.state)
#             docs.append(data)
#             doc_id = obj.id
#             refs.append(f'{col}/{doc_id}')

#     # Save employees to Firestore.
#     update_documents(refs, docs, database=db)
#     return docs


def sync_metrc_plants(
        track: Metrc,
        org_id: str,
        licenses: list
    ):
    """Sync Metrc strains with Firestore."""
    # TODO: Handle starting / ending dates.
    start_date = datetime.fromisoformat('2021-01-01')
    end_date = datetime.fromisoformat('2021-02-01')
    delta = end_date - start_date
    date_list = [start_date + timedelta(days=x) for x in range(delta.days + 1)]
    iso_date_list = [d.isoformat() for d in date_list]

    # Get all strains from each license.
    docs, refs = [], []
    org_col = f'organizations/{org_id}/metrc'
    for license_number in licenses:

        # TODO: Get vegetative plants.
        plants = track.get_plants(
            action='vegetative',
            license_number=cultivator.license_number,
            start=today
        )

        # TODO: Get flowering plants.


        col = f'{org_col}/{license_number}/plants'
        try:
            objs = track.get_plants(license_number=license_number)
        except MetrcAPIError as e:
            print(f'ERROR GETTING PLANTS ({license_number})', e)
            continue
        for obj in objs:
            data = obj.to_dict()
            data['synced_at'] = get_timestamp(zone=track.state)
            docs.append(data)
            doc_id = obj.id
            refs.append(f'{col}/{doc_id}')

    # Save employees to Firestore.
    update_documents(refs, docs, database=db)
    return docs


def metrc_sync(data, context):
    """Sync Metrc data with Firestore."""
    #-------------------------------------------------------------------
    # Setup.
    #-------------------------------------------------------------------
    
    # Determine the document that changed.
    path_parts = context.resource.split('/documents/')[1].split('/')
    org_id = path_parts[1]
    metrc_hash = path_parts[3]
    ref = f'organizations/{org_id}/metrc_user_api_keys/{metrc_hash}'

    #-------------------------------------------------------------------
    # Handle API key deletion.
    #-------------------------------------------------------------------

    # If the document is deleted, delete Metrc data.
    event_type = context.event_type
    print("Event type:", event_type)
    if event_type == 'google.cloud.firestore.document_v1.EventType.DELETE':

        # TODO: Implement removal of Metrc data.
        print('REMOVE METRC DATA')

        # TODO: Email admin that a key was deleted.

    # Determine if syncing is necessary.
    # Note: These are double entered.
    # The doc with `user` == True can be disregarded.
    sync = data['value']['fields']['sync']['booleanValue']
    user = data['value']['fields']['user']['booleanValue']
    if not sync or user:
        print('No sync necessary.')
        return

    #-------------------------------------------------------------------
    # Handle API key creation or update.
    # If the document is added or, perform initial Metrc sync.
    # If the document is changed, if `sync`, then perform sync.
    #-------------------------------------------------------------------
    # Sync: Get all Metrc data, category by category.
    #-------------------------------------------------------------------

    # Initialize Metrc.
    track = initialize_metrc_from_key_data(data)

    # Collect aggregate statistics
    stats = {}

    # Sync facilities.
    licenses = sync_metrc_facilities(track, org_id)
    stats['total_facilities'] = len(licenses)
    print('Saved facilities to Firestore.')

    # Sync employees.
    docs = sync_metrc_employees(track, org_id, licenses)
    stats['total_employees'] = len(docs)
    print('Saved employees to Firestore.')

    # Sync locations.
    docs = sync_metrc_locations(track, org_id, licenses)
    stats['total_locations'] = len(docs)
    print('Saved locations to Firestore.')

    # TODO: Sync strains.
    docs = sync_metrc_strains(track, org_id, licenses)
    stats['total_strains'] = len(docs)
    print('Saved strains to Firestore.')

    # TODO: Sync plants.

    # TODO: Sync plant batches.

    # TODO: Sync harvests.

    # TODO: Sync packages.

    # TODO: Sync items.

    # TODO: Sync transfers.

    # TODO: Sync lab Results.

    # TODO: Sync receipts.

    # TODO: Sync transactions.

    # TODO: Sync deliveries.

    # TODO: Sync patients.


    #-------------------------------------------------------------------
    # Update the Metrc API key data in Firestore.
    #-------------------------------------------------------------------

    # Update the API key data to indicate that syncing has finished.
    timestamp = get_timestamp(zone=track.state)
    refs = [ref]
    docs = [{'sync': False, 'synced_at': timestamp}]

    # Prepare the statistics document for Firestore.
    refs.append(f'organizations/{org_id}/metrc_stats/{metrc_hash}')
    docs.append(stats)

    # Save statistics / usage to Firestore.
    update_documents(refs, docs)

    # Email admin when API keys are added.
    if event_type == 'google.cloud.firestore.document_v1.EventType.CREATE':
        # TODO: Implement.
        print('EMAIL ADMIN THAT A KEY WAS CREATED')

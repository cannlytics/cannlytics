"""
Data Views | Cannlytics Website
Copyright (c) 2021-2022 Cannlytics

Authors: Keegan Skeate <keegan@cannlytics.com>
Created: 1/5/2021
Updated: 1/17/2022
License: MIT License <https://github.com/cannlytics/cannlytics-website/blob/main/LICENSE>
"""
# Standard imports
from datetime import datetime
from tempfile import NamedTemporaryFile

# External imports
from django.http import FileResponse
from django.http.response import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from pandas import DataFrame
from cannlytics.auth.auth import authenticate_request

# Internal imports.
from cannlytics.firebase import (
    create_log,
    get_collection,
    upload_file,
)
from website.settings import STORAGE_BUCKET


@csrf_exempt
def download_analyses_data(request):
    """Download analyses data."""

    # Define data points.
    # Optional: Store allowed data points in Firebase?
    data_points = [
        'analysis_id',
        'analytes',
        'color',
        'name',
        'singular',
        'units',
    ]

    # Get the data file to download if the user is signed in,
    # otherwise return an error.
    collection = 'public/data/analyses'
    claims = authenticate_request(request)
    temp_name, filename = download_dataset(claims, collection, data_points)
    if filename is None:
        response = {'success': False, 'message': 'Authentication required for suggestion.'}
        return JsonResponse(response)

    # Return the file to download.
    return FileResponse(open(temp_name, 'rb'), filename=filename)


@csrf_exempt
def download_lab_data(request):
    """Download lab data."""

    # Define data points.
    # Optional: Store allowed data points in Firebase?
    data_points = [
        'id',
        'name',
        'trade_name',
        'license',
        'license_url',
        'license_issue_date',
        'license_expiration_date',
        'status',
        'street',
        'city',
        'county',
        'state',
        'zip',
        'description',
        'formatted_address',
        'timezone',
        'longitude',
        'latitude',
        'capacity',
        'square_feet',
        'brand_color',
        'favicon',
        'email',
        'phone',
        'website',
        'linkedin',
        'image_url',
        'opening_hours',
        'analyses',
    ]

    # Get the data file to download if the user is signed in,
    # otherwise return an error.
    collection = 'public/data/labs'
    claims = authenticate_request(request)
    temp_name, filename = download_dataset(claims, collection, data_points)
    if filename is None:
        response = {'success': False, 'message': 'Authentication required for suggestion.'}
        return JsonResponse(response)

    # Return the file to download.
    return FileResponse(open(temp_name, 'rb'), filename=filename)


@csrf_exempt
def download_regulation_data(request):
    """Download regulation data."""

    # Define data points.
    # Optional: Store allowed data points in Firebase?
    data_points = [
        'state',
        'state_name',
        'traceability_system',
        'adult_use',
        'adult_use_permitted',
        'adult_use_permitted_source',
        'medicinal',
        'medicinal_permitted',
        'medicinal_permitted_source',
        'state_sales_tax',
        'state_excise_tax',
        'state_local_tax',
        'tax_rate_url',
        'sources',
    ]

    # Get the data file to download if the user is signed in,
    # otherwise return an error.
    collection = 'public/data/regulations'
    claims = authenticate_request(request)
    temp_name, filename = download_dataset(claims, collection, data_points)
    if filename is None:
        response = {'success': False, 'message': 'Authentication required for suggestion.'}
        return JsonResponse(response)

    # Return the file to download.
    return FileResponse(open(temp_name, 'rb'), filename=filename)


#------------------------------------------------------------------------------
# Download Utilities
#------------------------------------------------------------------------------

def download_dataset(claims, collection, data_points):
    """Download a given dataset."""

    # Get the user's data, returning if not authenticated.
    try:
        uid = claims['uid']
        user_email = claims['email']
        name = claims.get('name', 'Unknown')
    except KeyError:
        return None, None

    # Get data points in specified order.
    collection_data = get_collection(collection, order_by='state')
    dataframe = DataFrame.from_dict(collection_data, orient='columns')
    data = dataframe[data_points]

    # Convert JSON to CSV.
    with NamedTemporaryFile(delete=False) as temp:
        temp_name = temp.name + '.csv'
        data.to_csv(temp_name, index=False)
        temp.close()

    # Post a copy of the data to Firebase storage.
    now = datetime.now()
    timestamp = now.strftime('%Y-%m-%d_%H-%M-%S')
    destination = 'public/data/downloads/'
    data_type = collection.split('/')[-1]
    filename = f'{data_type}_{timestamp}.csv'
    ref = destination + filename
    upload_file(ref, temp_name, bucket_name=STORAGE_BUCKET)

    # Create an activity log.
    log_entry = {
        'data_points': len(data),
        'file': ref,
        'email': user_email,
        'name': name,
        'uid': uid,
    }
    create_log(
        ref='logs/website/downloads',
        claims=claims,
        action=f'User ({user_email}) downloaded {data_type} data.',
        log_type='download',
        key=f'download_{data_type}_data',
        changes=log_entry,
    )

    # Return the file that can be downloaded.
    return temp_name, filename

"""
Data Views | Cannlytics Console
Author: Keegan Skeate <keegan@cannlytics.com>
Created: 12/18/2020
Updated: 7/17/2021
"""

# Standard imports
import csv
from datetime import datetime
from json import loads

# External imports
from django.http import HttpResponse
from django.http.response import HttpResponseRedirect, JsonResponse
import numpy as np
import pandas as pd
import openpyxl

# Internal imports
from cannlytics.firebase import (
    get_document,
    update_document,
    verify_session_cookie,
)
from cannlytics.utils.utils import snake_case


def get_worksheet_headers(sheet):
    """Get the headres of a worksheet.
    Args:
        sheet (Worksheet): An openpyx; Excel file object.
    Returns:
        headers (list): A list of header strings.
    """
    headers = []
    for cell in sheet[1]:
        headers.append(snake_case(cell.value))
    return headers


def get_worksheet_data(sheet, headers):
    """Get the data of a worksheet.
    Args:
        sheet (Worksheet): An openpyx; Excel file object.
        headres (list): A list of headers to map the values.
    Returns:
        list(dict): A list of dictionaries.
    """
    data = []
    for row in sheet.iter_rows(min_row=2):
        values = {}
        for key, cell in zip(headers, row):
            values[key] = cell.value
        data.append(values)
    return data


def read_worksheet(path, filename='Upload'):
    """Read the imported data, iterating over the rows and
    getting value from each cell in row.
    Args:
        path (str or InMemoryFile): An Excel workbook to read.
        filename (str): The name of the worksheet to upload.
    Returns:
        (DataFrame): A Pandas DataFrame of the results.
    """
    # try:
    #     workbook = openpyxl.load_workbook(path, data_only=True)
    #     sheet = workbook.get_sheet_by_name(filename)
    #     headers = get_worksheet_headers(sheet)
    #     return pd.DataFrame(get_worksheet_data(sheet, headers))
    # except:
    print('Path:', path)
    data = pd.read_csv(path)
    data.columns = [snake_case(x) for x in data.columns]
    return data


def download_csv_data(request):
    """Download posted data as a CSV file.
    TODO: Pull requested data again (by ID) instead of using posted data.
    TODO: Limit the size / rate of downloads (tie to account usage / billing).
    """
    session_cookie = request.COOKIES.get('__session')
    claims = verify_session_cookie(session_cookie)
    if not claims: 
        return HttpResponse(status=401)
    data = loads(request.body.decode('utf-8'))['data']
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="download.csv"'
    writer = csv.writer(response)
    writer.writerow(list(data[0].keys()))
    for item in data:
        writer.writerow(list(item.values()))
    return response


def import_data(request):
    """Import data from an Excel worksheet for a given data model.
    TODO: Limit the size / rate of downloads (tie to account usage / billing).
    Optional: Handle .csv imports.
    Optional: Submit form without refresh.
    """
    # Authenticate the user.
    session_cookie = request.COOKIES.get('__session')
    claims = verify_session_cookie(session_cookie)
    if not claims:
        return HttpResponse(status=401)

    # Get the import parameters and file, validating the file.
    # Also, authorize that the user is part of the organization.
    model = request.GET.get('model')
    org_id = request.GET.get('organization_id')
    excel_file = request.FILES['excel_file']
    ext = excel_file.name.split('.').pop()
    if excel_file.size >= 1024 * 1000 * 500:
        return JsonResponse({'error': True, 'message': 'File too large.'}, status=406)
    if ext not in ['csv', 'xlsx', 'xlsm']:
        return JsonResponse({'error': True, 'message': 'Expected a .csv, .xlsx, or .xlsm file.'}, status=406)
    if org_id not in claims.get('team', []):
        return HttpResponse({'error': True, 'message': 'You are not a member of this organization.'}, status=403)

    # Read the data from Excel.
    data = read_worksheet(excel_file)

    # Get singular from data models, to identify the ID.
    data_model = get_document(f'organizations/{org_id}/data_models/{model}')
    model_singular = data_model['singular']

    # Clean data according to data type.
    # Optional: Add more validation / data cleaning by type.
    for field in data_model['fields']:
        key = field['key']
        data_type = field.get('type', 'text')
        if data_type == 'text' or data_type == 'textarea':
            data[key].replace(['0', '0.0', 0], '', inplace=True)

    # Save imported data to Firestore (FIXME: in reverse order for user sanity).
    updated_at = datetime.now().isoformat()
    for key, row in data.iterrows():
    # data = data.replace({np.nan: None})
    # for idx in reversed(data.index):
        # row = data.loc[idx]
        doc_id = row[f'{model_singular}_id']
        if doc_id:
            values = row.to_dict()
            values['updated_at'] = updated_at
            values['updated_by'] = claims['uid']
            update_document(f'organizations/{org_id}/{model}/{doc_id}', values)

    # Submit the form (FIXME: preferably without refreshing).
    # See: https://stackoverflow.com/questions/11647715/how-to-submit-form-without-refreshing-page-using-django-ajax-jquery
    return HttpResponseRedirect(f'/{model}')
    # return JsonResponse({'success': True}, status=200)

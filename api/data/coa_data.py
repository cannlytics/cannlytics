"""
CoA Data Endpoints | Cannlytics API
Copyright (c) 2021-2022 Cannlytics

Authors: Keegan Skeate <https://github.com/keeganskeate>
Created: 7/17/2022
Updated: 8/21/2022
License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description: API endpoints to interface with CoA data.
"""
# Standard imports.
from datetime import datetime
from json import loads
import os
import tempfile

# External imports
from django.http import HttpResponse
from django.http.response import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.response import Response

# Internal imports
from cannlytics.auth.auth import authenticate_request
from cannlytics.data.coas.coas import CoADoc
from cannlytics.firebase.firebase import create_log, update_documents

# Maximum number of files that can be parsed in one request.
MAX_NUMBER_OF_FILES = 10

# Maximum file size for a single file.
MAX_FILE_SIZE = 1024 * 1000 * 100 # (100 MB)

# Specify file types.
FILE_TYPES = ['pdf', 'png', 'jpg', 'jpeg']


@api_view(['GET', 'POST'])
def coa_data(request, sample_id=None):
    """Get CoA data (public API endpoint)."""

    # TODO: Authenticate the user, throttle requests if unauthenticated.
    throttle = False
    claims = authenticate_request(request)
    if not claims:
        throttle = True
        # return HttpResponse(status=401)

    # Get a specific CoA or query open-source CoAs.
    if request.method == 'GET':

        # FIXME: Implement querying pre-parsed CoA data!
        # That is, if a CoA is parsed once and is public, then we should be able to speedily retrieve that data for the user.
        params = request.query_params
        ref = 'public/coas/coa_data'

        # TODO: Get Metrc results here!!!


    # Parse posted CoA PDFs or URLs.
    if request.method == 'POST':

        # Get any user-posted data.
        try:
            body = loads(request.body.decode('utf-8'))
        except:
            body = {}
        urls = body.get('urls', [])

        # Get any user-posted files.
        pdfs, images = [], []
        request_files = request.FILES
        if request_files is not None:
            for key, coa_file in request.FILES.items():

                # File safety check.
                ext = coa_file.name.split('.').pop()

                # Reject files that are too large.
                if coa_file.size >= MAX_FILE_SIZE:
                    message = 'File too large. The maximum number of bytes is %i.' % MAX_FILE_SIZE
                    response = {'error': True, 'message': message}
                    return JsonResponse(response, status=406)
                
                # Reject files that are not PDFs or ZIPs or common image types.
                if ext.lower not in FILE_TYPES:
                    message = 'Invalid file type. Valid file types are: %s' % ', '.join(FILE_TYPES)
                    response = {'error': True, 'message': message}
                    return JsonResponse(response, status=406)

                # Save the file as a temp file for parsing.
                temp = tempfile.mkstemp(key)
                temp_file = os.fdopen(temp[0], 'wb')
                temp_file.write(coa_file.read())
                temp_file.close()
                filepath = temp[1]
                
                # Parse PDFs and images separately.
                if ext.lower() == 'pdf':
                    pdfs.append(filepath)
                else:
                    images.append(filepath)

        # Return an error if no PDFs or URLs are passed.
        if not urls and not pdfs and not images:
            message = 'Expecting an array of `urls`, `pdfs`, or `images` in the request body.'
            response = {'success': False, 'message': message}
            return Response(response, status=400)

        # Return an error if too many PDFs or URLs are passed.
        if len(urls) > MAX_NUMBER_OF_FILES:
            message = f'Too many files, please limit your request to {MAX_NUMBER_OF_FILES} files at a time.'
            response = {'success': False, 'message': message}
            return Response(response, status=400)

        # Parse COA data.
        parser = CoADoc()
        coa_data = []

        # Try to parse URLs and PDFs.
        for doc in urls + pdfs:
            try:
                data = parser.parse(doc)
            except:
                try:
                    data = parser.parse_with_ai(doc)
                except:
                    print('Failed to parse:', doc)
                    continue
            coa_data.append(data)

        # Try to parse images.
        for doc in images:
            try:
                coa_url = parser.scan(doc)
                print('Scanned:', coa_url)
                data = parser.parse(coa_url)
            except:
                try:
                    data = parser.parse_with_ai(url)
                except:
                    print('Failed to parse URL:', url)
                    continue
            coa_data.append(data)

        # Finish parsing.
        parser.quit()

        # TODO: Create a thumbnail of PDFs.

        # Create a usage log and save any public lab results.
        changes, refs, docs = [], [], []
        for item in data:
            if item.get('public'):
                changes.append(item)
                sample_id = item['sample_id']
                refs.append(f'public/data/lab_results/{sample_id}')
                docs.append(item)
        if refs:
            update_documents(refs, docs)
        create_log(
            'logs/website/coa_doc',
            claims=claims,
            action='Parsed COAs.',
            log_type='coa_data',
            key='coa_data',
            changes=changes
        )

        # Return any extracted data.
        response = {'success': True, 'data': data}
        return Response(response, status=200)


@csrf_exempt
def download_coa_data(request):
    """Download posted data as a .xlsx file. Pass a `data` field in the
    body with the data, an object or an array of objects, to standardize
    and save in a workbook."""

    # TODO: Authenticate the user, throttle requests if unauthenticated.
    throttle = False
    claims = authenticate_request(request)
    if not claims:
        throttle = True
        # return HttpResponse(status=401)

    # Read the posted data.
    data = loads(request.body.decode('utf-8'))['data']

    # Create an Excel Workbook response.
    content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    timestamp = datetime.now().isoformat()[:19].replace(':', '-')
    filename = f'coa-data-{timestamp}.xlsx'
    response = HttpResponse(content_type=content_type)
    response['Content-Disposition'] = f'attachment; filename={filename}'

    # Create the Workbook and save it to the response.
    parser = CoADoc(init_all=False)
    parser.save(data, response)
    parser.quit()
    return response

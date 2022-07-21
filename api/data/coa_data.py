"""
CoA Data Endpoints | Cannlytics API
Copyright (c) 2021-2022 Cannlytics

Authors: Keegan Skeate <https://github.com/keeganskeate>
Created: 7/17/2022
Updated: 7/19/2022
License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description: API endpoints to interface with CoA data.
"""
# Standard imports.
from csv import writer
from json import loads
import os
import tempfile

# External imports
from django.http import HttpResponse
from django.http.response import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from cannlytics.auth.auth import authenticate_request

# Internal imports
from cannlytics.data.coas import CoADoc

# Max file size set to 5 GB
MAX_FILE_SIZE = 1024 * 1000 * 500

# For safety, restrict the possible URLs to a whitelist.
WHITELIST = [
    'https://lims.tagleaf.com',
    'https://orders.confidentcannabis.com',

]

@api_view(['GET', 'POST'])
def coa_data(request, sample_id=None):
    """Get CoA data (public API endpoint)."""

    # Authenticate the user.
    throttle = False
    claims = authenticate_request(request)
    print('User:', claims)
    if not claims:
        # return HttpResponse(status=401)
        throttle = True

    # Get a specific CoA or query open-source CoAs.
    if request.method == 'GET':

        # TODO: Implement getting CoA data!
        params = request.query_params
        ref = 'public/coas/coa_data'

    # Parse posted CoA PDFs or URLs.
    if request.method == 'POST':

        # ref = 'public/coas/coa_data'

        # Get any user-posted data.
        try:
            body = loads(request.body.decode('utf-8'))
        except:
            body = {}
        print('User data:', body)
        urls = body.get('urls', [])

        # Get any user-posted files.
        print('Files:', request.FILES)
        request_files = request.FILES
        if request_files is not None:
            for key, coa_file in request.FILES.items():

                # File safety check.
                ext = coa_file.name.split('.').pop()
                if coa_file.size >= MAX_FILE_SIZE:
                    message = 'File too large. The maximum number of bytes is %i.' % MAX_FILE_SIZE
                    response = {'error': True, 'message': message}
                    return JsonResponse(response, status=406)
                if ext != 'pdf' and ext != 'zip':
                    message = 'Invalid file type. Expecting a .pdf or .zip file.'
                    response = {'error': True, 'message': message}
                    return JsonResponse(response, status=406)

                # Keep temp file to open as a PDF.
                temp = tempfile.mkstemp(key)
                temp_file = os.fdopen(temp[0], 'wb')
                temp_file.write(coa_file.read())
                temp_file.close()
                filepath = temp[1]
                urls.append(filepath)

        if not urls:
            message = 'Expecting an array of `urls` in the request body.'
            response = {'success': False, 'message': message}
            return Response(response, status=400)

        # Allow the user to pass parameters:
        # - headers
        # - kind
        # - lims
        # - max_delay
        # - persist

        # FIXME: Figure out how to handle URLs vs. PDFs.
        # print('URLs:', urls)

        # Parse CoA data.
        parser = CoADoc()
        data = parser.parse(urls)
        parser.quit()

        # TODO: Log errors and save public lab results.

        # Return either file or JSON.
        response = {'success': True, 'data': data}
        return Response(response, status=200)


def download_coa_data(request):
    """Download posted data as a CSV file.
    Future work: Limit the size / rate of downloads.
    """
    # Authenticate the user.
    throttle = False
    claims = authenticate_request(request)
    print('User:', claims)
    if not claims:
        # return HttpResponse(status=401)
        throttle = True

    # TODO: Normalize data into either a wide or long table.
    data = loads(request.body.decode('utf-8'))['data']
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="download.csv"'
    csv_writer = writer(response)
    csv_writer.writerow(list(data[0].keys()))
    for item in data:
        csv_writer.writerow(list(item.values()))
    return response


# def import_coa_data(request):
#     """Import data from an Excel worksheet for a given data model.
    
#     Optional: Handle .csv imports.
#     Optional: Submit form without refresh.
#     """
#     # Authenticate the user.
#     throttle = False
#     claims = authenticate_request(request)
#     print('User:', claims)
#     if not claims:
#         # return HttpResponse(status=401)
#         throttle = True

#     # TODO: Limit the size / rate of uploads.
    
    
#     # TODO: Keep track of usage. Limit the number and size of requests
#     # for unauthenticated users.


#     # TODO: Reject any bots that fell for the honey pot.
#     # honeypot = request.GET.get('super_special_email')
#     # if honeypot:
#     #     return HttpResponse(status=401)

#     # Parse the CoA file.
#     coa_file = request.FILES['coa_file']
#     ext = coa_file.name.split('.').pop()
#     if coa_file.size >= MAX_FILE_SIZE:
#         message = 'File too large. The maximum number of bytes is %i.' % MAX_FILE_SIZE
#         response = {'error': True, 'message': message}
#         return JsonResponse(response, status=406)
#     if ext != 'pdf' and ext != 'zip':
#         message = 'Invalid file type. Expecting a .pdf or .zip file.'
#         response = {'error': True, 'message': message}
#         return JsonResponse(response, status=406)

#     # Parse each CoA.
#     parser = CoADoc()
#     data = parser.parse(coa_file)
#     parser.quit()

#     # Optional: Create a datafile if specified?

#     # Return the data to the user!
#     response = {'success': True, 'data': data}
#     return JsonResponse(response, status=200)

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
# from csv import writer
from json import loads
import os
import tempfile

# External imports
from django.http import HttpResponse
from django.http.response import JsonResponse
from pandas import DataFrame, ExcelWriter
from rest_framework.decorators import api_view
from rest_framework.response import Response


# Internal imports
from cannlytics.auth.auth import authenticate_request
from cannlytics.data.coas import CoADoc
from cannlytics.firebase.firebase import create_log, update_documents

# Maximum number of files that can be parsed in 1 request.
MAX_NUMBER_OF_FILES = 420

# Maximum file size for a single file: 100 MB.
MAX_FILE_SIZE = 1024 * 1000 * 100

# For safety, restrict the possible URLs to a whitelist.
WHITELIST = [
    'https://orders.confidentcannabis.com',
    'https://client.sclabs.com',
    'https://reports.mcrlabs.com',
    'https://lims.tagleaf.com',
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

        if len(urls) > MAX_NUMBER_OF_FILES:
            message = 'Too many files, please limit your request to 420 files at a time.'
            response = {'success': False, 'message': message}
            return Response(response, status=400)

        # FIXME: Figure out how to handle URLs vs. PDFs.
        print('URLs:', urls)

        # FIXME: Parse CoA data.
        parser = CoADoc()
        data = parser.parse(urls)
        parser.quit()

        # DEV:
#         data = [{'notes': None,
#  'results': [{'compound': 'THCa',
#    'analysis': 'cannabinoid',
#    'lodloq': '0.05 / 0.14',
#    'mu': '±14.800',
#    'result-mass': '739.98',
#    'result-percent': '73.998'},
#   {'compound': 'Δ9-THC',
#    'analysis': 'cannabinoid',
#    'lodloq': '0.06 / 0.26',
#    'mu': '±1.835',
#    'result-mass': '68.46',
#    'result-percent': '6.846'},
#   {'compound': 'CBGa',
#    'analysis': 'cannabinoid',
#    'lodloq': '0.1 / 0.2',
#    'mu': '±1.44',
#    'result-mass': '35.4',
#    'result-percent': '3.54'},
#   {'compound': 'CBG',
#    'analysis': 'cannabinoid',
#    'lodloq': '0.06 / 0.19',
#    'mu': '±0.240',
#    'result-mass': '7.81',
#    'result-percent': '0.781'},
#   {'compound': 'CBCa',
#    'analysis': 'cannabinoid',
#    'lodloq': '0.07 / 0.28',
#    'mu': '±0.225',
#    'result-mass': '5.90',
#    'result-percent': '0.590'},
#   {'compound': 'THCVa',
#    'analysis': 'cannabinoid',
#    'lodloq': '0.07 / 0.20',
#    'mu': '±0.133',
#    'result-mass': '3.59',
#    'result-percent': '0.359'},
#   {'compound': 'CBDa',
#    'analysis': 'cannabinoid',
#    'lodloq': '0.02 / 0.19',
#    'mu': '±0.052',
#    'result-mass': '2.28',
#    'result-percent': '0.228'},
#   {'compound': 'CBC',
#    'analysis': 'cannabinoid',
#    'lodloq': '0.2 / 0.5',
#    'mu': 'N/A',
#    'result-mass': '<LOQ',
#    'result-percent': '<LOQ'},
#   {'compound': 'Δ8-THC',
#    'analysis': 'cannabinoid',
#    'lodloq': '0.1 / 0.4',
#    'mu': 'N/A',
#    'result-mass': 'ND',
#    'result-percent': 'ND'},
#   {'compound': 'THCV',
#    'analysis': 'cannabinoid',
#    'lodloq': '0.1 / 0.2',
#    'mu': 'N/A',
#    'result-mass': 'ND',
#    'result-percent': 'ND'},
#   {'compound': 'CBD',
#    'analysis': 'cannabinoid',
#    'lodloq': '0.07 / 0.29',
#    'mu': 'N/A',
#    'result-mass': 'ND',
#    'result-percent': 'ND'},
#   {'compound': 'CBDV',
#    'analysis': 'cannabinoid',
#    'lodloq': '0.04 / 0.15',
#    'mu': 'N/A',
#    'result-mass': 'ND',
#    'result-percent': 'ND'},
#   {'compound': 'CBDVa',
#    'analysis': 'cannabinoid',
#    'lodloq': '0.03 / 0.53',
#    'mu': 'N/A',
#    'result-mass': 'ND',
#    'result-percent': 'ND'},
#   {'compound': 'CBL',
#    'analysis': 'cannabinoid',
#    'lodloq': '0.06 / 0.24',
#    'mu': 'N/A',
#    'result-mass': 'ND',
#    'result-percent': 'ND'},
#   {'compound': 'CBN',
#    'analysis': 'cannabinoid',
#    'lodloq': '0.1 / 0.3',
#    'mu': 'N/A',
#    'result-mass': 'ND',
#    'result-percent': 'ND'},
#   {'compound': 'SUM OF CANNABINOIDS',
#    'analysis': 'cannabinoid',
#    'lodloq': '',
#    'mu': '',
#    'result-mass': '863.4 mg/g',
#    'result-percent': '86.34%'},
#   {'compound': 'β-Caryophyllene',
#    'analysis': 'terpenoid',
#    'lodloq': '0.004 / 0.012',
#    'mu': '±0.6152',
#    'result-mass': '22.209',
#    'result-percent': '2.2209'},
#   {'compound': 'Limonene',
#    'analysis': 'terpenoid',
#    'lodloq': '0.005 / 0.016',
#    'mu': '±0.2329',
#    'result-mass': '20.980',
#    'result-percent': '2.0980'},
#   {'compound': 'α-Humulene',
#    'analysis': 'terpenoid',
#    'lodloq': '0.009 / 0.029',
#    'mu': '±0.1930',
#    'result-mass': '7.718',
#    'result-percent': '0.7718'},
#   {'compound': 'α-Bisabolol',
#    'analysis': 'terpenoid',
#    'lodloq': '0.008 / 0.026',
#    'mu': '±0.2131',
#    'result-mass': '5.136',
#    'result-percent': '0.5136'},
#   {'compound': 'Guaiol',
#    'analysis': 'terpenoid',
#    'lodloq': '0.009 / 0.030',
#    'mu': '±0.1252',
#    'result-mass': '3.411',
#    'result-percent': '0.3411'},
#   {'compound': 'α-Pinene',
#    'analysis': 'terpenoid',
#    'lodloq': '0.005 / 0.017',
#    'mu': '±0.0213',
#    'result-mass': '3.182',
#    'result-percent': '0.3182'},
#   {'compound': 'β-Pinene',
#    'analysis': 'terpenoid',
#    'lodloq': '0.004 / 0.014',
#    'mu': '±0.0272',
#    'result-mass': '3.051',
#    'result-percent': '0.3051'},
#   {'compound': 'Linalool',
#    'analysis': 'terpenoid',
#    'lodloq': '0.009 / 0.032',
#    'mu': '±0.0760',
#    'result-mass': '2.568',
#    'result-percent': '0.2568'},
#   {'compound': 'trans-β-Farnesene',
#    'analysis': 'terpenoid',
#    'lodloq': '0.008 / 0.025',
#    'mu': '±0.0460',
#    'result-mass': '1.667',
#    'result-percent': '0.1667'},
#   {'compound': 'Terpineol',
#    'analysis': 'terpenoid',
#    'lodloq': '0.009 / 0.031',
#    'mu': '±0.0656',
#    'result-mass': '1.372',
#    'result-percent': '0.1372'},
#   {'compound': 'Fenchol',
#    'analysis': 'terpenoid',
#    'lodloq': '0.010 / 0.034',
#    'mu': '±0.0397',
#    'result-mass': '1.319',
#    'result-percent': '0.1319'},
#   {'compound': 'Caryophyllene Oxide',
#    'analysis': 'terpenoid',
#    'lodloq': '0.010 / 0.033',
#    'mu': '±0.0446',
#    'result-mass': '1.246',
#    'result-percent': '0.1246'},
#   {'compound': 'β-Ocimene',
#    'analysis': 'terpenoid',
#    'lodloq': '0.006 / 0.020',
#    'mu': '±0.0257',
#    'result-mass': '1.029',
#    'result-percent': '0.1029'},
#   {'compound': 'Nerolidol',
#    'analysis': 'terpenoid',
#    'lodloq': '0.006 / 0.019',
#    'mu': '±0.0212',
#    'result-mass': '0.433',
#    'result-percent': '0.0433'},
#   {'compound': 'Camphene',
#    'analysis': 'terpenoid',
#    'lodloq': '0.005 / 0.015',
#    'mu': '±0.0039',
#    'result-mass': '0.431',
#    'result-percent': '0.0431'},
#   {'compound': 'Borneol',
#    'analysis': 'terpenoid',
#    'lodloq': '0.005 / 0.016',
#    'mu': '±0.0136',
#    'result-mass': '0.417',
#    'result-percent': '0.0417'},
#   {'compound': 'Fenchone',
#    'analysis': 'terpenoid',
#    'lodloq': '0.009 / 0.028',
#    'mu': '±0.0050',
#    'result-mass': '0.223',
#    'result-percent': '0.0223'},
#   {'compound': 'Terpinolene',
#    'analysis': 'terpenoid',
#    'lodloq': '0.008 / 0.026',
#    'mu': '±0.0030',
#    'result-mass': '0.191',
#    'result-percent': '0.0191'},
#   {'compound': 'Valencene',
#    'analysis': 'terpenoid',
#    'lodloq': '0.009 / 0.030',
#    'mu': '±0.0097',
#    'result-mass': '0.181',
#    'result-percent': '0.0181'},
#   {'compound': 'Geraniol',
#    'analysis': 'terpenoid',
#    'lodloq': '0.002 / 0.007',
#    'mu': '±0.0024',
#    'result-mass': '0.070',
#    'result-percent': '0.0070'},
#   {'compound': 'α-Cedrene',
#    'analysis': 'terpenoid',
#    'lodloq': '0.005 / 0.016',
#    'mu': '±0.0013',
#    'result-mass': '0.054',
#    'result-percent': '0.0054'},
#   {'compound': 'Sabinene Hydrate',
#    'analysis': 'terpenoid',
#    'lodloq': '0.006 / 0.022',
#    'mu': '±0.0009',
#    'result-mass': '0.029',
#    'result-percent': '0.0029'},
#   {'compound': 'γ-Terpinene',
#    'analysis': 'terpenoid',
#    'lodloq': '0.006 / 0.018',
#    'mu': '±0.0004',
#    'result-mass': '0.026',
#    'result-percent': '0.0026'},
#   {'compound': 'Citronellol',
#    'analysis': 'terpenoid',
#    'lodloq': '0.003 / 0.010',
#    'mu': '±0.0008',
#    'result-mass': '0.020',
#    'result-percent': '0.0020'},
#   {'compound': 'Nerol',
#    'analysis': 'terpenoid',
#    'lodloq': '0.003 / 0.011',
#    'mu': '±0.0004',
#    'result-mass': '0.013',
#    'result-percent': '0.0013'},
#   {'compound': 'Myrcene',
#    'analysis': 'terpenoid',
#    'lodloq': '0.008 / 0.025',
#    'mu': 'N/A',
#    'result-mass': '<LOQ',
#    'result-percent': '<LOQ'},
#   {'compound': 'α-Terpinene',
#    'analysis': 'terpenoid',
#    'lodloq': '0.005 / 0.017',
#    'mu': 'N/A',
#    'result-mass': '<LOQ',
#    'result-percent': '<LOQ'},
#   {'compound': 'p-Cymene',
#    'analysis': 'terpenoid',
#    'lodloq': '0.005 / 0.016',
#    'mu': 'N/A',
#    'result-mass': '<LOQ',
#    'result-percent': '<LOQ'},
#   {'compound': 'Geranyl Acetate',
#    'analysis': 'terpenoid',
#    'lodloq': '0.004 / 0.014',
#    'mu': 'N/A',
#    'result-mass': '<LOQ',
#    'result-percent': '<LOQ'},
#   {'compound': 'Sabinene',
#    'analysis': 'terpenoid',
#    'lodloq': '0.004 / 0.014',
#    'mu': 'N/A',
#    'result-mass': 'ND',
#    'result-percent': 'ND'},
#   {'compound': 'α-Phellandrene',
#    'analysis': 'terpenoid',
#    'lodloq': '0.006 / 0.020',
#    'mu': 'N/A',
#    'result-mass': 'ND',
#    'result-percent': 'ND'},
#   {'compound': 'Δ3-Carene',
#    'analysis': 'terpenoid',
#    'lodloq': '0.005 / 0.018',
#    'mu': 'N/A',
#    'result-mass': 'ND',
#    'result-percent': 'ND'},
#   {'compound': 'Eucalyptol',
#    'analysis': 'terpenoid',
#    'lodloq': '0.006 / 0.018',
#    'mu': 'N/A',
#    'result-mass': 'ND',
#    'result-percent': 'ND'},
#   {'compound': 'Isopulegol',
#    'analysis': 'terpenoid',
#    'lodloq': '0.005 / 0.016',
#    'mu': 'N/A',
#    'result-mass': 'ND',
#    'result-percent': 'ND'},
#   {'compound': 'Camphor',
#    'analysis': 'terpenoid',
#    'lodloq': '0.006 / 0.019',
#    'mu': 'N/A',
#    'result-mass': 'ND',
#    'result-percent': 'ND'},
#   {'compound': 'Isoborneol',
#    'analysis': 'terpenoid',
#    'lodloq': '0.004 / 0.012',
#    'mu': 'N/A',
#    'result-mass': 'ND',
#    'result-percent': 'ND'},
#   {'compound': 'Menthol',
#    'analysis': 'terpenoid',
#    'lodloq': '0.008 / 0.025',
#    'mu': 'N/A',
#    'result-mass': 'ND',
#    'result-percent': 'ND'},
#   {'compound': 'Pulegone',
#    'analysis': 'terpenoid',
#    'lodloq': '0.003 / 0.011',
#    'mu': 'N/A',
#    'result-mass': 'ND',
#    'result-percent': 'ND'},
#   {'compound': 'Cedrol',
#    'analysis': 'terpenoid',
#    'lodloq': '0.008 / 0.027',
#    'mu': 'N/A',
#    'result-mass': 'ND',
#    'result-percent': 'ND'},
#   {'compound': 'TOTAL',
#    'analysis': 'terpenoid',
#    'lodloq': '',
#    'mu': '',
#    'result-mass': '76.976 mg/g',
#    'result-percent': '7.6976%'},
#   {'compound': 'Aldicarb',
#    'analysis': 'pesticide',
#    'lodloq': '0.03 / 0.08',
#    'action-limit': '≥ LOD',
#    'mu': 'N/A',
#    'result-mass': 'ND',
#    'result-pf': 'Pass'},
#   {'compound': 'Carbofuran',
#    'analysis': 'pesticide',
#    'lodloq': '0.02 / 0.05',
#    'action-limit': '≥ LOD',
#    'mu': 'N/A',
#    'result-mass': 'ND',
#    'result-pf': 'Pass'},
#   {'compound': 'Chlordane*',
#    'analysis': 'pesticide',
#    'lodloq': '0.03 / 0.08',
#    'action-limit': '≥ LOD',
#    'mu': 'N/A',
#    'result-mass': 'ND',
#    'result-pf': 'Pass'},
#   {'compound': 'Chlorfenapyr*',
#    'analysis': 'pesticide',
#    'lodloq': '0.03 / 0.10',
#    'action-limit': '≥ LOD',
#    'mu': 'N/A',
#    'result-mass': 'ND',
#    'result-pf': 'Pass'},
#   {'compound': 'Chlorpyrifos',
#    'analysis': 'pesticide',
#    'lodloq': '0.02 / 0.06',
#    'action-limit': '≥ LOD',
#    'mu': 'N/A',
#    'result-mass': 'ND',
#    'result-pf': 'Pass'},
#   {'compound': 'Coumaphos',
#    'analysis': 'pesticide',
#    'lodloq': '0.02 / 0.07',
#    'action-limit': '≥ LOD',
#    'mu': 'N/A',
#    'result-mass': 'ND',
#    'result-pf': 'Pass'},
#   {'compound': 'Daminozide',
#    'analysis': 'pesticide',
#    'lodloq': '0.02 / 0.07',
#    'action-limit': '≥ LOD',
#    'mu': 'N/A',
#    'result-mass': 'ND',
#    'result-pf': 'Pass'},
#   {'compound': 'Dichlorvos (DDVP)',
#    'analysis': 'pesticide',
#    'lodloq': '0.03 / 0.09',
#    'action-limit': '≥ LOD',
#    'mu': 'N/A',
#    'result-mass': 'ND',
#    'result-pf': 'Pass'},
#   {'compound': 'Dimethoate',
#    'analysis': 'pesticide',
#    'lodloq': '0.03 / 0.08',
#    'action-limit': '≥ LOD',
#    'mu': 'N/A',
#    'result-mass': 'ND',
#    'result-pf': 'Pass'},
#   {'compound': 'Ethoprophos',
#    'analysis': 'pesticide',
#    'lodloq': '0.03 / 0.10',
#    'action-limit': '≥ LOD',
#    'mu': 'N/A',
#    'result-mass': 'ND',
#    'result-pf': 'Pass'},
#   {'compound': 'Etofenprox',
#    'analysis': 'pesticide',
#    'lodloq': '0.02 / 0.06',
#    'action-limit': '≥ LOD',
#    'mu': 'N/A',
#    'result-mass': 'ND',
#    'result-pf': 'Pass'},
#   {'compound': 'Fenoxycarb',
#    'analysis': 'pesticide',
#    'lodloq': '0.03 / 0.08',
#    'action-limit': '≥ LOD',
#    'mu': 'N/A',
#    'result-mass': 'ND',
#    'result-pf': 'Pass'},
#   {'compound': 'Fipronil',
#    'analysis': 'pesticide',
#    'lodloq': '0.03 / 0.08',
#    'action-limit': '≥ LOD',
#    'mu': 'N/A',
#    'result-mass': 'ND',
#    'result-pf': 'Pass'},
#   {'compound': 'Imazalil',
#    'analysis': 'pesticide',
#    'lodloq': '0.02 / 0.06',
#    'action-limit': '≥ LOD',
#    'mu': 'N/A',
#    'result-mass': 'ND',
#    'result-pf': 'Pass'},
#   {'compound': 'Methiocarb',
#    'analysis': 'pesticide',
#    'lodloq': '0.02 / 0.07',
#    'action-limit': '≥ LOD',
#    'mu': 'N/A',
#    'result-mass': 'ND',
#    'result-pf': 'Pass'},
#   {'compound': 'Parathion-methyl',
#    'analysis': 'pesticide',
#    'lodloq': '0.03 / 0.10',
#    'action-limit': '≥ LOD',
#    'mu': 'N/A',
#    'result-mass': 'ND',
#    'result-pf': 'Pass'},
#   {'compound': 'Mevinphos',
#    'analysis': 'pesticide',
#    'lodloq': '0.03 / 0.09',
#    'action-limit': '≥ LOD',
#    'mu': 'N/A',
#    'result-mass': 'ND',
#    'result-pf': 'Pass'},
#   {'compound': 'Paclobutrazol',
#    'analysis': 'pesticide',
#    'lodloq': '0.02 / 0.05',
#    'action-limit': '≥ LOD',
#    'mu': 'N/A',
#    'result-mass': 'ND',
#    'result-pf': 'Pass'},
#   {'compound': 'Propoxur',
#    'analysis': 'pesticide',
#    'lodloq': '0.03 / 0.09',
#    'action-limit': '≥ LOD',
#    'mu': 'N/A',
#    'result-mass': 'ND',
#    'result-pf': 'Pass'},
#   {'compound': 'Spiroxamine',
#    'analysis': 'pesticide',
#    'lodloq': '0.03 / 0.08',
#    'action-limit': '≥ LOD',
#    'mu': 'N/A',
#    'result-mass': 'ND',
#    'result-pf': 'Pass'},
#   {'compound': 'Thiacloprid',
#    'analysis': 'pesticide',
#    'lodloq': '0.03 / 0.10',
#    'action-limit': '≥ LOD',
#    'mu': 'N/A',
#    'result-mass': 'ND',
#    'result-pf': 'Pass'},
#   {'compound': 'Aflatoxin B1',
#    'analysis': 'mycotoxin',
#    'lodloq': '2.0 / 6.0',
#    'action-limit': '',
#    'mu': 'N/A',
#    'result-mass': 'ND',
#    'result-pf': ''},
#   {'compound': 'Aflatoxin B2',
#    'analysis': 'mycotoxin',
#    'lodloq': '1.8 / 5.6',
#    'action-limit': '',
#    'mu': 'N/A',
#    'result-mass': 'ND',
#    'result-pf': ''},
#   {'compound': 'Aflatoxin G1',
#    'analysis': 'mycotoxin',
#    'lodloq': '1.0 / 3.1',
#    'action-limit': '',
#    'mu': 'N/A',
#    'result-mass': 'ND',
#    'result-pf': ''},
#   {'compound': 'Aflatoxin G2',
#    'analysis': 'mycotoxin',
#    'lodloq': '1.2 / 3.5',
#    'action-limit': '',
#    'mu': 'N/A',
#    'result-mass': 'ND',
#    'result-pf': ''},
#   {'compound': 'Total Aflatoxin',
#    'analysis': 'mycotoxin',
#    'lodloq': '',
#    'action-limit': '20',
#    'mu': '±',
#    'result-mass': 'ND',
#    'result-pf': 'Pass'},
#   {'compound': 'Ochratoxin A',
#    'analysis': 'mycotoxin',
#    'lodloq': '6.3 / 19.2',
#    'action-limit': '20',
#    'mu': 'N/A',
#    'result-mass': 'ND',
#    'result-pf': 'Pass'},
#   {'compound': '1,2-Dichloroethane',
#    'analysis': 'residual_solvents',
#    'lodloq': '0.05 / 0.1',
#    'action-limit': '1',
#    'mu': 'N/A',
#    'result-mass': 'ND',
#    'result-pf': 'Pass'},
#   {'compound': 'Benzene',
#    'analysis': 'residual_solvents',
#    'lodloq': '0.03 / 0.09',
#    'action-limit': '1',
#    'mu': 'N/A',
#    'result-mass': 'ND',
#    'result-pf': 'Pass'},
#   {'compound': 'Chloroform',
#    'analysis': 'residual_solvents',
#    'lodloq': '0.1 / 0.2',
#    'action-limit': '1',
#    'mu': 'N/A',
#    'result-mass': 'ND',
#    'result-pf': 'Pass'},
#   {'compound': 'Ethylene Oxide',
#    'analysis': 'residual_solvents',
#    'lodloq': '0.3 / 0.8',
#    'action-limit': '1',
#    'mu': 'N/A',
#    'result-mass': 'ND',
#    'result-pf': 'Pass'},
#   {'compound': 'Dichloromethane (Methylene Chloride)',
#    'analysis': 'residual_solvents',
#    'lodloq': '0.3 / 0.9',
#    'action-limit': '1',
#    'mu': 'N/A',
#    'result-mass': 'ND',
#    'result-pf': 'Pass'},
#   {'compound': 'Trichloroethylene',
#    'analysis': 'residual_solvents',
#    'lodloq': '0.1 / 0.3',
#    'action-limit': '1',
#    'mu': 'N/A',
#    'result-mass': 'ND',
#    'result-pf': 'Pass'},
#   {'compound': 'Arsenic',
#    'analysis': 'heavy_metals',
#    'lodloq': '0.02 / 0.1',
#    'action-limit': '0.2',
#    'mu': 'N/A',
#    'result-mass': 'ND',
#    'result-pf': 'Pass'},
#   {'compound': 'Cadmium',
#    'analysis': 'heavy_metals',
#    'lodloq': '0.02 / 0.05',
#    'action-limit': '0.2',
#    'mu': 'N/A',
#    'result-mass': 'ND',
#    'result-pf': 'Pass'},
#   {'compound': 'Lead',
#    'analysis': 'heavy_metals',
#    'lodloq': '0.04 / 0.1',
#    'action-limit': '0.5',
#    'mu': 'N/A',
#    'result-mass': 'ND',
#    'result-pf': 'Pass'},
#   {'compound': 'Mercury',
#    'analysis': 'heavy_metals',
#    'lodloq': '0.002 / 0.01',
#    'action-limit': '0.1',
#    'mu': 'N/A',
#    'result-mass': 'ND',
#    'result-pf': 'Pass'},
#   {'compound': 'Aspergillus flavus',
#    'analysis': 'microbiology',
#    'action-limit': 'Not Detected in 1g',
#    'result-mass': 'ND',
#    'result-pf': 'Pass'},
#   {'compound': 'Aspergillus fumigatus',
#    'analysis': 'microbiology',
#    'action-limit': 'Not Detected in 1g',
#    'result-mass': 'ND',
#    'result-pf': 'Pass'},
#   {'compound': 'Aspergillus niger',
#    'analysis': 'microbiology',
#    'action-limit': 'Not Detected in 1g',
#    'result-mass': 'ND',
#    'result-pf': 'Pass'},
#   {'compound': 'Aspergillus terreus',
#    'analysis': 'microbiology',
#    'action-limit': 'Not Detected in 1g',
#    'result-mass': 'ND',
#    'result-pf': 'Pass'},
#   {'compound': 'Salmonella spp.',
#    'analysis': 'microbiology',
#    'action-limit': 'Not Detected in 1g',
#    'result-mass': 'ND',
#    'result-pf': 'Pass'},
#   {'compound': 'Shiga toxin-producing Escherichia coli',
#    'analysis': 'microbiology',
#    'action-limit': 'Not Detected in 1g',
#    'result-mass': 'ND',
#    'result-pf': 'Pass'},
#   {'compound': 'Total Sample Area Covered by Sand, Soil, Cinders, or Dirt',
#    'analysis': 'foreign_material',
#    'action-limit': '>25%',
#    'result-pf': 'Pass'},
#   {'compound': 'Total Sample Area Covered by Mold',
#    'analysis': 'foreign_material',
#    'action-limit': '>25%',
#    'result-pf': 'Pass'},
#   {'compound': 'Total Sample Area Covered by an Imbedded Foreign Material',
#    'analysis': 'foreign_material',
#    'action-limit': '>25%',
#    'result-pf': 'Pass'},
#   {'compound': 'Insect Fragment Count',
#    'analysis': 'foreign_material',
#    'action-limit': '> 1 per 3 grams',
#    'result-pf': 'Pass'},
#   {'compound': 'Hair Count',
#    'analysis': 'foreign_material',
#    'action-limit': '> 1 per 3 grams',
#    'result-pf': 'Pass'},
#   {'compound': 'Mammalian Excreta Count',
#    'analysis': 'foreign_material',
#    'action-limit': '> 1 per 3 grams',
#    'result-pf': 'Pass'}],
#  'date_collected': '2022-05-27',
#  'date_received': '2022-05-27',
#  'source_metrc_uid': '1A4060300002199000003445',
#  'address': 'OAKLAND, CA 94621-4427',
#  'delta_9_thc_per_unit': 'Pass',
#  'total_terpenoids_mgtog': '76.976 mg/g',
#  'total_terpenoids_percent': '7.6976%',
#  'distributor_address': 'OAKLAND, CA 94621',
#  'distributor_city': 'OAKLAND',
#  'distributor_zip_code': '94621',
#  'city': 'OAKLAND',
#  'zip_code': '94621-4427',
#  'metrc_ids': ['1A4060300002199000003445'],
#  'product_type': 'Concentrate, Product Inhalable',
#  'images': [{'url': 'https://sclaboratories.s3.amazonaws.com/sample_photos/220527R012.jpg',
#    'filename': '220527R012.jpg'}],
#  'date_tested': '2022-05-31',
#  'status': 'Pass',
#  'batch_number': 'ROS32TP',
#  'batch_size': '1031.0 units',
#  'distributor': 'WELLNESS',
#  'distributor_license_number': 'C11-0000374-LIC',
#  'sum_of_cannabinoids': '86.34%',
#  'total_cannabinoids': '76.66%',
#  'total_thc': '71.742%',
#  'total_cbd': '0.20%',
#  'total_cbg': '3.89%',
#  'total_thcv': '0.315%',
#  'total_cbc': '0.517%',
#  'total_cbdv': 'ND',
#  'total_terpenes': '7.6976%',
#  'pesticides_status': 'Pass',
#  'mycotoxins_status': 'Pass',
#  'residual_solvents_status': 'Pass',
#  'heavy_metals_status': 'Pass',
#  'microbiology_status': 'Pass',
#  'foreign_material_status': 'Pass',
#  'coa_id': ' 220527R012-001',
#  'cannabinoid_method': 'QSP 1157 - Analysis of Cannabinoids by HPLC-DAD',
#  'terpenoid_method': 'QSP 1192 - Analysis of Terpenoids by GC-FID',
#  'pesticide_method': 'QSP 1212 - Analysis of Pesticides and Mycotoxins by LC-MS or QSP 1213 - Analysis of Pesticides by GC-MS',
#  'mycotoxin_method': 'QSP 1212 - Analysis of Pesticides and Mycotoxins by LC-MS',
#  'residual_solvents_method': 'QSP 1204 - Analysis of Residual Solvents by GC-MS',
#  'heavy_metals_method': 'QSP 1160 - Analysis of Heavy Metals by ICP-MS',
#  'microbiology_method': 'QSP 1221 - Analysis of Microbiological Contaminants',
#  'foreign_material_method': 'QSP 1226 - Analysis of Foreign Material in Cannabis and Cannabis Products',
#  'product_name': 'Test Product',
#  'sample_id': 'test-sample',
#  }]

        # Create usage log and save any public lab results.
        # changes = []
        # refs = []
        # docs = []
        # for item in data:
        #     if item.get('public'):
        #         changes.append(item)
        #         sample_id = item['sample_id']
        #         refs.append(f'public/data/lab_results/{sample_id}')
        #         docs.append(item)
        # if refs:
        #     update_documents(refs, docs)
        # create_log(
        #     'logs/website/coa_doc',
        #     claims=claims,
        #     action='Parsed CoAs.',
        #     log_type='coa_data',
        #     key='coa_data',
        #     changes=changes
        # )

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

    # FIXME: Gracefully handle errors!

    # Read the posted data.
    data = loads(request.body.decode('utf-8'))['data']

    # Optional: Perform safety checks?

    # FIXME: Create the Excel file as desired!

    # Create the response.
    # response = HttpResponse(content_type='text/csv')
    # response['Content-Disposition'] = 'attachment; filename="download.csv"'
    response = HttpResponse(data,content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=download.xlsx'

    # Create a long table of results.
    results = []
    for i, item in enumerate(data):
        for result in item['results']:
            result['sample_id'] = item['sample_id']
            results.append(result)
        del data[i]['results']

    # Save as double sheet Excel.
    writer = ExcelWriter(response)
    DataFrame(data).to_excel(writer, 'Details')
    DataFrame(results).to_excel(writer, 'Results')
    writer.save()

    # Save the results.
    # csv_writer = writer(response)
    # csv_writer.writerow(list(data[0].keys()))
    # for item in data:
    #     csv_writer.writerow(list(item.values()))

    # TODO: Sort the columns in a logical manner.

    return response

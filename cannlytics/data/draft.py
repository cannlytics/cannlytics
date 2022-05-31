import math
import requests

def nearest_number(x, base=50):
    """Round the given number, x, to the nearest base."""
    return base * math.ceil(x / base)


# FIXME:
def get_patent_details(patent_number, fields):
    """Get details for a specific patent."""
    base = 'https://api.patentsview.org/patents/query'
    fields = [f'"{x}"' for x in fields]
    url = base + r'?q={"patent_number": "' + patent_number + r'"}'
    url += '&f=[' + ','.join(fields) + ']'
    response = requests.get(url)
    data = response.json()['patents'][0]
    return data

# for index, values in patents.iterrows():
#     print(values['patent_number'])
#     patent_details = get_patent_details('D952244', ['patent_type'])

# # FIXME: Doesn't work with newer patent numbers, e.g. 11330778
# # For each patent, get the patent's details with it's patent number.
# # Guide: <https://patentsview.org/apis/api-endpoints/patents>
# patent_fields = [
#     'inventor_id',
#     'inventor_first_name',
#     'inventor_last_name',
#     'inventor_city',
#     'inventor_state',
#     'inventor_county',
#     'inventor_country',
#     'inventor_latitude',
#     'inventor_longitude',
#     'inventor_total_num_patents',
#     'patent_number',
#     'patent_date',
#     'patent_abstract',
#     'patent_kind',
#     'patent_title',
#     'patent_type',
# ]
# patent_details = get_patent_details('PP27475', patent_fields)


# Unnecessary? Get patent date.
# tables = soup.findAll('table')
# table = tables[2]
# patent_date = table.findAll('td')[-1].text
# patent_date = patent_date.replace('\n', '').strip()
# print('Patent date:', patent_date)

# Unnecessary? Get filed at.
# table = tables[3]
# values = table.findAll('tr')
# print([x.text for x in values])
# filed_at = values[-2].text

# Define time frame to search.
START = '2018-01-01T00:00:00Z'
TODAY = '2022-05-21T23:59:59Z'


    # 'fq':[
    #     f'appFilingDate:[{START} TO {TODAY}]',
    #     'appStatus:\"Patented Case\"'
    # ], # filter query
    # 'mm': '100%', # minimum match
    # 'sort': 'patentTitle asc',
    # 'start': '0',

#-----------------------------------------------------------------------
# SCRAP
#-----------------------------------------------------------------------

# from selenium import webdriver

# config = dotenv_values('../../.env')
# uspto_api_key = config['USPTO_API_KEY']

# # Test.
# base = 'https://tsdrapi.uspto.gov/ts/cd/casestatus/sn78787878/download.pdf'
# headers = {
#     'Accept': 'text/plain',
#     'USPTO-API-KEY': uspto_api_key
# }
# response = requests.get(base, headers=headers)

# base = 'https://patft.uspto.gov/netacgi/nph-Parser'
# params = {
#     'Sect1': 'PTO2',
#     'Sect2': 'HITOFF',
#     'p': '1',
#     'u': '%2Fnetahtml%2FPTO%2Fsearch-adv.htm',
#     'r': '1',
#     'f': 'G',
#     'l': '50',
#     'd': 'PTXT',
#     'S1': 'PP30434.PN.',
#     'OS': 'pn/PP30434',
#     'RS': 'PN/PP30434',
# }
# response = requests.get(base, headers=headers, params=params)

# import urllib

# &NextList2=Next+50+Hits

# abs_file_path = '../../.datasets/ai/plant-patents/pdfs/test.html'

# url = 'https://patft.uspto.gov/netacgi/nph-Parser?Sect1=PTO2&Sect2=HITOFF&u=%2Fnetahtml%2FPTO%2Fsearch-adv.htm&r=63&f=G&l=50&d=PTXT&s1=cannabis&p=2&OS=cannabis&RS=cannabis'
# with urllib.request.urlopen(url) as response, open(abs_file_path, 'wb') as out_file:

#     eventID = 123456

#     length = response.getheader('content-length')
#     if length:
#         length = int(length)
#         blocksize = max(4096, length//100)
#     else:
#         blocksize = 1000000 # just made something up


#     size = 0
#     while True:
#         buf1 = response.read(blocksize)
#         if not buf1:
#             break
#         out_file.write(buf1)
#         size += len(buf1)
#         if length:
#             print('\r[{:.1f}%] Downloading: {}'.format(size/length*100, eventID), end='')#print('\rDownloading: {:.1f}%'.format(size/length*100), end='')
#     print()

# # US PP30,434 P3
# # US00PP30434P3
# # US0000PP030434P320190423

# # # Search for plant patents.
# # expression = 'firstNamedApplicant:(*grohe*)'
# # params = 'appFilingDate:[2000-01-01T00:00:00Z TO 2015-12-31T23:59:59Z]'


# # # Download document by document number
# # # Automatically guesses the document type (application, publication, patent) from the document number schema



#-----------------------------------------------------------------------
# 2. Parse data from the plant patent PDF.
#-----------------------------------------------------------------------

# import pdfplumber

# # Open a patent PDF.
# patent_id = 'US0000PP033332P320210810'
# folder = '../../.datasets/ai/plant-patents/pdfs'
# file_path = f'{folder}/{patent_id}.pdf'
# pdf = pdfplumber.open(file_path)

# # Get all table data.
# table_data = []
# for page in pdf.pages:
#     tables = page.find_tables()
#     for table in tables:
#         data = table.extract()
#         table_data += data

# # Save all images.
# image_dir = './../.datasets/ai/plant-patents/images'
# for page in pdf.pages:
#     page_height = page.height
#     n = page.page_number

# page = pdf.pages[-1]
# page_height = page.height
# for i, image in enumerate(page.images):
#     image_path = f'.{image_dir}/plant.jpg'
#     image_bbox = (
#         0, page_height - image['y1'],
#         612.0, page_height - image['y0'],
#     )
#     print(image_bbox)
#     cropped_page = page.crop(image_bbox)
#     image_obj = cropped_page.to_image(resolution=400)
#     image_obj.save(image_path)

# # Get the exact time the patent was issued.
# # issued_at = pdf.metadata['CreationDate'].replace('D:', '')
# # issued_at = pd.to_datetime(issued_at)


#-----------------------------------------------------------------------
# Download patent PDFs (hard!).
#-----------------------------------------------------------------------

# Download the PDF for the patent.
user_agent = 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0'
headers = {'User-Agent': user_agent}
patent_number = '11330778'
base = 'https://pdfpiw.uspto.gov/.piw'
url = f'{base}?PageNum=0&docid={patent_number}'

# Test
url = 'http://www.pat2pdf.org/pat2pdf/foo.pl?number=PP33483'
response = requests.get(url, headers= headers)
soup = BeautifulSoup(response.content, features='lxml')
embed = soup.find('div', {'id': 'plugin'})
pdf_path = '../../.datasets/ai/plant-patents/pdfs'
pdf_path = download_file_from_url(url, pdf_path, ext='.pdf')


from selenium import webdriver

options = webdriver.ChromeOptions()
url = 'http://www.pat2pdf.org/pat2pdf/foo.pl?number=PP33483'
download_folder = '../../.datasets/ai/plant-patents/pdfs'  
profile = {
    'plugins.plugins_list': [{
        'enabled': False,
        'name': 'Chrome PDF Viewer'
    }],
    'download.default_directory': download_folder,
    'download.extensions_to_open': ''
}
options.add_experimental_option('prefs', profile)
driver = webdriver.Chrome(chrome_options=options)
driver.get(url)
filename = url.split('/')[4].split('.cfm')[0]
print("File: {}".format(filename))
print("Status: Download Complete.")
print("Folder: {}".format(download_folder))
driver.close()



user_agent = 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0'
headers = {'User-Agent': user_agent}

#-----------------------------------------------------------------------
# Future work: Make the functionality accessible through an API.
#-----------------------------------------------------------------------

class CannPatent(object):
    """An instance of this class communicates with the
    United States Patent and Trademark Office API to
    retrieve cannabis-related patent data.
    
    Get an API key: <https://account.uspto.gov/api-manager/>
    """


    def __init__(self):
        """Initialize an Open Data API client."""
        self.base = 'https://masscannabiscontrol.com/resource/'
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1667.0 Safari/537.36'}
        self.session = requests.Session()
    






analytes = {


    'delta_9_thc': {

        'cas': '',
        'keys': [
            'delta_9_thc',
            'd9-THC',
        ],
        'units': ['percent', 'mg/g']

    },

}


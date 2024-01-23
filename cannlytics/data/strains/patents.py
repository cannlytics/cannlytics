"""
CannPatent | Cannlytics
Copyright (c) 2022-2024 Cannlytics

Created: 5/21/2022
Updated: 1/21/2024
Authors: Keegan Skeate <https://github.com/keeganskeate>
License: MIT License <https://opensource.org/licenses/MIT>

Description:

    Find and curate data for cannabis patents. In particular, this
    script collects detailed data for plant patents. Subsequent
    intellectual property (IP) analytics provide actionable insights
    for cannabis cultivar inventors and consumers. For example,
    cultivators can use the methodology to predict if a particular
    cultivar would make a good patent candidate given its lab results.
    Consumers can find the nearest patented strain to a set of lab results
    printed on a cultivar's label.

Data Source:

    - United States Patent and Trademark Office
    URL: <www.uspto.gov>

Requirements

    - ImageMagick
    Download: <https://imagemagick.org/script/download.php#windows>
    Running in the Cloud: <https://stackoverflow.com/questions/43036268/do-i-have-access-to-graphicsmagicks-or-imagemagicks-in-a-google-cloud-function>

"""
# Standard imports:
from datetime import datetime
import math
import os
import re
from time import sleep
from typing import Any, Optional, Union

# External imports:
from bs4 import BeautifulSoup
import pdfplumber
import pandas as pd
from pytesseract import  image_to_string
import requests

# Internal imports:
from cannlytics.utils.constants import DEFAULT_HEADERS
from cannlytics.data.web import initialize_selenium
from cannlytics.firebase.firebase import (
    initialize_firebase,
    update_document,
    update_documents,
)
from cannlytics.utils.utils import (
    camel_to_snake,
    clean_dictionary,
    kebab_case,
)

# Selenium imports:
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# DEV:
# from PIL import Image
# import tempfile
# from pdf2image import convert_from_path
# import pdfplumber
# from pytesseract import image_to_pdf_or_hocr


# class StrainLabResults(BaseModel):
#     """A data class representing a cannabis strain."""
#     key: str
#     avg: float
#     min: float
#     max: float
#     median: float
#     std: float
#     sample_ids: List[str]


# class Strain(BaseModel):
#     """A data class representing a cannabis strain."""
#     cultivar: str
#     strain_name: str
#     first_produced_at: str
#     first_produced_by: str
#     first_produced_state: str
#     number_of_tests: int
#     results: List[StrainLabResults]


# class CannPatent():
#     """Cultivar identifier."""
#     pass


# FIXME: Try to find a working URL.
PATENT_SEARCH_BASE_URL = 'http://appft.uspto.gov/netacgi/nph-Parser'
PATENT_SEARCH_URL = 'https://ppubs.uspto.gov/pubwebapp/static/pages/ppubsbasic.html'
# Old: 'https://developer.uspto.gov/ibd-api'


def search_patents(
        query: str,
        limit: Optional[int] = 50,
        details: Optional[bool] = False,
        pause: Optional[float] = None,
        term: Optional[str] = '',
    ) -> pd.DataFrame:
    """Search for patents.
    Args:
        query (str): The search term.
        limit (int): The number of patents to retrieve, 50 by default.
            The algorithm requests patents in batches of 50.
        details (bool): Whether or not to return extensive details for
            each patent. The default is `False`.
    Returns:
        (DataFrame): The patents' data.
    """

    # Define the query URL.
    query = query.replace(' ', '+')
    base = PATENT_SEARCH_BASE_URL
    headers = DEFAULT_HEADERS
    # headers = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0'}
    url = f'{base}?Sect1=PTO2&Sect2=HITOFF&u=%2Fnetahtml%2FPTO%2Fsearch-adv.htm&r=0&p=1&f=S&l=50&Query='
    url += f'{term}"{query}"&d=PTXT'
    print(url)

    # Future work: Allow user to specify date ranges for the search query.
    # ISD/11/1/1997->5/12/1998

    # Iterate over found items, 50 per page.
    patents = pd.DataFrame()
    pages = math.ceil(limit / 50)
    page_range = range(0, int(pages))
    for increment_page in page_range[:1]:

        # Get cannabinoid patents.
        if increment_page:
            url += f'&OS={query}&RS={query}'
            url += f'&TD=6080&Srch1={query}&NextList{increment_page + 1}=Next+50+Hits'
        # FIXME:
        # try:
        response = requests.get(url, headers=headers)
        # except:
        #     print('Error on page', increment_page)
        #     sleep(62)
        #     response.connection.close()
        #     response = requests.get(url, headers=headers)
        #     # try:
        #     #     response = requests.get(url, headers=headers)
        #     # except:
        #     #     continue
        if pause:
            sleep(pause)

        # Create lists of patents, titles, and URLs.
        soup = BeautifulSoup(response.content, features='html.parser')
        ids = []
        patent_numbers = []
        titles = []
        links = []
        for link in soup.find_all('a', href=True):
            if link.text and (link.text.startswith('PP') or (len(link.text) <= 10 and ',' in link.text)):
                ids.append(link.text)
                patent_number = link.text.replace(',', '')
                patent_numbers.append(patent_number)
                title_link = link.findNext('a')
                titles.append(title_link.text.strip())
                links.append('http://patft.uspto.gov' + title_link['href'])

        # Format the patents as a DataFrame.
        if patent_numbers == 0:
            break
        patents = pd.concat([patents, pd.DataFrame({
            'patent_number': patent_numbers,
            'patent_number_formatted': ids,
            'patent_title': titles,
            'patent_url': links,
        })])

        # Optionally get details for each patent.
        # Note: This can probably be done more efficiently.
        if details:
            patent_details = []
            for _, patent in patents[:limit].iterrows():
                patent_detail = get_patent_details(patent)
                patent_details.append(patent_detail)
            patents = pd.concat(patent_details, axis=1)
            if isinstance(patents, pd.Series):
                patents = patents.to_frame()
            patents = patents.transpose()

    # Return the patents found.
    return patents


def get_patent_details(
        data: Optional[Any] = None,
        patent_number: Optional[str] = None,
        patent_url: Optional[str] = None,
        headers = None,
        fields: Optional[Union[str, list]] = None,
        search_field: Optional[str] = 'patentNumber',
        search_fields: Optional[str] = 'patentNumber',
        query: Optional[str] = 'patentNumber',
    ) -> Any:
    """Get details for a given patent, given it's patent number and URL.
    Args:
        data (Series): Existing patent data with `patent_number` and
            `patent_url` fields (optional). If not specified, then
            pass `patent_number` and `patent_url` arguments.
        patent_number (str): A specific patent number (optional).
        patent_url (str): A specific patent URL (optional).
        user_agent (str): Your browser agent (optional). A typical Chrome
            agent by default.
        fields (list): A list of fields to return. You can use '*' for
            all fields. A curated selection is used by default.
    Returns:
        (Series): The detailed patent data.
    References:
        - https://ped.uspto.gov/peds/#!/#%2FapiDocumentation
    """

    # Ensure that a patent number and patent URL are passed.
    if data is None and patent_number:
        patent = pd.Series({
            'patent_number': patent_number,
            'patent_url': patent_url,
        })
    elif data is not None:
        patent = data
        patent_number = patent['patent_number']
    else:
        raise ValueError

    # Specify the fields to return.
    if fields is None:
        fields = [
            'appType',
            'appFilingDate',
            # 'inventorName',
            # 'inventors',
            # 'patentIssueDate',
        ] # 'attrnyAddr',
    if isinstance(fields, str):
        field_list = fields
    else:
        field_list = ','.join(fields)

    # FIXME: Request fields for the patent.
    base = 'https://ped.uspto.gov/api/queries'
    if headers is None:
        # headers = DEFAULT_HEADERS
        headers = headers = {'Content-Type': 'application/json'}
    patent_id = patent_number.replace('US-', '').replace(',', '').split('-')[0]
    data = {
        'searchText': f'{query}:({patent_id})',
        'fl': field_list, # field list
        'df': search_field, # default field to search
        'qf': search_fields, # multiple fields to search
        'facet': 'false',
        'mm': '80%', # minimum match
        'sort': f'{search_field} asc',
        'start': '0',
    }
    print('Querying:', data)
    response = requests.post(base, json=data, headers=headers)
    print(response.text)

    # Add the patent details.
    data = response.json()
    docs = data['queryResults']['searchResponse']['response']['docs']
    doc = docs[0]
    doc = clean_dictionary(doc, function=camel_to_snake)

    # Optional: Get the attorney data.
    # doc['attorney'] = [clean_dictionary(x, function=camel_to_snake) for x in doc['attrny_addr']]
    # del doc['attrny_addr']
    
    # FIXME: Get the inventor data (from the text if not present here).
    try:
        doc['inventor_name'] = doc['inventor_name'].title()
        doc['inventors'] = [clean_dictionary(x, function=camel_to_snake) for x in doc['inventors']]
        inventor = doc['inventors'][0]
        doc['inventor_city'] = inventor['city'].replace(',', '').title()
        doc['inventor_state'] = inventor['geo_code']
        doc['inventor_country'] = inventor['country'].replace('(', '').replace(')', '')
    except KeyError:
        pass
    
    # Merge details with patent.
    patent = pd.concat([patent, pd.Series(doc)])

    # Get patent text by parsing the patent's webpage.
    response = requests.get(patent['patent_url'], headers=headers)
    soup = BeautifulSoup(response.content, features='html.parser')

    # Get the abstract.
    patent['abstract'] = soup.p.text.strip().replace('\n     ', ' ')

    # Get the applicant.
    tables = soup.findAll('table')
    values = [x.text.strip() for x in tables[3].findAll('td')]
    try:
        patent['applicant_name'] = values[2]
        patent['applicant_city'] = values[3]
        patent['applicant_state'] = values[4]
        patent['applicant_country'] = values[5]
    except IndexError:
        print('Error parsing applicant:', values)

    # Get the claims.
    # Test: Handle `It is claimed:`.
    claims = soup.text.split('claimed is:')[-1].split('claimed:')[0]
    claims = claims.split('Description  BACKGROUND OF THE INVENTION')[0]
    claims = claims.strip()
    claims = re.split('(\n\s\d.\s\s)', claims)
    claims = claims[::2]
    claims[0] = claims[0].replace('1.  ', '')
    patent['claims'] = [x.replace('\n', ' ').strip() for x in claims]

    # TODO: Get plant details.

    # '\nSeeds\n '
    # Market Class: 
    # patent['parentage'] = soup.text.split('Parentage: ')[1].split(':')[0]
    # patent['classification'] = soup.text.split('Classification: ')[1].split(':')[0]

    # TODO: Get lab results?
    # soup.text.split('TABLE-US-')[1]

    # TODO: Get more patent details.
    # - citations_applicant_count
    # - full text (description)

    # TODO: Extract links to references.
    # tables[8].text

    # Return the augmented patent data.
    return patent

# DEV:
# get_patent_details(patent)
get_patent_details(pd.Series({
    'patent_number': '*'
}),)


def get_strain_name(x):
    """Get a strain name in text surrounded by tildes."""
    try:
        return re.search('`(.*)`', x).group(1)
    except AttributeError:
        return ''


# === Tests ===
# Tested: 2024-01-21 by Keegan Skeate <keegan@cannlytics.com>
if __name__ == '__main__':

    # === Setup ===

    # Specify directories.
    data_dir = 'D://data/strains/patents/datasets/'
    pdf_dir = 'D://data/strains/patents/pdfs/'
    image_dir = 'D://data/strains/patents/images/'
    env_file = '.env'


    #-------------------------------------------------------------------
    # Find cannabis plant patents.
    #-------------------------------------------------------------------

    # TODO: Iterate over search terms.
    queries = [
        ('cannabis', ''),
        ('cannabis', 'plant'),
        ('cannabis', 'cultivar'),
        ('cannabis', 'variety'),
        ('hemp', ''),
        ('hemp', 'plant'),
        ('hemp', 'cultivar'),
        ('hemp', 'variety'),
        ('marijuana', ''),
        ('marijuana', 'plant'),
        ('marijuana', 'cultivar'),
        ('marijuana', 'variety'),
    ]

    # Initialize a web driver.
    driver = initialize_selenium(headless=False)

    # Get the patent search page.
    driver.get(PATENT_SEARCH_URL)

    # Search for patents.
    # TODO: Iterate over all search terms.
    search_terms = {
        'searchText1': 'cannabis',
        'searchText2': 'cultivar'
    }
    for element_id, term in search_terms.items():
        input_element = driver.find_element(By.ID, element_id)
        input_element.clear()
        input_element.send_keys(term)

    # Click the search button.
    search_button = driver.find_element(by=By.ID, value='searchText2')
    search_button.send_keys(Keys.ENTER)
    sleep(3)

    # Iterate over search result pages.
    iterate = True
    patents = []
    while iterate:

        # Wait until the overlay is no longer visible.
        WebDriverWait(driver, 3).until(EC.invisibility_of_element((By.CSS_SELECTOR, '.overlay.full-page')))

        # Extract the page number and total number of pages.
        page_info_span = driver.find_element(By.ID, 'pageInfo')
        page_info_text = page_info_span.text
        current_page, total_pages = page_info_text.split(" of ")
        current_page = current_page.replace('Page ', '')
        
        # Get the metadata for each patent.
        metadata = []
        table = driver.find_element(by=By.ID, value='searchResults')
        rows = table.find_elements(by=By.TAG_NAME, value='tr')[1:]
        print('Getting %i patents on page' % len(rows), current_page, 'of', total_pages)
        for row in rows:
            metadata.append({
                'query_number': row.find_element(By.XPATH, './td[1]').text,
                'patent_number': row.find_element(By.XPATH, './td[2]').text,
                'patent_title': row.find_element(By.XPATH, './td[4]').text,
                'inventor_name': row.find_element(By.XPATH, './td[5]').text,
                'date_published': row.find_element(By.XPATH, './td[6]').text,
                'page_count': int(row.find_element(By.XPATH, './td[7]').text)
            })

        # Add URLs to the list of dictionaries.
        count = 0
        links = driver.find_elements(by=By.TAG_NAME, value='a')
        for i, link in enumerate(links):
            href = link.get_attribute('href')
            if href and 'image-ppubs.uspto.gov' in href:
                metadata[count]['patent_url'] = href
                count += 1
        
        # Record the patent data.
        patents.extend(metadata)
        
        # Click the next button if it's not the last page.
        if current_page != total_pages:
            next_button = WebDriverWait(driver, 3).until(
                EC.element_to_be_clickable((By.ID, 'paginationNextItem'))
            )
            next_button.click()
        else:
            iterate = False

    # Close the driver.
    print('Found %i patents, closing driver.' % len(patents))
    driver.quit()

    # Save the patent metadata.
    print('Saving patent metadata...')
    date = datetime.now().strftime('%Y-%m-%d')
    metadata_file = f'D://data/strains/patents/patent-metadata-{date}.xlsx'
    patent_data = pd.DataFrame(patents)
    patent_data.to_excel(metadata_file)
    print('Patent metadata saved:', metadata_file)


    #-----------------------------------------------------------------------
    # Get patents with strain names in their titles.
    #-----------------------------------------------------------------------

    # Isolate plant patents.
    strains = patent_data.loc[
        (patent_data['patent_title'].str.contains('plant', case=False)) |
        (patent_data['patent_title'].str.contains('cultivar', case=False))
    ]
    print('Found %i cultivar patents.' % len(strains))

    # Extract all text after "named"
    strain_names = strains['patent_title'].str.extract(r"named (.*)")

    # Remove apostrophes from the extracted strain names
    strain_names = strain_names.replace("'", "")

    # Remove non-standard characters from the strain names
    strains = strains.assign(strain_name=strain_names)
    strains['strain_name'] = strains['strain_name'].apply(
        lambda x: re.sub(r'[^a-zA-Z0-9\s]', '', str(x)) \
            if pd.notnull(x) else x).str.strip()

    # Keep only strains with strain names.
    strains = strains.loc[strains['strain_name'].notnull()]
    print(strains['strain_name'].unique())


    #------------------------------------------------------------
    # Extract data from downloaded patents.
    #------------------------------------------------------------

    # Download patent images.
    print('Downloading patent images...')
    for index, patent in strains.iterrows():
        outfile = os.path.join(pdf_dir, patent['patent_number'] + '.pdf')
        if os.path.exists(outfile):
            print('Cached:', outfile)
            continue
        response = requests.get(patent['patent_url'])
        with open(outfile, 'wb') as file:
            file.write(response.content)
        print('Downloaded:', outfile)

    # Extract the text from all strain patents.
    extracted_data = {}
    for index, strain in strains.iterrows():
        patent_number = strain['patent_number']
        original_file = os.path.join(pdf_dir, patent_number + '.pdf')
        pdf_image = os.path.join(image_dir, patent_number + '.png')

        # Check the number of pages.
        report = pdfplumber.open(original_file)
        page_count = len(report.pages)
        print('Parsing patent %s (%i pages)...' % (patent_number, page_count))

        # Save the first page as an image.
        im = report.pages[0].to_image(resolution=90)
        im.save(pdf_image, format='PNG')

        # Close the report.
        report.close()

        # Read the text of the first page.
        page_text = image_to_string(pdf_image)
        abstract = page_text.split('ABSTRACT')[1].split('Claims')[0]

        # Record the extracted data.
        obs = {'abstract': abstract}
        extracted_data[patent_number] = {**strain.to_dict(), **obs}
        print('Extracted data for patent:', patent_number)


    # TODO: Explore the abstracts with OpenAi's ChatGPT model!
    for patent_number, obs in extracted_data.items():
        print(len(obs['abstract'].split(' ')))

    # Get additional patent details.
    for index, patent in strains.iterrows():
        patent_number = patent['patent_number']
        patent_detail = get_patent_details(patent)
        extracted_data[patent_number] = {**extracted_data[patent_number], **patent_detail.to_dict()}
        print('Extracted details for patent:', patent_number)

    
    # TODO: Extract data points:
    # - patent_number_formatted
    # - patent_type
    # - patent_link
    # - patent_issue_date
    # - patent_year
    # - patent_month
    # - app_type
    # - app_filing_date
    # - inventors
    # - inventor_name
    # - inventor_city
    # - inventor_state
    # - strain_name
    # - key
    # - type
    # - description
    # - lineage
    # - average total cannabinoids
    # - average total thc
    # - average total cbd
    # - average total terpenes
    # - major terpenes
    # - THCV to THC ratio.
    # - THCV to total cannabinoid ratio.
    # - THC / CBD ratio.
    # - CBD / CBC / THC ratio.
    # - All terpene ratios!!!


    # TODO: Save the extracted patent data.
        

    
    # #-------------------------------------------------------------------
    # # 3. Organize all plant patent data points.
    # # - Key
    # # - Type
    # # - Description
    # # - Possible values
    # # - Relation to other variables?
    # #-------------------------------------------------------------------
        
    # FIXME: Refactor statistics.

    # # # Read manually collected plant patent data.
    # # datafile = '../../.datasets/ai/plant-patents/plant-patents.xlsx'
    # # results = pd.read_excel(datafile, sheet_name='Patent Lab Results')
    # # results['patent_number'] = results['patent_number'].astype(str)

    # # Read programmatically collected plant patent data.
    # filename = 'plant-patents.xlsx'
    # datafile = os.path.join(data_dir, filename)
    # details = pd.read_excel(datafile, sheet_name='Patent Details')
    # details['patent_type'] = 'Plant'
    # details['patent_link'] = 'http://www.pat2pdf.org/pat2pdf/foo.pl?number=' + details['patent_number'].astype(str)
    # details['patent_number'] = details['patent_number'].astype(str)

    # # # Merge average lab results with details.
    # # avg_results = results.groupby('patent_number', as_index=False).mean()
    # # details = pd.merge(
    # #     left=details,
    # #     right=avg_results,
    # #     left_on='patent_number',
    # #     right_on='patent_number',
    # # )

    # # Count plant patents over time.
    # details['date'] = pd.to_datetime(details['patent_issue_date'])
    # group = details.groupby(pd.Grouper(key='date', freq='Y'), as_index=True)
    # yearly = group['patent_number'].count()
    # yearly = yearly.to_frame()
    # yearly['year'] = pd.to_datetime(yearly.index).strftime('%Y')
    # yearly.rename(columns={'patent_number': 'plant_patents'}, inplace=True)
    # annual_stats = yearly[['plant_patents', 'year']].to_dict(orient='records')

    # # Optional: Calculate statistics from patent data.
    # # - THCV to THC ratio.
    # # - THCV to total cannabinoid ratio.
    # # - THC / CBD ratio.
    # # - CBD / CBC / THC ratio.
    # # - All terpene ratios!!!

    # # Ridge plots for cultivars with cannabinoid terpene data.
    # # BONUS: Use as an image for the patent (chemotype fingerprint)!


    # # Regression plots of ratios with all strains colored by strain.


    # #-------------------------------------------------------------------
    # # 4. Upload the patent data.
    # #-------------------------------------------------------------------

    # # # Initialize Firebase!
    # # initialize_firebase(env_file=env_file)
        
    # TODO: Download the PDF for the patent.
    # - Upload the PDF to Firebase Storage, saving the ref with the data.
        
    # TODO: Crop all images for each patent.
    # Upload the images to Firebase Storage for access online / through the API.

    # # # Update the base patents document with statistics.
    # # update_document('public/stats/patents/plant_patents', {
    # #     'annual_plant_patents': annual_stats,
    # # })

    # # # Upload the plant patent data to Firestore for API access.
    # # col = 'public/data/patents'
    # # refs = [f'{col}/{x}' for x in details['patent_number']]
    # # data = details.to_dict(orient='records')
    # # update_documents(refs, data)

    # # # Upload the patent lab results data to Firestore for API access.
    # # results['id'] = results.index
    # # values = results[['patent_number', 'id']].values
    # # refs = [f'{col}/{x[0]}/patent_lab_results/lab_result_{x[1]}' for x in values]
    # # data = results.to_dict(orient='records')
    # # update_documents(refs, data)


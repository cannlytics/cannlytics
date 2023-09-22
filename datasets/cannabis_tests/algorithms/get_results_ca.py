"""
Get California cannabis lab results
Copyright (c) 2023 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
    Candace O'Sullivan-Sutherland <https://github.com/candy-o>
Created: 5/25/2023
Updated: 5/30/2023
License: <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description:

    Archive California cannabis lab result data.

Data Sources:

    - [Glass House Farms Strains](https://glasshousefarms.org/strains/)

"""
# Standard imports:
from datetime import datetime
import os
from time import sleep

# External imports:
from cannlytics.data.coas.coas import CoADoc
from bs4 import BeautifulSoup
from cannlytics.utils.constants import DEFAULT_HEADERS
import pandas as pd
import requests


# Glass House Farms constants.
GLASS_HOUSE_FARMS = {
    'business_dba_name': 'Glass House Farms',
    'business_website': 'https://glasshousefarms.org',
    'business_image_url': 'https://glassfarms.wpenginepowered.com/wp-content/uploads/2021/10/new-ghf-menu.svg',
    'producer_license_number': 'CCL18-0000512',
    'producer_latitude': 34.404930,
    'producer_longitude': -119.518250,
    'producer_street_address': '5601 Casitas Pass Rd, Carpinteria, CA 93013',
    'producer_city': 'Carpinteria',
    'producer_county': 'Santa Barbara',
    'producer_state': 'CA',
    'lab_results_url': 'https://glasshousefarms.org/strains/',
    # TODO: The data below should be pulled from the license data.
    'license_status': 'Active',
    'license_status_date': '2023-04-07T00:00:00',
    'license_term': 'Annual',
    'license_type': 'Cultivation -  Small Mixed-Light Tier 1',
    'license_designation': 'Medicinal',
    'issue_date': '2019-03-11T00:00:00',
    'expiration_date': '2024-03-11T00:00:00',
    'licensing_authority_id': 'CCL',
    'licensing_authority': 'CalCannabis Cultivation Licensing (CCL)',
    'business_legal_name': 'Mission Health Associates, Inc. dba Glass House Farms',
    'business_owner_name': 'Graham Farrar, Kyle Kazan',
    'business_structure': 'Corporation',
    'business_phone': '(805) 252-5755',
    'parcel_number': '001-060-042',
}

# Strain type constants.
STRAIN_TYPES = {
    'sativa': {'sativa_percentage': 1.0, 'indica_percentage': 0.0},
    'sativaDominant': {'sativa_percentage': 0.75, 'indica_percentage': 0.25},
    'hybrid': {'sativa_percentage': 0.5, 'indica_percentage': 0.5},
    'indica': {'sativa_percentage': 0.0, 'indica_percentage': 1.0},
    'indicaDominant': {'sativa_percentage': 0.25, 'indica_percentage': 0.75},
    'cbd': {'sativa_percentage': 0.0, 'indica_percentage': 0.0},
    'cbdt': {'sativa_percentage': 0.0, 'indica_percentage': 0.0},
}

# TODO: Get license data from either Hugging Face or locally.
# from datasets import load_dataset

# license_number = GLASS_HOUSE_FARMS['producer_license_number']
# licenses = load_dataset('cannlytics/cannabis_licenses', 'ca')
# licenses = licenses['data'].to_pandas()
# licenses = pd.read_csv(f'../../cannabis_licenses/data/ca/licenses-ca-latest.csv')
# criterion = licenses['license_number'].str.contains(license_number)
# match = licenses.loc[criterion]
# if len(match) != 0:
#     licensee = match.iloc[0]
#     print('Found licensee data:', licensee)
#     obs['producer_county'] = licensee['premise_county']
#     obs['producer_latitude'] = licensee['premise_latitude']
#     obs['producer_longitude'] = licensee['premise_longitude']
#     obs['producer_license_number'] = licensee['license_number']


def get_glass_house_farms_lab_results(data_dir: str, overwrite=False):
    """Get lab results published by Glass House Farms.
    Data points:
        ✓ image_url
        ✓ strain_id
        ✓ strain_name
        ✓ strain_type
        ✓ indica_percentage
        ✓ sativa_percentage
        ✓ strain_url
        ✓ lineage
        ✓ lab_result_id
        ✓ coa_url
    """

    # Create output directory.
    license_number = GLASS_HOUSE_FARMS['producer_license_number']
    license_pdf_dir = os.path.join(data_dir, f'.datasets/{license_number}/pdfs')
    if not os.path.exists(license_pdf_dir):
        os.makedirs(license_pdf_dir)

    # Read the strains website.
    url = 'https://glasshousefarms.org/strains/'
    response = requests.get(url, headers=DEFAULT_HEADERS)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Get the data for each strain.
    observations = []
    strains = soup.find_all(class_='item')
    for strain in strains:
        obs = {}

        # Extract image URL
        img_tag = strain.find('img')
        obs['image_url'] = img_tag['src']

        # Extract item type
        strain_type = strain.find('h5').text
        obs['strain_type'] = strain_type

        # Extract item name
        strain_name = strain.find('h4').text
        strain_name = strain_name.replace('\n', '').replace(strain_type, '').strip()
        obs['strain_name'] = strain_name

        # Get the strain URL.
        strain_url = strain.find('a', class_='exp')['href']
        obs['strain_url'] = strain_url

        # Get the strain ID.
        obs['strain_id'] = strain_url.rstrip('/').split('/')[-1]

        # Get the indica and sativa percentages.
        wave = strain.find('div', class_='wave')
        wave_class = wave.get('class')
        wave_class = [cls for cls in wave_class if cls != 'wave']
        if wave_class:
            for cls in wave_class:
                if cls in STRAIN_TYPES:
                    obs['indica_percentage'] = STRAIN_TYPES[cls]['indica_percentage']
                    obs['sativa_percentage'] = STRAIN_TYPES[cls]['sativa_percentage']
                    break

        # Record the observation.
        observations.append(obs)

    # Compile the strain data.
    strain_data = pd.DataFrame(observations)

    # Save the strain data.
    date = datetime.now().strftime('%Y-%m-%d')
    outfile = os.path.join(data_dir, f'ca-strains-{date}.xlsx')
    strain_data.to_excel(outfile, index=False)

    # Get the lab results for each strain.
    lab_results = []
    for obs in observations:

        # Get the strain page.
        sleep(3.33)
        response = requests.get(obs['strain_url'] , headers=DEFAULT_HEADERS)
        soup = BeautifulSoup(response.content, 'html.parser')

        # Get the lineage.
        try:
            content = soup.find('div', class_='content')
            divs = content.find_all('div', class_='et_pb_column')
        except:
            print('No content found:', obs['strain_url'])
            continue
        try:
            lineage = divs[2].text.split('Lineage')[1].replace('\n', '').strip()
            obs['lineage'] = lineage.split(' x ')
        except:
            print('No lineage found:', obs['strain_url'])
            obs['lineage'] = []

        # Get all of the COA PDF links found.
        pdf_links = []
        for link in soup.find_all('a'):
            href = link.get('href')
            if href and href.endswith('.pdf'):
                pdf_links.append(href)

        # Format all of the COA PDF links found.
        for link in pdf_links:
            lab_result_id = link.split('/')[-1].split('.')[0]
            result = {'coa_url': link, 'lab_result_id': lab_result_id}
            lab_results.append({**GLASS_HOUSE_FARMS, **obs, **result})

    # Download COA PDFs.
    for lab_result in lab_results:
        lab_result_id = lab_result['lab_result_id']
        outfile = os.path.join(license_pdf_dir, f'{lab_result_id}.pdf')
        if os.path.exists(outfile) and not overwrite:
            continue
        sleep(1)
        response = requests.get(lab_result['coa_url'], headers=DEFAULT_HEADERS)
        with open(outfile, 'wb') as pdf:
            pdf.write(response.content)
        print('Downloaded: %s' % outfile)

    # Save all lab results.
    results = pd.DataFrame(lab_results)
    date = datetime.now().strftime('%Y-%m-%d')
    outfile = os.path.join(data_dir, f'ca-lab-results-{date}.xlsx')
    results.to_excel(outfile, index=False)

    # Initialize CoADoc.
    parser = CoADoc()

    # Parse the data from all COAs.
    coa_data = []
    for _, result in results.iterrows():
        lab_result_id = result['lab_result_id']
        pdf_file = os.path.join(license_pdf_dir, f'{lab_result_id}.pdf')  
        if not os.path.exists(pdf_file):
            print('File not found:', pdf_file)
            continue
        try:
            parsed = parser.parse(pdf_file)
            coa_data.append({**result.to_dict(), **parsed[0]})
            print('Parsed:', pdf_file)
        except:
            print('Error parsing:', pdf_file)
            continue

    # Save the lab results.
    date = datetime.now().strftime('%Y-%m-%d')
    outfile = os.path.join(data_dir, f'ca-lab-results-{date}.xlsx')
    try:
        parser.save(coa_data, outfile)
    except:
        try:
            coa_df = pd.DataFrame(coa_data)
            coa_df.to_excel(outfile, index=False)
            print('Saved %i results:' % len(coa_data), outfile)
        except:
            print('Error saving:', outfile)
    
    # Return the data.
    return pd.DataFrame(coa_data)


# === Test ===
# [✓] Tested: 2023-08-14 by Keegan Skeate <keegan@cannlytics>
if __name__ == '__main__':

    # Specify where your data lives.
    data_dir = 'D://data/california/lab_results'

    # Get CA lab results.
    # ca_results = get_glass_house_farms_lab_results(data_dir)


# DEV: Parse all COAs in directory.
parser = CoADoc()
license_number = GLASS_HOUSE_FARMS['producer_license_number']
license_pdf_dir = os.path.join(data_dir, f'.datasets/{license_number}/pdfs')
# pdf_files = os.listdir(license_pdf_dir)
# pdf_files.reverse()

outfile = os.path.join(data_dir, f'ca-lab-results-2023-09-21.xlsx')
results = pd.read_excel(outfile)

# Parse the data from all COAs.
coa_data = []
for _, result in results.iterrows():
    lab_result_id = result['lab_result_id']
    pdf_file = os.path.join(license_pdf_dir, f'{lab_result_id}.pdf')  
    if not os.path.exists(pdf_file):
        print('File not found:', pdf_file)
        continue
    try:
        parsed = parser.parse(pdf_file)
        coa_data.append({**result.to_dict(), **parsed[0]})
        print('Parsed:', pdf_file)
    except:
        print('Error parsing:', pdf_file)
        continue
# coa_data = []
# for index, result in results.iterrows():
#     try:
#         file_name = os.path.join(license_pdf_dir, pdf_file)
#         obs = parser.parse(file_name)
#         coa_data.append(obs[0])
#         print('Parsed:', pdf_file)
#     except Exception as e:
#         print('Error parsing:', pdf_file)
#         print(e)
#         continue

# Save the lab results.
date = datetime.now().strftime('%Y-%m-%d')
outfile = os.path.join(data_dir, f'ca-lab-results-{date}.xlsx')
try:
    parser.save(coa_data, outfile)
except:
    try:
        coa_df = pd.DataFrame(coa_data)
        coa_df.to_excel(outfile, index=False)
    except:
        print('Error saving:', outfile)

print('Saved %i results:' % len(coa_data), outfile)

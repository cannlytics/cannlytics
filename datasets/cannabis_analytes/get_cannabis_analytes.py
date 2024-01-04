"""
Cannabis Analytes
Copyright (c) 2023 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
    Candace O'Sullivan-Sutherland <https://github.com/candy-o>
Created: 10/10/2023
Updated: 10/10/2023
License: <https://huggingface.co/datasets/cannlytics/cannabis_analytes/blob/main/LICENSE>
"""
# Standard imports:
import json
import os
from time import sleep

# External imports:
from bs4 import BeautifulSoup
import requests


def get_chemical_data(url):
    """Get chemical data from Wikipedia page."""
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    infobox = soup.find('table', {'class': 'infobox'})
    if not infobox:
        return None
    rows = infobox.find_all('tr')
    data = {}
    for row in rows:
        header_cell = row.find('th')
        data_cell = row.find('td')
        if header_cell and data_cell:
            key_text = header_cell.get_text()
            if 'Chemical formula' in key_text or 'Formula' in key_text:
                data['chemical_formula'] = data_cell.get_text().strip()
            elif 'Molar mass' in key_text:
                data['molar_mass'] = data_cell.get_text().strip()
            elif 'Density' in key_text:
                data['density'] = data_cell.get_text().strip()
            elif 'Boiling point' in key_text:
                data['boiling_point'] = data_cell.get_text().strip()
    if not data:
        for row in rows:
            row_text = row.get_text()
            if 'Chemical formula' in row_text or 'Formula' in row_text:
                key = 'chemical_formula'
            elif 'Molar mass' in row_text:
                key = 'molar_mass'
            elif 'Density' in row_text:
                key = 'density'
            elif 'Boiling point' in row_text:
                key = 'boiling_point'
            else:
                continue
            parts = [x for x in row_text.split('\n') if x]
            data[key] = parts[1].strip()
    return data


def standardize_chemical_data(data: dict):
    """Standardize chemical data.
    Notes: Density is measured in g/mL, Molar mass is measured in g/mol,
    and boiling point is measured in °C.
    """
    standardized_data = {}
    
    # Standard chemical formula.
    standardized_data['chemical_formula'] = data.get('chemical_formula')
    
    # Standard molar mass.
    try:
        standardized_data['molar_mass'] = float(data['molar_mass'].split()[0])
    except:
        standardized_data['molar_mass'] = None
  
    # Standard density.
    try:
        density_value = float(data['density'].split('\xa0g')[0])
    except:
        density_value = None
    standardized_data['density'] = density_value
    
    # Standard Celsius boiling point.
    try:
        bp_celsius = float(data['boiling_point'].split('\xa0°C;')[0])
    except:
        bp_celsius = None
    standardized_data['boiling_point'] = bp_celsius
  
    return standardized_data


def add_chemical_data_for_analytes(analytes):
    """Augment the chemical data for a list of analytes."""
    for i, analyte in enumerate(analytes):
        url = analyte['wikipedia_url']
        if not url:
            continue
        chemical_data = get_chemical_data(url)
        if chemical_data:
            standard_chemical_data = standardize_chemical_data(chemical_data)
            analytes[i].update(standard_chemical_data)
        sleep(1)
    return analytes


def get_wikipedia_summary(title, num_sentences=3):
    """Get a brief summary of a Wikipedia page using the Wikipedia API."""
    try:
        base_url = "https://en.wikipedia.org/w/api.php"
        params = {
            'format': 'json',
            'action': 'query',
            'prop': 'extracts',
            'exintro': True,
            'explaintext': True,
            'titles': title,
            'exsentences': num_sentences
        }
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        data = response.json()
        page = next(iter(data['query']['pages'].values()))
        return page.get('extract', None)
    except Exception as e:
        print(f"Error fetching summary for {title}: {e}")
        return None


def add_descriptions_to_analytes(analytes):
    """Fetch and add Wikipedia summaries to analytes."""
    for analyte in analytes:
        analyte_name = analyte.get('scientific_name', analyte['name'])
        description = get_wikipedia_summary(analyte_name)
        sleep(1)
        if description:
            analyte['description'] = description.strip()
    return analytes


def add_images_to_analytes(analytes, base_url):
    """Add image and formula image URLs to analytes."""
    for i, analyte in enumerate(analytes):
        analysis = analyte['type']
        key = analyte['key']
        if os.path.exists(f'images/{analysis}s/{key}.png'):
            image_url = f'{base_url}/images/{analysis}s/{key}.png'
            analytes[i]['image_url'] = image_url
        else:
            print('Missing PNG:', analysis, analyte['key'])
        if os.path.exists(f'images/{analysis}s/{key}.svg'):
            analytes[i]['chemical_structure_image_url'] = image_url.replace('.png', '.svg')
        else:    
            print('Missing SVG:', analysis, analyte['key'])
    return analytes


def save_to_json(filename, data):
    """Save data to a JSON file."""
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)


def save_data(analytes):
    """Organize and save analytes data."""
    analytes_by_type = categorize_analytes_by_type(analytes)
    for analyte_type, items in analytes_by_type.items():
        save_to_json(f"data/{analyte_type}s.json", items)
    save_to_json("data/analytes.json", analytes)


def categorize_analytes_by_type(analytes):
    """Categorize analytes by their type."""
    analytes_by_type = {}
    for analyte in analytes:
        analyte_type = analyte['type']
        analytes_by_type.setdefault(analyte_type, []).append(analyte)
    return analytes_by_type


def get_cannabis_analytes(analytes):
    """Get cannabis analytes."""
    analytes = add_chemical_data_for_analytes(analytes)
    base_url = 'https://huggingface.co/datasets/cannlytics/cannabis_analytes/blob/main'
    analytes = add_images_to_analytes(analytes, base_url)
    analytes = add_descriptions_to_analytes(analytes)
    save_data(analytes)
    return analytes


# === Test ===
# [✓] Tested: 2023-10-10 by Keegan Skeate <keegan@cannlytics>
if __name__ == '__main__':
    
    # Beginning analyte data.
    analytes = [
      {
        'description': '',
        'key': 'delta_9_thc',
        'name': 'Delta-9 THC',
        'scientific_name': 'Δ-9-Tetrahydrocannabinol',
        'type': 'cannabinoid',
        'wikipedia_url': 'https://en.wikipedia.org/wiki/Tetrahydrocannabinol',
        'degrades_to': [],
        'precursors': ['thca'],
        'subtype': '',
        'CAS_number': '1972-08-3'
      },
      {
        'description': '',
        'key': 'thca',
        'name': 'THCA',
        'scientific_name': 'Tetrahydrocannabinolic acid',
        'type': 'cannabinoid',
        'wikipedia_url': 'https://en.wikipedia.org/wiki/Tetrahydrocannabinolic_acid',
        'degrades_to': ['delta_9_thc'],
        'precursors': [],
        'subtype': '',
        'CAS_number': '23978-85-0'
      },
      {
        'description': '',
        'key': 'delta_8_thc',
        'name': 'Delta-8 THC',
        'scientific_name': 'Δ-8-Tetrahydrocannabinol',
        'type': 'cannabinoid',
        'wikipedia_url': 'https://en.wikipedia.org/wiki/Delta-8-Tetrahydrocannabinol',
        'degrades_to': [],
        'precursors': [],
        'subtype': '',
        'CAS_number': '5957-75-5'
      },
      {
        'description': '',
        'key': 'thcv',
        'name': 'THCV',
        'scientific_name': 'Tetrahydrocannabivarin',
        'type': 'cannabinoid',
        'wikipedia_url': 'https://en.wikipedia.org/wiki/Tetrahydrocannabivarin',
        'degrades_to': [],
        'precursors': ['thcva'],
        'subtype': '',
        'CAS_number': '31262-37-0'
      },
      {
        'description': '',
        'key': 'thcva',
        'name': 'THCVA',
        'scientific_name': 'Tetrahydrocannabivarinic acid',
        'type': 'cannabinoid',
        'wikipedia_url': 'https://en.wikipedia.org/wiki/Tetrahydrocannabivarinic_acid',
        'degrades_to': ['thcv'],
        'precursors': [],
        'subtype': '',
        'CAS_number': '24274-48-4'
      },
      {
        'description': '',
        'key': 'cbg',
        'name': 'CBG',
        'scientific_name': 'Cannabigerol',
        'type': 'cannabinoid',
        'wikipedia_url': 'https://en.wikipedia.org/wiki/Cannabigerol',
        'degrades_to': [],
        'precursors': ['cbga'],
        'subtype': '',
        'CAS_number': '25654-31-3'
      },
      {
        'description': '',
        'key': 'cbga',
        'name': 'CBGA',
        'scientific_name': 'Cannabigerolic acid',
        'type': 'cannabinoid',
        'wikipedia_url': 'https://en.wikipedia.org/wiki/Cannabigerolic_acid',
        'degrades_to': ['cbg'],
        'precursors': [],
        'subtype': '',
        'CAS_number': '25555-57-1'
      },
      {
        'description': '',
        'key': 'cbn',
        'name': 'CBN',
        'scientific_name': 'Cannabinol',
        'type': 'cannabinoid',
        'wikipedia_url': 'https://en.wikipedia.org/wiki/Cannabinol',
        'degrades_to': [],
        'precursors': [],
        'subtype': '',
        'CAS_number': '521-35-7'
      },
      {
        'description': '',
        'key': 'cbdv',
        'name': 'CBDV',
        'scientific_name': 'Cannabidivarin',
        'type': 'cannabinoid',
        'wikipedia_url': 'https://en.wikipedia.org/wiki/Cannabidivarin',
        'degrades_to': [],
        'precursors': ['cbdva'],
        'subtype': '',
        'CAS_number': '24274-48-4'
      },
      {
        'description': '',
        'key': 'cbdva',
        'name': 'Cannabidivarinic acid (CBDVA)',
        'type': 'cannabinoid',
        'wikipedia_url': 'https://en.wikipedia.org/wiki/Cannabidivarinic_acid',
        'degrades_to': ['cbdv'],
        'precursors': [],
        'subtype': '',
        'CAS_number': '1245629-14-6'
      },
      {
        'description': '',
        'key': 'cbc',
        'name': 'CBC',
        'scientific_name': 'Cannabichromene',
        'type': 'cannabinoid',
        'wikipedia_url': 'https://en.wikipedia.org/wiki/Cannabichromene',
        'degrades_to': [],
        'precursors': ['cbca'],
        'subtype': '',
        'CAS_number': '20675-51-8'
      },
      {
        'description': '',
        'key': 'cbca',
        'name': 'CBCA',
        'scientific_name': 'Cannabichromenenic acid',
        'type': 'cannabinoid',
        'wikipedia_url': 'https://en.wikipedia.org/wiki/Cannabichromenic_acid',
        'degrades_to': ['cbc'],
        'precursors': [],
        'subtype': '',
        'CAS_number': '32556-78-4'
      },
      {
        'description': '',
        'key': 'cbcv',
        'name': 'CBCV',
        'scientific_name': 'Cannabichromevarin',
        'type': 'cannabinoid',
        'wikipedia_url': 'https://en.wikipedia.org/wiki/Cannabichromevarin',
        'degrades_to': [],
        'precursors': [],
        'subtype': '',
        'CAS_number': '62248-85-9'
      },
      {
        'description': '',
        'key': 'cbt',
        'name': 'CBT',
        'scientific_name': 'Cannabitriol',
        'type': 'cannabinoid',
        'wikipedia_url': 'https://en.wikipedia.org/wiki/Cannabitriol',
        'degrades_to': [],
        'precursors': [],
        'subtype': '',
        'CAS_number': '52298-89-8'
      },
      {
        'description': '',
        'key': 'cbl',
        'name': 'CBL',
        'scientific_name': 'Cannabicyclol',
        'type': 'cannabinoid',
        'wikipedia_url': 'https://en.wikipedia.org/wiki/Cannabicyclol',
        'degrades_to': [],
        'precursors': [],
        'subtype': '',
        'CAS_number': '55286-91-5'
      },
      {
        'description': '',
        'key': 'cbla',
        'name': 'CBLA',
        'scientific_name': 'Cannabicyclolic acid',
        'type': 'cannabinoid',
        'wikipedia_url': 'https://en.wikipedia.org/wiki/Cannabicyclolic_acid',
        'degrades_to': ['cbl'],
        'precursors': [],
        'subtype': '',
        'CAS_number': '22198-35-0'
      },
      {
        'description': '',
        'key': 'beta_pinene',
        'name': 'beta-Pinene',
        'type': 'terpene',
        'wikipedia_url': 'https://en.wikipedia.org/wiki/Beta-Pinene',
        'degrades_to': [],
        'precursors': [],
        'subtype': 'monoterpene',
        'CAS_number': '127-91-3'
      },
      {
        'description': '',
        'key': 'd_limonene',
        'name': 'D-Limonene',
        'type': 'terpene',
        'wikipedia_url': 'https://en.wikipedia.org/wiki/Limonene',
        'degrades_to': ['p_cymene'],
        'precursors': [],
        'subtype': 'monoterpene',
        'CAS_number': '5989-27-5'
      },
      {
        'description': '',
        'key': 'p_cymene',
        'name': 'p-Cymene',
        'type': 'terpene',
        'wikipedia_url': 'https://en.wikipedia.org/wiki/p-Cymene',
        'degrades_to': [],
        'precursors': ['d_limonene'],
        'subtype': 'monoterpene',
        'CAS_number': '99-87-6'
      },
      {
        'description': '',
        'key': 'beta_caryophyllene',
        'name': 'beta-Caryophyllene',
        'type': 'terpene',
        'wikipedia_url': 'https://en.wikipedia.org/wiki/Caryophyllene',
        'degrades_to': ['caryophyllene_oxide'],
        'precursors': [],
        'subtype': 'sesquiterpene',
        'CAS_number': '87-44-5'
      },
      {
        'description': '',
        'key': 'caryophyllene_oxide',
        'name': 'Caryophyllene Oxide',
        'type': 'terpene',
        'wikipedia_url': 'https://en.wikipedia.org/wiki/Caryophyllene_oxide',
        'degrades_to': [],
        'precursors': ['beta_caryophyllene'],
        'subtype': 'sesquiterpenoid',
        'CAS_number': '1139-30-6'
      },
      {
        'description': '',
        'key': 'gamma_terpinene',
        'name': 'Gamma Terpinene',
        'type': 'terpene',
        'wikipedia_url': 'https://en.wikipedia.org/wiki/Gamma-Terpinene',
        'degrades_to': [],
        'precursors': [],
        'subtype': 'monoterpene',
        'CAS_number': '99-85-4'
      },
      {
        'description': '',
        'key': 'alpha_terpinene',
        'name': 'Alpha Terpinene',
        'type': 'terpene',
        'wikipedia_url': 'https://en.wikipedia.org/wiki/Alpha-Terpinene',
        'degrades_to': [],
        'precursors': [],
        'subtype': 'monoterpene',
        'CAS_number': '99-86-5'
      },
      {
        'description': '',
        'key': 'alpha_pinene',
        'name': 'Alpha-Pinene',
        'type': 'terpene',
        'wikipedia_url': 'https://en.wikipedia.org/wiki/Alpha-Pinene',
        'degrades_to': [],
        'precursors': [],
        'subtype': 'monoterpene',
        'CAS_number': '80-56-8'
      },
      {
        'description': '',
        'key': 'beta_myrcene',
        'name': 'Beta-Myrcene',
        'type': 'terpene',
        'wikipedia_url': 'https://en.wikipedia.org/wiki/Myrcene',
        'degrades_to': [],
        'precursors': [],
        'subtype': 'monoterpene',
        'CAS_number': '123-35-3'
      },
      {
        'description': '',
        'key': 'ocimene',
        'name': 'Ocimene',
        'type': 'terpene',
        'wikipedia_url': 'https://en.wikipedia.org/wiki/Ocimene',
        'degrades_to': [],
        'precursors': [],
        'subtype': 'monoterpene',
        'CAS_number': '13877-91-3'
      },
      {
        'description': '',
        'key': 'carene',
        'name': 'Carene',
        'type': 'terpene',
        'wikipedia_url': 'https://en.wikipedia.org/wiki/Carene',
        'degrades_to': [],
        'precursors': [],
        'subtype': 'monoterpene',
        'CAS_number': '13466-78-9'
      },
      {
        'description': '',
        'key': 'camphene',
        'name': 'Camphene',
        'type': 'terpene',
        'wikipedia_url': 'https://en.wikipedia.org/wiki/Camphene',
        'degrades_to': [],
        'precursors': [],
        'subtype': 'monoterpene',
        'CAS_number': '79-92-5'
      },
      {
        'description': '',
        'key': 'terpinolene',
        'name': 'Terpinolene',
        'type': 'terpene',
        'wikipedia_url': 'https://en.wikipedia.org/wiki/Terpinolene',
        'degrades_to': [],
        'precursors': [],
        'subtype': 'monoterpene',
        'CAS_number': '586-62-9'
      },
      {
        'description': '',
        'key': 'humulene',
        'name': 'Humulene',
        'type': 'terpene',
        'wikipedia_url': 'https://en.wikipedia.org/wiki/Humulene',
        'degrades_to': [],
        'precursors': [],
        'subtype': 'sesquiterpene',
        'CAS_number': '6753-98-6'
      },
      {
        'description': '',
        'key': 'guaiol',
        'name': 'Guaiol',
        'type': 'terpene',
        'wikipedia_url': 'https://en.wikipedia.org/wiki/Guaiol',
        'degrades_to': [],
        'precursors': [],
        'subtype': 'sesquiterpenoid',
        'CAS_number': '489-86-1'
      },
      {
        'description': '',
        'key': 'nerolidol',
        'name': 'Nerolidol',
        'type': 'terpene',
        'wikipedia_url': 'https://en.wikipedia.org/wiki/Nerolidol',
        'degrades_to': [],
        'precursors': [],
        'subtype': 'sesquiterpene',
        'CAS_number': '7212-44-4'
      },
      {
        'description': '',
        'key': 'eucalyptol',
        'name': 'Eucalyptol',
        'type': 'terpene',
        'wikipedia_url': 'https://en.wikipedia.org/wiki/Eucalyptol',
        'degrades_to': [],
        'precursors': [],
        'subtype': 'monoterpenoid',
        'CAS_number': '470-82-6'
      },
      {
        'description': '',
        'key': 'linalool',
        'name': 'Linalool',
        'type': 'terpene',
        'wikipedia_url': 'https://en.wikipedia.org/wiki/Linalool',
        'degrades_to': [],
        'precursors': [],
        'subtype': 'monoterpenoid',
        'CAS_number': '78-70-6'
      },
      {
        'description': '',
        'key': 'isopulegol',
        'name': 'Isopulegol',
        'type': 'terpene',
        'wikipedia_url': 'https://en.wikipedia.org/wiki/Isopulegol',
        'degrades_to': [],
        'precursors': [],
        'subtype': 'monoterpenoid',
        'CAS_number': '89-79-2'
      },
      {
        'description': '',
        'key': 'alpha_bisabolol',
        'name': 'Alpha-Bisabolol',
        'type': 'terpene',
        'wikipedia_url': 'https://en.wikipedia.org/wiki/Bisabolol',
        'degrades_to': [],
        'precursors': [],
        'subtype': 'sesquiterpenoid',
        'CAS_number': '23089-26-1'
      },
      {
        'description': '',
        'key': 'geraniol',
        'name': 'Geraniol',
        'type': 'terpene',
        'wikipedia_url': 'https://en.wikipedia.org/wiki/Geraniol',
        'degrades_to': [],
        'precursors': ['linalool'],
        'subtype': 'sesquiterpenoid',
        'CAS_number': '106-24-1'
      }
      # TODO: Add analytes for additional analyses:
      # - residual_solvents
      # - pesticides
      # - heavy_metals
      # - microbes
      # - mycotoxins
      # - other (water_activity, moisture_content, foreign_matter)
    ]

    # Augment analytes.
    analytes = get_cannabis_analytes(analytes)

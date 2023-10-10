# Standard imports:
import json
import os
from time import sleep

# External imports:
from bs4 import BeautifulSoup
import requests

# Beginning analyte data.
analytes = [
  {
    'description': '',
    'key': 'delta_9_thc',
    'name': 'THC',
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
    'name': 'Tetrahydrocannabivarinic acid (THCVA)',
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
    'name': 'Cannabigerol (CBG)',
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
    'name': 'Cannabigerolic acid (CBGA)',
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
    'name': 'Cannabinol (CBN)',
    'type': 'cannabinoid',
    'wikipedia_url': 'https://en.wikipedia.org/wiki/Cannabinol',
    'degrades_to': [],
    'precursors': [],
    'subtype': '',
    'CAS_number': '521-35-7'
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
]


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
                data['Boiling point'] = data_cell.get_text().strip()
    return data


def standardize_chemical_data(data):
    """Standardize chemical data.
    Notes: Density is measured in g/mL, Molar mass is measured in g/mol,
    and boiling point is measured in °C.
    """
    standardized_data = {}
    
    # Standard chemical formula.
    standardized_data['chemical_formula'] = data['chemical_formula']
    
    # Standard molar mass.
    standardized_data['molar_mass'] = float(data['Molar mass'].split()[0])
    
    # Standard density.
    density_value = float(data['density'].split('\xa0g/mL')[0])
    standardized_data['density'] = density_value
    
    # Standard Celsius boiling point.
    bp_celsius = float(data['boiling_point'].split('\xa0°C;')[0])
    standardized_data['boiling_point'] = bp_celsius
    
    return standardized_data


# === Augment chemical data ===

# Get chemical data for each analyte.
for i, analyte in enumerate(analytes):
    url = analyte['wikipedia_url']
    if not url:
        continue
    chemical_data = get_chemical_data(url)
    if chemical_data:
      standard_chemical_data = standardize_chemical_data(chemical_data)
      analytes[i] = {**analyte, **standard_chemical_data}
    if i < len(analytes) - 1:
      sleep(1)

# TODO: Add images
# - image_url
# - chemical_formula_image_url


# === Save the data ===

# Create a dictionary to categorize analytes by their type.
analytes_by_type = {}
for analyte in analytes:
    analyte_type = analyte['type']
    if analyte_type not in analytes_by_type:
        analytes_by_type[analyte_type] = []
    analytes_by_type[analyte_type].append(analyte)

# Save each type to a separate JSON file in the 'data' directory.
for analyte_type, items in analytes_by_type.items():
    filename = f"data/{analyte_type}s.json"
    with open(filename, 'w') as f:
        json.dump(items, f, indent=2)

# Save all of the analytes.
filename = f"data/analytes.json"
with open(filename, 'w') as f:
    json.dump(items, f, indent=4)

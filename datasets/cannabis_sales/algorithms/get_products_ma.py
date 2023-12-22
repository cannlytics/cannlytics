"""
Get Products MA
Copyright (c) 2023 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
Created: 11/2/2023
Updated: 12/7/2023
License: <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>
"""
from datetime import datetime
from matplotlib import pyplot as plt
import pandas as pd
import requests
from time import sleep


# === Initialization ===

# Setup plotting style.
plt.style.use('fivethirtyeight')
plt.rcParams.update({
    'font.family': 'Times New Roman',
    'font.size': 24,
})

# # Initialize OpenAI client.
# env_file = '../../../.env'
# os.environ['OPENAI_API_KEY'] = dotenv_values(env_file)['OPENAI_API_KEY']
# openai_api_key = os.environ['OPENAI_API_KEY']
# client = OpenAI()



# Define product columns.
MA_PRODUCT_COLUMNS = {
    'id': 'product_id',
    'category': 'product_type',
    'facilityName': 'producer',
    'imageUrl': 'image_url',
    'ingredients': 'ingredients',
    'license': 'license_number',
    'name': 'product_name',
    'quantityType': 'units',
    'state': 'state',
    'cbdContent': 'total_cbd',
    'cbdContentUnitOfMeasure': 'total_cbd_units',
    'cbdContentDose': 'total_cbd_dose',
    'cbdContentDoseUnitOfMeasure': 'total_cbd_dose_units',
    'cbdPotency': 'cbd',
    'thcContent': 'total_thc',
    'thcContentUnitOfMeasure': 'total_thc_units',
    'thcContentDose': 'total_thc_dose',
    'thcContentDoseUnitOfMeasure': 'total_thc_dose_units',
    'thcPotency': 'thc',
    'isArchived': 'archived',
    'retailAvailability': 'status'
}


def query_metrc_products(
        categories=[],
        items=[],
        license_numbers=[],
        quantities=[],
        query='',
        skip=0,
        states=[],
        sort='',
    ):
    """Get data for a specific category from the Metrc product catalog API."""
    base_url = 'https://catalog.metrc.com/v1/searchApi/items/search'
    params = {
        'query': query,
        'sort': sort,
        'skip': skip,
        'itemNames': items,
        'itemCategories': categories,
        'states': states,
        'licenseNumbers': license_numbers,
        'quantityTypes': quantities,
    }
    response = requests.post(base_url, json=params)
    if response.status_code == 200:
        return response.json()
    else:
        print(f'Failed to get data: {response.text}')
        return None


def get_metrc_products(
        items_per_page=24,
        verbose=True,
    ):
    """Get all products from the Metrc product catalog API."""

    # Get all products.
    all_data = []
    categories = [
        'Buds',
        'Raw Pre-Rolls',
        'Infused (edible)',
        'Vape Product',
        'Concentrate (Each)',
    ]
    for category in categories:
        if verbose:
            print('Collecting products for category:', category)
        skip = 0  # Start at the beginning for each category
        while True:
            content = query_metrc_products(categories=[category], skip=skip)
            if content and content['items']:
                all_data.extend(content['items'])
                skip += items_per_page
                if verbose:
                    print('Collected %i / %i items.' % (len(all_data), content['meta']['total']))
            else:
                if verbose:
                    print(f'Completed Category: {category}, Collected: {skip} items.')
                break
            sleep(0.33)  # Respectful delay to not overwhelm the server.

    # Standardize the data.
    df = pd.DataFrame(all_data)

    # Rename columns.
    df.rename(columns=MA_PRODUCT_COLUMNS, inplace=True)

    # Add base URL to image URLs if not archived.
    df['image_url'] = df.apply(lambda x: 'https://catalog.metrc.com' + x['image_url'] if not pd.isna(x['image_url']) else x['image_url'], axis=1)

    # Save to a CSV file
    timestamp = datetime.now().isoformat()[:19].replace(':', '-')
    df.to_csv(f'ma-products-{timestamp}.csv', index=False)
    if verbose:
        print(f'Saved {len(df)} products to CSV file.')

    # Return the data.
    return df


# === Tests ===
if __name__ == '__main__':

    # Get all products.
    df = get_metrc_products()

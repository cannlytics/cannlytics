"""
Get Products MA
Copyright (c) 2023 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
Created: 11/2/2023
Updated: 12/6/2023
License: <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>
"""
from datetime import datetime
import pandas as pd
import requests
from time import sleep


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

    import json
    import os
    from dotenv import dotenv_values
    import matplotlib.pyplot as plt
    from openai import OpenAI

    # Get all products.
    df = get_metrc_products()

    # Explore the data.
    df = pd.read_csv('../../../.datasets/products/ma-products-2023-12-06T01-56-39.csv')

    # TODO: Merge with license data.

    # Visualize product types proportions.
    stats = df['product_type'].value_counts().to_dict()
    plt.figure(figsize=(8, 6))
    plt.pie(stats.values(), labels=stats.keys(), autopct='%1.1f%%', startangle=140)
    plt.title('Product Type Distribution')
    plt.show()

    # Visualize total THC vs. total CBD.
    sample = df.loc[
        (~df['total_thc'].isna()) &
        (~df['total_cbd'].isna()) &
        (df['total_thc_units'] == 'mg')
    ]
    sample = sample.loc[
        (df['product_type'] == 'Concentrate (Each)') |
        (df['product_type'] == 'Vape Product')
    ]
    sample = sample.loc[
        (sample['total_thc'] < 1_000) &
        (sample['total_cbd'] < 1_000)
    ]
    sample_total_thc = sample['total_thc'].div(10)
    sample_total_cbd = sample['total_cbd'].div(10)
    plt.figure(figsize=(10, 6))
    # Points where the sum of THC and CBD is less than or equal to 100%
    plt.scatter(sample_total_thc[sample_total_thc + sample_total_cbd <= 100], 
                sample_total_cbd[sample_total_thc + sample_total_cbd <= 100], 
                alpha=0.5, color='blue')

    # Points where the sum of THC and CBD is greater than 100%
    plt.scatter(sample_total_thc[sample_total_thc + sample_total_cbd > 100], 
                sample_total_cbd[sample_total_thc + sample_total_cbd > 100], 
                alpha=0.5, color='red')
    # plt.scatter(sample['total_cbd'], sample['total_thc'], alpha=0.5)
    plt.title('Scatterplot of Total THC vs Total CBD')
    plt.ylabel('Total THC (%)')
    plt.xlabel('Total CBD (%)')
    plt.grid(True)
    plt.show()

    # Find all the edibles with "organic" in the ingredients.
    # Find edibles with "organic" in the ingredients, case insensitive
    edibles = df[df['product_type'] == 'Infused (edible)']
    organic_edibles = edibles[edibles['ingredients'].str.contains('organic', case=False, na=False)]
    organic_stats = organic_edibles.describe()
    print(organic_stats)

    # Find all the "Vape Product"s with "terpenes" in the ingredients.
    # Find vape products with "terpene" in the ingredients, case insensitive
    vapes = df[df['product_type'] == 'Vape Product']
    terpene_vapes = vapes[vapes['ingredients'].str.contains('terpene', case=False, na=False)]
    terpene_stats = terpene_vapes.describe()
    print(terpene_stats)

    # Initialize OpenAI client.
    env_file = '../../../.env'
    os.environ['OPENAI_API_KEY'] = dotenv_values(env_file)['OPENAI_API_KEY']
    openai_api_key = os.environ['OPENAI_API_KEY']
    client = OpenAI()

    # Use OpenAI to create a column of DBA names.
    names = list(df['producer'].unique())
    names = [x.replace(' Inc.', '').replace(' Inc', '').replace(' INC.', '').replace(' LLC', '') for x in names]
    names = [x.strip().rstrip(',') for x in names]
    prompt = 'Return JSON. Given a list of business names, return a list of DBA names, e.g. {"names": []}. Try to use a standard DBA when there are name variations, e.g. "Curaleaf Massachusetts, Inc". and "Curaleaf North Shore, Inc." have the same DBA name "Curaleaf". Please make sure the DBA names are in the same order as the business names and there are just as many DBA names as business names.'
    prompt += '\n\nBusiness Names:\n'
    prompt += '\n'.join(names)
    prompt += '\n\nDBA Names:\n'
    messages = [{'role': 'user', 'content': prompt}]
    completion = client.chat.completions.create(
        model='gpt-4-1106-preview',
        messages=messages,
        max_tokens=4_096,
        temperature=0.0,
        user='cannlytics',
    )
    usage = completion.model_dump()['usage']
    cost = 0.01 / 1_000 * usage['prompt_tokens'] + 0.03 / 1_000 * usage['completion_tokens']
    content = completion.choices[0].message.content
    extracted_json = content.split('```json\n')[-1].split('\n```')[0]
    extracted_data = json.loads(extracted_json)
    print('Cost:', cost)
    print('Extracted:', extracted_data)

    # Merge DBAs with product data.
    dba = extracted_data['names']
    llc_to_dba = {llc: dba for llc, dba in zip(names, dba)}
    df['producer_dba_name'] = df['producer'].map(llc_to_dba)

    # TODO: Look at production by DBA.

    # Save the data.
    timestamp = datetime.now().strftime('%Y-%m-%d')
    df.to_csv(f'augmented-ma-products-{timestamp}.csv', index=False)

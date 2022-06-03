"""
Get Cannabis Data from Illinois
Copyright (c) 2022 Cannlytics

Authors:
    Candace O'Sullivan-Sutherland <https://github.com/candy-o>
    Can Saruhan <https://github.com/CSaruhan>
    Keegan Skeate <https://github.com/keeganskeate>
Created: 5/31/2021
Updated: 4/25/2022
License: MIT License <https://opensource.org/licenses/MIT>

Data Sources:

    - Illinois Cannabis Data
    https://www.idfpr.com/profs/adultusecan.asp

    - Illinois Retailers
    https://www.idfpr.com/LicenseLookup/AdultUseDispensaries.pdf

"""
# Standard imports.
from datetime import datetime
import os
from urllib.parse import urljoin

# External imports.
from bs4 import BeautifulSoup
try:
    from dotenv import dotenv_values
except ImportError:
    pass
from fredapi import Fred
import numpy as np
import pandas as pd
import pdfplumber
import requests

# Internal imports.
from cannlytics.firebase import (
    initialize_firebase,
    update_documents,
)
from cannlytics.utils.logistics import geocode_addresses
# from cannlytics.utils import (
#     convert_month_year_to_date,
#     end_of_period_timeseries,
# )
from pandas import NaT


def end_of_period_timeseries(data, period='M'):
    """Convert a DataFrame from beginning-of-the-period to
    end-of-the-period timeseries.
    Args:
        data (DataFrame): The DataFrame to adjust timestamps.
        period (str): The period of the time series, monthly "M" by default.
    Returns:
        (DataFrame): The adjusted DataFrame, with end-of-the-month timestamps.
    """
    data.index = data.index.to_period(period).to_timestamp(period)
    return data

def convert_month_year_to_date(x):
    """Convert a month, year series to datetime. E.g. `'April 2022'`."""
    try:
        return datetime.strptime(x.replace('.0', ''), '%B %Y')
    except:
        return NaT

# Specify the state abbreviation.
STATE = 'IL'


def get_retailers_il(data_dir, filename):
    """Get retailers operating in Illinois.
    Args:
        data_dir (str): A directory for the data to live.
        filename (str): A filename, without extension, for the data.
    Returns:
        (DataFrame): Returns the retailer data.
    """

    # Download the licensees PDF.
    if not os.path.exists(data_dir):
        os.mkdir(data_dir)
    url = 'https://www.idfpr.com/LicenseLookup/AdultUseDispensaries.pdf'
    raw_file = os.path.join(data_dir, filename + '.pdf')
    response = requests.get(url)
    with open(raw_file, 'wb') as doc:
        doc.write(response.content)

    # Read the licensees PDF.
    pdf = pdfplumber.open(raw_file)

    # Get all of the table data.
    table_data = []
    for page in pdf.pages:
        table = page.extract_table()
        table_data += table

    # Remove the header.
    table_data = table_data[4:]

    # Remove missing cells.
    table_data = [list(filter(None, x)) for x in table_data]

    # Create a DataFrame from the table data.
    licensee_columns = [
        'organization',
        'trade_name',
        'address',
        'medical',
        'license_issue_date',
        'license_number',
    ]
    licensees = pd.DataFrame(table_data, columns=licensee_columns)

    # Clean the names.
    licensees['organization'] = licensees['organization'].str.replace('\n', '')
    licensees['trade_name'] = licensees['trade_name'].str.replace('\n', '',)
    licensees['trade_name'] = licensees['trade_name'].str.replace('*', '', regex=False)

    # Convert issue date to a datetime.
    licensees['license_issue_date'] = pd.to_datetime(licensees['license_issue_date'])

    # Separate address into 'street', 'city', 'state', 'zip_code', 'phone_number'.
    # Note: This could probably be done more elegantly and it's not perfect.
    streets, cities, states, zip_codes, phone_numbers = [], [], [], [], []
    for _, row in licensees.iterrows():
        parts = row.address.split(' \n')
        streets.append(parts[0])
        phone_numbers.append(parts[-1])
        locales = parts[1]
        city_locales = locales.split(', ')
        state_locales = city_locales[-1].split(' ')
        cities.append(city_locales[0])
        states.append(state_locales[0])
        zip_codes.append(state_locales[-1])
    licensees['street'] = pd.Series(streets)
    licensees['city'] = pd.Series(cities)
    licensees['state'] = pd.Series(states)
    licensees['zip_code'] = pd.Series(zip_codes)
    licensees['phone_number'] = pd.Series(phone_numbers)
    licensees['address'] = licensees[['street', 'city', 'state']] \
        .agg(', '.join, axis=1) + ' ' + retailers['zip_code']

    # Set the index as the license number.
    licensees.index = licensees['license_number']

    # Map medical status to True / False.
    licensees = licensees.replace({'medical': {'Yes': True, 'No': False}})

    # Save the licensees data.
    output_file = os.path.join(data_dir, filename + '.xlsx')
    licensees.to_excel(output_file, sheet_name='Data')
    return licensees


def get_sales_il(data_dir, filename, url=None):
    """Get cannabis sales data in Illinois.
    Args:
        data_dir (str): A directory for the data to live.
        filename (str): A filename, without extension, for the data.
        url (str): The URL to a specific sales report (optional).
    Returns:
        (DataFrame): Returns the sales data.
    """

    # Get the sales URL programatically if no URL is provided.
    if url is None:
        url = 'https://www.idfpr.com/profs/adultusecan.asp'
        headers = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0'}
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        for link in soup.select("a[href$='.pdf']"):
            if link.text.startswith('Illinois Adult Use Cannabis Monthly Sales'):
                url = urljoin(url, link['href'])
                break

    # Download the sales data PDF.
    raw_file = os.path.join(data_dir, filename + '.pdf')
    response = requests.get(url)
    with open(raw_file, 'wb') as doc:
        doc.write(response.content)

    # Read the sales data PDF.
    pdf = pdfplumber.open(raw_file)

    # Get all of the table data.
    table_data = []
    for page in pdf.pages:

        # Get all of the tables on the page.
        tables = page.find_tables()
        for table in tables:
            data = table.extract()
            table_data += data

    # Add the year to each observation, assuming that the tables are in
    # reverse chronological order, starting at the beginning of 2020 and
    # incrementing a year for each table.
    year = 2020
    for row in reversed(table_data):
        row.append(year)
        if row[0] == 'January':
            year += 1

    # Create a DataFrame from the table data.
    sales_columns = [
        'month',
        'items_sold',
        'in_state_sales',
        'out_of_state_sales',
        'total_sales',
        'year',
    ]
    sales_data = pd.DataFrame(table_data, columns=sales_columns)

    # Set the time index.
    dates = sales_data.month.map(str) + ' ' + sales_data.year.map(str)
    dates = dates.apply(convert_month_year_to_date)
    sales_data.index = dates
    sales_data = sales_data.loc[sales_data.index.notnull()]
    sales_data.sort_index(inplace=True)

    # Convert string columns to numeric, handling dollar signs.
    # FIXME: An `out_of_state_sales` observation has 2 decimal places.
    columns = sales_data.columns[1:]
    sales_data[columns] = sales_data[columns] \
        .replace('[\$,]', '', regex=True) \
        .astype(float, errors='ignore')

    # Set the index as the end of the month.
    sales_data = end_of_period_timeseries(sales_data)
    sales_data['date'] = sales_data.index.map(lambda x: datetime.isoformat(x))

    # Save the sales data.
    output_file = os.path.join(data_dir, filename + '.xlsx')
    sales_data.to_excel(output_file, sheet_name='Data')
    return sales_data


def calculate_stats_il(licensees, timeseries, env_file='../.env'):
    """Calculate cannabis statistics in Illinois.
    Args:
        licensees (DataFrame): Licensee data.
        timeseries (DataFrame): Timeseries data.
    Returns:
        (DataFrame): Returns the augmented timeseries data.
    """

    # Create total retailers by month series.
    total_retailers = []
    for index, _ in timeseries.iterrows():
        licensed_retailers = licensees.loc[licensees['license_issue_date'] <= index]
        count = len(licensed_retailers)
        total_retailers.append(count)
    timeseries['total_retailers'] = pd.Series(total_retailers, index=timeseries.index)

    # Get the Illinois population data.
    fred_api_key = os.environ.get('FRED_API_KEY')
    if fred_api_key is None:
        config = dotenv_values(env_file)
        fred_api_key = config.get('FRED_API_KEY')
    fred = Fred(api_key=fred_api_key)
    observation_start = timeseries.index.min().isoformat()
    population = fred.get_series(f'{STATE}POP', observation_start=observation_start)
    population = population.multiply(1000) # thousands of people

    # Conjecture that the population remains constant in 2022.
    # Future work: Make this dynamically add any missing years.
    new_row = pd.DataFrame([population[-1]], index=[pd.to_datetime('2022-12-31')])
    population = pd.concat([population, pd.DataFrame(new_row)], ignore_index=False)

    # Project monthly population.
    # Future work: Assume population grows / declines linearly.
    monthly_population = population.resample('M').mean().pad()
    monthly_population = monthly_population.loc[monthly_population.index <= timeseries.index.max()]

    # Calculate retailers per capita.
    capita = monthly_population / 100_000
    timeseries['retailers_per_capita'] = timeseries['total_retailers'] / capita[0]

    # Calculate sales per retailer.
    timeseries['sales_per_retailer'] = timeseries['total_sales'] / timeseries['total_retailers']

    # Calculate months of adult use.
    timeseries['months_of_adult_use'] = np.arange(1, len(timeseries) + 1)

    # Return the timeseries with calculated statistics.
    return timeseries


def get_data_il(event, context, data_dir='/tmp'):
    """Get cannabis data for illinois (Google Cloud Function).
    Args:
        event (dict): Event payload.
        context (google.cloud.functions.Context): Metadata for the event.
        data_dir (str): The directory to save the data, '/tmp' by default.
    """

    # Get the current date.
    date = datetime.now().isoformat().split('T')[0]
    print(date, 'Updating Illinois statistics.')

    # Get retail data.
    retailers = get_retailers_il(data_dir, 'retailers')
    print(date, 'Found %i licensees.' % len(retailers))

    # Get sales data.
    sales = get_sales_il(DATA_DIR, 'sales')
    print(date, 'Found %i months of sales.' % len(sales))

    # Calculate statistics.
    stats = calculate_stats_il(retailers, sales)
    print(date, 'Calculated %i months of statistics.' % len(stats))

    # 5. TODO: Finalize with code below: Create and upload forecasts!!!

    # # Upload data and statistics to Firestore database.
    # database = initialize_firebase()
    # licensee_refs = [
    #     f"data/illinois/licensees/{x['license_number']}"
    #     for x in retailers
    # ]
    # stats_refs = [
    #     f"data/illinois/monthly_stats/{x['date']}"
    #     for x in stats
    # ]
    # update_documents(licensee_refs, retailers.to_dict('records'), database)
    # update_documents(stats_refs, stats.to_dict('records'), database)
    # print(date, 'Updated Illinois statistics.')


if __name__ == '__main__':

    # Test.
    DATA_DIR = '../../../.datasets/ai/illinois'

    # Get retail data.
    retailers = get_retailers_il(DATA_DIR, 'retailers_il_test')

    # Pertinent (geocoding and website search are costly!):
    # Get retailers from the Cannlytics API so it's 
    # not necessary to geocode any retailers that have already
    # been geocoded before or search for websites that have
    # already been found.

    # Geocode retail licensees.
    # google_maps_api_key = os.environ.get('GOOGLE_MAPS_API_KEY')
    # retailers = geocode_addresses(retailers, api_key=google_maps_api_key)

    # 1. TODO: Try to find the retailers website. Then:
    # utils.web.get_page_metadata
    from cannlytics.utils.logistics import get_place_details



    # 2. TODO: Add current local statistics from Census and FRED for each licensee.


    # # Get sales data.
    # sales = get_sales_il(DATA_DIR, 'sales_il_test')

    # # Calculate statistics.
    # stats = calculate_stats_il(retailers, sales)


    # 3. TODO: Update aggregate state statistics from Census and FRED for each point in time.
    # - inflation?
    # - fertilizer prices?


    # 4. TODO: Create and upload forecasts!!!
    # ARIMAX with months and inflation ;)


    # # Upload data and statistics to Firestore database.
    # TIME = datetime.now().isoformat()
    # DATE = TIME.split('T')[0]
    # retailers['updated_at'] = TIME
    # stats['updated_at'] = TIME
    # database = initialize_firebase()
    # licensee_refs = [
    #     f"data/illinois/licensees/{x['license_number']}"
    #     for x in retailers
    # ]
    # stats_refs = [
    #     f"data/illinois/monthly_stats/{x['date']}"
    #     for x in stats
    # ]
    # update_documents(licensee_refs, retailers.to_dict(orient='records'))
    # update_documents(stats_refs, stats.to_dict(orient='records'))

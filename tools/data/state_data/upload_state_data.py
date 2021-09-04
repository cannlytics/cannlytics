"""
Define Data Sources | Cannlytics

Author: Keegan Skeate <keegan@cannlytics.com>  
Created: 8/20/2021  
Updated: 9/3/2021  
License: MIT License <https://opensource.org/licenses/MIT>  

Manage scientific instruments and measurements from the instruments.
"""
# Standard imports
from datetime import datetime
from dotenv import dotenv_values
import os

# External imports
from fredapi import Fred

# Internal imports
import sys
sys.path.append('../../../')
from cannlytics import firebase # pylint: disable=import-error
# from get_data_OK import get_cannabis_data_ok

data_sources = [
    {
        'state': 'AL',
        'state_name': 'Alabama',
        'medicinal': True,
        'recreational': False,
    },
    {
        'state': 'AK',
        'state_name': 'Alaska',
        'medicinal': True,
        'recreational': True,
    },
    {
        'state': 'AZ',
        'state_name': 'Arizona',
        'medicinal': True,
        'recreational': True,
    },
    {
        'state': 'AR',
        'state_name': 'Arkansas',
    },
    {
        'state': 'CA',
        'state_name': 'California',
        'medicinal': True,
        'recreational': True,
    },
    {
        'state': 'CO',
        'state_name': 'Colorado',
        'medicinal': True,
        'recreational': True,
    },
    {
        'state': 'CT',
        'state_name': 'Connecticut',
        'medicinal': True,
        'recreational': True,
    },
    {
        'state': 'DE',
        'state_name': 'Delaware',
        'medicinal': True,
        'recreational': False,
    },
    {
        'state': 'DC',
        'state_name': 'District of Columbia',
        'medicinal': True,
        'recreational': True,
    },
    {
        'state': 'FL',
        'state_name': 'Florida',
        'medicinal': True,
        'recreational': False,
    },
    {
        'state': 'GA',
        'state_name': 'Georgia',
        'medicinal': True,
        'recreational': False,
    },
    {
        'state': 'HI',
        'state_name': 'Hawaii',
        'medicinal': True,
        'recreational': False,
    },
    {
        'state': 'ID',
        'state_name': 'Idaho',
        'medicinal': False,
        'recreational': False,
    },
    {
        'state': 'IL',
        'state_name': 'Illinois',
        'medicinal': True,
        'recreational': True,
    },
    {
        'state': 'IN',
        'state_name': 'Indiana',
        'medicinal': False,
        'recreational': False,
    },
    {
        'state': 'IA',
        'state_name': 'Iowa',
        'medicinal': False,
        'recreational': False,
    },
    {
        'state': 'KS',
        'state_name': 'Kansas',
        'medicinal': False,
        'recreational': False,
    },
    {
        'state': 'KY',
        'state_name': 'Kentucky',
        'medicinal': False,
        'recreational': False,
    },
    {
        'state': 'LA',
        'state_name': 'Louisiana',
        'medicinal': True,
        'recreational': False,
    },
    {
        'state': 'ME',
        'state_name': 'Maine',
        'medicinal': True,
        'recreational': True,
    },
    {
        'state': 'MD',
        'state_name': 'Maryland',
        'medicinal': True,
        'recreational': False,
    },
    {
        'state': 'MA',
        'state_name': 'Massachusetts',
        'medicinal': True,
        'recreational': True,
    },
    {
        'state': 'MI',
        'state_name': 'Michigan',
        'medicinal': True,
        'recreational': True,
    },
    {
        'state': 'MN',
        'state_name': 'Minnesota',
        'medicinal': True,
        'recreational': False,
    },
    {
        'state': 'MS',
        'state_name': 'Mississippi',
        'medicinal': False,
        'recreational': False,
    },
    {
        'state': 'MO',
        'state_name': 'Missouri',
        'medicinal': True,
        'recreational': False,
    },
    {
        'state': 'MT',
        'state_name': 'Montana',
        'medicinal': True,
        'recreational': True,
    },
    {
        'state': 'NE',
        'state_name': 'Nebraska',
        'medicinal': False,
        'recreational': False,
    },
    {
        'state': 'NV',
        'state_name': 'Nevada',
        'medicinal': True,
        'recreational': True,
    },
    {
        'state': 'NH',
        'state_name': 'New Hampshire',
        'medicinal': True,
        'recreational': False,
    },
    {
        'state': 'NJ',
        'state_name': 'New Jersey',
        'medicinal': True,
        'recreational': True,
    },
    {
        'state': 'NM',
        'state_name': 'New Mexico',
        'medicinal': True,
        'recreational': True,
    },
    {
        'state': 'NY',
        'state_name': 'New York',
        'medicinal': True,
        'recreational': True,
    },
    {
        'state': 'NC',
        'state_name': 'North Carolina',
        'medicinal': False,
        'recreational': False,
    },
    {
        'state': 'ND',
        'state_name': 'North Dakota',
        'medicinal': True,
        'recreational': False,
    },
    {
        'state': 'OH',
        'state_name': 'Ohio',
        'medicinal': True,
        'recreational': False,
    },
    {
        'state': 'OK',
        'state_name': 'Oklahoma',
        'medicinal': True,
        'recreational': False,
        'sources': [
            {'name': 'Medical Marijuana Excise Tax', 'url': 'https://oklahomastate.opengov.com/transparency#/33894/accountType=revenues&embed=n&breakdown=types&currentYearAmount=cumulative&currentYearPeriod=months&graph=bar&legendSort=desc&month=5&proration=false&saved_view=105742&selection=A49C34CEBF1D01A1738CB89828C9274D&projections=null&projectionType=null&highlighting=null&highlightingVariance=null&year=2021&selectedDataSetIndex=null&fiscal_start=earliest&fiscal_end=latest'},
            {'name': 'List of Licensed Businesses', 'url': 'https://oklahoma.gov/omma/businesses/list-of-businesses.html'},
        ],
        'background_image': 'https://firebasestorage.googleapis.com/v0/b/cannlytics.appspot.com/o/public%2Fimages%2Fbackgrounds%2Fstates%2Foklahoma_city.jpg?alt=media&token=83bb9264-2674-4a09-b682-9f96251164e1',
    },
    {
        'state': 'OR',
        'state_name': 'Oregon',
        'medicinal': True,
        'recreational': True,
    },
    {
        'state': 'PA',
        'state_name': 'Pennsylvania',
        'medicinal': True,
        'recreational': False,
    },
    # {
    #     'state': 'PR',
    #     'state_name': 'Puerto Rico',
    #     'medicinal': True,
    #     'recreational': False,
    # },
    {
        'state': 'RI',
        'state_name': 'Rhode Island',
        'medicinal': True,
        'recreational': False,
    },
    {
        'state': 'SC',
        'state_name': 'South Carolina',
        'medicinal': False,
        'recreational': False,
    },
    {
        'state': 'SD',
        'state_name': 'South Dakota',
        'medicinal': True,
        'recreational': False,
    },
    {
        'state': 'TN',
        'state_name': 'Tennessee',
        'medicinal': False,
        'recreational': False,
    },
    {
        'state': 'TX',
        'state_name': 'Texas',
        'medicinal': True,
        'recreational': False,
    },
    {
        'state': 'UT',
        'state_name': 'Utah',
        'medicinal': True,
        'recreational': False,
    },
    {
        'state': 'VT',
        'state_name': 'Vermont',
        'medicinal': True,
        'recreational': True,
    },
    {
        'state': 'VA',
        'state_name': 'Virginia',
        'medicinal': True,
        'recreational': True,
    },
    {
        'state': 'WA',
        'state_name': 'Washington',
        'medicinal': True,
        'recreational': True,
    },
    {
        'state': 'WV',
        'state_name': 'West Virginia',
        'medicinal': True,
        'recreational': False,
    },
    {
        'state': 'WI',
        'state_name': 'Wisconsin',
        'medicinal': False,
        'recreational': False,
    },
    {
        'state': 'WY',
        'state_name': 'Wyoming',
        'medicinal': False,
        'recreational': False,
    }
]


def get_state_current_population(state_data):
    """Get a given state's latest population from the Fed Fred API,
    getting the number in 1000's and returning the absolute value."""
    config = dotenv_values('../../../.env')
    fred = Fred(api_key=config['FRED_API_KEY'])
    state_code = state_data['state']
    population_source_code = f'{state_code}POP'
    population = fred.get_series(population_source_code)
    real_population = int(population.iloc[-1] * 1000)
    population_date = population.index[-1].isoformat()[:10]
    return {
        'population': f'{real_population:,}',
        'population_source_code': population_source_code,
        'population_source': f'https://fred.stlouisfed.org/series/{population_source_code}',
        'population_at': population_date,
    }


if __name__ == '__main__':
    
    # Get the population for each state.
    for n in range(len(data_sources)):
        data_source = data_sources[n]
        population_data = get_state_current_population(data_source)
        data_sources[n] = {**data_source, **population_data}
        print(data_source['state'], 'Population:', population_data['population'])

    # TODO: Get supplementary data for each state.
    # -> licensing costs
    # -> Regulations
        # - Testing requirements

    # TODO: Rank states
    
    # Add Id to each state.
    for n in range(len(data_sources)):
        data_source = data_sources[n]
        data_sources[n]['id'] = data_source['state'].lower()
        
    # Initialize Firebase.
    config = dotenv_values('../../../.env')
    credentials = config['GOOGLE_APPLICATION_CREDENTIALS']
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials
    firebase.initialize_firebase()

    # Upload data to Firestore.
    for data_source in data_sources:
        state = data_source['state'].lower()
        firebase.update_document(f'public/data/state_data/{state}', data_source)

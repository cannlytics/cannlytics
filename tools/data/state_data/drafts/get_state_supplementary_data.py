"""
Get State Supplementary Data | Cannlytics

Author: Keegan Skeate
Contact: <keegan@cannlytics.com>
Created: 8/31/2021
Updated: 8/31/2021
License: MIT License <https://opensource.org/licenses/MIT>
"""
from dotenv import dotenv_values
from fredapi import Fred


DATA_SOURCES = [
    {
        'state': 'OK',
        'state_name': 'Oklahoma',
        'medicinal': True,
        'recreational': False,
        'sources': [
            {'name': 'Medical Marijuana Excise Tax', 'url': 'https://oklahomastate.opengov.com/transparency#/33894/accountType=revenues&embed=n&breakdown=types&currentYearAmount=cumulative&currentYearPeriod=months&graph=bar&legendSort=desc&month=5&proration=false&saved_view=105742&selection=A49C34CEBF1D01A1738CB89828C9274D&projections=null&projectionType=null&highlighting=null&highlightingVariance=null&year=2021&selectedDataSetIndex=null&fiscal_start=earliest&fiscal_end=latest'},
            {'name': 'List of Licensed Businesses', 'url': 'https://oklahoma.gov/omma/businesses/list-of-businesses.html'},
        ],
    },
]

if __name__ == '__main__':
    
    # Get supplementary data (such as population) for each state.

    # Read in a Fred API key.
    config = dotenv_values('../.env')
    
    # Get the effective federal funds rate from Fred.
    fred = Fred(api_key=config['FRED_API_KEY'])
    data['interest_rate'] = fred.get_series(
        'FEDFUNDS',
        observation_start='1/1/2017',
        observation_end='4/1/2021'
    )
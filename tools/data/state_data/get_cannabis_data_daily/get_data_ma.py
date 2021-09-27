"""
Get MAssachussets Data | Cannlytics

Author: Keegan Skeate
Contact: <keegan@cannlytics.com>
Created: 9/20/2021
Updated: 9/20/2021
License: MIT License <https://opensource.org/licenses/MIT>
"""
import os
import pandas as pd
import matplotlib.pyplot as plt
import requests
# from sodapy import Socrata
import yaml


DATASETS = [
    {
        'name': 'Adult-Use Marijuana Retail Sales by Date and Product Type',
        'id': 'xwf2-j7g9',
        'fields': [
             {
                 'key': 'saledate',
                 'type': 'timestamp',
                 'standard_key': 'updated_at',
             },
             {
                 'key': 'productcategoryname',
                 'type': 'text',
                 'standard_key': 'sample_type',
             },
             {
                 'key': 'dollartotal',
                 'type': 'float',
                 'standard_key': 'total_sales',
             },
        ],
        'data_source': 'https://dev.socrata.com/foundry/opendata.mass-cannabis-control.com/xwf2-j7g9',
        'endpoint': 'https://opendata.mass-cannabis-control.com/resource/xwf2-j7g9.json',
    },
    {
        'name': 'Approved Massachusetts Licensees',
        'id': 'hmwt-yiqy',
        'data_source': 'https://dev.socrata.com/foundry/opendata.mass-cannabis-control.com/hmwt-yiqy',
        'endpoint': 'https://opendata.mass-cannabis-control.com/resource/hmwt-yiqy.json',
    },
    {
     
        'name': 'Average Monthly Price per Ounce for Adult-Use Cannabis',
        'id': 'rqtv-uenj',
        'data_source': 'https://dev.socrata.com/foundry/opendata.mass-cannabis-control.com/rqtv-uenj',
        'endpoint': 'https://opendata.mass-cannabis-control.com/resource/rqtv-uenj.json',
        'fields': [
             {
                 'key': 'date',
                 'type': 'timestamp',
                 'standard_key': 'date',
             },
             {
                 'key': 'avg_1oz',
                 'type': 'float',
                 'standard_key': 'monthly_avg_price_per_ounce',
             },
        ],
    },
    {
        'name': 'Marijuana Establishment Adult-use Plant Activity and Volume',
        'id': 'j3q7-3usu',
        'data_source': 'https://dev.socrata.com/foundry/opendata.mass-cannabis-control.com/j3q7-3usu',
        'endpoint': 'https://opendata.mass-cannabis-control.com/resource/j3q7-3usu.json',
        
     
    },
    # Optional: Weekly sales by product type
    # https://dev.socrata.com/foundry/opendata.mass-cannabis-control.com/87rp-xn9v
    # https://opendata.mass-cannabis-control.com/Industry-and-Products/Website-Previous-Week-Adult-Use-Sales/pnfk-d3cf
]


if __name__ == '__main__':
    
    #--------------------------------------------------------------------------
    # 1. Get the data.
    #--------------------------------------------------------------------------
    
    # Get the App Token.
    app_token = None
    with open('env.yaml', 'r') as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
        app_token = config['APP_TOKEN']

    # Define headers for all requests.
    headers = {
        'X-App-Token': app_token,
        'Content-Type': 'application/json'
    }
    
    # Define the base URL.
    base = 'https://opendata.mass-cannabis-control.com/resource'
     
    # Get sales by product type.
    url = f'{base}/xwf2-j7g9.json'
    params = {
        '$limit': 1000, 
        '$order': 'saledate DESC',
    }
    response = requests.get(url,  headers=headers, params=params)
    products = pd.DataFrame(response.json())
    
    # Get licensees.
    url = f'{base}/hmwt-yiqy.json'
    params = {
        '$limit': 1000, 
        '$order': 'app_create_date DESC',
    }
    response = requests.get(url,  headers=headers, params=params)
    licensees = pd.DataFrame(response.json())
    
    # Get the monthly average price per ounce.
    url = f'{base}/rqtv-uenj.json'
    params = {
        '$limit': 1000, 
        '$order': 'date DESC',
    }
    response = requests.get(url,  headers=headers, params=params)
    prices = pd.DataFrame(response.json())
    
    # Get production stats (total employees, total plants, etc.) j3q7-3usu
    url = f'{base}/j3q7-3usu.json'
    params = {
        '$limit': 1000, 
        '$order': 'activitysummarydate DESC',
    }
    response = requests.get(url,  headers=headers, params=params)
    production = pd.DataFrame(response.json())
    
    #--------------------------------------------------------------------------
    # 2. Clean the data, standardizing variables.
    #--------------------------------------------------------------------------
    
    
    
    #--------------------------------------------------------------------------
    # 3. Calculate interesting statistics.
    #--------------------------------------------------------------------------

    # plt.plot(production_data.activitysummarydate, production_data.total_employees)
    
    #--------------------------------------------------------------------------
    # Upload the data!
    #--------------------------------------------------------------------------
    
    
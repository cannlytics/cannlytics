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
from sodapy import Socrata


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
    # https://opendata.mass-cannabis-control.com/Industry-and-Products/Public-View-Marijuana-Establishment-Facility-Activ/j3q7-3usu
]


if __name__ == '__main__':
    
    # Print let's rock and roll baby!!!
    
    #--------------------------------------------------------------------------
    # 1. Get the data.
    #--------------------------------------------------------------------------
    
    # Initialize a Socrata client.
    app_token = os.environ.get('APP_TOKEN', None)
    client = Socrata('opendata.mass-cannabis-control.com', app_token)
    
    # Get sales by product type.
    results = client.get('xwf2-j7g9', limit=2000)
    results_df = pd.DataFrame.from_records(results)
    
    # Get licensees.
    results = client.get("hmwt-yiqy", limit=2000)
    results_df = pd.DataFrame.from_records(results)
    
    # Get the monthly average price per ounce.
    results = client.get("rqtv-uenj", limit=2000)
    results_df = pd.DataFrame.from_records(results)
    
    # Get production stats (total employees, total plants, etc.)
    results = client.get("j3q7-3usu", limit=2000)
    results_df = pd.DataFrame.from_records(results)
    
    #--------------------------------------------------------------------------
    # 2. Clean the data, standardizing variables.
    #--------------------------------------------------------------------------
    
    
    
    #--------------------------------------------------------------------------
    # 3. Calculate interesting statistics.
    #--------------------------------------------------------------------------

    
    #--------------------------------------------------------------------------
    # Upload the data, boiii!!!
    #--------------------------------------------------------------------------
    
    
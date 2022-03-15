"""
Get Massachussets Data | Cannlytics

Authors: Keegan Skeate <keegan@cannlytics.com>
Created: 9/20/2021
Updated: 10/4/2021
License: MIT License <https://opensource.org/licenses/MIT>
"""
# Standard imports
from datetime import datetime
import yaml

# External imports
from fredapi import Fred
import pandas as pd
import requests

# Internal imports
from cannlytics.firebase import initialize_firebase, update_document
from utils import end_of_period_timeseries, reverse_dataframe

STATE = 'ma'

LICENSE_TYPES = {
    'cultivator': ['Marijuana Cultivator',],
    'processor': ['Marijuana Product Manufacturer',],
    'retailer': ['Marijuana Retailer',],
    'lab': ['Independent Testing Laboratory',],
    'transporter': [
        'Marijuana Transporter with Other Existing ME License',
        'Third Party Marijuana Transporter',
    ],
    'other': ['Marijuana Microbusiness', 'Craft Marijuana Cooperative'],
}

PRODUCT_TYPES = {
    'flower': ['Buds',],
    'concentrate': ['Concentrate (Each)', 'Concentrate', 'Concentrate (Bulk)',],
    'inhalation_product': ['Vape Product',],
    'liquid_edible': ['Infused Beverage',],
    'solid_edible': ['Infused (edible)',],
    'infused_mix': ['Infused (non-edible)', 'Kief',],
    'mix': ['Shake/Trim (by strain)', 'Shake/Trim'],
    'pre_roll': ['Infused Pre-Rolls', 'Raw Pre-Rolls',],
}

FED_DATASETS = {
    'labor_force': 'MALF',
    'population': 'MAPOP',
    'state_gdp': 'MANQGSP',
    'total_employees': 'MANA',
}

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


def get_data_ma():
    """Get public data for Massachusetts."""
    raise NotImplementedError


if __name__ == '__main__':
    
    # Run the Massachusetts data collectio routine.
    # get_data_ma()
    
    #--------------------------------------------------------------------------
    # Get the data.
    #--------------------------------------------------------------------------
    
    # Get the Socrata App Token.
    app_token = None
    api_key = None
    with open('env.yaml', 'r') as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
        app_token = config['APP_TOKEN']
        api_key = config['FRED_API_KEY']

    # Define headers for all requests.
    headers = {'X-App-Token': app_token, 'Content-Type': 'application/json'}
    
    # Define the base URL.
    base = 'https://opendata.mass-cannabis-control.com/resource'
     
    # Get sales by product type data.
    url = f'{base}/xwf2-j7g9.json'
    params = {'$limit': 10000, '$order': 'saledate DESC'}
    response = requests.get(url,  headers=headers, params=params)
    products = pd.DataFrame(response.json(), dtype=float)
    products = reverse_dataframe(products)
    
    # Get licensees data.
    url = f'{base}/hmwt-yiqy.json'
    params = {'$limit': 10000,  '$order': 'app_create_date DESC'}
    response = requests.get(url,  headers=headers, params=params)
    licensees = pd.DataFrame(response.json(), dtype=float)
    
    # Get the monthly average price per ounce.
    url = f'{base}/rqtv-uenj.json'
    params = {'$limit': 10000, '$order': 'date DESC'}
    response = requests.get(url,  headers=headers, params=params)
    prices = pd.DataFrame(response.json(), dtype=float)
    prices = reverse_dataframe(prices)
    prices.set_index('date', inplace=True)
    
    # Calculate the average price per specific quantity.
    price_per_gram = prices.avg_1oz.astype(float).divide(28).round(2)
    price_per_teenth = prices.avg_1oz.astype(float).divide(16).round(2)
    price_per_eighth = prices.avg_1oz.astype(float).divide(8).round(2)
    price_per_quarter = prices.avg_1oz.astype(float).divide(4).round(2)
    
    # Get production stats (total employees, total plants, etc.)
    url = f'{base}/j3q7-3usu.json'
    params = {'$limit': 10000, '$order': 'activitysummarydate DESC'}
    response = requests.get(url,  headers=headers, params=params)
    production = pd.DataFrame(response.json(), dtype=float)
    production = reverse_dataframe(production)

    # Initialize Fed FRED client.
    fred = Fred(api_key=api_key)

    # Find the observation time start.
    observation_start = production['activitysummarydate'].min().split('T')[0]

    # Get the civilian labor force data.
    labor_force_id = FED_DATASETS['labor_force']
    labor_force = fred.get_series(
                        labor_force_id,
                        observation_start=observation_start
                    )
    labor_force.index = labor_force.index.to_period('M').to_timestamp('M')

    # Get total employees in the state.
    total_employees_id = FED_DATASETS['total_employees']
    total_state_employees = fred.get_series(
                                total_employees_id,
                                observation_start=observation_start
                            )
    total_state_employees = end_of_period_timeseries(total_state_employees)
    total_state_employees = total_state_employees.multiply(1000) # Thousands of people

    # Get the state population (conjecturing that population remains constant from the last observed date).
    population_id = FED_DATASETS['population']
    population = fred.get_series(population_id, observation_start=observation_start)
    population = end_of_period_timeseries(population, 'Y')
    population = population.multiply(1000) # Thousands of people
    new_row = pd.DataFrame([population[-1]], index=[pd.to_datetime('2021-12-31')])
    population = pd.concat([population, pd.DataFrame(new_row)], ignore_index=False)

    #--------------------------------------------------------------------------
    # Clean the data, standardize variables, and calculate interesting statistics.
    #--------------------------------------------------------------------------
    
    # Calculate sales difference.
    production['sales'] = production['salestotal'].diff()
    
    # FIX: Fix outlier that appears to have an extra 0.
    outlier = production.loc[production.sales >= 100000000]
    production.at[outlier.index, 'sales'] = outlier.sales / 10
    
    # Aggregate daily production data into totals.
    production['date'] = pd.to_datetime(production['activitysummarydate'])
    production.set_index('date', inplace=True)
    monthly_avg_production = production.resample('M').mean()
    quarterly_avg_production = production.resample('Q').mean()
    
    # Calculate GDP from consumption (sales).
    cannabis_gdp = production['sales']
    state_gdp_id = FED_DATASETS['state_gdp']
    quarterly_cannabis_gdp = cannabis_gdp.resample('Q').sum()
    quarterly_cannabis_gdp = quarterly_cannabis_gdp.divide(1000000) # Millions of dollars
    state_gdp = fred.get_series(state_gdp_id, observation_start=observation_start)
    state_gdp.index = state_gdp.index.to_period('Q').to_timestamp('Q')
    
    # Calculate cannabis percent of GDP.
    cannabis_percent_of_gdp = (quarterly_cannabis_gdp / state_gdp) * 100

    # Calculate percent of annual GDP.
    annual_cannabis_gdp = cannabis_gdp.resample('Y').sum()
    annual_cannabis_gdp = annual_cannabis_gdp.divide(1000000) # Millions of dollars
    annual_state_gdp = state_gdp.resample('Y').sum()
    annual_percent_of_gdp = annual_cannabis_gdp / annual_state_gdp * 100
    
    # Calculate (Estimate) the cannabis GDP per Capita in MA.
    gdp_per_capita = (annual_state_gdp / population[0]) * 1000000
    cannabis_gdp_per_capita = (annual_cannabis_gdp / population[0]) * 1000000
    
    # Calculate the percent of the labor force that are cannabis employees.
    cannabis_portion_of_labor_force = monthly_avg_production.total_employees \
                                      / labor_force * 100

    # Calculate average number of employees per month.
    monthly_employee_avg = production['total_employees'].resample('M').mean()

    # Calculate cannabis employees as a percent of all employees.
    cannabis_employees_percent = monthly_employee_avg / total_state_employees * 100
    
    #--------------------------------------------------------------------------
    # Aggregate the statistics.
    #--------------------------------------------------------------------------

    # Record current and change.
    stats = {}
    stats_map = {
        'avg_price_per_gram': price_per_gram,
        'avg_price_per_teenth': price_per_teenth,
        'avg_price_per_eighth': price_per_eighth,
        'avg_price_per_quarter': price_per_quarter,
        'avg_price_per_ounce': prices,
        'gdp_per_capita': gdp_per_capita,
        'cannabis_gdp_per_capita': cannabis_gdp_per_capita,
        'population': population,
        'total_employees': production.total_employees,
        'total_inventory_items': production.total_active_packagecount,
        'total_plants': production.total_planttrackedcount,
        'total_flowering_plants': production.total_plantfloweringcount,
        'total_vegetative_plants': production.total_plantvegetativecount,
        'total_immature_plants': production.total_plantimmaturecount,
        'total_harvested_plants': production.total_active_harvestcount,
    }
    for stat, values in stats_map.items():
        stats[stat] = values.iloc[-1]
        try:
            difference = values.diff().iloc[-1]
            change = difference / values.iloc[-2]
            stats[f'{stat}_change'] = round(change * 100, 2)
        except:
            stats[f'{stat}_change'] = 'n/a'
        
    # Remove series.
    for stat, values in stats.items():
        if isinstance(stats[stat], pd.Series):
            stats[stat] == values.iloc[0]
        

    # Total licensees and total licensees by license type.
    stats['total_licensees'] = len(licensees)
    for license_type in LICENSE_TYPES:
        type_licenees = licensees.loc[licensees['license_type'] == license_type]
        stats[f'total_{license_type}s'] = len(type_licenees)

    # Calculate current month, last month, and year-to-date sales.
    now = datetime.now()
    current_month = now.month
    current_year = now.year
    current_date = now.isoformat()[:10]
    last_year = current_year
    if current_month == 1:
        last_month = 12
        last_year = current_year - 1
    else:
        last_month = current_month - 1
    current_month_date = pd.to_datetime(f'{current_month}/1/{current_year}')
    last_month_date = pd.to_datetime(f'{last_month}/1/{last_year}')
    stats['current_month_sales'] = round(production.loc[
                                       production.index >= current_month_date
                                   ].sales.sum(), 2)
    stats['last_month_sales'] = round(production.loc[
                                    (production.index >= last_month_date) &
                                    (production.index < current_month_date)
                                ].sales.sum(), 2)
    stats['year_to_date_sales'] = round(production.loc[
                                      production.index >= pd.to_datetime(current_year)
                                  ].sales.sum(), 2)
    
    #--------------------------------------------------------------------------
    # Format statistics for upload.
    #--------------------------------------------------------------------------

    # TODO: For each series, calculate the percent change.
    
    # Format daily statistics.
    daily_stats = production.copy()
    for product_type, categories in PRODUCT_TYPES.items():
        product_data = products.loc[products.productcategoryname.isin(categories)]
        product_data.index = product_data.saledate
        daily_products_data = product_data.groupby(product_data.saledate).sum()
        daily_stats[f'total_{product_type}_sales'] = daily_products_data.dollartotal.values

    # Format weekly statistics.

    # Format monthly statistics.
    # TODO: Add prices

    #--------------------------------------------------------------------------
    # Future Work: Create forecasts.
    #--------------------------------------------------------------------------

    # Sales by product type.Year-to-date sales
    # Future work: Forecasting
    # 2021 forecast / 2022 forecast
    # stats['forecast_2021_sales'] = 
    # stats['forecast_2022_sales'] = 
    
    #--------------------------------------------------------------------------
    # Upload daily, weekly, monthly data.
    # Optional: Only upload the last day, week, and month.
    #--------------------------------------------------------------------------

    # Add collected_at timestamp.
    stats['collected_at'] = datetime.now()

    # Upload the current stats.
    # update_document(f'public/stats/state_stats/{STATE}', stats)
    
    # Upload last day, week, and month.
    last_day_stats = daily_stats.iloc[-1].to_dict()
    last_day_date = last_day_stats['activitysummarydate'][:10]
    # ref = f'public/stats/state_stats/{STATE}/daily_stats/{last_day_date}'
    # update_document(ref, last_day_stats)

    # Upload licensees.
    # TODO: Get lat and latitude from geocoded_column.
    # licensees['latitude'] = licensees.geocoded_column['coordinates'][0]
    # licensees['longitude'] = licensees.geocoded_column['coordinates'][1]
    licensee_columns = {
        'business_name': 'organization',
        'dba_name': 'trade_name',
    }
    # licensees.rename(columns=licensee_columns, inplace=True)
    # for _, values in licensees.iterrows():
    #     license_number = values.license_number
    #     ref = f'public/data/licensees/state_licensees/{STATE}/{license_number}'
    #     update_document(ref, values)
    
    #--------------------------------------------------------------------------
    # Optional: Upload datasets as .xlsx files.
    #--------------------------------------------------------------------------
    

    #--------------------------------------------------------------------------
    # Optional: Create charts and report on the 1st of every month.
    #--------------------------------------------------------------------------
    
    # Plot quarterly GDP.
    # quarterly_cannabis_gdp[:len(state_gdp)].plot()
    # state_gdp.plot()
    
    # Plot the percent of GDP that cannabis constitutes.
    # cannabis_percent_of_gdp.plot()
    
    # Plot the GDP and percent of GDP.
    # annual_cannabis_gdp.plot(
    #     kind='bar',
    #     title='Annual Cannabis GDP (Millions of Dollars) in MA'
    # )
    # annual_percent_of_gdp.plot()
    
    # Plot the total employees.
    # monthly_employee_avg.plot()
    # total_state_employees.plot()   
    
    # Cannabis employees as a percent of all employees in the state.
    # cannabis_employees_percent.plot()

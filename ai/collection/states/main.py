"""
Get Daily Cannabis Data
Copyright (c) 2021 Cannlytics

Author: Keegan Skeate <keegan@cannlytics.com>
Created: 9/16/2021
Updated: 11/22/2021
License: MIT License <https://github.com/cannlytics/cannlytics-ai/blob/main/LICENSE>
Description:
    Get public cannabis data that needs to be updated daily.
"""
# Standard imports.
import os

# Internal imports.
# from .get_data_ct import get_data_ct
# from .get_data_ma import get_data_ma
from .get_state_data import get_state_current_population # pylint: disable=relative-beyond-top-level

DATA_POINTS = [
    'state',
    'date',
    'total_sales',
    'total_quantity',
    'total_rec_sales',
    'total_rec_quantity',
    'total_med_sales',
    'total_med_quantity',
    'total_licenses',
    'total_cultivators',
    'total_processors',
    'total_labs',
    'total_retailers',
    'total_transporters',
    'total_patients',
]

DATA_SOURCES = [
    # {
    #     'state': 'AL',
    #     'state_name': 'Alabama',
    #     'medicinal': True,
    #     'recreational': False,
    #     'script': 'get_data_al',
    # },
    # {
    #     'state': 'AK',
    #     'state_name': 'Alaska',
    #     'medicinal': True,
    #     'recreational': True,
    #     'script': 'get_data_ak',
    #     'traceability_system': 'Metrc',
    # },
    # {
    #     'state': 'AZ',
    #     'state_name': 'Arizona',
    #     'medicinal': True,
    #     'recreational': True,
    #     'script': 'get_data_az',
    # },
    # {
    #     'state': 'AR',
    #     'state_name': 'Arkansas',
    # },
    # {
    #     'state': 'CA',
    #     'state_name': 'California',
    #     'medicinal': True,
    #     'recreational': True,
    #     'script': 'get_data_ca',
    #     'traceability_system': 'Metrc',
    # },
    # {
    #     'state': 'CO',
    #     'state_name': 'Colorado',
    #     'medicinal': True,
    #     'recreational': True,
    #     'script': 'get_data_co',
    #     'traceability_system': 'Metrc',
    # },
    # {
    #     'state': 'CT',
    #     'state_name': 'Connecticut',
    #     'medicinal': True,
    #     'recreational': True,
    #     'script': 'get_data_ct',
    #     'update_daily_data': True,
    #     'update_weekly_data': True,
    #     'update_monthly_data': True,
    # },
    # {
    #     'state': 'DE',
    #     'state_name': 'Delaware',
    #     'medicinal': True,
    #     'recreational': False,
    # },
    # {
    #     'state': 'DC',
    #     'state_name': 'District of Columbia',
    #     'medicinal': True,
    #     'recreational': True,
    # },
    # {
    #     'state': 'FL',
    #     'state_name': 'Florida',
    #     'medicinal': True,
    #     'recreational': False,
    # },
    # {
    #     'state': 'GA',
    #     'state_name': 'Georgia',
    #     'medicinal': True,
    #     'recreational': False,
    # },
    # {
    #     'state': 'HI',
    #     'state_name': 'Hawaii',
    #     'medicinal': True,
    #     'recreational': False,
    # },
    # {
    #     'state': 'ID',
    #     'state_name': 'Idaho',
    #     'medicinal': False,
    #     'recreational': False,
    # },
    # {
    #     'state': 'IL',
    #     'state_name': 'Illinois',
    #     'medicinal': True,
    #     'recreational': True,
    #     'script': 'get_data_il',
    # },
    # {
    #     'state': 'IN',
    #     'state_name': 'Indiana',
    #     'medicinal': False,
    #     'recreational': False,
    # },
    # {
    #     'state': 'IA',
    #     'state_name': 'Iowa',
    #     'medicinal': False,
    #     'recreational': False,
    # },
    # {
    #     'state': 'KS',
    #     'state_name': 'Kansas',
    #     'medicinal': False,
    #     'recreational': False,
    # },
    # {
    #     'state': 'KY',
    #     'state_name': 'Kentucky',
    #     'medicinal': False,
    #     'recreational': False,
    # },
    # {
    #     'state': 'LA',
    #     'state_name': 'Louisiana',
    #     'medicinal': True,
    #     'recreational': False,
    #     'script': 'get_data_la',
    #     'traceability_system': 'Metrc',
    # },
    # {
    #     'state': 'ME',
    #     'state_name': 'Maine',
    #     'medicinal': True,
    #     'recreational': True,
    #     'script': 'get_data_me',
    #     'traceability_system': 'Metrc',
    # },
    # {
    #     'state': 'MD',
    #     'state_name': 'Maryland',
    #     'medicinal': True,
    #     'recreational': False,
    #     'script': 'get_data_md',
    #     'traceability_system': 'Metrc',
    # },
    {
        'id': 'ma',
        'state': 'MA',
        'state_name': 'Massachusetts',
        'medicinal': True,
        'recreational': True,
        'script': 'get_data_ma',
        'traceability_system': 'Metrc',
        'state_sales_tax': 6.25,
        'state_excise_tax': 10.75,
        'state_local_tax': 3,
        'tax_rate_url': 'https://opendata.mass-cannabis-control.com/stories/s/xwwk-y3zr',
        'update_daily_data': True,
        'update_weekly_data': True,
        'update_monthly_data': True,
    },
    # {
    #     'state': 'MI',
    #     'state_name': 'Michigan',
    #     'medicinal': True,
    #     'recreational': True,
    #     'script': 'get_data_mi',
    #     'traceability_system': 'Metrc',
    # },
    # {
    #     'state': 'MN',
    #     'state_name': 'Minnesota',
    #     'medicinal': True,
    #     'recreational': False,
    # },
    # {
    #     'state': 'MS',
    #     'state_name': 'Mississippi',
    #     'medicinal': False,
    #     'recreational': False,
    # },
    # {
    #     'state': 'MO',
    #     'state_name': 'Missouri',
    #     'medicinal': True,
    #     'recreational': False,
    #     'traceability_system': 'Metrc',
    # },
    # {
    #     'state': 'MT',
    #     'state_name': 'Montana',
    #     'medicinal': True,
    #     'recreational': True,
    #     'script': 'get_data_mt',
    #     'traceability_system': 'Metrc',
    # },
    # {
    #     'state': 'NE',
    #     'state_name': 'Nebraska',
    #     'medicinal': False,
    #     'recreational': False,
    # },
    # {
    #     'state': 'NV',
    #     'state_name': 'Nevada',
    #     'medicinal': True,
    #     'recreational': True,
    #     'script': 'get_data_nv',
    #     'traceability_system': 'Metrc',
    # },
    # {
    #     'state': 'NH',
    #     'state_name': 'New Hampshire',
    #     'medicinal': True,
    #     'recreational': False,
    # },
    # {
    #     'state': 'NJ',
    #     'state_name': 'New Jersey',
    #     'medicinal': True,
    #     'recreational': True,
    # },
    # {
    #     'state': 'NM',
    #     'state_name': 'New Mexico',
    #     'medicinal': True,
    #     'recreational': True,
    # },
    # {
    #     'state': 'NY',
    #     'state_name': 'New York',
    #     'medicinal': True,
    #     'recreational': True,
    # },
    # {
    #     'state': 'NC',
    #     'state_name': 'North Carolina',
    #     'medicinal': False,
    #     'recreational': False,
    # },
    # {
    #     'state': 'ND',
    #     'state_name': 'North Dakota',
    #     'medicinal': True,
    #     'recreational': False,
    # },
    # {
    #     'state': 'OH',
    #     'state_name': 'Ohio',
    #     'medicinal': True,
    #     'recreational': False,
    #     'script': 'get_data_oh',
    #     'traceability_system': 'Metrc',
    # },
    # {
    #     'state': 'OK',
    #     'state_name': 'Oklahoma',
    #     'medicinal': True,
    #     'recreational': False,
    #     'script': 'get_data_ok',
    #     'sources': [
    #         {'name': 'Medical Marijuana Excise Tax', 'url': 'https://oklahomastate.opengov.com/transparency#/33894/accountType=revenues&embed=n&breakdown=types&currentYearAmount=cumulative&currentYearPeriod=months&graph=bar&legendSort=desc&month=5&proration=false&saved_view=105742&selection=A49C34CEBF1D01A1738CB89828C9274D&projections=null&projectionType=null&highlighting=null&highlightingVariance=null&year=2021&selectedDataSetIndex=null&fiscal_start=earliest&fiscal_end=latest'},
    #         {'name': 'List of Licensed Businesses', 'url': 'https://oklahoma.gov/omma/businesses/list-of-businesses.html'},
    #     ],
    #     'background_image': 'https://firebasestorage.googleapis.com/v0/b/cannlytics.appspot.com/o/public%2Fimages%2Fbackgrounds%2Fstates%2Foklahoma_city.jpg?alt=media&token=83bb9264-2674-4a09-b682-9f96251164e1',
    #     'traceability_system': 'Metrc',
    #     'update_daily_data': True,
    #     'update_weekly_data': True,
    #     'update_monthly_data': True,
    # },
    # {
    #     'state': 'OR',
    #     'state_name': 'Oregon',
    #     'medicinal': True,
    #     'recreational': True,
    #     'script': 'get_data_or',
    #     'traceability_system': 'Metrc',
    # },
    # {
    #     'state': 'PA',
    #     'state_name': 'Pennsylvania',
    #     'medicinal': True,
    #     'recreational': False,
    # },
    # # {
    # #     'state': 'PR',
    # #     'state_name': 'Puerto Rico',
    # #     'medicinal': True,
    # #     'recreational': False,
    # # },
    # {
    #     'state': 'RI',
    #     'state_name': 'Rhode Island',
    #     'medicinal': True,
    #     'recreational': False,
    # },
    # {
    #     'state': 'SC',
    #     'state_name': 'South Carolina',
    #     'medicinal': False,
    #     'recreational': False,
    # },
    # {
    #     'state': 'SD',
    #     'state_name': 'South Dakota',
    #     'medicinal': True,
    #     'recreational': False,
    # },
    # {
    #     'state': 'TN',
    #     'state_name': 'Tennessee',
    #     'medicinal': False,
    #     'recreational': False,
    # },
    # {
    #     'state': 'TX',
    #     'state_name': 'Texas',
    #     'medicinal': True,
    #     'recreational': False,
    # },
    # {
    #     'state': 'UT',
    #     'state_name': 'Utah',
    #     'medicinal': True,
    #     'recreational': False,
    # },
    # {
    #     'state': 'VT',
    #     'state_name': 'Vermont',
    #     'medicinal': True,
    #     'recreational': True,
    #     'script': 'get_data_vt',
    # },
    # {
    #     'state': 'VA',
    #     'state_name': 'Virginia',
    #     'medicinal': True,
    #     'recreational': True,
    # },
    # {
    #     'state': 'WA',
    #     'state_name': 'Washington',
    #     'medicinal': True,
    #     'recreational': True,
    #     'script': 'get_data_wa',
    # },
    # {
    #     'state': 'WV',
    #     'state_name': 'West Virginia',
    #     'medicinal': True,
    #     'recreational': False,
    #     'traceability_system': 'Metrc',
    # },
    # {
    #     'state': 'WI',
    #     'state_name': 'Wisconsin',
    #     'medicinal': False,
    #     'recreational': False,
    # },
    # {
    #     'state': 'WY',
    #     'state_name': 'Wyoming',
    #     'medicinal': False,
    #     'recreational': False,
    # }
]


def get_cannabis_data(event, context):
    """Triggered from a message on a Cloud Pub/Sub topic.
    Args:
         event (dict): Event payload.
         context (google.cloud.functions.Context): Metadata for the event.
    """
    print('Initializing Get Cannabis Daily Data Routine.')

    # Get environment variables.
    fred_api_key = os.environ.get('FRED_API_KEY')
    if fred_api_key is None:
        import yaml
        dir_path = os.path.dirname(os.path.realpath(__file__))
        with open(f'{dir_path}/env.yaml', 'r') as env:
            config = yaml.load(env, Loader=yaml.FullLoader)
            fred_api_key = config['FRED_API_KEY']

    # Get the population for each state.
    print('Getting population for each state...')
    for i, data_source in enumerate(DATA_SOURCES):
        state = data_source['state']
        population_data = get_state_current_population(state, fred_api_key)
        DATA_SOURCES[i] = {**data_source, **population_data}
        print(state, 'Population:', population_data['population'])


    # Future work: Get supplementary data for each state.
    # -> licensing costs
    # -> Regulations
        # - Testing requirements


    # Future work: Rank states by various metrics: total sales, etc.

        
    # Initialize Firebase.
    # firebase.initialize_firebase()

    # Upload data to Firestore.
    # for data_source in data_sources:
    #     state = data_source['state'].lower()
    #     firebase.update_document(f'public/data/state_data/{state}', data_source)

    # Run all state daily data collection scripts.
    count = 0
    # for data_source in DATA_SOURCES:
    #     state = data_source['id']
    #     script = data_source['script']
    #     print('Getting data for %s.' % state)
    #     try:
    #         eval(script + '()')
    #         print('Successfully retrieved data for %s.' % state)
    #         success += 1
    #     except:
    #         print('Failed getting data for %s.' % state)
    print('Finished collecting data for %i states.' % count)
    return count


# def monthly_state_report():
#     """
#     Once a month, collect cannabis data points from all states
#     with permitted recreational and or medicinal cannabis sales.
#     All available monthly series will be collected, with an emphasis
#     on the following data points:

#         - Total cannabis sales (total_sales)
#         - Total cannabis sold (total_quantity)
#         - Recreational cannabis sales (total_rec_sales)
#         - Recreational cannabis soled (total_rec_quantity)
#         - Medicinal cannabis sales (total_med_sales)
#         - Medicinal cannabis sold (total_med_quantity)
#         - Number of licensees (total_licenses)
#         - Number of cultivation licenses (total_cultivators)
#         - Number of processor licenses (total_processors)
#         - Number of laboratory licenses (total_labs)
#         - Number of retail licenses (total_retailers)
#         - Number of transportation licenses (total_transporters)

#     Optional data points include:

#         - Number of medical patients (total_patients)

#     Detailed information will be collected about each laboratory.
#     Sales data can also be grouped into `flower`, `oil`, and `edibles`.

#     Once data is collected, summary statistics and visualization are
#     prepared on a state-by-state basis and aggregate totals are
#     calculated.

#     This will provide a monthly "State of the Industry" report that 
#     will include 12-month ahead forecasts.
#     """
#     raise NotImplementedError

    # TODO: Collect monthly data for each state.


    # TODO: Aggregate the monthly data.


    # TODO: Calculate statistics.


    # TODO: Prepare figures.


    # TODO: Render LaTeX text and tables.


# TODO: Write function to create Excel archive of data.
# from openpyxl import Workbook
# from openpyxl.styles import Font, Color, Alignment, Border, Side
# from openpyxl.styles import PatternFill

# def create_data_collection_workbook(sources, date):
#     """Create a workbook that is used on a month-by-month
#     basis to collect cannabis data for states. The workbook
#     can be easily read and aggregated with existing data."""

#     # Create workbook and set the sheetname.
#     workbook = Workbook()
#     sheet = workbook.active
#     sheet.title = 'State Data'
    
#     # Add the headers and the data.
#     sheet.append(DATA_POINTS)
#     for source in sources:
#         sheet.append([source['state'], date])

#     # Style the workbook
#     cell_color = Color(rgb='00FFF2CC')
#     cell_fill = PatternFill(patternType='solid', fgColor=cell_color)
#     bottom_border = Border(bottom=Side(border_style='thin'))
#     for i in range(len(DATA_POINTS)):
#         sheet.cell(row=1, column=i+1).border = bottom_border
#         sheet.cell(row=1, column=i+1).fill = cell_fill

#     # Save the workbook.
#     directory = './.datasets/monthly_state_data'
#     workbook.save(filename=f'{directory}/state_data_{date}.xlsx')

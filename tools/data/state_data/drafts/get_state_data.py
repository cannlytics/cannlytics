"""
Title | Project

Author: Keegan Skeate
Contact: <keegan@cannlytics.com>
Created: 
Updated: 
License: MIT License <https://opensource.org/licenses/MIT>
"""

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


def monthly_state_report():
    """
    Once a month, collect cannabis data points from all states
    with permitted recreational and or medicinal cannabis sales.
    All available monthly series will be collected, with an emphasis
    on the following data points:

        - Total cannabis sales (total_sales)
        - Total cannabis sold (total_quantity)
        - Recreational cannabis sales (total_rec_sales)
        - Recreational cannabis soled (total_rec_quantity)
        - Medicinal cannabis sales (total_med_sales)
        - Medicinal cannabis sold (total_med_quantity)
        - Number of licensees (total_licenses)
        - Number of cultivation licenses (total_cultivators)
        - Number of processor licenses (total_processors)
        - Number of laboratory licenses (total_labs)
        - Number of retail licenses (total_retailers)
        - Number of transportation licenses (total_transporters)

    Optional data points include:

        - Number of medical patients (total_patients)

    Detailed information will be collected about each laboratory.
    Sales data can also be grouped into `flower`, `oil`, and `edibles`.

    Once data is collected, summary statistics and visualization are
    prepared on a state-by-state basis and aggregate totals are
    calculated.

    This will provide a monthly "State of the Industry" report that 
    will include 12-month ahead forecasts.
    """

    # TODO: Collect monthly data for each state.


    # TODO: Aggregate the monthly data.


    # TODO: Calculate statistics.


    # TODO: Prepare figures.


    # TODO: Render LaTeX text and tables.
    

if __name__ == '__main__':
    
    print('Getting all state public cannabis data...')


    # TODO: This is a CRON job that is run periodically
    # to collect as much state data as is possible (automatically).
    # datasets = {}
    # datasets['ok'] = get_cannabis_data_ok()

    
    # TODO: Get supplementary data for each state.
    # -> licensing costs
    # -> Regulations
        # - Testing requirements
    
    # Create workbook to collect July 2021 data.
    # create_data_collection_workbook(sources, date)

    # TODO: Ensure data is collected for each month.
    
    # TODO: Ensure data is uploaded for each month.
    
    # TODO: Ensure data can be aggregated.
    
    # TODO: Create the report!
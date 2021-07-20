"""
Worksheets | Cannlytics

Author: Keegan Skeate <keegan@cannlytics.com>
Created: 7/18/2021
Updated: 7/19/2021
License: MIT License <https://opensource.org/licenses/MIT>
"""
# Standard packages
import os

# External packages.
from dotenv import load_dotenv
from pandas import DataFrame
import requests
import xlwings as xw
from xlwings.utils import rgb_to_int

# Internal packages.
from cannlytics.firebase import get_collection
from cannlytics.utils.utils import snake_case

ID_CELL = 'A8'
META_CELLS = 'A3:B6'
ORG_ID_CELL = 'B3'
STATUS_CELL = 'H2'
SUCCESS_COLOR = (150, 230, 161)
ERROR_COLOR = (255, 177, 167)


def get_data_block(sheet, coords, expand=None):
    """Get a data block.
    Args:
        sheet (Sheet): The worksheet containing the data block.
        coords (str): The inclusive coordinates of the data block.
        expand (str): Optionally expand the range of values.
    """
    data = {}
    values = sheet.range(coords).options(expand=expand).value
    for item in values:
        key = snake_case(item[0])
        value = item[1]
        data[key] = value
    return data


def show_status_message(sheet, coords, message, background=None, color=None):
    """Show a status message in an Excel spreadsheet.
    Args:
        sheet (Sheet): The sheet where the status message will be written.
        coords (str): The location of the status message.
        message (str): A status message to write to Excel.
        background (tuple): Optional background color.
        color (tuple): Optional font color.
    """
    sheet.range(coords).value = message
    if background:
        sheet.range(coords).color = background
    if color:
        sheet.range(coords).api.Font.Color = rgb_to_int(color)


@xw.sub
def import_worksheet_data(model_type):
    """A function called from Excel to import data by ID
    from Firestore into the Excel workbook."""
    book = xw.Book.caller()
    worksheet = book.sheets.active
    config_sheet = book.sheets['cannlytics.conf']
    config = get_data_block(config_sheet, 'A1', expand='table')

    # Show status message.
    show_status_message(
        worksheet,
        coords='H2',
        message='Importing %s data...' % model_type,
        background=config['success_color'],
    )

    # Read IDs.
    ids = worksheet.range(config['id_cell']).options(expand='down').value

    # Determine model type.
    meta_data = get_data_block(worksheet, config['meta_cells'])
    model = meta_data['data_model'].lower()
    
    # Get Cannlytics API key from .env.
    env_path = config['env_path']
    load_dotenv(env_path)
    api_key = os.getenv('CANNLYTICS_API_KEY')
    
    # TODO: Get data using model type and ID through the API.
    
    # TODO: Fill the data into Excel.
    
    # Show status message.
    show_status_message(
        worksheet,
        coords=config['status_cell'],
        message='Imported %s data.' % model_type,
    )
    

@xw.sub
def upload_worksheet_data(model_type):
    """A function called from Excel to import data by ID
    from Firestore into the Excel workbook."""

    # Initialize workbook.
    book = xw.Book.caller()
    worksheet = book.sheets.active
    datasheet = book.sheets['Upload']
    config_sheet = book.sheets['cannlytics.conf']
    config = get_data_block(config_sheet, 'A1', expand='table')
    show_status_message(
        worksheet,
        coords=config['status_cell'],
        message='Uploading %s data...' % model_type,
        background=config['success_color'],
    )

    # Read table data, cleaning the column names.
    table = datasheet.range('A1').expand('table')
    data = table.options(DataFrame, index=False).value
    data.columns = list(map(snake_case, data.columns))

    # Determine the model type.
    org_id = worksheet.range(ORG_ID_CELL).value
    model_singular = data.columns[0].replace('_id', '')
    meta_data = get_data_block(worksheet, config['meta_cells'])
    model = meta_data['data_model'].lower()

    # Get Cannlytics API key from .env using env_path in config.
    env_path = config['env_path']
    load_dotenv(env_path)
    api_key = os.getenv('CANNLYTICS_API_KEY')

    # Upload data using model type, ID, and data through the API.
    headers = {
        'Authorization': 'Bearer %s' % api_key,
        'Content-type': 'application/json',
    }
    base = config['api_url']
    for index, row in data.iterrows():
        json = row.to_dict()
        doc_id = json[f'{model_singular}_id']
        url = f'{base}/{model}?organization_id={org_id}'
        response = requests.post(url, json=json, headers=headers)
        if response.status_code == 200:
            show_status_message(
                worksheet,
                coords=config['status_cell'],
                message='Uploaded %s %s' % (model_type, doc_id),
            )
        else:
            show_status_message(
                worksheet,
                coords=config['status_cell'],
                message='Error uploading %s %s.' % (model_type, doc_id),
            )
            return
    
    # Show status message.
    show_status_message(
        worksheet,
        coords=config['status_cell'],
        message='Uploaded %s data.' % model_type,
    )

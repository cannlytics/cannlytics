"""
Worksheets | Cannlytics
Copyright (c) 2021-2022 Cannlytics

Authors: Keegan Skeate <https://github.com/keeganskeate>
Created: 7/18/2021
Updated: 1/10/2022
License: MIT License <https://opensource.org/licenses/MIT>
"""
# Standard packages
from ast import literal_eval
from typing import Any, List, Optional, Tuple, Union

# External packages.
from dotenv import dotenv_values
from pandas import DataFrame, to_datetime
import requests
try:
    import xlwings
    from xlwings.utils import rgb_to_int
except ImportError:
    # FIXME: Work on alternatives as xlwings doesn't work in App Engine.
    pass

# Internal packages.
from ..utils.utils import snake_case


def format_values(data: Union[list, dict], columns: List[str]) -> List[dict]:
    """Format response data by given columns. Handles a list or dictionary of data.
    Args:
        data (list,dict): A list of values or a dictionary of values.
        columns (list): A list of column names used to get values from the data.
    Returns:
        (list): Returns a list of items.
    """
    items = []
    try:
        for item in data:
            values = []
            for column in columns:
                values.append(item.get(column))
            items.append(values)
    except AttributeError:
        values = []
        for column in columns:
            values.append(data.get(column))
        items = [values]
    return items


def get_data_block(sheet: Any, coords: str, expand: Optional[str] = None) -> dict:
    """Get a data block.
    Args:
        sheet (Sheet): The worksheet containing the data block.
        coords (str): The inclusive coordinates of the data block.
        expand (str): Optionally expand the range of values.
    Returns
        (dict): A dictionary of the data in the data block.
    """
    data = {}
    values = sheet.range(coords).options(expand=expand).value
    for item in values:
        key = snake_case(item[0])
        value = item[1]
        data[key] = value
    return data


def get_data_model(worksheet: Any, config: dict, model_type: str, ids: List[str]) -> Any:
    """Get a specific data model from the Cannlytics API.
    Args:
        worksheet (Worksheet): An xlwings Excel worksheet instance.
        config (dict): A dictionary of user configuration.
        model_type (str): The data model name.
        ids (list): Specific IDs to retrieve from the API.
    Returns:
        (HTTPResponse): An HTTP response from the Cannlytics API.
    """
    base = config['api_url']
    org_id = worksheet.range(config['org_id_cell']).value
    env_variables = dotenv_values(config['env_path'])
    api_key = env_variables['CANNLYTICS_API_KEY']
    headers = {
        'Authorization': 'Bearer %s' % api_key,
        'Content-type': 'application/json',
    }
    if len(ids) == 1:
        url = f'{base}/{model_type}/{ids[0]}?organization_id={org_id}'
    else:
        url = f'{base}/{model_type}?organization_id={org_id}&items={str(ids)}'
    response = requests.get(url, headers=headers)
    return response


def increment_row(coords: str) -> str:
    """Increment a row given its starting coordinates.
    Args:
        coords (str):
    Returns:
        (str): The incremented row coordinates.
    """
    column = ''.join([i for i in coords if not i.isdigit()])
    seq_type = type(coords)
    row = int(seq_type().join(filter(seq_type.isdigit, coords))) + 1
    return column + str(row)


def import_worksheet(
        filename: str,
        sheetname: str,
        range_start: Optional[str] = 'A1',
    ) -> List[dict]:
    """Read the data from a given worksheet using xlwings.
    Args:
        filename (str): The name of the Excel workbook to read.
        sheetname (str): The name of the worksheet to import.
        range_start (str): Optional starting cell.
    Returns:
        list(dict): A list of dictionaries.
    """
    app = xlwings.App(visible=False)
    book = xlwings.Book(filename)
    sheet = book.sheets(sheetname)
    excel_data = sheet.range(range_start).expand('table').value
    keys = [snake_case(key) for key in excel_data[0]]
    data = [dict(zip(keys, values)) for values in excel_data[1:]]
    book.close()
    app.quit()
    return data


@xlwings.sub
def import_worksheet_data(model_type: str):
    """A function called from Excel to import data by IDs in the worksheet
    from Firestore into the Excel workbook.
    Args:
        model_type (str): The data model at hand.
    """

    # Initialize the workbook.
    worksheet, config = initialize_workbook()
    status_cell = config['status_cell']
    show_status_message(
        worksheet,
        coords=status_cell,
        message='Importing %s data...' % model_type,
        background=config['success_color'],
    )

    # Read the IDs.
    id_cell = increment_row(config['table_cell'])
    ids = worksheet.range(id_cell).options(expand='down', ndim=1).value

    # Get the worksheet columns.
    columns = worksheet.range(config['table_cell']).options(expand='right', ndim=1).value
    columns = [snake_case(x) for x in columns]

    # Get data using model type and ID through the API.
    response = get_data_model(worksheet, config, model_type, ids)
    if response.status_code != 200:
        show_status_message(
            worksheet,
            coords=status_cell,
            message='Error importing data.',
            background=config['error_color']
        )
        return

    # Format the values.
    try:
        data = response.json()['data']
        items = format_values(data, columns)
    except TypeError:
        show_status_message(
            worksheet,
            coords=status_cell,
            message='No data found.',
            background=config['error_color']
        )
        return

    # Insert all rows at the same time.
    worksheet.range(id_cell).value = items

    # Show success status message.
    show_status_message(
        worksheet,
        coords=status_cell,
        message='Imported %i %s.' % (len(ids), model_type),
    )


def initialize_workbook() -> Tuple:
    """Initialize an xlwings workbook and return the config worksheet data.
    Returns:
        (Worksheet): Returns the active worksheet.
        (dict): Returns a dictionary of user configuration.
    """
    book = xlwings.Book.caller()
    worksheet = book.sheets.active
    config_sheet = book.sheets['cannlytics.conf']
    config = get_data_block(config_sheet, 'A1', expand='table')
    return worksheet, config


def read_table_data(worksheet: Any, cell: str) -> dict:
    """Read table data from a worksheet and clean the columns and data.
    Args:
        worksheet (Worksheet): A worksheet containing the table data.
        cell (str): The cell range of the table.
    Returns:
        (dict): Returns the data in the worksheet table as a dictionary.
    """
    table = worksheet.range(cell)
    data = table.options(DataFrame, index=False, expand='table').value
    data.columns = list(map(snake_case, data.columns))
    for column in data.columns:
        if column.endswith('_at'):
            try:
                data[column] = to_datetime(data[column]).dt.strftime('%Y-%m-%dT%H:%M%:%SZ')
            except:
                pass
    return data.fillna('')


@xlwings.sub
def upload_worksheet_data(model_type):
    """A function called from Excel to import data by IDs in the worksheet
    from Firestore into the Excel workbook."""

    # Initialize the workbook.
    worksheet, config = initialize_workbook()
    status_cell = config['status_cell']
    show_status_message(
        worksheet,
        coords=status_cell,
        message='Uploading %s data...' % model_type,
        background=config['success_color'],
    )

    # Read the table data, cleaning the column names.
    data = read_table_data(worksheet, config['table_cell'])

    # Determine the model type and the organization.
    org_id = worksheet.range(config['org_id_cell']).value
    model_singular = data.columns[0].replace('_id', '')
    if not org_id:
        show_status_message(
            worksheet,
            coords=status_cell,
            message='Organization ID required.',
            background=config['error_color']
        )
        return

    # Get Cannlytics API key from .env using env_path in config.
    env_variables = dotenv_values(config['env_path'])
    api_key = env_variables['CANNLYTICS_API_KEY']

    # TODO: Split this into a separate function.
    # Upload data using model type, ID, and data through the API.
    headers = {
        'Authorization': 'Bearer %s' % api_key,
        'Content-type': 'application/json',
    }
    base = config['api_url']
    for _, row in data.iterrows():
        # Optional: Clean based on data model fields.
        json = row.to_dict()
        doc_id = json[f'{model_singular}_id']
        if not doc_id:
            continue
        url = f'{base}/{model_type}?organization_id={org_id}'
        response = requests.post(url, json=json, headers=headers)
        if response.status_code == 200:
            show_status_message(
                worksheet,
                coords=status_cell,
                message='Uploaded %s' % doc_id,
            )
        else:
            show_status_message(
                worksheet,
                coords=status_cell,
                message='Error uploading %s. Check your organization, internet connection and API key.' % doc_id, # pylint:disable=line-too-long
                background=config['error_color']
            )
            return

    # Show success status message.
    show_status_message(
        worksheet,
        coords=status_cell,
        message='Uploaded %i %s.' % (len(data), model_type),
    )


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
        sheet.range(coords).color = literal_eval(background)
    if color:
        sheet.range(coords).api.Font.Color = rgb_to_int(literal_eval(color))


# openpyxl and pandas methods for reading data.

# def get_worksheet_headers(sheet):
#     """Get the headres of a worksheet.
#     Args:
#         sheet (Worksheet): An openpyx; Excel file object.
#     Returns:
#         headers (list): A list of header strings.
#     """
#     headers = []
#     for cell in sheet[1]:
#         headers.append(snake_case(cell.value))
#     return headers


# def get_worksheet_data(sheet, headers):
#     """Get the data of a worksheet.
#     Args:
#         sheet (Worksheet): An openpyx; Excel file object.
#         headres (list): A list of headers to map the values.
#     Returns:
#         list(dict): A list of dictionaries.
#     """
#     data = []
#     for row in sheet.iter_rows(min_row=2):
#         values = {}
#         for key, cell in zip(headers, row):
#             values[key] = cell.value
#         data.append(values)
#     return data


# def read_worksheet(path, filename='Upload'):
#     """Read the imported data, iterating over the rows and
#     getting value from each cell in row.
#     Args:
#         path (str or InMemoryFile): An Excel workbook to read.
#         filename (str): The name of the worksheet to upload.
#     Returns:
#         (DataFrame): A Pandas DataFrame of the results.
#     """
#     # try:
#     #     workbook = openpyxl.load_workbook(path, data_only=True)
#     #     sheet = workbook.get_sheet_by_name(filename)
#     #     headers = get_worksheet_headers(sheet)
#     #     return pd.DataFrame(get_worksheet_data(sheet, headers))
#     # except:
#     data = pd.read_csv(path)
#     data.columns = [snake_case(x) for x in data.columns]
#     return data

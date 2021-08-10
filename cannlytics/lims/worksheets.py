"""
Worksheets | Cannlytics

Author: Keegan Skeate <keegan@cannlytics.com>
Created: 7/18/2021
Updated: 7/20/2021
License: MIT License <https://opensource.org/licenses/MIT>
"""

try:

    # Standard packages
    from ast import literal_eval
    import os

    # External packages.
    from dotenv import load_dotenv
    from pandas import DataFrame, to_datetime
    import requests
    import xlwings
    from xlwings.utils import rgb_to_int

    # Internal packages.
    from cannlytics.utils.utils import snake_case

except:
    pass # FIXME: Docs can't import.


def get_data_block(sheet, coords, expand=None):
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


def increment_row(coords):
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


def import_worksheet(filename, sheetname, range_start='A1'):
    """Read the data from a given worksheet using xlwings.
    Args:
        filename (str): The name of the Excel file to read.
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
def import_worksheet_data(model_type):
    """A function called from Excel to import data by ID
    from Firestore into the Excel workbook.
    Args:
        model_type (str): The data model at hand.
    """

    # Initialize the workbook.
    book = xlwings.Book.caller()
    worksheet = book.sheets.active
    config_sheet = book.sheets['cannlytics.conf']
    config = get_data_block(config_sheet, 'A1', expand='table')
    show_status_message(
        worksheet,
        coords=config['status_cell'],
        message='Importing %s data...' % model_type,
        background=config['success_color'],
    )

    # Read the IDs.
    id_cell = increment_row(config['table_cell'])
    ids = worksheet.range(id_cell).options(expand='down', ndim=1).value

    # Get your Cannlytics API key from your .env file, location specified
    # by env_path on the cannlytics.config sheet.
    load_dotenv(config['env_path'])
    api_key = os.getenv('CANNLYTICS_API_KEY')

    # Get the worksheet columns.
    columns = worksheet.range(config['table_cell']).options(expand='right', ndim=1).value
    columns = [snake_case(x) for x in columns]

    # Get data using model type and ID through the API.
    base = config['api_url']
    org_id = worksheet.range(config['org_id_cell']).value
    headers = {
        'Authorization': 'Bearer %s' % api_key,
        'Content-type': 'application/json',
    }
    if len(ids) == 1:
        url = f'{base}/{model_type}/{ids[0]}?organization_id={org_id}'
    else:
        url = f'{base}/{model_type}?organization_id={org_id}&items={str(ids)}'
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        show_status_message(
            worksheet,
            coords=config['status_cell'],
            message='Error importing data.',
            background=config['error_color']
        )
        return

    # Format the values.
    items = []
    data = response.json()['data']
    if not data:
        show_status_message(
            worksheet,
            coords=config['status_cell'],
            message='No data found.',
            background=config['error_color']
        )
        return
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

    # Insert all rows at the same time.
    worksheet.range(id_cell).value = items

    # Show success status message.
    show_status_message(
        worksheet,
        coords=config['status_cell'],
        message='Imported %i %s.' % (len(ids), model_type),
    )


@xlwings.sub
def upload_worksheet_data(model_type):
    """A function called from Excel to import data by ID
    from Firestore into the Excel workbook."""

    # Initialize the workbook.
    book = xlwings.Book.caller()
    worksheet = book.sheets.active
    config_sheet = book.sheets['cannlytics.conf']
    config = get_data_block(config_sheet, 'A1', expand='table')
    show_status_message(
        worksheet,
        coords=config['status_cell'],
        message='Uploading %s data...' % model_type,
        background=config['success_color'],
    )

    # Read the table data, cleaning the column names.
    table = worksheet.range(config['table_cell'])
    data = table.options(DataFrame, index=False, expand='table').value
    data.columns = list(map(snake_case, data.columns))

    # Clean columns. (Optional: Clean more efficiently.)
    for column in data.columns:
        if column.endswith('_at'):
            try:
                data[column] = to_datetime(data[column]).dt.strftime('%Y-%m-%dT%H:%M%:%SZ')
            except:
                pass
    data = data.fillna('')

    # Determine the model type and the organization.
    org_id = worksheet.range(config['org_id_cell']).value
    model_singular = data.columns[0].replace('_id', '')
    if not org_id:
        show_status_message(
            worksheet,
            coords=config['status_cell'],
            message='Organization ID required.',
            background=config['error_color']
        )
        return

    # Get Cannlytics API key from .env using env_path in config.
    load_dotenv(config['env_path'])
    api_key = os.getenv('CANNLYTICS_API_KEY')

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
                coords=config['status_cell'],
                message='Uploaded %s' % doc_id,
            )
        else:
            show_status_message(
                worksheet,
                coords=config['status_cell'],
                message='Error uploading %s. Check your organization, internet connection and API key.' % doc_id, # pylint:disable=line-too-long
                background=config['error_color']
            )
            return

    # Show success status message.
    show_status_message(
        worksheet,
        coords=config['status_cell'],
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

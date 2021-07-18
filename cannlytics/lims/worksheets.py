"""
Worksheets | Cannlytics

Author: Keegan Skeate <keegan@cannlytics.com>
Created: 7/18/2021
Updated: 7/18/2021
License: MIT License <https://opensource.org/licenses/MIT>
"""
import requests
import xlwings as xw


def show_status_message(sheet, coords, message, background, color):
    """Show a status message in an Excel spreadsheet.
    Args:
        sheet
        coords
        message
        background
        color
    """


@xw.sub
def import_worksheet_data(model_type):
    """A function called from Excel to import data by ID
    from Firestore into the Excel workbook."""
    book = xw.Book.caller()
    
    # TODO: Show status message.
    
    # TODO: Read IDs.
    
    # TODO: Determine model type.
    
    # TODO: Get Cannlytics API key from .env.
    
    # TODO: Get data using model type and ID through the API.
    
    # TODO: Fill the data into Excel.
    
    # TODO: Show status message.
    

@xw.sub
def upload_worksheet_data(model_type):
    """A function called from Excel to import data by ID
    from Firestore into the Excel workbook."""
    book = xw.Book.caller()
    
    # TODO: Show status message.
    
    # TODO: Read table data.
    
    # TODO: Determine model type.
    
    # TODO: Get Cannlytics API key from .env.
    
    # TODO: Uplad data using model type, ID, and data through the API.
    
    # TODO: Fill the data into Excel.
    
    # TODO: Show status message.


# if __name__ == '__main__':
#     xw.Book('myproject.xlsm').set_mock_caller()
#     main()
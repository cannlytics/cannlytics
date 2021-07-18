"""
Upload Worksheet Data | Cannlytics Console

Author: Keegan Skeate <keegan@cannlytics.com>
Created: 7/18/2021
Updated: 7/18/2021
License: MIT License <https://opensource.org/licenses/MIT>
"""
import xlwings as xw


def upload_worksheet_data():
    """A function called from Excel to import data by ID
    from Firestore into the Excel workbook."""
    book = xw.Book.caller()


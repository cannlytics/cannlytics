"""
CoA Generation | Cannlytics

Author: Keegan Skeate <keegan@cannlytics.com>  
Created: 2/6/2021  
Updated: 7/15/2021  
License: MIT LIcense <https://opensource.org/licenses/MIT>

TODO:
    - Allow users to create CoA's with a myriad of templates! (.docx, .xlsx, etc.)
    - Import any docx template styed with Django formatting and let'r'rip.
    - Use your own templates or download the started templates and customize them to your heart's galore.
"""
from cannlytics.firebase import get_document, update_document



def create_coa():
    """
    Creates a certificate of analysis.
    """

    # TODO: Get sample details.

    # Get project details.

    # Get client details.

    # Get template.

    # Fill template

    # Create PDF in /tmp

    # Upload PDF to storage

    # Create short link (preferably create before upload?)

    # Create QR code

    # Update PDF, re-upload.

    return NotImplementedError


def delete_coa():
    """
    Delete a certificate of analysis from storage.
    """
    # Remove certificate from storage.
    # delete_file(bucket_name, blob_name)
    # Remove the certificate data.
    # update_document(ref, {'coa_url': '', 'coa_ref': ''})
    return NotImplementedError


def email_coas():
    """
    Email certificates of analysis to their recipients.
    """
    # Get the certificate data.
    # Email links (optional attachments) to the contacts.
    return NotImplementedError


def text_coas():
    """
    Text certificates of analysis to their recipients.
    """
    # Get the certificate data.
    # Text links to the contacts.
    return NotImplementedError


def send_coas():
    """
    Email and/or text certificates of analysis to their recipients.
    """
    # Email and / or text CoAs using email_coas and text_coas.
    return NotImplementedError


def get_coa_urls():
    """
    Get CoA URLs for given samples or projects.
    """
    # Get certificate data and return the short links.
    return NotImplementedError


def merge_coas():
    """
    Merge two CoAs together, either existing templates
    or existing PDFs.
    """
    # Get certificate data for the desired CoAs.
    # Download the existing PDFs for the certificates.
    # Merge the downloaded PDFs.
    # Upload the merged PDF to storage.
    # Create short link.
    # Create QR code.
    # Re-upload the PDF.
    return NotImplementedError



def approve_coa():
    """
    Creates a certificate of analysis.
    """
    # Verify the user's pin.
    # Get the user's signature.
    # Insert the user's signature on the certificate.
    return NotImplementedError


def review_coa():
    """
    Creates a certificate of analysis.
    """
    # Validate the user's pin.
    # Get the user's signature.
    # Insert the signature into the CoA template.
    # Create the PDF.
    # Upload the PDF to storage.
    # Save the reviewer data.
    return NotImplementedError


def upload_coa():
    """
    Upload a certificate of analysis to storage.
    """
    # Read file data.
    # Upload file data to storage.
    # Update certificate data.
    return NotImplementedError


def upload_coa_template():
    """
    Upload a certificate of analysis template to storage.
    """
    # Read in the file data.
    # Upload the template to storage.
    # Create a download link for the template.
    # Save the template data.
    return NotImplementedError


def create_short_url():
    """
    Create a short URL for a CoA link.
    """
    return NotImplementedError


# def insert_qr_code(sheet, coords, url):
#     """Insert a QR code into a CoA template.
#     Args:
#         sheet (Worksheet): The worksheet to insert the QR Code
#         ref (str): The location to insert the QR code.
#         url (str): The URL that the QR code should link.
#     Returns:
#     """
#     qr = qrcode.QRCode(
#         version=1,
#         error_correction=qrcode.constants.ERROR_CORRECT_L,
#         box_size=10,
#         border=4,
#     )
#     qr.add_data(url)
#     qr.make(fit=True)
#     img = qr.make_image(fill_color='black', back_color='white')
#     img.save('qr_code.png')
#     logo = Image('qr_code.png')
#     logo.height = 150
#     logo.width = 150
#     sheet.add_image(logo, coords)
#     # workbook.save(filename="hello_world_logo.xlsx")

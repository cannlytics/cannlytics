"""
CoA Generation | Cannlytics

Author: Keegan Skeate <keegan@cannlytics.com>
Created: 2/6/2021
Updated: 6/23/2021
License: MIT LIcense <https://opensource.org/licenses/MIT>

TODO:
    - Allow users to create CoA's with a myriad of templates! (.docx, .xlsx, etc.)
    - Import any docx template styed with Django formatting and let'r'rip.
    - Use your own templates or download the started templates and customize them to your heart's galore.
"""


def approve_coa():
    """
    Creates a certificate of analysis.
    """
    return NotImplementedError


def create_coa():
    """
    Creates a certificate of analysis.
    """
    return NotImplementedError


def delete_coa():
    """
    Delete a certificate of analysis from storage.
    """
    return NotImplementedError


def email_coas():
    """
    Email certificates of analysis to their recipients.
    """
    return NotImplementedError


def get_coa_urls():
    """
    Get CoA URLs for given samples or projects.
    """
    return NotImplementedError


def merge_coas():
    """
    Merge two CoAs together, either existing templates
    or existing PDFs.
    """
    return NotImplementedError


def review_coa():
    """
    Creates a certificate of analysis.
    """
    return NotImplementedError


def upload_coa():
    """
    Upload a certificate of analysis to storage.
    """
    return NotImplementedError


def upload_coa_template():
    """
    Upload a certificate of analysis template to storage.
    """
    return NotImplementedError

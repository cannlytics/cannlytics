"""
Transfer Management | Cannlytics

Author: Keegan Skeate <keegan@cannlytics.com>  
Created: 6/23/2021  
Updated: 6/23/2021  
License: MIT License <https://opensource.org/licenses/MIT>  

Tools to help manage transfers of laboratory samples.
"""


def receive_transfer(transfer_id):
    """
    Receive a transfer of laboratory samples.
    """
    packages = track.get_packages(license_number=cultivator.license_number)
    return NotImplementedError


def reject_transfer():
    """
    Reject a transfer of laboratory samples.
    """
    return NotImplementedError


"""
Transfer Management | Cannlytics

Author: Keegan Skeate <keegan@cannlytics.com>  
Created: 6/23/2021  
Updated: 6/23/2021  
License: MIT License <https://opensource.org/licenses/MIT>  

Tools to help manage transfers of laboratory samples.
"""

def create_transfer():
    """Create a transfer of samples to a lab for analysis. The sending
    organization specifies the sample details and the analyses requested.
    The receiving organization, the lab, can create projects from the
    sample details and analyses requested. The lab can edit sample details
    stored in a project, but only the sender can edit sample details in
    the transfer. By default, the sending organization will receive
    results when they are released."""

    return NotImplementedError


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


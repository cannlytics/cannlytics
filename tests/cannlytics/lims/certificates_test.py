"""
Certificates Test | Cannlytics

Author: Keegan Skeate <keegan@cannlytics.com>  
Created: 8/2/2021  
Updated: 8/2/2021  
License: MIT License <https://opensource.org/licenses/MIT>
"""
# Standard packages
import sys

# Internal imports.
sys.path.append('../../../')
# from cannlytics.lims import generate_coas # pylint: disable=import-error


EXAMPLE_CONTEXT = {
    'organization.logo': '',
    'organization.address': '',
    'organization.phone': '',
    'organization.license_number': '',
    'reviewed_by': '',
    'approved_by': '',
    'moisture_content.result': '',
    'moisture_content.limit': '',
    'water_activity_rate.result': '',
    'water_activity_rate.limit': '',
    'cannabinoids': '',
    'foreign_matter': '',
    'terpenes': '',
    'microbes': '',
    'heavy_metals': '',
    'mycotoxins': '',
    'residual_solvents': '',
    'pesticides': '',
}


if __name__ == '__main__':

    # TODO: Create a CoA PDF.
    print('Creating CoA PDF....')


    # TODO: Review a CoA.
    print('Creating CoA PDF....')


    # TODO: Approve a CoA PDF.
    print('Creating CoA PDF....')

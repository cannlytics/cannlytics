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
from cannlytics.lims import generate_coas # pylint: disable=import-error
from cannlytics.lims.certificates import approve_coa, review_coa
from cannlytics import firebase


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
    'notes': 'If you have any questions concerning this certificate of analysis, then please contact support@cannlytics.com. Abbreviations that may be used include: "nd", not-detected, "n/a", not applicable, "LOQ", lowest order of quantification, "LOD", lowest order of detection, "TNTC", too numerous to count.',
    'current_page': 1,
    'total_pages': 1,
}


if __name__ == '__main__':

    # TODO: Create a CoA PDF.
    print('Creating CoA PDF....')
    pages = ['Template']
    limits = {}
    coa_template = './coa_template.xlsm'
    coa_data = generate_coas(
        EXAMPLE_CONTEXT,
        coa_template=coa_template,
        output_pages=pages,
        limits=limits
    )


    # TODO: Review a CoA.
    custom_claims = firebase.get_custom_claims('test@cannlytics.com')
    for coa in coa_data:
        print('Reviewing CoA PDF....')
        review_coa(coa, custom_claims)


    # TODO: Approve a CoA PDF.
    print('Approving CoA PDF....')
    for coa in coa_data:
        print('Reviewing CoA PDF....')
        approve_coa(coa, custom_claims)

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
    'organization.logo': 'Logo',
    'organization.address': 'Olympia, Washington',
    'organization.phone': '(828) 395-3954',
    'organization.license_number': 'n/a',
    'reviewed_by': 'KLS',
    'approved_by': 'KLS',
    'moisture_content.result': '0',
    'moisture_content.limit': '0',
    'water_activity_rate.result': '0',
    'water_activity_rate.limit': '0',
    'cannabinoids': '0',
    'foreign_matter': '0',
    'terpenes': '0',
    'microbes': '0',
    'heavy_metals': '0',
    'mycotoxins': '0',
    'residual_solvents': '0',
    'pesticides': '0',
    'notes': 'If you have any questions concerning this certificate of analysis, then please contact support@cannlytics.com. Abbreviations that may be used include: "nd", not-detected, "n/a", not applicable, "LOQ", lowest order of quantification, "LOD", lowest order of detection, "TNTC", too numerous to count.',
    'current_page': 1,
    'total_pages': 1,
}


if __name__ == '__main__':

    # TODO: Create a CoA PDF.
    print('Creating CoA PDF....')
    pages = ['Page 1']
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

"""
Generate CoAs Test | Cannlytics

Authors: Keegan Skeate <keegan@cannlytics.com>  
Created: 8/1/2021  
Updated: 8/1/2021  
License: MIT License <https://opensource.org/licenses/MIT>
"""
# Standard packages
import sys

# Internal imports.
sys.path.append('../../../')
from cannlytics.lims import generate_coas # pylint: disable=import-error


if __name__ == '__main__':

    # Read in analyte limits.
    limits = generate_coas.get_analyte_limits()

    # Define test template and files.
    files = './Export Files'
    pages = ['Page 1', 'Page 2', 'Page 3', 'Page 4']

    # Test CoA generation.
    generate_coas.generate_coas(
        files,
        output_pages=pages,
        # coa_template=args.template,
        limits=limits
    )

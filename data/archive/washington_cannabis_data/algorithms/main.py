"""
Washington Cannabis Data
Copyright (c) 2022-2023 Cannlytics
Copyright (c) 2022-2023 Cannabis Data

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
    Candace O'Sullivan-Sutherland <https://github.com/candy-o>
Created: 1/7/2023
Updated: 5/5/2023
License: CC-BY 4.0 <https://huggingface.co/datasets/cannlytics/cannabis_tests/blob/main/LICENSE>

Original author: Cannabis Data
Original license: MIT <https://github.com/cannabisdata/cannabisdata/blob/main/LICENSE>

Data Source:

    - WSLCB PRR (latest)
    URL: <https://lcb.app.box.com/s/l9rtua9132sqs63qnbtbw13n40by0yml>

Command-line Usage:

    python cannabis_sales/washington/main.py

"""
# Internal imports:
try:
    from .curate_ccrs_lab_results import curate_ccrs_lab_results
    from .curate_ccrs_inventory import curate_ccrs_inventory
    # from .curate_ccrs_sales import curate_ccrs_sales
    # from .curate_ccrs_strains import curate_ccrs_strains
except:
    from curate_ccrs_lab_results import curate_ccrs_lab_results
    from curate_ccrs_inventory import curate_ccrs_inventory
    # from curate_ccrs_sales import curate_ccrs_sales
    # from curate_ccrs_strains import curate_ccrs_strains


# === Test ===
if __name__ == '__main__':

    # Specify the date of the public records request.
    DATE = '4-4-23'

    # TODO: Unzip the initial zipped folder.

    # Specify where your data lives.
    base = 'D:\\data\\washington\\'
    DATA_DIR = f'{base}\\CCRS PRR ({DATE})\\CCRS PRR ({DATE})\\'
    STATS_DIR = f'{base}\\ccrs-stats\\'
    curate_ccrs_lab_results(DATA_DIR, STATS_DIR)
    curate_ccrs_inventory(DATA_DIR, STATS_DIR)
    # curate_ccrs_sales(DATA_DIR, STATS_DIR)
    # curate_ccrs_strains(DATA_DIR, STATS_DIR)

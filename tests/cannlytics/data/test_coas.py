"""
CoADoc Tests
Copyright (c) 2022-2023 Cannlytics

Authors: Keegan Skeate <https://github.com/keeganskeate>
Created: 8/1/2022
Updated: 6/12/2023
License: <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description:  A rigorous test of CoADoc parsing.
"""
# Standard imports:
import os
import tempfile

# External imports:
import pandas as pd

# Internal imports:
from cannlytics.data.coas import CoADoc
from cannlytics.data.data import create_hash


#-----------------------------------------------------------------------
# [✓] TEST: Parse a directory of COA PDFs.
#-----------------------------------------------------------------------

def parse_coa_directory(data_dir: str, temp_path = None):

    # Initialize a parser.
    parser = CoADoc()

    # Create the output data directory before beginning.
    datafile_dir = f'{data_dir}/datafiles'
    if not os.path.exists(datafile_dir):
        os.makedirs(datafile_dir)

    # Iterate over PDF directory.
    all_data = []
    for path, subdirs, files in os.walk(data_dir):
        for name in files:

            # Only parse PDFs.
            if not name.endswith('.pdf'):
                continue

            # Parse COA PDFs one by one.
            try:
                filename = os.path.join(path, name)
                coa_data = parser.parse(filename, temp_path=temp_path)
                all_data.extend(coa_data)
                print('Parsed:', filename)
            except:
                print('Error:', filename)

    # Format the data as a DataFrame.
    data = pd.DataFrame(all_data)

    # Create hashes.
    coa_df = data.where(pd.notnull(data), None)
    coa_df['results_hash'] = coa_df['results'].apply(
        lambda x: create_hash(x),
    )
    coa_df['sample_hash'] = coa_df.loc[:, coa_df.columns != 'sample_hash'].apply(
        lambda x: create_hash(x.to_dict()),
        axis=1,
    )
    data_hash = create_hash(coa_df)

    # Standardize and save the CoA data.
    outfile = f'{datafile_dir}/{data_hash}.xlsx'
    parser.save(coa_df, outfile)
    print('Saved CoA data:', outfile)


#-----------------------------------------------------------------------
# [✓] TEST: Parse a directory of COA QR codes.
#-----------------------------------------------------------------------

def parse_coa_images(data_dir: str, temp_path = None):

    # Initialize a parser.
    parser = CoADoc()

    # Define directories.
    if temp_path is None:
        temp_directory = tempfile.gettempdir()
        temp_path = os.path.join(temp_directory, 'cannlytics')

    # Iterate over PDF directory.
    coa_urls = []
    images = os.listdir(data_dir)
    print('Scanning %i images.' % len(images))
    for path in images:
        filename = os.path.join(data_dir, path)
        qr_code_url = parser.scan(filename, temp_path=temp_path)
        if qr_code_url:
            coa_urls.append(qr_code_url)
            print('Scanned:', qr_code_url)

    # Keep only unique URLs.
    coa_urls = list(set(coa_urls))
    print('Scanned %i unique QR codes.' % len(coa_urls))

    # Try to parse each URL.
    all_data = []
    for coa_url in coa_urls:
        try:
            coa_data = parser.parse(coa_url, temp_path=temp_path)
            all_data.extend(coa_data)
            print('Parsed:', coa_url)
        except:
            print('Error:', coa_url)

    # Standardize and save the CoA data.
    outfile = os.path.join(temp_path, 'coa-data.xlsx')
    parser.save(all_data, outfile)
    print('Saved data for %i COAs:' % len(all_data), outfile)
    return all_data


#-----------------------------------------------------------------------
# [ ] TEST: Parse COAs with AI.
#-----------------------------------------------------------------------

# TODO: Write a test to batch parse COAs with AI.

# # Get a sample of COA PDFs.
# pdf_files = glob.glob(os.path.join(DATA_DIR, "*.pdf"))

# # Parse each COA PDF with AI.
# parsed_coas = []
# for pdf_file in pdf_files[:5]:
#     coa_data = parse_coa_with_ai(pdf_file)
#     coa_data['filename'] = pdf_file
#     parsed_coas.append(coa_data)

# # Format the data as a DataFrame.
# coa_df = pd.DataFrame(parsed_coas)

# # Remove any COAs that could not be parsed.
# coa_df.dropna(inplace=True)

# # Save the data.
# coa_df.to_csv(os.path.join(DATA_DIR, 'parsed-fl-coas.csv'), index=False)


# === Tests ===
# Performed 2023-06-12 by Keegan Skeate <admin@cannlytics.com>.
if __name__ == '__main__':

    # Specify where your data lives.
    DATA_DIR = '.datasets/coas/Flore COA'
    TEMP_PATH = '.datasets/coas/tmp'

    # [✓] TEST: Parse a directory of COA PDFs.
    parse_coa_directory(DATA_DIR, TEMP_PATH)

    # [✓] TEST: Parse a directory of QR code images.
    IMAGE_DIR = '../../../.datasets\coas\qr-codes'
    parse_coa_images(IMAGE_DIR)

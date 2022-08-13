"""
CoADoc Test
Copyright (c) 2022 Cannlytics

Authors: Keegan Skeate <https://github.com/keeganskeate>
Created: 8/1/2022
Updated: 8/12/2022
License: <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description:

    A rigorous test of CoADoc parsing.

"""
# Standard imports.
from ast import literal_eval
from datetime import datetime
import os
from time import sleep

# External imports.
import pandas as pd

# Internal imports.
from cannlytics.data.coas import CoADoc
from cannlytics.firebase import initialize_firebase, update_documents
from cannlytics.utils.utils import to_excel_with_style


# Specify where your data lives.
DATA_DIR = '../../../.datasets/coas/Flore COA'

# Initialize a parser.
parser = CoADoc()

# Create the output data directory before beginning.
datafile_dir = f'{DATA_DIR}/datafiles'
if not os.path.exists(datafile_dir):
    os.makedirs(datafile_dir)

# Iterate over PDF directory.
all_data = []
identified = []
unidentified = []
skip = [
    # 'Peanutbutter Breath.pdf', # Betty Project (Anresco Laboratories)
    # 'MothersMilk.pdf', # Kiva (Cannalysis)
    # 'BlueDream.pdf', # Peak (Sonoma Lab Works)
    # 'LemonTree.pdf', # Peak (Sonoma Lab Works)
    # 'RainbowBeltz.pdf' # Peak (Sonoma Lab Works)
]
for path, subdirs, files in os.walk(DATA_DIR):
    for name in reversed(files):

        # DEV: Look at the 1st CoA.
        # if len(identified) > 1:
        #     break

        # Only parse PDFs.
        if not name.endswith('.pdf'):
            continue

        # [✓] Test: Identify the lab or LIMS from the CoA PDF.
        file_name = os.path.join(path, name)
        lab = parser.identify_lims(file_name)
        if lab:
            identified.append(file_name)
            print('Identified:', lab, file_name.split('/')[-1])
        elif name in skip:
            continue
        else:
            unidentified.append(file_name)

        # DEV: Only collect CoAs from a specific lab / LIMS.
        if lab != 'SC Labs':
            continue

        # Dev: Skip recorded CoAs.
        # file_name = os.path.join(path, name)
        # if file_name in identified or file_name in skip:
        #     continue

        # try:

        # Parse CoA PDFs one by one.
        file_name = os.path.join(path, name)
        coa_data = parser.parse(file_name)
        all_data.extend(coa_data)

        # Save the individual data files.
        timestamp = datetime.now().isoformat()[:19].replace(':', '-')
        outfile = f'{datafile_dir}/coa-data-{timestamp}.xlsx'
        parser.save(coa_data, outfile)
        # to_excel_with_style(pd.DataFrame(coa_data), outfile)
        print('Parsed:', name)
        identified.append(file_name)

        # except:
        #     print('Failed to parse:', name)
        #     unidentified.append(file_name)
        #     skip.append(file_name)

percent = len(identified) / (len(identified) + len(unidentified)) * 100
print('Identified %.2f%% of the CoAs.' % percent)

# FIXME:
# data = pd.read_excel(f'{datafile_dir}/coa-aggregated-data-2022-08-09T15-12-38.xlsx')
# data['results'] = data['results'].apply(literal_eval)

# Format the data.
data = pd.DataFrame(all_data)

# Aggregate all of the individual data files.
timestamp = datetime.now().isoformat()[:19].replace(':', '-')
outfile = f'{datafile_dir}/coa-aggregated-data-{timestamp}.xlsx'
data.index = data['sample_id']
parser.save(data, outfile)


# TODO:
# # Format any public data to upload to Firestore.
# refs, updates = [], []
# for index, values in data.iterrows():
#     if not values['public']:
#         continue
#     sample_id = values['sample_id']
#     refs.append(f'public/data/lab_results/{sample_id}')
#     updates.append(values.to_dict())

# # Upload any public data to Firestore!
# if updates:
#     database = initialize_firebase()
#     update_documents(refs, updates, database=database)
#     print('Uploaded %i results to Firestore!' % len(updates))

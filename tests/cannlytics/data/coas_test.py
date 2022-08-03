"""
CoADoc Test
Copyright (c) 2022 Cannlytics

Authors: Keegan Skeate <https://github.com/keeganskeate>
Created: 8/1/2022
Updated: 8/1/2022
License: <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description:

    A rigorous test of CoA parsing.

"""
# Standard imports.
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

# Iterate over PDF directory.
all_data = []
identified = []
unidentified = []
skip = [
    'Peanutbutter Breath.pdf', # Betty Project (Anresco Laboratories)
    'MothersMilk.pdf', # Kiva (Cannalysis)
    'BlueDream.pdf', # Peak (Sonoma Lab Works)
    'LemonTree.pdf', # Peak (Sonoma Lab Works)
    'RainbowBeltz.pdf' # Peak (Sonoma Lab Works)
]
for path, subdirs, files in os.walk(DATA_DIR):
    for name in files:

        # Only parse PDFs.
        if not name.endswith('.pdf'):
            continue

        # See which PDFs we can identify :p
        file_name = os.path.join(path, name)
        lab = parser.identify_lims(file_name)


        if lab != 'SC Labs':
            continue

        if lab:
            identified.append(file_name)
            print('Identified:', lab, file_name.split('/')[-1])
        elif name in skip:
            continue
        else:
            unidentified.append(file_name)

        # Parse CoAs one by one!
        coa_data = parser.parse(file_name)
        all_data.extend(coa_data)

        # Save the individual data files.
        timestamp = datetime.now().isoformat()[:19].replace(':', '-')
        outfile = f'{DATA_DIR}/datafiles/coa-data-{timestamp}.xlsx'
        to_excel_with_style(pd.DataFrame(coa_data), outfile)

        print('Parsed:', name)

percent = len(identified) / (len(identified) + len(unidentified)) * 100
print('Identified %.2f%% of the CoAs.' % percent)

# Aggregate all of the individual data files.
data = pd.DataFrame(all_data)
data.index = data['sample_id']

# Widen and elongate the data.
long_data = pd.json_normalize(data['results'])

# Save the data.
timestamp = datetime.now().isoformat()[:19].replace(':', '-')
outfile = f'{DATA_DIR}/datafiles/coa-data-{timestamp}.xlsx'
writer = pd.ExcelWriter(outfile)
pd.DataFrame(data).to_excel(writer, 'Details')
pd.DataFrame(long_data).to_excel(writer, 'Results')
writer.save()
writer.close()

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

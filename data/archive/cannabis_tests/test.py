"""
Test Cannabis Tests Dataset
Copyright (c) 2022 Cannlytics

Authors: Keegan Skeate <https://github.com/keeganskeate>
Created: 9/16/2022
Updated: 9/16/2022
License: CC-BY 4.0 <https://huggingface.co/datasets/cannlytics/cannabis_tests/blob/main/LICENSE>
"""
from cannlytics.data.coas import CoADoc
from datasets import load_dataset
import pandas as pd

# Download Raw Garden lab result details.
repo = 'cannlytics/cannabis_tests'
dataset = load_dataset(repo, 'rawgarden')
details = dataset['details']

# Save the data locally with "Details", "Results", and "Values" worksheets.
outfile = 'rawgarden.xlsx'
parser = CoADoc()
parser.save(details.to_pandas(), outfile)

# Read the values.
values = pd.read_excel(outfile, sheet_name='Values')

# Read the results.
results = pd.read_excel(outfile, sheet_name='Results')

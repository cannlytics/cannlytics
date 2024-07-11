"""
Get Cannabis Results | Hawaii
Copyright (c) 2024 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
Created: 7/10/2024
Updated: 7/10/2024
License: CC-BY 4.0 <https://huggingface.co/datasets/cannlytics/cannabis_tests/blob/main/LICENSE>

Data Source:

    - Public records request

"""
# Standard imports:
import json
import os

# External imports:
from cannlytics.data.coas.coas import CoADoc
from cannlytics.data.coas import standardize_results
from cannlytics.data.coas.parsing import find_unique_analytes
from cannlytics.utils.utils import convert_to_numeric, snake_case
import pandas as pd


def extract_samples(datafile, verbose=True):
    """Extract samples from CSV layout."""

    # Read the datafile, line by line.
    if verbose: print('Processing:', datafile)
    with open(datafile, 'r') as file:
        lines = file.readlines()

    # Define rows to skip.
    skip_rows = [
        '"',
        "Date",
        "Report:",
        "LicenseNum:",
        "Start:",
        "End:",
        "Status:",
        "Report Timestamp"
    ]

    # Extract the data for each sample.
    parser = CoADoc()
    samples = []
    obs = None
    analyses, results = [], []
    for i, line in enumerate(lines):

        # Skip nuisance rows.
        skip = False
        for skip_row in skip_rows:
            if line.startswith(skip_row):
                skip = True
                break
        if skip:
            continue
        
        # Get all values.
        values = line.replace('\n', '').split(',')

        # Skip blank rows.
        if all([x == '' for x  in values]):
            continue

        # Identify samples as rows that start with a date.
        try: date = pd.to_datetime(values[0])
        except: date = None
        if date and values[0] != '':

            # Record results for any existing observation.
            if obs is not None:
                obs['analyses'] = json.dumps(analyses)
                obs['results'] = json.dumps(results)
                samples.append(obs)
                analyses, results = [], []

            # Get the details for each sample.
            try:
                ids = values[4]
                batch_number = ids.split('(')[0].split(':')[-1].strip()
                sample_id = ids.split(':')[-1].replace(')', '').strip()
                obs = {
                    'date_tested': date.isoformat(),
                    'product_type': values[1],
                    'strain_name': values[2],
                    'product_name': values[3],
                    'batch_number': batch_number,
                    'sample_id': sample_id,
                    'status': values[-3],
                    'producer': values[-2],
                    'producer_license_number': values[-1],
                }
            # Handle long product names.
            except:
                try:
                    row = lines[i + 1].replace('\n', '').split(',')
                    ids = row[1]
                except:
                    row = lines[i + 1].replace('\n', '').split(',') + lines[i + 2].replace('\n', '').split(',')
                    ids = row[-4]
                batch_number = ids.split('(')[0].split(':')[-1].strip()
                sample_id = ids.split(':')[-1].replace(')', '').strip()
                obs = {
                    'date_tested': date.isoformat(),
                    'product_type': values[1],
                    'strain_name': values[2],
                    'product_name': ' '.join([values[3], row[0]]),
                    'batch_number': batch_number,
                    'sample_id': sample_id,
                    'status': row[-3],
                    'producer': row[-2],
                    'producer_license_number': row[-1],
                }
            continue

        # Get the cannabinoid results.
        if values[0] == 'Potency Analysis Test':
            analyses.append('cannabinoids')
            n_analytes = 5
            for n in range(1, n_analytes + 1):
                row = lines[i + n].replace('\n', '').split(',')
                name = row[0]
                key = parser.analytes.get(snake_case(name), snake_case(name))
                if name == 'Total':
                    obs['total_cannabinoids'] = convert_to_numeric(row[1].replace('%', ''))
                    continue
                results.append({
                    'analysis': 'cannabinoids',
                    'key': key,
                    'name': name,
                    'value': convert_to_numeric(row[1].replace('%', '')),
                    'status': row[2],
                })
            continue

        # Get the foreign matter results.
        if values[0] == 'Foreign Matter Inspection Test':
            analyses.append('foreign_matter')
            row = lines[i + 1].replace('\n', '').split(',')
            results.append({
                'analysis': 'foreign_matter',
                'key': 'foreign_matter',
                'name': 'Foreign Matter',
                'value': convert_to_numeric(row[1].replace('%', '')),
                'status': row[2],
            })
            continue

        # Get the microbe results.
        if values[0] == 'Microbiological Screening Test':
            analyses.append('microbes')
            n_analytes = 6
            for n in range(1, n_analytes + 1):
                row = lines[i + n].replace('\n', '').split(',')
                name = row[0]
                key = parser.analytes.get(snake_case(name), snake_case(name))
                if name == '': continue
                results.append({
                    'analysis': 'microbes',
                    'key': key,
                    'name': name,
                    'value': convert_to_numeric(row[1].split(' ')[0]),
                    'units': row[1].split(' ')[-1],
                    'status': row[2],
                })
            continue

        # Get the mycotoxin results.
        if values[0] == 'Mycotoxin Screening Test':
            analyses.append('mycotoxins')
            row = lines[i + 1].replace('\n', '').split(',')
            name = row[0]
            key = parser.analytes.get(snake_case(name), snake_case(name))
            results.append({
                'analysis': 'mycotoxins',
                'key': key,
                'name': name,
                'value': convert_to_numeric(row[1].split(' ')[0]),
                'status': row[2],
            })
            continue

        # Get the moisture content result.
        if values[0] == 'Moisture Content Test':
            analyses.append('moisture_content')
            row = lines[i + 1].replace('\n', '').split(',')
            value = convert_to_numeric(row[1].replace('%', ''))
            obs['moisture_content'] = value
            continue

        # Get the residual solvent results.
        # See: https://health.hawaii.gov/medicalcannabis/files/2022/05/Chapter-11-850-Hawaii-Administrative-Interim-Rules-Effective-April-29-2022.pdf
        if values[0] == 'Residual Solvent Test':
            analyses.append('residual_solvents')
            solvents = [
                'Benzene',
                'Butane',
                'Ethanol',
                'Heptane',
                'Hexane',
                'Pentane',
                'Toluene',
                'Total xylenes'
            ]
            for n in range(1, len(solvents) + 1):
                row = lines[i + n].replace('\n', '').split(',')
                name = solvents[n - 1]
                key = parser.analytes.get(snake_case(name), snake_case(name))
                results.append({
                    'analysis': 'residual_solvents',
                    'key': key,
                    'name': name,
                    'value': convert_to_numeric(row[1].split(' ')[0]),
                    'units': row[1].split(' ')[-1],
                    'status': row[2],
                })
            continue

    # Record the last sample's results.
    obs['analyses'] = json.dumps(analyses)
    obs['results'] = json.dumps(results)
    samples.append(obs)

    # Return the samples.
    return pd.DataFrame(samples)


# === Tests ===
# [ ] Tested: 2024-07-10 by Keegan Skeate <keegan@cannlytics.com>
if __name__ == '__main__':
        
    # Define where the data lives.
    data_dir = 'D://data/hawaii/public-records'
    datafiles = [os.path.join(data_dir, x) for x in os.listdir(data_dir) if x.endswith('.csv')]

    # Process each CSV file.
    data = [extract_samples(file) for file in datafiles]

    # Aggregate all samples.
    results = pd.concat(data, ignore_index=True)
    print('Number of results:', len(results))

    # Standardize the results.
    analytes = find_unique_analytes(results)
    analytes = sorted(list(analytes))
    results = standardize_results(results, analytes)

    # Standardize time.
    results['date'] = pd.to_datetime(results['date_tested'], format='mixed')
    results['week'] = results['date'].dt.to_period('W').astype(str)
    results['month'] = results['date'].dt.to_period('M').astype(str)
    results = results.sort_values('date')

    # Save the results.
    last_test_date = results['date'].max().strftime('%Y-%m-%d')
    outfile = f'D://data/hawaii/hi-results-{last_test_date}.xlsx'
    outfile_csv = f'D://data/hawaii/hi-results-latest.csv'
    outfile_json = f'D://data/hawaii/hi-results-latest.jsonl'
    results.to_excel(outfile, index=False)
    results.to_csv(outfile_csv, index=False)
    results.to_json(outfile_json, orient='records', lines=True)
    print('Saved Excel:', outfile)
    print('Saved CSV:', outfile_csv)
    print('Saved JSON:', outfile_json)

    # Print out features.
    features = {x: 'string' for x in results.columns}
    print('Number of features:', len(features))
    print('Features:', features)

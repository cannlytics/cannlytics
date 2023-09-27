"""
Get MD Lab Result Data
Copyright (c) 2023 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
    Candace O'Sullivan-Sutherland <https://github.com/candy-o>
Created: 8/13/2023
Updated: 8/13/2023
License: CC-BY 4.0 <https://huggingface.co/datasets/cannlytics/cannabis_tests/blob/main/LICENSE>

Description:

    Collect all public Maryland lab result data.

Data Sources:
    
    - Public records request from the Maryland Cannabis Administration (MCA).

"""
import os
import re
import numpy as np
import pandas as pd
import pdfplumber
from datetime import datetime
from cannlytics.utils import snake_case


STATE = 'MD'


def extract_info(line):
    """Extracts the tag, category, test name, test passed, and result from a line of text."""
    # Extract Tag and Category.
    tag, rest_of_line = line.split(" ", 1)
    category, rest_of_line = rest_of_line.split(" ", 1)

    # Identify if Test Passed is merged or not.
    if "TR PUlaEnt" in rest_of_line:
        test_passed = "TRUE"
        test_name, rest_of_line = rest_of_line.rsplit("TR PUlaEnt", 1)
    elif "FA PLlSaEnt" in rest_of_line:
        test_passed = "FALSE"
        test_name, rest_of_line = rest_of_line.rsplit("FA PLlSaEnt", 1)
    elif " TRUE" in rest_of_line:
        test_passed = "TRUE"
        test_name, rest_of_line = rest_of_line.rsplit(" TRUE", 1)
    elif " FALSE" in rest_of_line:
        test_passed = "FALSE"
        test_name, rest_of_line = rest_of_line.rsplit(" FALSE", 1)
    else:
        test_passed = None
        test_name = None

    # Extract result using regex.
    result_match = re.search(r'(\d+(\.\d+)?)', rest_of_line)
    result = result_match.group(1) if result_match else None
    return tag, category, test_name, test_passed, result


def extract_producer_id(label):
    """Extracts the producer ID from a Metrc label."""
    return label[7:13]


def extract_data_from_pdf(pdf_path):

    # Read the PDF.
    pdf = pdfplumber.open(pdf_path)

    # Define the folder path and create it if it doesn't exist
    dataset_folder = os.path.join(os.path.dirname(pdf_path), ".datasets")
    if not os.path.exists(dataset_folder):
        os.makedirs(dataset_folder)

    # Chunk up the pages.
    page_numbers = list(range(0, len(pdf.pages), 100))
    if page_numbers[-1] != len(pdf.pages):
        page_numbers.append(len(pdf.pages))

    # Define the columns.
    columns = [
        'metrc_lab_id',
        'product_type',
        'analyte',
        'status',
        'value'
    ]

    # Loop through each page in the PDF.
    dates = []
    for start, end in zip(page_numbers[:-1], page_numbers[1:]):

        if start < 3999:
            continue

        results = []
        for page in pdf.pages[start:end]:

            # Extract data from the PDF page.
            text = page.extract_text()
            lines = text.split('\n')
            try:
                extracted_data = [extract_info(row) for row in lines]
                df = pd.DataFrame(
                    extracted_data,
                    columns=columns
                )
                results.append(df)
                df = pd.concat(results[1:])
            except:
                # FIXME: Figure out how to augment dates.
                # dates.extend(lines)
                continue

        # Combine the results.
        
        # df['date_tested'] = dates[1:len(df) + 1]

        # Convert the 'product_name' column to snake_case
        df['analyte'] = df['analyte'].apply(lambda x: snake_case(str(x)))

        # Pivot the dataframe
        pivot_df = df.pivot_table(
            index=['metrc_lab_id', 'product_type',], # 'date_tested'
            columns='analyte',
            values='value',
            aggfunc='first'
        ).reset_index()

        # Determine the "status" based on the "date_tested" column
        status = df.groupby('metrc_lab_id')['status'].apply(lambda x: 'Fail' if 'FALSE' in x.values else 'Pass')
        pivot_df = pivot_df.merge(status, left_on='metrc_lab_id', right_index=True)

        # FIXME: Rename columns
        # pivot_df = pivot_df.rename(columns={
        #     'thc_percent_raw_plant_material': 'delta_9_thc',
        #     'thca_percent_raw_plant_material': 'thca',
        #     'total_yeast_and_mold_count_cfutog_raw': 'microbes'
        # })

        # TODO: Keep track of "R&D Testing".

        # TODO: Keep track of stability testing.

        # TODO: Calculate total THC.
        # df['total_thc'] = 0.877 * df['thca'] + df['delta_9_thc']

        # Assign producer ID.
        df['producer_id'] = df['metrc_lab_id'].apply(extract_producer_id)
        df['producer_state'] = STATE

        # # TODO: Add standard data.
        # pivot_df['analyses'] = ["cannabinoids", "microbes"]
        # obs['sample_hash'] = create_hash(obs)
        # # sample_id
        filename = os.path.join(dataset_folder, f"md_results_{start}_{end-1}.csv")
        pivot_df.to_csv(filename, index=False)
        print(f"Data saved: {filename}")

    # Close the PDF.
    pdf.close()

    # Save the dates.
    dates_df = pd.DataFrame(dates, columns=['date_tested'])
    dates_df.to_excel(os.path.join(dataset_folder, 'md_dates.xlsx'), index=False)
    print(f"Dates saved: {os.path.join(dataset_folder, 'md_dates.xlsx')}")


def aggregate_datasets(folder_path, output_filename):
    """
    Aggregates and saves all datasets in the specified folder.

    Args:
        folder_path (str): Path to the folder containing individual dataset CSV files.
        output_filename (str): Name of the output CSV file to save the compiled dataset.
    """
    all_files = [os.path.join(folder_path, filename) for filename in os.listdir(folder_path) if filename.endswith('.csv')]
    dfs = [pd.read_csv(file) for file in all_files]
    compiled_df = pd.concat(dfs, ignore_index=True)
    compiled_df.to_csv(output_filename, index=False)
    print(f"Data compiled and saved: {output_filename}")


def standardize_data(df, output_filename):
    """Standardizes the data and saves it to a CSV file."""

    # TODO: Standardize the data.

    # Extract product subtype
    product_types = [
        'raw_plant_material',
        'edibles',
        'infused_non_edibles',
        'inhalabletovape_concentrate'
    ]
    df['product_type'] = None
    for subtype in product_types:
        mask = df.filter(like=subtype).notnull().any(axis=1)
        df.loc[mask, 'product_type'] = subtype

    # FIXME: Standardize columns
    # df['delta_9_thc'] = df['thc_percent_raw_plant_material']
    # df['thca'] = df['thca_percent_raw_plant_material']
    # df['microbes'] = df['total_yeast_and_mold_count_cfutog_raw']

    # FIXME: Add a dummy variable for R&D.
    # df['is_r_and_d'] = (df.filter(like='randd_testing').notnull().any(axis=1)).astype(int)

    # TODO: Add a dummy variable for stability tests.

    # FIXME: Remove old columns
    # cols_to_remove = df.filter(like='randd_testing').columns.tolist()
    # cols_to_remove.extend(['thc_percent_raw_plant_material', 'thca_percent_raw_plant_material', 'total_yeast_and_mold_count_cfutog_raw'])
    # df = df.drop(columns=cols_to_remove)

    # Save the resulting DataFrame as a CSV file
    df.to_csv(output_filename, index=False)
    print(f"Data standardized and saved: {output_filename}")


def get_unique_analytes(df):
    """Get a list of all analytes."""
    unique_analytes = set()
    for col in list(df.columns):
        analyte_name = col.split('(')[0].strip()
        unique_analytes.add(analyte_name)
    return sorted(list(unique_analytes))


def standardize_long_results():
    """Standardize the long results data."""

    data_dir = r"D:\data\maryland\prr"

    # Aggregate all lab results.
    all_data = []

    for dirpath, _, filenames in os.walk(data_dir):
        for filename in filenames:
            if filename.endswith('.csv'):
                filepath = os.path.join(dirpath, filename)
                df = pd.read_csv(filepath)
                all_data.append(df)

    # Combine all dataframes (if necessary)
    df = pd.concat(all_data, ignore_index=True)

    # TODO: Standardize the data.

    # Pivot the dataframe
    pivot_df = df.pivot_table(
        index=['TestYear', 'PackageId', 'StrainName', 'TestingFacilityId',], # 'date_tested'
        columns='TestTypeName',
        values='TestResultLevel',
        aggfunc='first'
    ).reset_index()

    # Determine the "status" based on the "date_tested" column
    status = df.groupby('PackageId')['TestPassed'].apply(lambda x: 'Fail' if False in x.values else 'Pass')
    pivot_df = pivot_df.merge(status, left_on='PackageId', right_index=True)

    # # Isolate a specific test.
    # test = 'Total Yeast and Mold Count (CFU/g) Raw Plant Material'
    # ym = pivot_df[pivot_df[test].notna()]

    # Standardize the columns.
    std = pd.DataFrame(pivot_df)
    std['product_subtype'] = None

    # Get a list of all analytes.
    analytes = get_unique_analytes(pivot_df)
    elements_to_remove = ['TestPassed', 'TestingFacilityId', 'TestYear', 'StrainName']
    analytes = [x for x in analytes if x not in elements_to_remove]
    for analyte in analytes:
        std[analyte] = np.nan

    # FIXME: Get the result for each analyte.
    skip_columns = ['PackageId', 'TestingFacilityId', 'TestPassed',
                    'TestYear', 'StrainName']
    for index, row in pivot_df.iterrows():
        for col in pivot_df.columns:
            if col not in skip_columns:
                if pd.notna(row[col]):
                    analyte = col.split('(')[0].strip()
                    subtype = col.split(')')[-1].strip()
                    std.at[index, 'product_subtype'] = subtype
                    std.at[index, analyte] = row[col]

    # Remove the old columns.
    std = std[[col for col in std.columns if "(" not in col]]

    # Add standard columns.
    std['sample_id'] = pivot_df['PackageId']

    # TODO: Rename columns.
    # std['year'] = pivot_df['TestYear']
    # std['strain_name'] = pivot_df['StrainName']
    # std['lab_id'] = pivot_df['TestingFacilityId']

    # Save the results.
    outfile = "../data/md/raw/md-lab-results-2023-09-27.csv"
    std.to_csv(outfile, index=False)
    print(f"Data standardized and saved: {outfile}")


# === Test ===
# [✓] Tested: 2023-09-27 by Keegan Skeate <keegan@cannlytics>
if __name__ == "__main__":

    # Extract all data.
    pdf_path = "../data/md/raw/public-records-request-md-2023-06-30.pdf"
    extract_data_from_pdf(pdf_path)

    # Aggregate the data.
    dataset_folder = os.path.join(os.path.dirname(pdf_path), ".datasets")
    aggregate_datasets(dataset_folder, "../data/md/raw/md-lab-results-2023-06-30.csv")

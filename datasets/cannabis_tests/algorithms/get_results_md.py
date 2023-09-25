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
import pandas as pd
import pdfplumber
from datetime import datetime
from cannlytics.utils import snake_case


# def extract_columns_from_page(page, column_widths):
#     column_texts = []
#     left_edge = 0
#     for width in column_widths:
#         right_edge = left_edge + width
#         bbox = (left_edge, 0, right_edge, page.height)
#         column = page.crop(bbox)
#         column_text = column.extract_text()
#         column_texts.append(column_text)
#         left_edge = right_edge
#     return column_texts


def extract_info(line):
    """Extracts the tag, category, test name, test passed, and result from a line of text."""
    # Extract Tag and Category
    tag, rest_of_line = line.split(" ", 1)
    category, rest_of_line = rest_of_line.split(" ", 1)

    # Identify if Test Passed is merged or not
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

    # Extract result using regex
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
        'category',
        'analyte',
        'status',
        'value'
    ]

    # Loop through each page in the PDF.
    dates = []
    for start, end in zip(page_numbers[:-1], page_numbers[1:]):

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
            except:
                # TODO: Figure out how to augment dates.
                # dates.extend(lines)
                continue

        # Combine the results.
        df = pd.concat(results[1:])
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

        # Calculate total THC.
        # df['total_thc'] = 0.877 * df['thca'] + df['delta_9_thc']

        # Assign producer ID.
        df['producer_id'] = df['metrc_lab_id'].apply(extract_producer_id)

        # # TODO: Add standard data.
        # pivot_df['analyses'] = ["cannabinoids", "microbes"]
        # obs['sample_hash'] = create_hash(obs)
        # # sample_id
        filename = os.path.join(dataset_folder, f"md_results_{start}_{end-1}.csv")
        pivot_df.to_csv(filename, index=False)

    # Close the PDF.
    pdf.close()


def aggregate_datasets(folder_path, output_filename):
    """
    Aggregates and saves all datasets in the specified folder.

    Args:
        folder_path (str): Path to the folder containing individual dataset CSV files.
        output_filename (str): Name of the output CSV file to save the compiled dataset.
    """
    all_files = [os.path.join(folder_path, filename) for filename in os.listdir(folder_path) if filename.endswith('.csv')]
    
    # List comprehension to read each CSV file into a DataFrame
    dfs = [pd.read_csv(file) for file in all_files]
    
    # Concatenate all DataFrames into a single DataFrame
    compiled_df = pd.concat(dfs, ignore_index=True)
    
    # Save the resulting DataFrame as a CSV file
    compiled_df.to_csv(output_filename, index=False)
    print(f"Data compiled and saved: {output_filename}")



# TODO: Standardize the data.
def standardize_data(df, output_filename):

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

    # FIXME: Remove old columns
    # cols_to_remove = df.filter(like='randd_testing').columns.tolist()
    # cols_to_remove.extend(['thc_percent_raw_plant_material', 'thca_percent_raw_plant_material', 'total_yeast_and_mold_count_cfutog_raw'])
    # df = df.drop(columns=cols_to_remove)

    # Save the resulting DataFrame as a CSV file
    df.to_csv(output_filename, index=False)
    print(f"Data standardized and saved: {output_filename}")


# def save_data(all_results):
#     # Save the results to Excel.
#     data = pd.DataFrame(all_results)
#     date = datetime.now().isoformat()[:10]
#     data_dir = "./data"  # Define your data directory path
#     if not os.path.exists(data_dir):
#         os.makedirs(data_dir)
#     datafile = f'{data_dir}/ma-lab-results-{date}.xlsx'
#     try:
#         data.to_excel(datafile, index=False)
#     except:
#         print("Error occurred when saving the data to Excel.")


# === Test ===
# [ ] Tested:
if __name__ == "__main__":

    # Extract all data.
    pdf_path = "../data/md/raw/public-records-request-md-2023-06-30.pdf"
    extract_data_from_pdf(pdf_path)

    # Aggregate the data.
    dataset_folder = os.path.join(os.path.dirname(pdf_path), ".datasets")
    aggregate_datasets(dataset_folder, "../data/md/raw/public-records-request-md-2023-06-30.csv")

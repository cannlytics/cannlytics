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
import pandas as pd
import pdfplumber
from datetime import datetime

def extract_data_from_pdf(pdf_path):
    # Initialize the pdfplumber object with the PDF file path.
    pdf = pdfplumber.open(pdf_path)

    # Loop through each page in the PDF.
    results, dates = [], []
    for page in pdf.pages:

        # Extract tables from the PDF page.
        text = page.extract_text()
        lines = text.split('\n')
        if lines[0].startswith('Tag'):
            header = 'Tag'
            lines = lines[1:]
        elif lines[0].startswith('Packaged Date'):
            header = 'Packaged Date'
            lines = lines[1:]

        # Loop through each line of the table to records results.
        for line in lines:
            if header == 'Tag':
                # FIXME: Format results as a list of dictionaries.
                results.append(line)

            elif header == 'Packaged Date':
                # FIXME: Make sure just the date is added to the list.
                dates.append(line)


            if header[0] == "Tag":
                for row in table[1:]:
                    # Append row data to all_results.
                    all_results.append(dict(zip(header, row)))
                    
            elif header[0] == "Packaged Date":
                # Capture the packaged date.
                packaged_date = table[1][0]  # Assuming one row of data per table.
                # Add packaged date to previous lab results
                for result in all_results[-len(table)+1:]:
                    result['Packaged Date'] = packaged_date

    pdf.close()

    # Standardize and save the data
    save_data(all_results)


def save_data(all_results):
    # Save the results to Excel.
    data = pd.DataFrame(all_results)
    date = datetime.now().isoformat()[:10]
    data_dir = "./data"  # Define your data directory path
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    datafile = f'{data_dir}/ma-lab-results-{date}.xlsx'
    try:
        data.to_excel(datafile, index=False)
    except:
        print("Error occurred when saving the data to Excel.")


# === Test ===
# [ ] Tested:
if __name__ == "__main__":

    # Call the function
    extract_data_from_pdf("D://data/maryland/raw/public-records-request-md-2023-06-30.pdf")

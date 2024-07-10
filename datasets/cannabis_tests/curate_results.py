import os
import pandas as pd

# Path constants
ALGORITHMS_PATH = 'datasets/cannabis_tests/algorithms'
DATA_PATH = 'datasets/cannabis_tests/data'
README_PATH = r"C:\Users\keega\Documents\cannlytics\cannlytics\datasets\cannabis_tests\readme.md"

# Function to extract data sources from algorithm docstrings
def extract_data_sources(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    start = content.find('Data Sources:')
    end = content.find('"""', start)
    data_sources = []
    if start != -1 and end != -1:
        data_sources_section = content[start:end]
        lines = data_sources_section.split('\n')
        for line in lines:
            if line.strip().startswith('- '):
                data_sources.append(line.strip()[2:].strip())
    return data_sources

# Function to count observations in a CSV file
def count_observations(file_path):
    try:
        df = pd.read_csv(file_path)
        return len(df)
    except Exception as e:
        print(f'Error reading {file_path}: {e}')
        return 0

# Main function to curate results and update README.md
def curate_results():
    # Step 1: Extract data sources from algorithms
    algorithms = {}
    for root, _, files in os.walk(ALGORITHMS_PATH):
        for file in files:
            if file.endswith('.py') and file not in ['main.py', 'parse_coas_ai.py']:
                key = file.replace('get_results_', '').replace('.py', '').replace('_', '-')
                file_path = os.path.join(root, file)
                sources = extract_data_sources(file_path)
                algorithms[key] = sources

    # Step 2: Count observations in data files
    observations = {}
    for root, _, files in os.walk(DATA_PATH):
        for file in files:
            if file.endswith('-results-latest.csv'):
                key = root.split(os.sep)[-1]
                file_path = os.path.join(root, file)
                count = count_observations(file_path)
                observations[key] = count

    # Step 3: Update README.md
    dataset_rows = []
    for key in sorted(algorithms.keys()):
        state_abbr = key.split('-')[0].upper()
        dataset = f'`{key}`'
        sources = ', '.join(algorithms[key])
        count = observations.get(key.split('-')[0], '')
        row = f'| {dataset} | {state_abbr} | {sources} | {count} |'
        dataset_rows.append(row)

    new_table_content = """| Dataset | State | Sources | Observations |
|--------|------|---------|--------------|\n""" + "\n".join(dataset_rows) + "\n"

    with open(README_PATH, 'r', encoding='utf-8') as readme_file:
        readme_content = readme_file.readlines()

    # Find the index of the table start
    table_start_index = readme_content.index("<!-- Automated Table -->\n") + 1

    # Remove the old table content
    table_end_index = table_start_index
    while table_end_index < len(readme_content) and readme_content[table_end_index].startswith('|'):
        table_end_index += 1
    
    # Insert the new table content
    readme_content = readme_content[:table_start_index] + [new_table_content] + readme_content[table_end_index:]

    with open(README_PATH, 'w', encoding='utf-8') as readme_file:
        readme_file.writelines(readme_content)

    print('README.md updated successfully.')

if __name__ == "__main__":
    curate_results()

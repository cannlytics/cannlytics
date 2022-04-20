"""
Augment Data with Quantities from NLP
Copyright (c) 2021 Cannlytics

Authors: Keegan Skeate <keegan@cannlytics.com>
Created: 3/11/2022
Updated: 3/11/2022
License: MIT License <https://opensource.org/licenses/MIT>

Description: The main function, `augment_quantities`, takes a dataset and a
field with human-written text that contains quantities (weights), parses
the weights from the text with natural language processing (NLP), and returns
the data augmented with any found quantities, cleanly formatted for your use.
"""
# Standard imports.
import re

# External imports.
import spacy


MILLIGRAMS_PER_UNIT = {
    'g': 1000.0,
    'gr': 1000.0,
    'gram': 1000.0,
    'grams': 1000.0,
    'teenth': 1771.845,
    'sixteenth': 1771.845,
    'eighth': 3543.69,
    '1\/8 oz': 3543.69,
    'quarter': 7087.381,
    'ounce': 28_349.52,
    'ounces': 28_349.52,
    'oz': 28_349.52,
    'pound': 28_349.52 * 16,
    'lb': 28_349.52 * 16,
    'mg': 1.0,
    'milligram': 1.0,
    'milligrams': 1.0,
    'kg': 100_000.0,
    'kilogram': 100_000.0,
    'kilograms': 100_000.0,
}


def calculate_milligrams(row, quantity_field='parsed_quantity', units_field='parsed_uom'):
    """Calculate the milligram weight of a given observation.
    Args:
        row (Series): A Pandas series with a quantity and units field.
        quantity_field (str): The field of the series containing the quantity (float).
            (Optional) Defaults to `parsed_quantity`.
        units_field (str): The field of the series containing the units (str).
            (Optional) Defaults to `parsed_uom`.
    Returns:
        (float): Returns the milligram quantity.
    """
    return MILLIGRAMS_PER_UNIT.get(row[units_field].lower(), 0) * row[quantity_field]


def calculate_price_per_mg_thc(
        row,
        price_field='price_total',
        thc_field='cannabinoid_d9_thc_percent',
        thca_field='cannabinoid_d9_thca_percent',
        weight_field='weight',
):
    """Calculate the price per milligram of THC for a given observation.
    Args:
        row (Series): A Pandas series with price, THC, THCA, and weight fields.
        price_field (str): The field of the series containing the price (float).
            (Optional) Defaults to `price_total`.
        thc_field (str): The field of the series containing the THC concentration (float).
            (Optional) Defaults to `cannabinoid_d9_thc_percent`.
        thca_field (str): The field of the series containing the THCA concentration (float).
            (Optional) Defaults to `cannabinoid_d9_thca_percent`.
        weight_field (str): The field of the series containing the weight (float).
            (Optional) Defaults to `weight`.
    Returns:
        (float): Returns the price per milligram of THC.
    Notes:
        Source for decarboxylated value conversion factor: https://www.conflabs.com/why-0-877/
    """
    try:
        thca = row[thca_field] * 0.877
    except TypeError:
        thca = 0
    thc_mg = row[weight_field] * (row[thc_field] + thca) * 0.01
    # TODO: Apply any multiplier!
    try:
        return round(row[price_field] / thc_mg, 2)
    except ZeroDivisionError:
        return 0.00


def split_on_letter(string: str) -> list:
    """Split a string at the first letter.
    Args:
        string (str): A string to split at the first letter.
    Returns:
        (list): Returns a list of strings.
    Credit: C_Z_ https://stackoverflow.com/a/35610194
    License: CC-BY-SA-3.0 https://creativecommons.org/licenses/by-sa/3.0/
    """
    match = re.compile('[^\W\d]').search(string)
    return [string[:match.start()], string[match.start():]]


def parse_weights(nlp_client, row, field='product_name'):
    """Parse weights from an observation's name field.
    Args:
        nlp_client (NLP): A SpaCy natural language processing client.
        row (Series): A row of a Pandas DataFrame.
        field (str): The field to search for human-written weights (optional),
            `product_name` by default.
    Returns:
        (tuple): Returns a tuple of the weight and the unit of measure. Returns
            (1, ea) if an error occurs or no quantity is found.
    """
    try:
        doc = nlp_client(row[field])
        for entity in doc.ents:
            if entity.label_ == 'QUANTITY':
                parts = split_on_letter(entity.text.replace(' ', ''))
                weight = float(parts[0])
                units = parts[1]
                return (weight, units)
    except (AttributeError, ValueError):
        pass
    return (1, 'ea')


def augment_quantities_with_nlp(nlp_client, data, field='product_name'):
    """Augment data with parsed weights from a name field with NLP.
    Args:
        nlp_client (NLP): A SpaCy natural language processing client.
        data (DataFrame): The data to be augmented.
        field (str): The field to search for human-written weights (optional),
            `product_name` by default. 
    Returns:
        (DataFrame): Returns the data augmented with quantities.
    """
    data = data.assign(parsed_uom='ea', parsed_quantity=1)
    parsed_quantities = data.apply(lambda x: parse_weights(nlp_client, x, field), axis=1)
    data.loc[:, 'parsed_quantity'] = parsed_quantities.map(lambda x: x[0])
    data.loc[:, 'parsed_uom'] = parsed_quantities.map(lambda x: x[1])
    mgs = data.apply(calculate_milligrams, axis=1)
    data = data.assign(weight=mgs)
    thc_prices = data.apply(calculate_price_per_mg_thc, axis=1)
    data = data.assign(price_per_mg_thc=thc_prices)
    return data


def augment_quantities(data, field='product_name'):
    """Augment a given dataset with quantities found in a given name field.
    Args:
        data (DataFrame): The data to be augmented.
        field (str): A field name with human-written quantities (optional),
            `product_name` by default.
    Returns:
        (DataFrame): Returns the data with parsed_quantity, parsed_uom, weight,
        and price per mg of total THC where possible.
    """
    nlp = spacy.load('en_core_web_sm') # en_core_web_trf
    patterns = [
        {
            'label': 'MULTIPLIER',
            'pattern': [
                {'LIKE_NUM': True},
                {'LOWER': {'IN': [
                    '(2)', 'x', 'pk', 'pack', 'packs'
                ]}}
            ],
        },
        {
            'label': 'QUANTITY',
            'pattern': [
                {'LIKE_NUM': True},
                {'LOWER': {'IN': [
                    'g', 'gr', 'gram', 'grams', 'teenth', 'sixteenth', 'eighth',
                    'quarter', 'ounce', 'ounces', 'oz', 'pound', 'lb', 'mg', 'kg',
                    'milligram', 'milligrams', 'kilogram', 'kilograms',
                    '1\/8 oz'
                ]}}
            ],
        },
    ]
    try:
        ruler = nlp.add_pipe('entity_ruler', before='ner')
    except ValueError:
        nlp.remove_pipe('entity_ruler')
        ruler = nlp.add_pipe('entity_ruler', before='ner')
    ruler.add_patterns(patterns)
    data = augment_quantities_with_nlp(nlp, data, field)
    return data


if __name__ == '__main__':

    import pandas as pd
    import warnings
    warnings.filterwarnings('ignore')

    # Read in the data from where your data lives.
    DATA_DIR = 'D:\\leaf-data'
    DATA_FILE = f'{DATA_DIR}/samples/random-sales-items-2022-03-05.csv'
    data = pd.read_csv(DATA_FILE)

    # Augment the data with weights.
    data = augment_quantities(data)

    # Save the augmented data.
    SAVE_FILE = f'{DATA_DIR}/samples/random-sales-items-2022-03-11.csv'
    data = data.to_csv(SAVE_FILE, index=False)

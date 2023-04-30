"""
Open Cannabis AI | Prompt Engineering and Evaluation
Copyright (c) 2023 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
Created: 2/2/2023
Updated: 3/29/2023
License: <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

References:

    - OpenAI Tokenizer Tool
    URL: <https://platform.openai.com/tokenizer?view=bpe>

    - OpenAI GPT Models
    URL: <https://platform.openai.com/docs/models/gpt-3>

"""
# External imports:
from typing import Optional
from dotenv import dotenv_values
import openai

# TEST: Compare CoADoc to GPT-3.
import pdfplumber
from cannlytics.firebase import access_secret_version
from cannlytics.data.coas import CoADoc
import google.auth


TARGETS = [
    {
        'key': '`analyses`',
        'example': '[\'cannabinoids\']',
        'description': 'A list of analyses performed on a given sample.'
    },
    # {
    #     'key': '`{analysis}_method`',
    #     'example': 'HPLC',
    #     'description': 'The method used for each analysis.'
    # },
    # {
    #     'key': '`{analysis}_status`',
    #     'example': 'pass',
    #     'description': 'The pass, fail, or N/A status for pass / fail analyses.'
    # },
    # {
    #     'key': '`coa_urls`',
    #     'example': '[{url: , filename: }]',
    #     'description': 'A list of certificate of analysis (COA) URLs.'
    # },
    {
        'key': '`date_collected`',
        'example': '2022-04-20T04:20',
        'description': 'An ISO-formatted time when the sample was collected.'
    },
    {
        'key': '`date_tested`',
        'example': '2022-04-20T16:20',
        'description': 'An ISO-formatted time when the sample was tested.'
    },
    {
        'key': '`date_received`',
        'example': '2022-04-20T12:20',
        'description': 'An ISO-formatted time when the sample was received.'
    },
    {
        'key': '`distributor`',
        'example': 'Your Favorite Dispo',
        'description': 'The name of the product distributor, if applicable.'
    },
    {
        'key': '`distributor_address`',
        'example': 'Under the Bridge, SF, CA 55555',
        'description': 'The distributor address, if applicable.'
    },
    {
        'key': '`distributor_street`',
        'example': 'Under the Bridge',
        'description': 'The distributor street, if applicable.'
    },
    {
        'key': '`distributor_city`',
        'example': 'SF',
        'description': 'The distributor city, if applicable.'
    },
    {
        'key': '`distributor_state`',
        'example': 'CA',
        'description': 'The distributor state, if applicable.'
    },
    {
        'key': '`distributor_zipcode`',
        'example': '55555',
        'description': 'The distributor zip code, if applicable.'
    },
    {
        'key': '`distributor_license_number`',
        'example': 'L2Stat',
        'description': 'The distributor license number, if applicable.'
    },
    # {
    #     'key': '`images`',
    #     'example': '[{url: , filename: }]',
    #     'description': 'A list of image URLs for the sample.'
    # },
    # {
    #     'key': '`lab_results_url`',
    #     'example': 'https://cannlytics.com/results',
    #     'description': 'A URL to the sample results online.'
    # },
    {
        'key': '`producer`',
        'example': 'GrowMagnate',
        'description': 'The producer of the sampled product.'
    },
    {
        'key': '`producer_address`',
        'example': '3rd & Army, SF, CA 55555',
        'description': "The producer's address."
    },
    {
        'key': '`producer_street`',
        'example': '3rd & Army',
        'description': "The producer's street."
    },
    {
        'key': '`producer_city`',
        'example': 'SF',
        'description': "The producer's city."
    },
    {
        'key': '`producer_state`',
        'example': 'CA',
        'description': "The producer's state."
    },
    {
        'key': '`producer_zipcode`',
        'example': '55555',
        'description': "The producer's zipcode."
    },
    {
        'key': '`producer_license_number`',
        'example': 'L2Calc',
        'description': "The producer's license number."
    },
    {
        'key': '`product_name`',
        'example': 'Blue Rhino Pre-Roll',
        'description': 'The name of the product.'
    },
    {
        'key': '`lab_id`',
        'example': 'Sample-0001',
        'description': 'A lab-specific ID for the sample.'
    },
    {
        'key': '`product_type`',
        'example': 'flower',
        'description': 'The type of product.'
    },
    {
        'key': '`batch_number`',
        'example': 'Order-0001',
        'description': 'A batch number for the sample or product.'
    },
    {
        'key': '`metrc_ids`',
        'example': '[1A4060300002199000003445]',
        'description': 'A list of relevant Metrc IDs.'
    },
    {
        'key': '`metrc_lab_id`',
        'example': '1A4060300002199000003445',
        'description': 'The Metrc ID associated with the lab sample.'
    },
    {
        'key': '`metrc_source_id`',
        'example': '1A4060300002199000003445',
        'description': 'The Metrc ID associated with the sampled product.'
    },
    {
        'key': '`product_size`',
        'example': '2000',
        'description': 'The size of the product in milligrams.'
    },
    {
        'key': '`serving_size`',
        'example': '1000',
        'description': 'An estimated serving size in milligrams.'
    },
    {
        'key': '`servings_per_package`',
        'example': '2',
        'description': 'The number of servings per package.'
    },
    {
        'key': '`sample_weight`',
        'example': '1',
        'description': 'The weight of the product sample in grams.'
    },
    # {
    #     'key': '`results`',
    #     'example': '[{...},...]',
    #     'description': 'A list of results, see below for result-specific fields.'
    # },
    {
        'key': '`status`',
        'example': 'pass',
        'description': 'The overall pass / fail status for all contaminant screening analyses.'
    },
    {
        'key': '`total_cannabinoids`',
        'example': '14.20',
        'description': 'The analytical total of all cannabinoids measured.'
    },
    {
        'key': '`total_thc`',
        'example': '14.00',
        'description': 'The analytical total of THC and THCA.'
    },
    {
        'key': '`total_cbd`',
        'example': '0.20',
        'description': 'The analytical total of CBD and CBDA.'
    },
    {
        'key': '`total_terpenes`',
        'example': '0.42',
        'description': 'The sum of all terpenes measured.'
    },
    {
        'key': '`strain_name`',
        'example': 'Blue Rhino',
        'description': 'A strain name, if specified. Otherwise, can be attempted to be parsed from the `product_name`.'
    }
]


def initialize_openai(env_file='./.env'):
    """Initialize the OpenAI API, trying to get credentials from
    Google Secret Manager and then from an `env_file`.
    API key URL: <https://platform.openai.com/account/api-keys>
    """
    try:
        _, project_id = google.auth.default()
        openai_api_key = access_secret_version(
            project_id=project_id,
            secret_id='OPENAI_API_KEY',
            version_id='latest',
        )
        openai.api_key = openai_api_key
    except:
        config = dotenv_values(env_file)
        openai.api_key = config['OPENAI_API_KEY']


def openai_text_search(
        text: str,
        key: str,
        description: str,
        example: Optional[str] = None,
        temperature: Optional[float] = 0.0,
        max_tokens: Optional[int] = 4200,
        iterations: Optional[int] = 1,
    ):
    """Ask the OpenAI API to find a given key in text with a description
    and an optional example."""
    # Format the prompt.
    if example:
        prompt = f"""Find {key} ({description}) (e.g. {example}) in: {text}"""
    else:
        prompt = f"""Find {key} ({description}) in: {text}"""

    # Query the API.
    response = openai.Completion.create(
        model='text-davinci-003',
        prompt=prompt,
        max_tokens=max_tokens,
        temperature=temperature,
        n=iterations,
    )

    # Return the text.
    # try:
    return response['choices'][0]['text']
    # except:
    #     return ''


# Get the example text file.
example_file = 'test_coa.pdf'

# Read text from PDF.
text = pdfplumber.open(example_file).pages[1].extract_text()

# FIXME: Get data with CoA Doc to measure accuracy.
parser = CoADoc()
data = parser.parse(example_file)

# TODO: Try to get all metadata from the first page.
prediction = {}
for target in TARGETS:
    key = target['key']
    description = target['description']
    example = target['example']
    value = openai_text_search(
        text=text,
        key=key,
        description=description,
        example=example,
        temperature=0.0,
        max_tokens=4200,
        iterations=1,
    )
    print(f'{key}: {value}')
    prediction[key] = value

# TODO: Custom prompts to get results iterating over each page.

# TODO: Get the images with PDF plumber.
# {
#     'key': '`images`',
#     'example': '[{url: , filename: }]',
#     'description': 'A list of image URLs for the sample.'
# }

# TODO: After data is extracted, generate:
# - sample_id
# - results_hash
# - sample_hash

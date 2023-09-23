"""
COA AI | CoADoc
Copyright (c) 2021-2023 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
    Candace O'Sullivan-Sutherland <https://github.com/candy-o>
Created: 6/12/2023
Updated: 9/16/2023
License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description:

    Parse COAs with the aid of OpenAI's API.

"""
# Standard imports:
from datetime import datetime
import os
import json
import tempfile
from time import sleep
from typing import Any, Optional

# External imports:
from dotenv import dotenv_values
import openai
import pandas as pd
import pdfplumber
import requests

# Internal imports:
from cannlytics import __version__
from cannlytics.ai import (
    AI_WARNING,
    INSTRUCTIONAL_PROMPT,
    initialize_openai,
    get_messages_price,
    split_into_token_chunks,
)
from cannlytics.data import create_hash, create_sample_id
from cannlytics.utils import snake_case
from cannlytics.utils.constants import DEFAULT_HEADERS


#-----------------------------------------------------------------------
# First, try to get the metadata from the front page.
#-----------------------------------------------------------------------

# Prompt to parse metadata from the first page.
COA_PROMPT = """Given text, extract JSON, where:

| Field | Example | Description |
|-------|---------|-------------|
| `analyses` | ["cannabinoids"] | A list of analyses performed on a given sample. |
| `{analysis}_status` | "pass" | The pass, fail, or N/A status for pass / fail analyses.   |
| `methods` | [{"analysis: "cannabinoids", "method": "HPLC"}] | The methods used for each analysis. |
| `date_collected` | 2022-04-20T04:20 | An ISO-formatted time when the sample was collected. |
| `date_tested` | 2022-04-20T16:20 | An ISO-formatted time when the sample was tested. |
| `date_received` | 2022-04-20T12:20 | An ISO-formatted time when the sample was received. |
| `lab` | "MCR Labs" | The lab that tested the sample. |
| `lab_address` | "85 Speen St, Framingham, MA 01701" | The lab's address. |
| `lab_street` | "85 Speen St" | The lab's street. |
| `lab_city` | "Framingham" | The lab's city. |
| `lab_state` | "MA" | The lab's state. |
| `lab_zipcode` | "01701" | The lab's zipcode. |
| `distributor` | "Fred's Dispensary" | The name of the product distributor, if applicable. |
| `distributor_address` | "420 State Ave, Olympia, WA 98506" | The distributor address, if applicable. |
| `distributor_street` | "420 State Ave" | The distributor street, if applicable. |
| `distributor_city` | "Olympia" | The distributor city, if applicable. |
| `distributor_state` | "WA" | The distributor state, if applicable. |
| `distributor_zipcode` | "98506" | The distributor zip code, if applicable. |
| `distributor_license_number` | "L-123" | The distributor license number, if applicable. |
| `producer` | "Grow House" | The producer of the sampled product. |
| `producer_address` | "3rd & Army, San Francisco, CA 55555" | The producer's address. |
| `producer_street` | "3rd & Army" | The producer's street. |
| `producer_city` | "San Francisco" | The producer's city. |
| `producer_state` | "CA" | The producer's state. |
| `producer_zipcode` | "55555" | The producer's zipcode. |
| `producer_license_number` | "L2Calc" | The producer's license number. |
| `product_name` | "Blue Rhino Pre-Roll" | The name of the product. |
| `lab_id` | "Sample-0001" | A lab-specific ID for the sample. |
| `product_type` | "flower" | The type of product. |
| `batch_number` | "Order-0001" | A batch number for the sample or product. |
| `traceability_ids` | ["1A4060300002199000003445"] | A list of relevant traceability IDs. |
| `product_size` | 2000 | The size of the product in milligrams. |
| `serving_size` | 1000 | An estimated serving size in milligrams. |
| `servings_per_package` | 2 | The number of servings per package. |
| `sample_weight` | 1 | The weight of the product sample in grams. |
| `status` | "pass" | The overall pass / fail status for all contaminant screening analyses. |
| `total_cannabinoids` | 14.20 | The analytical total of all cannabinoids measured. |
| `total_thc` | 14.00 | The analytical total of THC and THCA. |
| `total_cbd` | 0.20 | The analytical total of CBD and CBDA. |
| `total_terpenes` | 0.42 | The sum of all terpenes measured. |
| `sample_id` | "{sha256-hash}" | A generated ID to uniquely identify the `producer`, `product_name`, and `date_tested`. |
| `strain_name` | "Blue Rhino" | A strain name, if specified. Otherwise, can be attempted to be parsed from the `product_name`. |
"""

# Prompt used to parse results from all pages.
RESULTS_PROMPT = """Given text, extract JSON. Extract only `results` as a list of JSON objects, e.g.:

{
    "results": [
        {
            "analysis": str,
            "key": str,
            "name": str,
            "value": float,
            "mg_g": float,
            "units": str,
            "limit": float,
            "lod": float,
            "loq": float,
            "status": str
        }
    ]
}

Where:

| Field | Example| Description |
|-------|--------|-------------|
| `analysis` | "pesticides" | The analysis used to obtain the result. |
| `key` | "pyrethrins" | A standardized key for the result analyte. |
| `name` | "Pyrethrins" | The lab's internal name for the result analyte |
| `value` | 0.42 | The value of the result. |
| `mg_g` | 0.00000042 | The value of the result in milligrams per gram. |
| `units` | "ug/g" | The units for the result `value`, `limit`, `lod`, and `loq`. |
| `limit` | 0.5 | A pass / fail threshold for contaminant screening analyses. |
| `lod` | 0.01 | The limit of detection for the result analyte. Values below the `lod` are typically reported as `ND`. |
| `loq` | 0.1 | The limit of quantification for the result analyte. Values above the `lod` but below the `loq` are typically reported as `<LOQ`. |
| `status` | "pass" | The pass / fail status for contaminant screening analyses. |
"""


def parse_coa_with_ai(
        parser: Any,
        doc: str,
        temp_path: Optional[str] = None,
        session: Optional[Any] = None,
        headers: Optional[dict] = DEFAULT_HEADERS,
        use_cached: Optional[bool] = False,
        openai_api_key: Optional[str] = None,
        model: Optional[str] = 'gpt-4-0314',
        max_tokens: Optional[int] = 4_000,
        temperature: Optional[float] = 0.0,
        initial_cost: Optional[float] = 0.0,
        instructional_prompt: Optional[str] = None,
        results_prompt: Optional[str] = None,
        coa_prompt: Optional[str] = None,
        max_prompt_length: Optional[int] = 1_000,
        verbose: Optional[bool] = False,
        user: Optional[str] = None,
        retry_pause: Optional[float] = 3.33,
    ) -> dict:
    """Parse a COA with OpenAI's GPT model and return the data as JSON."""

    # === DEV ===
    # from cannlytics.data.coas.coas import CoADoc
    # parser = CoADoc()
    # model = 'gpt-4'
    # max_tokens = 4_000
    # temperature = 0.0
    # initial_cost = 0.0
    # use_cached = True
    # instructional_prompt = INSTRUCTIONAL_PROMPT
    # coa_prompt = COA_PROMPT
    # results_prompt = RESULTS_PROMPT
    # max_prompt_length = 1_000
    # verbose = True
    # user = 'cannlytics'
    # doc = '../../../tests/assets/coas/gtl/Pineapple-XX-5-13-2129146.pdf'

    # Initialize prompts.
    if instructional_prompt is None:
        instructional_prompt = INSTRUCTIONAL_PROMPT
    if coa_prompt is None:
        coa_prompt = COA_PROMPT
    if results_prompt is None:
        results_prompt = RESULTS_PROMPT

    # Parse an observation.
    obs = {}

    # Track costs and prompts.
    cost = initial_cost
    prompts = []

    # If the `doc` is a URL, then download the PDF to the `temp_path`.
    # Then use the path of the downloaded PDF as the doc.
    coa_url = None
    if isinstance(doc, str):
        if doc.startswith('https'):
            # FIXME: This raises an error with Firebase Storage URLs.
            coa_url = doc
            if temp_path is None: temp_path = tempfile.gettempdir()
            if not os.path.exists(temp_path): os.makedirs(temp_path)
            try:
                filename = doc.split('/')[-1].split('?')[0] + '.pdf'
            except:
                filename = 'coa.pdf'
            coa_pdf = os.path.join(temp_path, filename)
            if session is not None:
                response = session.get(doc)
            else:
                response = requests.get(doc, headers=headers)
            with open(coa_pdf, 'wb') as pdf:
                pdf.write(response.content)
            report = parser.open_pdf_with_ocr(coa_pdf)
            obs['coa_pdf'] = filename
        else:
            report = parser.open_pdf_with_ocr(doc)
            obs['coa_pdf'] = doc.replace('\\', '/').split('/')[-1]
    else:
        report = doc
        obs['coa_pdf'] = report.stream.name.replace('\\', '/').split('/')[-1]

    # Get the text of the PDF.
    front_page_text = report.pages[0].extract_text()
    all_text = '\n\n'.join([page.extract_text() for page in report.pages])

    # Record the COA URL.
    if coa_url is None:
        coa_url = parser.find_pdf_qr_code_url(report)
    if coa_url is not None:
        filename = coa_url.split('/')[-1].split('?')[0] + '.pdf'
        obs['coa_urls'] = json.dumps([{'url': coa_url, 'filename': filename}])
        obs['lab_results_url'] = coa_url
    else:
        obs['coa_urls'] = None
        obs['lab_results_url'] = None

    # TODO: Get images from the PDF.
    images = []

    # Close the report.
    report.close()

    # See if the PDF or URL has already been parsed.
    # by checking if the hash exists in the database.
    coa_hash = create_hash(all_text, private_key='')
    obs['coa_hash'] = coa_hash
    # if use_cached:
    #     try:
    #         database = initialize_firebase()
    #         results = get_collection(
    #             'public/data/lab_results',
    #             filters=[{'key': 'coa_hash', 'operation': '==', 'value': coa_hash}],
    #             limit=1,
    #             database=database,
    #         )
    #         if results:
    #             return results[0], [], 0
    #     except:
    #         pass

    # Format the prompt.
    metadata_prompt = 'Text: ' + front_page_text + '\n\nJSON:'
    try:
        messages = [
            {'role': 'system', 'content': coa_prompt},
            {'role': 'system', 'content': instructional_prompt},
            {'role': 'user', 'content': metadata_prompt},
        ]
        cost += get_messages_price(messages, model=model)
        if verbose:
            print('MESSAGES:', messages)
        try:
            initialize_openai(openai_api_key)
            metadata_response = openai.ChatCompletion.create(
                model=model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                user=user,
            )
        except:
            if retry_pause:
                sleep(retry_pause)
                initialize_openai(openai_api_key)
                metadata_response = openai.ChatCompletion.create(
                    model=model,
                    messages=messages,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    user=user,
                )
        
        # Print the response.
        if verbose:
            print('RESPONSE:', json.dumps(metadata_response.to_dict()))
        
        # Record the prompt.
        prompts.append({
            'messages': messages,
            'completion': json.dumps(metadata_response.to_dict()),
        })

        # Record the content.
        content = metadata_response['choices'][0]['message']['content']
        if verbose:
            print('CONTENT:', json.dumps(content))
    except:
        if verbose:
            print('Parse metadata OpenAI query failed.')
    
    # Get the structured the data.
    try:
        start_index = content.find('{')
        end_index = content.rfind('}') + 1
        metadata = json.loads(content[start_index:end_index])
        obs = {**obs, **metadata}
    except:
        if verbose:
            print('Metadata JSON parsing failed.')

    #-----------------------------------------------------------------------
    # Second, try to get results from each page.
    #-----------------------------------------------------------------------

    # Extract the results
    results = []

    # Split the long string into smaller strings.
    # Optional: Try to compress the data.
    # substrings = split_string(all_text, max_prompt_length - round(0.1 * max_prompt_length))
    substrings = split_into_token_chunks(all_text, max_prompt_length)

    # Format the message.
    for substring in substrings:
        messages = [
            {'role': 'system', 'content': results_prompt},
            {'role': 'system', 'content': instructional_prompt},
        ]
        content = 'Text: ' + substring #  + '\n\nList of results as JSON:'
        messages.append({'role': 'user', 'content': content})

        # TODO: Try compression.
        # json_data = json.dumps(obs)
        # compressed_data = zlib.compress(json_data.encode())

        # Extend results.
        # FIXME: The logic is overly complicated.
        try:
            if verbose:
                print('MESSAGES:', messages)
            cost += get_messages_price(messages, model=model)
            initialize_openai(openai_api_key)
            try:
                initialize_openai(openai_api_key)
                results_response = openai.ChatCompletion.create(
                    model=model,
                    messages=messages,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    user=user,
                )
            except:
                if retry_pause:
                    sleep(retry_pause)
                    initialize_openai(openai_api_key)
                    results_response = openai.ChatCompletion.create(
                        model=model,
                        messages=messages,
                        max_tokens=max_tokens,
                        temperature=temperature,
                        user=user,
                    )
            if verbose:
                print('RESPONSE:', json.dumps(results_response.to_dict()))

            prompts.append({
                'messages': messages,
                'completion': json.dumps(results_response.to_dict()),
            })

            # Extend results from each prompt.
            for choice in results_response['choices']:
                content = choice['message']['content']
                if verbose:
                    print('CONTENT:', json.dumps(content))

                # Handle results that are a list.
                if content.startswith('['):
                    start_index = content.find('[')
                    end_index = content.rfind(']') + 1
                    partial_results = json.loads(content[start_index:end_index])

                # Handle results that are JSON.
                else:
                    try:
                        start_index = content.find('{')
                        end_index = content.rfind('}') + 1
                        partial_results = json.loads(content[start_index:end_index])
                        partial_results = partial_results.get('results', [])

                    # Otherwise, try to handle as a list.
                    except:
                        start_index = content.find('[')
                        end_index = content.rfind(']') + 1
                        partial_results = json.loads(content[start_index:end_index])
                
                # Extend the results.
                try:
                    results.extend(partial_results)
                    print('EXTENDED RESULTS:', partial_results)
                except:
                    if verbose:
                        print('Failed to extend results.')
        except:
            if verbose:
                print('Parse results OpenAI query failed.')

    #-----------------------------------------------------------------------
    # Finally, combine and standardize the data,
    # warning users that the data was generated by AI.
    # Optional: If parsing does not work well, break up parsing requests.
    #-----------------------------------------------------------------------

    # Standardize analyses and methods.
    # TODO: Standardize analyses names.
    try:
        obs['analyses'] = json.dumps(list(set(obs['analyses'])))
    except:
        pass
    try:
        obs['methods'] = json.dumps(list(set(obs['methods'])))
    except:
        pass

    # TODO: Lookup additional details.
    # - lab_phone
    # - lab_email
    # - lab_image_url
    # - lab_county
    # - lab_latitude
    # - lab_longitude

    # FIXME: Apply snake case to columns.

    # Standardize results.
    for i, result in enumerate(results):
        key = snake_case(result.get('name', 'Unknown'))
        results[i]['key'] = parser.analytes.get(key, key)

    # Standardize dates.
    date_columns = [x for x in obs.keys() if x.startswith('date')]
    for date_column in date_columns:
        try:
            obs[date_column] = pd.to_datetime(obs[date_column]).isoformat()
        except:
            pass

    # Standardize the data.
    obs['coa_algorithm'] = 'coa_ai.py'
    obs['coa_algorithm_entry_point'] = 'parse_coa_with_ai'
    obs['coa_algorithm_version'] = __version__
    obs['coa_parsed_at'] = datetime.now().isoformat()
    obs['images'] = json.dumps(images)
    obs['results'] = json.dumps(results)
    obs['results_hash'] = create_hash(obs['results'])
    obs['sample_id'] = create_sample_id(
        private_key=json.dumps(results),
        public_key=obs.get('product_name', 'Unknown'),
        salt=obs.get('producer', obs.get('date_tested', 'cannlytics.eth')),
    )
    obs['sample_hash'] = create_hash(obs)
    obs['warning'] = AI_WARNING

    # Return the data.
    return obs, prompts, cost


# === Tests ===
# [✓] Tested: 2023-09-05 by Keegan Skeate <admin@cannlytics.com>
if __name__ == '__main__':

    # Initialize CoADoc
    from cannlytics.data.coas.coas import CoADoc

    # Initialize OpenAI.
    config = dotenv_values('../../../.env')
    openai_api_key = config['OPENAI_API_KEY']
    
    # [✓] TEST: Parse a COA with AI.
    # Note: Does not work with `gpt-4-0613`.
    doc = '../../../tests/assets/coas/gtl/Pineapple-XX-5-13-2129146.pdf'
    parser = CoADoc()
    data, prompts, cost = parse_coa_with_ai(
        parser,
        doc,
        openai_api_key=openai_api_key,
        verbose=True,
    )
    assert data is not None
    print(data)

    # Save the data.
    data['cost'] = cost
    timestamp = datetime.now().isoformat().replace(':', '-')
    outfile = f'../../../tests/assets/coas/gtl/pineapple-xx-{timestamp}.json'
    with open(outfile, 'w') as f:
        json.dump(data, f, indent=4)

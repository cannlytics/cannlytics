"""
COA AI | CoADoc
Copyright (c) 2021-2022 Cannlytics

Authors: Keegan Skeate <https://github.com/keeganskeate>
Created: 6/12/2023
Updated: 6/12/2023
License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description: Parse COAs with AI.
"""
import json
from dotenv import dotenv_values

import openai
import pdfplumber
import tiktoken
from typing import Optional
import zlib


#-----------------------------------------------------------------------
# Setup OpenAI for data modelling.
#-----------------------------------------------------------------------

# OpenAI API model prices (as of 2023-06-06) per 1000 tokens.
PRICE_PER_1000_TOKENS = {
    'gpt-4': {'prompt': 0.03, 'completion': 0.06},
    'gpt-3.5-turbo': {'prompt': 0.002, 'completion': 0.002},
    'ada': {'prompt': 0.0004, 'completion': 0.0004, 'training': 0.0004, 'usage': 0.0016},
    'babbage': {'prompt': 0.0005, 'completion': 0.0005, 'training': 0.0006, 'usage': 0.0024},
    'curie': {'prompt': 0.002, 'completion': 0.002, 'training': 0.003, 'usage': 0.012},
    'davinci': {'prompt': 0.02, 'completion': 0.02, 'training': 0.03, 'usage': 0.12},
    'dalle_1024': {'usage': 0.02},
    'dalle_512': {'usage': 0.018},
    'dalle_256': {'usage': 0.016},
    'whisper': {'usage': 0.006},
}


def num_tokens_from_messages(messages: list, model: Optional[str] = 'gpt-4'):
    """Returns the number of tokens used by a list of messages.
    Credit: OpenAI
    License: MIT <https://github.com/openai/openai-cookbook/blob/main/LICENSE>
    """
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        encoding = tiktoken.get_encoding("cl100k_base")
    if model == "gpt-3.5-turbo":
        return num_tokens_from_messages(messages, model="gpt-3.5-turbo-0301")
    elif model == "gpt-4":
        return num_tokens_from_messages(messages, model="gpt-4-0314")
    elif model == "gpt-3.5-turbo-0301":
        tokens_per_message = 4  # every message follows <|start|>{role/name}\n{content}<|end|>\n
        tokens_per_name = -1  # if there's a name, the role is omitted
    elif model == "gpt-4-0314":
        tokens_per_message = 3
        tokens_per_name = 1
    else:
        raise NotImplementedError(f"""num_tokens_from_messages() is not implemented for model {model}. See https://github.com/openai/openai-python/blob/main/chatml.md for information on how messages are converted to tokens.""")
    num_tokens = 0
    for message in messages:
        num_tokens += tokens_per_message
        for key, value in message.items():
            num_tokens += len(encoding.encode(value))
            if key == "name":
                num_tokens += tokens_per_name
    num_tokens += 3  # every reply is primed with <|start|>assistant<|message|>
    return num_tokens


def num_tokens_from_string(string: str, model: Optional[str] = 'gpt-4') -> int:
    """Returns the number of tokens in a text string."""
    return num_tokens_from_messages([{'role': 'user', 'content': string},], model=model)


def get_prompt_price(prompt, model='gpt-4', prices=PRICE_PER_1000_TOKENS):
    """Returns the price to generate a prompt."""
    num_tokens = num_tokens_from_string(prompt, model)
    return num_tokens / 1_000 * prices[model]['prompt']


def get_message_price(messages, model='gpt-4', prices=PRICE_PER_1000_TOKENS):
    """Returns the price to generate a prompt."""
    num_tokens = num_tokens_from_messages(messages, model)
    return num_tokens / 1_000 * prices[model]['prompt']


def split_string(string, max_length):
    return [string[i:i+max_length] for i in range(0, len(string), max_length)]


#-----------------------------------------------------------------------
# First, try to get the metadata from the front page.
#-----------------------------------------------------------------------


# Define the engineered prompts.
COA_PROMPT = """Extract as many of these data points to JSON:
{
    "product_name": str,
    "product_type": str,
    "producer": str,
    "total_thc_percent": float,
    "total_cbd_percent": float,
    "beta_pinene_percent": float,
    "d_limonene_percent": float,
}
From the following text:
"""
SYSTEM_PROMPT = 'Return only JSON and always return at least an empty object if no data can be found.'


def parse_coa_with_ai(
        doc: str,
        openai_api_key: Optional[str] = None,
        model: Optional[str] = 'gpt-4',
        max_tokens: Optional[int] = 4_000,
        temperature: Optional[float] = 0.0,
        initial_cost: Optional[float] = 0.0,
    ) -> dict:
    """Parse a COA with OpenAI's GPT model and return the data as JSON."""

    # Track costs.
    cost = initial_cost

    # Initialize OpenAI.
    if openai_api_key is None:
        openai_api_key = os.environ['OPENAI_API_KEY']

    # Get the text of the PDF.
    pdf = pdfplumber.open(doc)
    front_page_text = pdf.pages[0].extract_text()
    
    # Format the prompt.
    prompt = COA_PROMPT
    prompt += front_page_text
    try:
        messages = [
            {'role': 'system', 'content': SYSTEM_PROMPT},
            {'role': 'user', 'content': prompt},
        ]
        cost += get_message_price(messages, model=model)
        response = openai.ChatCompletion.create(
            model=model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
        )
        content = response['choices'][0]['message']['content'] 
        print('CONTENT:', content)
    except:
        print('AI query failed.')
        return {}
    
    # Get the structured the data.
    try:
        start_index = content.find('{')
        end_index = content.rfind('}') + 1
        coa_data = json.loads(content[start_index:end_index])
    except:
        print('JSON parsing failed.')
        coa_data = {}

    #-----------------------------------------------------------------------
    # Second, try to get results from each page.
    #-----------------------------------------------------------------------

    # Example usage.
    MAX_PROMPT_LENGTH = 3500

    # Split the long string into smaller strings.
    substrings = split_string(compressed_data, MAX_PROMPT_LENGTH - 100)

    # Format the message.
    messages = [
        {'role': 'system', 'content': 'You are a data scientist writing a description for a laboratory sample of a cannabis product.'},
    ]
    for substring in substrings:
        content = """Part of data in bytes, wait to reply:"""
        content += str(substring)
        messages.append({'role': 'user', 'content': content})

        # TODO: Try compression.
        # Convert the list to a JSON string.
        json_data = json.dumps(obs)

        # Compress the JSON string using zlib compression.
        compressed_data = zlib.compress(json_data.encode())

        # Print the length of the compressed data.
        print("Compressed data length:", len(compressed_data))

    try:
        cost += get_message_price(messages, model=model)
        response = openai.ChatCompletion.create(
            model=model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
        )
        content = response['choices'][0]['message']['content'] 
        print('CONTENT:', content)
    except:
        print('AI query failed.')
        return {}

    # Get the structured the data.
    try:
        start_index = content.find('{')
        end_index = content.rfind('}') + 1
        coa_data = json.loads(content[start_index:end_index])
    except:
        print('JSON parsing failed.')
        coa_data = {}



    # EXAMPLE:
    # cost = 0
    # system_prompt = """Please listen while I tell you about of the cannabis plant patents.
    # Only respond with "OK" after I tell you about a patent. Once I say "FINISHED",
    # then respond with "READY" and I will ask you about the patents."""
    # messages = [{'role': 'system', 'content': system_prompt}]
    # cost += get_prompt_price(system_prompt, model=model)

    # # Keep track of generated responses.
    # generated_data = []

    # # Specify the patent details to use in the prompt.
    # details = ['strain_name', 'patent_number', 'patent_title', 
    #         'inventor_name', 'date_published', 'abstract']

    # # Isolate a sample of patents.
    # sample = patents[:5]

    # # Populate memory.
    # for patent_number, obs in sample.iterrows():

    #     # Format prompt.
    #     prompt = """Cannabis plant patent details: """
    #     # TODO: Try the same prompt with compressed data.
    #     prompt += obs[details].to_json()
    #     # prompt += zlib.compress(obs[details].to_json().encode())

    #     # Add the prompt.
    #     messages.append({'role': 'user', 'content': prompt})

    #     # Estimate the cost of training.
    #     cost += get_prompt_price(prompt, model=model)

    # # Add the question.
    # messages.append({'role': 'user', 'content': 'READY'})
    # question = """Do any of the cannabis plant patents mention aroma?"""
    # messages.append({'role': 'user', 'content': question})
    # cost += get_prompt_price(question + 'READY', model=model)
    # print('Expected cost of training ≈ $%f' % cost)

    # # Submit all prompts at the same time.
    # response = openai.ChatCompletion.create(
    #     model=model,
    #     temperature=temperature,
    #     max_tokens=max_tokens,
    #     messages=messages
    # )
    # content = response['choices'][0]['message']['content']  
    # print(content)
    # generated_data.append({'prompt': prompt, 'response': content})

    # # Save the responses.
    # date = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
    # responses = pd.DataFrame(generated_data)
    # try:
    #     responses.to_excel(f'.datasets/ai/prompts/ai-prompts-responses-{date}.xlsx')
    # except:
    #     print('Failed to save responses.')



    #-----------------------------------------------------------------------
    # Finally, combine and standardize the data,
    # warning users that the data was generated by AI.
    #-----------------------------------------------------------------------
    warning = "This data was extracted by AI. Please verify it before using it. You can submit feedback to dev@cannlytics.com"


    # Return the data.
    return coa_data


# === Tests ===
if __name__ == '__main__':

    # Initialize OpenAI.
    config = dotenv_values('../../.env')
    openai.api_key = config['OPENAI_API_KEY']



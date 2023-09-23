# Strains Data

The `cannlytics.data.strains.strains_ai` module provides functionalities for generating and analyzing information related to cannabis strains. The functionalities include generating strain art images, generating strain descriptions, identifying strains, and training models to identify strain names.

## Strains AI Functionality

### `generate_strain_art`

Generates an art image URL based on the provided strain name.

Parameters:

- `name`: Name of the strain.
- `openai_api_key` (Optional): OpenAI API key.
- `art_style` (Default: ' in the style of pixel art'): Desired art style.
- `n` (Default: 1): Number of image prompts.
- `size` (Default: '1024x1024'): Image size.
- `user` (Optional, Default: 'cannlytics'): OpenAI user.

Returns: Image URL string.

### `generate_strain_description`

Generates a description for a given strain or product.

Parameters:

- `name` (str): Name of the strain or product.
- `stats` (dict, Optional): Lab results or other statistical data. Defaults to None.
- `instructions` (str, Optional): Additional instructions for the prompt. Defaults to None.
- `model` (str, Optional): OpenAI model. Defaults to 'gpt-4'.
- `openai_api_key` (str, Optional): API key to authenticate with OpenAI. Defaults to None.
- `max_tokens` (int, Optional): Maximum number of tokens for the generated description. Defaults to 1,000.
- `temperature` (float, Optional): Sampling temperature for the generated description. Defaults to 0.42.
- `word_count` (int, Optional): Desired word count for the description. Defaults to 50.
- `user` (str, Optional): User identifier for the OpenAI request. Defaults to 'cannlytics'.
- `retry_pause` (float, Optional): Time to wait in seconds before retrying the OpenAI request if the initial request fails. Defaults to 3.33.
- `verbose` (bool, Optional): Indicates if verbose printing should be enabled. If True, it will print messages and the OpenAI response. Defaults to False.

Returns: Description string.

### `identify_strains`

Identifies the closest cannabis strain(s) based on the given name or text.

Parameters:

- `text` (str): Name or text of the product.
- `model` (str, Optional): OpenAI model. Defaults to 'gpt-4'.
- `openai_api_key` (str, Optional): API key to authenticate with OpenAI. Defaults to None.
- `max_tokens` (int, Optional): Maximum number of tokens for the generated description. Defaults to 1,000.
- `temperature` (float, Optional): Sampling temperature for the generated description. Defaults to 0.0.
- `user` (str, Optional): User identifier for the OpenAI request. Defaults to 'cannlytics'.
- `verbose` (bool, Optional): Indicates if verbose printing should be enabled. If True, it will print messages and the OpenAI response. Defaults to False.
- `retry_pause` (float, Optional): Time to wait in seconds before retrying the OpenAI request if the initial request fails. Defaults to 3.33.
- `instructional_prompt` (str, Optional): Optional custom instructional prompt to use. If not provided, the default instructional prompt will be used. Defaults to None.
- `identification_prompt` (str, Optional): Optional custom identification prompt to use. If not provided, a default prompt will be used. Defaults to None.
- `json_key` (str, Optional): The key in the returned JSON to extract the strain data from. Defaults to 'strains'.

Returns: List of identified strain names.


## Examples

```python
from dotenv import dotenv_values

# Initialize OpenAI.
config = dotenv_values('.env')
openai_api_key = config['OPENAI_API_KEY']

# Identify strain names.
text = 'GARCIA HAND PICKED DARK KARMA'
strain_names = identify_strains(text)
print(strain_names)

# Generate strain art.
image_url = generate_strain_art(
    text,
    openai_api_key=openai_api_key,
)
print(image_url)

# Generate strain description.
short_description = generate_strain_description(
    text,
    model='gpt-3.5-turbo',
    temperature=0.5,
    word_count=420,
    verbose=True,
)
```

!!! info "Note: Ensure you have access to the OpenAI API and provide the API key where required."

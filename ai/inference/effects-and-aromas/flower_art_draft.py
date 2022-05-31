"""
Flower Art AI
Copyright (c) 2022 Cannlytics

Authors: Keegan Skeate <https://github.com/keeganskeate>
Created: 5/29/2022
Updated: 5/30/2022
License: MIT License <https://opensource.org/licenses/MIT>

Description:

    Programmatically create flower art given effects and aromas.
    E.g. skunk -> green heat wave coming off of flower

Resources:

    - https://github.com/benyaminahmed/nft-image-generator/blob/main/generate.ipynb

"""
import json
from time import sleep
from bs4 import BeautifulSoup
import requests
import urllib.parse


AROMAS = [
    'aroma_citrus',
    'aroma_earthy',
    'aroma_grape',
    'aroma_ammonia',
    'aroma_pine',
    'aroma_pungent',
    'aroma_diesel',
    'aroma_orange',
    'aroma_sweet',
    'aroma_spicytoherbal',
    'aroma_tea',
    'aroma_grapefruit',
    'aroma_woody',
    'aroma_apple',
    'aroma_pear',
    'aroma_vanilla',
    'aroma_lemon',
    'aroma_mint',
    'aroma_sage',
    'aroma_cheese',
    'aroma_flowery',
    'aroma_menthol',
    'aroma_tropical',
    'aroma_coffee',
    'aroma_berry',
    'aroma_blueberry',
    'aroma_pineapple',
    'aroma_chemical',
    'aroma_pepper',
    'aroma_skunk',
    'aroma_tree',
    'aroma_fruit',
    'aroma_lime',
    'aroma_butter',
    'aroma_nutty',
    'aroma_lavender',
    'aroma_honey',
    'aroma_mango',
    'aroma_tobacco',
    'aroma_rose',
    'aroma_peach',
    'aroma_chestnut',
    'aroma_tar',
    'aroma_plum',
    'aroma_violet',
    'aroma_strawberry',
    'aroma_apricot',
    'aroma_blue_cheese',
]

EFFECTS = [
    'effect_happy',
    'effect_relaxed',
    'effect_talkative',
    'effect_uplifted',
    'effect_creative',
    'effect_euphoric',
    'effect_focused',
    'effect_tingly',
    'effect_hungry',
    'effect_sleepy',
    'effect_dry_mouth',
    'effect_energetic',
    'effect_giggly',
    'effect_dizzy',
    'effect_dry_eyes',
    'effect_aroused',
    'effect_paranoid',
    'effect_headache',
    'effect_depression',
    'effect_anxiety',
    'effect_migraines',
    'effect_anxious',
    'effect_eye_pressure',
    'effect_fatigue',
    'effect_pain',
    'effect_seizures',
    'effect_arthritis',
    'effect_epilepsy',
    'effect_stress',
    'effect_spasticity',
]


def get_color_association(string):
    """Get a color associated with a given word or phrase.
    The algorithm uses Colorize, a tool that uses a search engine to
    find image results for a word or phrase, and then calculates the
    average color across approximately 25 image results.
    Credit: Alex Beals
    URL: https://alexbeals.com/projects/colorize/
    """
    base = 'https://alexbeals.com/projects/colorize/search.php?q='
    url = base + urllib.parse.quote_plus(string)
    response = requests.get(url)
    soup = BeautifulSoup(response.content, features='html.parser')
    a = soup.find_all('span', {'class': 'hex'})
    return a[0].text

# Format aroma data.
aroma_data = []
for key in AROMAS:
    outcome = key.replace('aroma_', '')
    outcome = outcome.replace('_', ' ')
    outcome = outcome.title()
    color = get_color_association(outcome)
    aroma_data.append({
        'key': key,
        'name': outcome,
        'icon': '',
        'icon_url': '',
        'color': color,
    })
    sleep(0.2)

# Format effect data.
effect_data = []
for key in EFFECTS:
    outcome = key.replace('effect_', '')
    outcome = outcome.replace('_', ' ')
    outcome = outcome.title()
    color = get_color_association(outcome)
    effect_data.append({
        'key': key,
        'name': outcome,
        'icon': '',
        'icon_url': '',
        'color': color,
    })
    sleep(0.2)

# Save the aroma data.
data_dir = '../../../.datasets/website/'
with open(data_dir + 'aromas.json', 'w+') as datafile:
    json.dump(aroma_data, datafile, indent=4, sort_keys=True)

# Save the effects data.
effect_data = [dict(item, **{'positive': True}) for item in effect_data]
with open(data_dir + 'effects.json', 'w+') as datafile:
    json.dump(effect_data, datafile, indent=4, sort_keys=True)



# Future work: Create image from the effects and aromas of a particular strain.

# from PIL import Image

# img = Image.new('RGB', (width, height))
# img.putdata(my_list)
# img.save('image.png')

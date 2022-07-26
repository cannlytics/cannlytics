"""
FlowerArt | Cannlytics AI
Copyright (c) 2022 Cannlytics

Authors: Keegan Skeate <https://github.com/keeganskeate>
Created: 5/29/2022
Updated: 7/25/2022
License: MIT License <https://opensource.org/licenses/MIT>

Description:

    Programmatically create flower art given effects and aromas.
    E.g. skunk -> green heat wave coming off of flower

Resources:

    - https://github.com/benyaminahmed/nft-image-generator/blob/main/generate.ipynb

"""
import cv2
from bs4 import BeautifulSoup
import json
import numpy as np
import random
import requests
from time import sleep
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


class FlowerArt():
    """Create cannabis art and cannabis strain NFTs."""

    def __init__(self,
        line_size = 7,
        blur_value = 7,
        number_of_filters = 10, # 5 (fast) to 10 (slow) filters recommended.
        total_color = 9,
        sigmaColor = 200,
        sigmaSpace = 200,
    ) -> None:
        """Initialize the FlowerArt client."""
        # TODO: Incorporate randomness here!!!
        self.line_size = line_size
        self.blur_value = blur_value
        self.number_of_filters = number_of_filters
        self.total_color = total_color
        self.sigmaColor = sigmaColor
        self.sigmaSpace = sigmaSpace
    
    def cartoonize_image(self, filename):
        """Create a NFT for a given strain given a representative image.
        Combine edge mask with the colored image.
        Apply bilateral filter to reduce the noise in the image.
        This blurs and reduces the sharpness of the image.
        """
        img = cv2.imread(filename)
        edges = self.edge_mask(img, self.line_size, self.blur_value)
        img = self.color_quantization(img, self.total_color)
        blurred = cv2.bilateralFilter(
            img,
            d=self.number_of_filters,
            sigmaColor=self.sigmaColor,
            sigmaSpace=self.sigmaSpace,
        )
        cartoon = cv2.bitwise_and(blurred, blurred, mask=edges)
        outfile = f'../../../.datasets/strains/images/cannabis-flower-cartoon.jpg'
        cv2.imwrite(outfile, cartoon)
        cv2.imshow('image', cartoon)
        cv2.waitKey()
        return img
    
    def color_quantization(self, img, k):
        """Reduce the color palette, because a drawing has fewer colors
        than a photo. Color quantization is performed by the K-Means
        clustering algorithm of OpenCV."""
        data = np.float32(img).reshape((-1, 3))
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 20, 0.001)
        _, label, center = cv2.kmeans(data, k, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
        center = np.uint8(center)
        result = center[label.flatten()]
        result = result.reshape(img.shape)
        return result
    
    def edge_mask(self, img, line_size, blur_value):
        """Create an edge mask, emphasizing the thickness of the edges
        to give a cartoon-style to the image."""
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray_blur = cv2.medianBlur(gray, blur_value)
        edges = cv2.adaptiveThreshold(gray_blur, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, line_size, blur_value)
        return edges

    def get_color_association(self, string):
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


#-----------------------------------------------------------------------
# Example: Create strain NFTs based on chemotypes and a gallery of images.
# URL: <https://towardsdatascience.com/turn-photos-into-cartoons-using-python-bb1a9f578a7e>
#-----------------------------------------------------------------------

# [✓] TEST: Create a cartoon image for a given strain.
art = FlowerArt()
filename = f'../../../.datasets/strains/images/cannabis-flower.jpg'
image_data = art.cartoonize_image(filename)

# -- The Cannlytics 420 --

# TODO: Create 420 unique images for the top 420 strains.


# TODO: Mint NFTs for each image.


#-----------------------------------------------------------------------
# Example: Get colors associated with effect and aroma words.
#-----------------------------------------------------------------------

# # Format aroma data.
# aroma_data = []
# for key in AROMAS:
#     outcome = key.replace('aroma_', '')
#     outcome = outcome.replace('_', ' ')
#     outcome = outcome.title()
#     color = get_color_association(outcome)
#     aroma_data.append({
#         'key': key,
#         'name': outcome,
#         'icon': '',
#         'icon_url': '',
#         'color': color,
#     })
#     sleep(0.2)

# # Format effect data.
# effect_data = []
# for key in EFFECTS:
#     outcome = key.replace('effect_', '')
#     outcome = outcome.replace('_', ' ')
#     outcome = outcome.title()
#     color = get_color_association(outcome)
#     effect_data.append({
#         'key': key,
#         'name': outcome,
#         'icon': '',
#         'icon_url': '',
#         'color': color,
#     })
#     sleep(0.2)

# # Save the aroma data.
# data_dir = '../../../.datasets/website/'
# with open(data_dir + 'aromas.json', 'w+') as datafile:
#     json.dump(aroma_data, datafile, indent=4, sort_keys=True)

# # Save the effects data.
# effect_data = [dict(item, **{'positive': True}) for item in effect_data]
# with open(data_dir + 'effects.json', 'w+') as datafile:
#     json.dump(effect_data, datafile, indent=4, sort_keys=True)


#-----------------------------------------------------------------------
# Future work: Get details about each compound to incorporate in image.
#-----------------------------------------------------------------------

# TODO: Get details for each cannabinoid and terpene.
{
    'analyte_type': '',
    'cas_number': '',
    'name': '',
    'key': '',
    'common_names': [],
    'units': [],
}

# TODO: Save the compounds to Firestore.

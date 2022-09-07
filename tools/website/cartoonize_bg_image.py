"""
Create Strain NFT Art
Copyright (c) 2022 Cannlytics

Authors: Keegan Skeate <https://github.com/keeganskeate>
Created: 8/15/2022
Updated: 8/15/2022
License: <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description:

    Cartoonize an image for use as a background image.

"""
from cannlytics.data.flower_art import FlowerArt



# Create an art AI client.
art = FlowerArt(
    line_size = 7,
    blur_value = 7,
    number_of_filters = 10, # 5 (fast) to 10 (slow) filters recommended.
    total_colors = 50,
    sigmaColor = 50,
    sigmaSpace = 50,
)

# Get the image file and output file.
image_file = ''
outfile = ''

# Cartoonize the background image.
art.cartoonize_image(image_file, outfile)

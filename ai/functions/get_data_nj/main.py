"""


Data Source:

    - https://data.nj.gov/Reference-Data/New-Jersey-Cannabis-Dispensary-List/p3ry-ipie

"""

import requests

# Socrata endpoint: https://data.nj.gov/api/odata/v4/p3ry-ipie

# Get retail licensees.
base = 'https://data.nj.gov/resource'
endpoint = 'p3ry-ipie'
url = f'{base}/{endpoint}.json'
response = requests.get(url)
data = response.json()

# TODO: Augment with Census data.

# TODO: Augment with Fed FRED data.

# TODO: Calculate statistics for the retailers!

# TODO: Estimate sales for the retailers using model from other states!
# Use factors such as retailers per capita.
# LinkedIn post promoting Saturday Morning Statistics!!!
# Brag that we're the first estimate!!! Estimate sales this month, May, and 2022.

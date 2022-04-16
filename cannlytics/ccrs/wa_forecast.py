"""
WA Forecast
Copyright (c) 2022 Cannlytics

Authors: Keegan Skeate <keegan@cannlytics.com>
Created: 4/10/2022
Updated: 4/13/2022
License: MIT License <https://opensource.org/licenses/MIT>

Description: This script iterates on Washington State forecasts.

Data sources:

    - CCRS PRR All Data Up To 3-12-2022
    https://lcb.app.box.com/s/7pi3wqrmkuo3bh5186s5pqa6o5fv8gbs

Setup:

    1. pip install cannlytics

"""
from cannlytics.utils.utils import snake_case
import pandas as pd

# Use CCRS interface.
from ccrs import CCRS
# from constants import analyses, analysis_map, model_names


# Create a place for your data to live.
DATA_DIR = 'D:\\data\\washington'
folder = 'CCRS PRR All Data Up To 3-12-2022'

#------------------------------------------------------------------------------
# Read the data.
#------------------------------------------------------------------------------

# Initialize a CCRS client.
ccrs = CCRS()

# Read lab results.
lab_results = ccrs.read_lab_results(DATA_DIR, folder)

# Read licensee data.
licensees = ccrs.read_licensees(DATA_DIR, folder)

# Read areas data.


# Read contacts data.


# Read integrator data.


# Read inventory data.


# Read inventory adjustment data.


# Read inventory plant transfer data.


# Read plant data.


# Read plant destruction data.


# Read product data.


# Read sale header data.


# Read sale detail data.


# Read strain data.


# Read transfer data.


#------------------------------------------------------------------------------
# Clean the data.
#------------------------------------------------------------------------------


#------------------------------------------------------------------------------
# Explore the data.
#------------------------------------------------------------------------------

fail = lab_results.loc[lab_results['LabTestStatus'] == 'Fail']


#------------------------------------------------------------------------------
# Augment the data.
#------------------------------------------------------------------------------

# Get lab prices.

# Estimate laboratory revenue.

# Estimate laboratory market share.


#------------------------------------------------------------------------------
# Summarize the data.
#------------------------------------------------------------------------------


#------------------------------------------------------------------------------
# Analyze the data.
#------------------------------------------------------------------------------


#------------------------------------------------------------------------------
# Estimate ARIMAX for every variable.
#------------------------------------------------------------------------------


#------------------------------------------------------------------------------
# Save the date and forecasts.
#------------------------------------------------------------------------------


# TODO: Upload the data and make it available
# through the Cannlytics API.

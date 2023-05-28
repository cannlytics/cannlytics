"""
Upload Cannabis Sales Data
Copyright (c) 2023 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
Created: 5/26/2023
Updated: 5/26/2023
License: <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Command-line Usage:

    python data/archive/upload_sales.py all

"""
# Standard imports:
from datetime import datetime
import os
from typing import List

# External imports:
from cannlytics import firebase
from datasets import load_dataset
from dotenv import dotenv_values
import pandas as pd


# Specify where your data lives.
DATA_DIR = 'D://data'


# TODO: Aggregate all sales data for each state.


# TODO: Create timeseries.
# - monthly


# TODO: Calculate summary statistics.
# - sales_per_100_000_adults
# - sales_per_retailer

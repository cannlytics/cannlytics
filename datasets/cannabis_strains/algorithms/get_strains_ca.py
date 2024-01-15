# Standard imports:
import ast
import os
from time import sleep

# External imports:
from cannlytics.utils import snake_case
import pandas as pd
import re
import requests
import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from collections import Counter

from PIL import Image
from rembg import remove


# Read all of the SC Labs results.
datafile ="D://data/california/lab_results/datasets/sclabs/ca-lab-results-sclabs-2024-01-02-00-39-36.xlsx"
data = pd.read_excel(datafile)

# Find all of the results from California.
results = data.loc[data['lab_state'] == 'CA']


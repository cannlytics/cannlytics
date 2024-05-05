
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


# TODO: Read latest aggregated FL lab results.

# TODO: Find all of the unique stains.
# Note: NLP will be required.


# TODO: Calculate statistics for each strain.
# - totals by month
# - average_total_cannabinoids
# - average_total_thc
# - average_total_cbd
# - average_{cannabinoid}
# - average_total_terpenes
# - average_{terpene}
# - first_date_tested
# - first_producer


# TODO: Archive the strain statistics.
# - created_at
# - updated_at


# TODO: Save images for each strain.
# - Crop the image
# - Upload to Firebase Storage
# - Get a dynamic URL
# - Save the URL and reference to Firestore

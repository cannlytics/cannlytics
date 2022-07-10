"""
Strain Statistics
Copyright (c) 2022 Cannlytics

Authors: Keegan Skeate <https://github.com/keeganskeate>
Created: 7/3/2022
Updated: 7/3/2022
License: MIT License <https://opensource.org/licenses/MIT>

Description:

    Create product descriptions given product details using NLP.

Data Sources:

    - Data from: Over eight hundred cannabis strains characterized
    by the relationship between their subjective effects, perceptual
    profiles, and chemical compositions
    URL: <https://data.mendeley.com/datasets/6zwcgrttkp/1>
    License: CC BY 4.0. <https://creativecommons.org/licenses/by/4.0/>

Resources:

    - Over eight hundred cannabis strains characterized by the
    relationship between their psychoactive effects, perceptual
    profiles, and chemical compositions
    URL: <https://www.biorxiv.org/content/10.1101/759696v1.abstract>

    - Effects of cannabidiol in cannabis flower:
    Implications for harm reduction
    URL: <https://pubmed.ncbi.nlm.nih.gov/34467598/>


    https://www.infoq.com/news/2022/04/eleutherai-gpt-neox/

    https://arankomatsuzaki.wordpress.com/2021/06/04/gpt-j/

    https://github.com/vsuthichai/paraphraser

    https://datascience.stackexchange.com/questions/60261/generate-new-sentences-based-on-keywords

"""
# Standard imports.
from datetime import datetime
import os
from typing import Any, Optional

# External imports.
# from dotenv import dotenv_values
import pandas as pd

# Internal imports.
# from cannlytics.firebase import (
#     initialize_firebase,
#     update_documents,
# )
# from cannlytics.stats import (
#     calculate_model_statistics,
#     estimate_discrete_model,
#     get_stats_model,
#     predict_stats_model,
#     upload_stats_model,
# )
from cannlytics.utils.utils import snake_case
# from cannlytics.utils.data import (
#     combine_columns,
#     nonzero_columns,
#     nonzero_rows,
#     sum_columns,
# )
# from cannlytics.utils.files import download_file_from_url, unzip_files

# Ignore convergence errors.
import warnings
from statsmodels.tools.sm_exceptions import ConvergenceWarning
warnings.simplefilter('ignore', ConvergenceWarning)
warnings.simplefilter('ignore', RuntimeWarning)


def curate_strain_reviews(
        data_dir: str, 
        strain_folder: Optional[str] = 'Strain data/strains',
):
    """Curate cannabis strain reviews.
    Args:
        data_dir (str): The directory where the data lives.
        strain_folder (str): The folder where the review data lives.
    Returns:
        (DataFrame): Returns the strain reviews.
    """

    # Create a panel of reviews of strain lab results.
    panel = pd.DataFrame()
    directory = os.fsencode(os.path.join(data_dir, strain_folder))
    for file in os.listdir(directory):
        filename = os.fsdecode(file)
        if filename.endswith('.p'):

            # Read the strain's effects and aromas data.
            file_path = os.path.join(data_dir, strain_folder, filename)
            strain = pd.read_pickle(file_path)

            # Assign dummy variables for effects and aromas.
            reviews = strain['data_strain']
            strain_id = strain['strain']
            category = list(strain['categorias'])[0]
            for n, review in enumerate(reviews):

                # Create panel observation, combining prior compound data.
                obs = pd.Series(dtype='object')
                for aroma in review['sabores']:
                    key = 'aroma_' + snake_case(aroma)
                    obs[key] = 1
                for effect in review['efectos']:
                    key = 'effect_' + snake_case(effect)
                    obs[key] = 1

                # Assign category determined from original authors NLP.
                strain_name = strain_id.replace('-', ' ').title()
                obs['category'] = category
                obs['strain_id'] = strain_id
                obs['strain_name'] = strain_name
                obs['review'] = review['reporte']
                obs['user'] = review['usuario']

                # Record the observation.
                obs.name = '-'.join([strain_id, str(n)])
                obs = obs.to_frame().transpose()
                panel = pd.concat([panel, obs])

    # Return the panel with null effects and aromas coded as 0.
    return panel.fillna(0)


#-----------------------------------------------------------------------
# Get the data.
#-----------------------------------------------------------------------

# Read in all of the reviews
print('Curating reviews...')
DATA_DIR = '../../../.datasets/subjective-effects'
reviews = curate_strain_reviews(DATA_DIR)

# Save the reviews.
timestamp = datetime.now().isoformat()[:19].replace(':', '-')
reviews.to_excel(f'{DATA_DIR}/strain-reviews-{timestamp}.xlsx')


#-----------------------------------------------------------------------
# Exploring the data.
#-----------------------------------------------------------------------

# Count the number of strains.
strain_count = reviews.groupby('strain_name')['strain_name'].nunique()
print('Identified %i strains.' % len(strain_count))


#-----------------------------------------------------------------------
# Preprocessing the data.
#-----------------------------------------------------------------------

# De-duplicate the reviews.
reviews.drop_duplicates(subset='review', inplace=True)

# Save the processed.
timestamp = datetime.now().isoformat()[:19].replace(':', '-')
reviews.to_excel(f'{DATA_DIR}/curated-strain-reviews-{timestamp}.xlsx')



#-----------------------------------------------------------------------
# Modeling the data.
#-----------------------------------------------------------------------

# import nltk
# from nltk.sentiment.util import *
# from nltk.sentiment.vader import SentimentIntensityAnalyzer as SIA


# TODO: Determine sentiment for all strains


# TODO: Assign percentile for each strain


# TODO: Parse activities, conditions, and effects for each strain.


# TODO: Group strains by similarity somehow?


#-----------------------------------------------------------------------
# Training the model.
#-----------------------------------------------------------------------

# Train with a subset of the strain reviews.


#-----------------------------------------------------------------------
# Testing the model.
#-----------------------------------------------------------------------

# Test if we can predict the effects and aromas.


#-----------------------------------------------------------------------
# Evaluating the model.
#-----------------------------------------------------------------------

# Re-fit the model with the entire dataset.

# TODO: Create strain entries with every detail possible.
strain = {
    'antidepressant_avg': 0,
    'antidepressant_percentile': 0,
    'engagement_avg': 0,
    'engagement_percentile': 0,
    'lab_results_avg': {},
    'lab_results_std': {},
    'lab_results_number': 0,
    'number_of_reviews': 0,
    'personality_avg': {
        'openness': 0,
        'conscientiousness': 0,
        'extraversion': 0,
        'agreeableness': 0,
        'neuroticism': 0,
    },
    'personality_percentile': {
        'openness': 0,
        'conscientiousness': 0,
        'extraversion': 0,
        'agreeableness': 0,
        'neuroticism': 0,
    },
    'polarity': 'Neutral',
    'predicted_aromas': [],
    'predicted_effects': [],
    'sentiment_avg': 0,
    'sentiment_percentile': 0,
    'similar_strains': [],
    'strain_id': '',
    'strain_name': '',
    'strain_category': 'Sativa',
    'strain_category_percentile': 100,
    'well_being_avg': 0,
    'well_being_percentile': 0,   
}


#-------------
# Future work
#-------------

# TODO: Create NFT for each strain!!!


# TODO: Create image for each strain.


# TODO: Use GLP to create a strain description for each!!!!


# TODO: Given lab results, return the percentile of lab results.
# 1. Estimate a t-distribution with mean and std.
# 2. Give percentile of lab results (e.g. total cannabinoids).


# TODO: Given a corpus of reviews for a given strain, calculate
# various NLP statistics.


#-------------
# HTML Ideas
#-------------

# Prompts for users to submit missing / supplementary data.
# Especially prompt if no lab results!

# Plot distributions.

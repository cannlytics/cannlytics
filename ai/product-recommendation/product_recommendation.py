"""
Product Recommendation Models
Copyright (c) 2022 Cannlytics

Authors: Keegan Skeate <https://github.com/keeganskeate>
Created: 7/7/2022
Updated: 7/9/2022
License: MIT License <https://opensource.org/licenses/MIT>

Description:

    Collaborative Filtering: Recommend products similar to a
    given product and an inventory of products.

    Collaborative Filtering: Given a consumer's characteristics,
    recommend products that other consumers with similar
    characteristics enjoyed.

    Content-Based: Given a body of a consumer's reviews and
    lab results for those products, rank an inventory of
    products by the estimated consumer's preferences.

Data Sources:

    - PSI Labs Test Results
    URL: <https://results.psilabs.org/test-results/>

    - SC Labs Test Results
    URL: <https://client.sclabs.com/>

    - Vergara, Daniela, Gaudino, Reggie, Blank, Thomas, & Keegan, Brian.
    (2020). Modeling cannabinoids from a large-scale sample of Cannabis
    sativa chemotypes [Data set].
    URL: <https://doi.org/10.5061/dryad.sxksn0314>

"""
# Internal imports.
import os

# External imports.
import pandas as pd


# Constants.
TRAINING_DATA = '../../../.datasets/lab_results/training_data'
MODEL_DATA = '../../../.datasets/lab_results/model_data'


#-----------------------------------------------------------------------
# Aggregate training data:
# ✓ PSI Labs test results (2015 through 2021).
# ✓ SC Labs test results (through the present, 2022).
# - Connecticut product test results.
# - Washington State test results (2018 through 2021).
# ✓ Strain reviews (Alethia de la Fuente et. al) (2019).
#-----------------------------------------------------------------------

# Optional: Helper function to download all training data from Cannlytics.

# Aggregate all of the lab results datasets.
data = pd.DataFrame()
directory = '../../../.datasets/lab_results/training_data'
datasets = [f for f in os.listdir(directory)]
for dataset in datasets:
    file_data = pd.read_excel(dataset)
    data = pd.concat([data, file_data])

# Read in the reviews data.
filename = 'curated-strain-reviews-2022-07-08T08-14-09.xlsx'
dataset = f'../../../.datasets/strains/training_data{filename}'
reviews = pd.read_excel(dataset)


#-----------------------------------------------------------------------
# Create a body of knowledge for GLP.
#-----------------------------------------------------------------------

# Create a body of knowledge from parsing relevant texts.
# - https://review.mcrlabs.com/#cannabinoids


#-----------------------------------------------------------------------
# The 💐 FloRE, the 🛢️ CoRE, and the 🍪 BoERE
#-----------------------------------------------------------------------
# A comprehensive cannabis recommendation engine that estimates
# and incorporates a large number of statistical models and data to
# rank a given inventory of products for a given consumer by
# the predicted utility the consumer would receive from each product.
#-----------------------------------------------------------------------

# Model wants:
# - Match sample type first and foremost. If the user likes flower,
# then they probably want flower. Concentrate users probably want
# concentrates. Edible users probably want edibles. However,
# it would be fun to offer users other product types that may
# still be similar in other type categories.

# TODO: Strain name should be a predicting factor. For example,
# if we know the user likes Jack Herer, then the model should
# be smart enough to recommend "Jack"-type strains.

# When present, cannabinoids and terpenes should be used as
# predictive factors, but the model needs to be flexible
# to be able to still make predictions if missing lab results.


# TODO: Save the model for use behind an API.


#-----------------------------------------------------------------------
# Flower Recommendation Engine 💐 (FloRE)
#-----------------------------------------------------------------------

# Create a rating model that uses user predicted personality traits
# to predict the rating that user's will give various strains,
# interacted with the cannabinoid concentrations of the various
# strains.

# Then, given a user's corpus of text and an inventory of products,
# first predict the user's personality and then use the model to predict
# the user's rating for all the products in the inventory.


#-----------------------------------------------------------------------
# Concentrate Recommendation Engine 🛢️ (CoRE)
#-----------------------------------------------------------------------

# Specifically recommend concentrates to consumers. Perhaps from factors:
# - terpenes
# - desired consumption amount (mg)


#-----------------------------------------------------------------------
# Beverage or Edible Recommendation Engine 🍪 (BoERE)
#-----------------------------------------------------------------------

# Specifically recommend edibles and / or beverages to a consumer. Factors:
# - THC:CBD ratio
# - Product name (perhaps in relation to consumer's personality)




#-----------------------------------------------------------------------
# Example: Using the FloRE, CoRE, and BoERE in a machine learning algorithm.
#-----------------------------------------------------------------------

# Step 1. Make a prediction for a user.
# Optional: New users can take a personality test and have strains
# recommended to them based on their personality!!!

# Step 2. Re-train the model after the user submits their review.

# Step 3. Make another prediction for the user, hopefully better
# than the first.


#-----------------------------------------------------------------------
# Example: API
#-----------------------------------------------------------------------

# Get lab results given a Metrc UID!


#-----------------------------------------------------------------------
# DRAFTS
#-----------------------------------------------------------------------

# Author: volodymyr (https://stats.stackexchange.com/users/46195/volodymyr)
# URL: https://stats.stackexchange.com/q/258302
# License: CC BY-SA 4.0 <https://creativecommons.org/licenses/by-sa/4.0/>

# from sklearn.preprocessing import StandardScaler
# from sklearn.neighbors import NearestNeighbors

# def get_matching_pairs(treated_df, non_treated_df, scaler=True):

#     treated_x = treated_df.values
#     non_treated_x = non_treated_df.values

#     if scaler == True:
#         scaler = StandardScaler()

#     if scaler:
#         scaler.fit(treated_x)
#         treated_x = scaler.transform(treated_x)
#         non_treated_x = scaler.transform(non_treated_x)

#     nbrs = NearestNeighbors(n_neighbors=1, algorithm='ball_tree').fit(non_treated_x)
#     distances, indices = nbrs.kneighbors(treated_x)
#     indices = indices.reshape(indices.shape[0])
#     matched = non_treated_df.iloc[indices]
#     return matched


# import pandas as pd
# import numpy as np

# import matplotlib.pyplot as plt

# treated_df = pd.DataFrame()
# np.random.seed(1)

# size_1 = 200
# size_2 = 1000
# treated_df['x'] = np.random.normal(0,1,size=size_1)
# treated_df['y'] = np.random.normal(50,20,size=size_1)
# treated_df['z'] = np.random.normal(0,100,size=size_1)

# non_treated_df = pd.DataFrame()
# # two different populations
# non_treated_df['x'] = list(np.random.normal(0,3,size=size_2)) + list(np.random.normal(-1,2,size=2*size_2))
# non_treated_df['y'] = list(np.random.normal(50,30,size=size_2)) + list(np.random.normal(-100,2,size=2*size_2))
# non_treated_df['z'] = list(np.random.normal(0,200,size=size_2)) + list(np.random.normal(13,200,size=2*size_2))


# matched_df = get_matching_pairs(treated_df, non_treated_df)

# fig, ax = plt.subplots(figsize=(6,6))
# plt.scatter(non_treated_df['x'], non_treated_df['y'], alpha=0.3, label='All non-treated')
# plt.scatter(treated_df['x'], treated_df['y'], label='Treated')
# plt.scatter(matched_df['x'], matched_df['y'], marker='x', label='matched')
# plt.legend()
# plt.xlim(-1,2)

# Nearest neighbors model:
# - Recommendation System in Python
# URL: https://www.geeksforgeeks.org/recommendation-system-in-python/
# from sklearn.neighbors import NearestNeighbors
# """
# Find similar movies using KNN
# """
# def find_similar_movies(movie_id, X, k, metric='cosine', show_distance=False):
      
#     neighbour_ids = []
      
#     movie_ind = movie_mapper[movie_id]
#     movie_vec = X[movie_ind]
#     k+=1
#     kNN = NearestNeighbors(n_neighbors=k, algorithm="brute", metric=metric)
#     kNN.fit(X)
#     movie_vec = movie_vec.reshape(1,-1)
#     neighbour = kNN.kneighbors(movie_vec, return_distance=show_distance)
#     for i in range(0,k):
#         n = neighbour.item(i)
#         neighbour_ids.append(movie_inv_mapper[n])
#     neighbour_ids.pop(0)
#     return neighbour_ids
  
# movie_titles = dict(zip(movies['movieId'], movies['title']))
# movie_id = 3
# similar_ids = find_similar_movies(movie_id, X, k=10)
# movie_title = movie_titles[movie_id]
# print(f"Since you watched {movie_title}")
# for i in similar_ids:
#     print(movie_titles[i])


# Option 1. Recommend based on reviews.

# Option 2. Recommend based on chemotype.

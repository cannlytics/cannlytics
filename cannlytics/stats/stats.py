"""
Stats | Cannlytics
Copyright (c) 2024 Cannlytics

Authors: Keegan Skeate <https://github.com/keeganskeate>
Created: 10/20/2024
Updated: 10/20/2024
License: <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description: Cannabis-related statistical functions.
"""

# External imports:
import numpy as np
import pandas as pd
from skimage import color


def calc_diversity_index(df: pd.DataFrame, compounds: list) -> list:
    """Calculate the Shannon Diversity Index given results and a list of compounds.
    Args:
        df (pd.DataFrame): The results DataFrame.
        compounds (list): The list of compounds to include in the diversity calculation.
    Returns (list): A list of Shannon Diversity Index values.
    """
    diversities = []
    for _, row in df.iterrows():
        proportions = [pd.to_numeric(row[compound], errors='coerce') for compound in compounds if pd.to_numeric(row[compound], errors='coerce') > 0]
        proportions = np.array(proportions) / sum(proportions)
        shannon_index = -np.sum(proportions * np.log2(proportions))
        diversities.append(shannon_index)
    return diversities


def calculate_purpleness(rgb, how='scale', shade=510):
    """Purple is dominant in red and blue channels, and low in green.
    Note: Adjust the formula for other shades of purple.
    Args:
        rgb (list): A list of RGB values.
        how (str): How to calculate purpleness.
            Options are 'scale' and 'normalized'.
            Scale will return a value between 0 and 1.
            Normalized will return a value between -1 and 1.
        shade (int): The shade of purple to use.
    Returns:
        float: The purpleness score.
    """
    purpleness = (rgb[0] + rgb[2]) - 2 * rgb[1]
    if how == 'scale':
        return (purpleness + shade) / (shade * 2)
    elif how == 'normalized':
        return purpleness / shade


def calculate_colourfulness(rgb, metric='M3') -> float:
    """Calculate the colourfulness of an image.
    Args:
        rgb (np.array): An image as a numpy array.
        metric (str): The metric to use. Options are 'M1', 'M2', and 'M3'.
    Returns:
        float: The colourfulness score.
    """
    img = color.rgb2lab(rgb)
    l, a, b = img[:, :, 0], img[:, :, 1], img[:, :, 2]
    sigma_a, sigma_b = np.std(a), np.std(b)
    mu_a, mu_b = np.mean(a), np.mean(b)
    sigma_ab = np.sqrt(sigma_a**2 + sigma_b**2)
    mu_ab = np.sqrt(mu_a**2 + mu_b**2)
    Chroma = np.sqrt(a**2 + b**2)
    _, mu_C = np.std(Chroma), np.mean(Chroma)
    R, G, B = rgb[:, :, 0], rgb[:, :, 1], rgb[:, :, 2]
    rg = R - G
    yb = 0.5 * (R + G) - B
    sigma_rg, sigma_yb = np.std(rg), np.std(yb)
    mu_rg, mu_yb = np.mean(rg), np.mean(yb)
    sigma_rg_yb = np.sqrt(sigma_rg**2 + sigma_yb**2)
    mu_rg_yb = np.sqrt(mu_rg**2 + mu_yb**2)
    if metric == 'M1':
        return sigma_ab + 0.37 * mu_ab
    elif metric == 'M2':
        return sigma_ab + 0.94 * mu_C
    elif metric == 'M3':
        return sigma_rg_yb + 0.3 * mu_rg_yb
    else:
        raise ValueError('Unknown metric: %s' % metric)

"""
Quality Control Tools | Cannlytics

Author: Keegan Skeate <keegan@cannlytics.com>  
Created: 2/6/2021  
Updated: 6/23/2021  
License: MIT License <https://opensource.org/licenses/MIT>  

Perform various quality control checks and analyses to ensure
that your laboratory is operating as desired.

TODO:
    - Trend analyte results.
    - Create predictions of lab results given available inputs!
    - Statistics for internal standards.
"""


def backup_data():
    """Backup data stored in Firestore."""
    return NotImplementedError


def calculate_relative_percent_diff():
    """Calculate relative perecent difference between two samples."""
    return NotImplementedError


def plot_area_response():
    """Plot area response over time for a group of samples."""
    return NotImplementedError


def plot_deviations():
    """Plot deviations in results for a group of samples."""
    return NotImplementedError


def track_deviations():
    """Track deviations in results for a group of samples."""
    return NotImplementedError


def metrc_reconciliation():
    """Reconcile Metrc data with Firestore data."""
    return NotImplementedError

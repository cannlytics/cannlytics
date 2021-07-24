"""
Calculate Statistics for Organizations | Cannlyitcs

Author: Keegan Skeate <keegan@cannlytics.com>
Created: 7/24/2021
Updated: 7/24/2021
License: MIT License <https://opensource.org/licenses/MIT>
"""

from firebase_admin import initialize_app


def calculate_stats():
    """Calculate statistics for a given organization."""
    
    print('Calculating statistics...')
    
    # Get the organization's data.
    try:
        initialize_app()
    except ValueError:
        pass
    
    # Get the organization's data model data.
    
    # Calculate statistics for the organization.
    
    # Save the statistics to the organizations stats collection in Firestore.

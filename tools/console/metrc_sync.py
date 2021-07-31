"""
Metrc Reconciliation | Cannlytics

Author: Keegan Skeate
Contact: keegan@cannlytics.com
Created: Mon Mar 29 14:18:18 2021
License: MIT License
"""

# Two algorithms

# 1. Backup data algorithm

# data should be synced from Metrc and stored in Firestore initially.

# Data should be retrieved from / posted to Firestore.

# 2. Standard data keeping algorithm

# Periodically data should be consolidated with Metrc.

# All requests get / post from / to Metrc first, then save entries in Firestore.


# Run the standard algorithm if Metrc is down (fails repeatedly)
# then fallback to backup.
# That is, getting / posting to Firestore and
# flagging the data to be consolidated later with a cloud function.
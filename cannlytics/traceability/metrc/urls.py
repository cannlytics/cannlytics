# -*- coding: utf-8 -*-
"""
cannlytics.traceability.metrc.urls
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Metrc API URLs.
"""

# FIXME: Make state dynamic
METRC_API_BASE_URL = 'https://sandbox-api-%s.metrc.com'
METRC_API_BASE_URL_TEST = 'https://sandbox-api-%s.metrc.com'

# FIXME: Ideally form complete URLs before execution?
METRC_BATCHES_URL = '/plantbatches/v1/%s'
METRC_EMPLOYEES_URL = '/employees/v1/'
METRC_FACILITIES_URL = '/facilities/v1/'
METRC_LOCATIONS_URL = '/locations/v1/%s'
METRC_HARVESTS_URL = '/harvests/v1/%s'
METRC_ITEMS_URL = '/items/v1/%s'
METRC_LAB_RESULTS_URL = '/labtests/v1/%s'
METRC_PACKAGES_URL = '/packages/v1/%s'
METRC_PATIENTS_URL = '/patients/v1/%s'
METRC_PLANTS_URL = '/plants/v1/%s'
METRC_RECEIPTS_URL = '/sales/v1/receipts/%s'
METRC_SALES_URL = '/sales/v1/%s'
METRC_STRAINS_URL = '/strains/v1/%s'
METRC_TRANSACTIONS_URL = '/sales/v1/transactions/%s'
METRC_TRANSFERS_URL = '/transfers/v1/%s'
METRC_TRANSFER_PACKAGES_URL = '/transfers/v1/delivery/%s/%s'
METRC_TRANSFER_TEMPLATE_URL = '/transfers/v1/templates/%s'
METRC_UOM_URL = '/unitsofmeasure/v1/active'

# Unused
# METRC_CREATE_PACKAGES_URL = '/harvests/v1/create/packages'
# METRC_CREATE_TESTING_PACKAGES_URL = '/harvests/v1/create/packages/testing'
# METRC_SHIPMENTS_URL = '/transfers/v1/%s/%s'
# METRC_TRANSFER_DETAILS_URL = '/transfers/v1/%s/%s/details'
# METRC_WASTE_TYPES_URL = '/harvests/v1/waste/types'


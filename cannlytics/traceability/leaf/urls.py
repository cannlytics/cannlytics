# -*- coding: utf-8 -*-
"""
cannlytics.traceability.leaf.urls
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Leaf Data Systems API urls.
"""

LEAF_API_BASE_URL = 'https://watest.leafdatazone.com/api/v1' # PRODUCTION: https://traceability.lcb.wa.gov/api/v1/
LEAF_API_BASE_URL_TEST = 'https://watest.leafdatazone.com/api/v1'

LEAF_AREAS_URL = LEAF_API_BASE_URL + '/areas'
LEAF_AREAS_UPDATE_URL = LEAF_API_BASE_URL + '/areas/update'
LEAF_AREAS_DELETE_URL = LEAF_API_BASE_URL + '/areas/%s'

LEAF_BATCHES_URL = LEAF_API_BASE_URL + '/batches'
LEAF_BATCHES_UPDATE_URL = LEAF_API_BASE_URL + '/batches/update'
LEAF_BATCHES_DELETE_URL = LEAF_API_BASE_URL + '/batches/%s'
LEAF_BATCHES_CURE_URL = LEAF_API_BASE_URL + '/batches/cure_lot'
LEAF_BATCHES_FINISH_URL = LEAF_API_BASE_URL + '/batches/finish_lot'

LEAF_DISPOSAL_URL = LEAF_API_BASE_URL + '/disposals'
LEAF_DISPOSAL_UPDATE_URL = LEAF_API_BASE_URL + '/disposals/update'
LEAF_DISPOSAL_DELETE_URL = LEAF_API_BASE_URL + '/disposals/%s'
LEAF_DISPOSAL_DISPOSE_URL = LEAF_API_BASE_URL + '/disposals/dispose'

LEAF_PLANTS_URL = LEAF_API_BASE_URL + '/plants'
LEAF_PLANTS_UPDATE_URL = LEAF_API_BASE_URL + '/plants/update'
LEAF_PLANTS_DELETE_URL = LEAF_API_BASE_URL + '/plants/%s'
LEAF_PLANTS_HARVEST_URL = LEAF_API_BASE_URL + '/plants/harvest_plants'
LEAF_PLANTS_AREAS_URL = LEAF_API_BASE_URL + '/plants_by_area'
LEAF_PLANTS_MOVE_URL = LEAF_API_BASE_URL + '/move_plants_to_inventory'

LEAF_INVENTORY_ADJUSTMENTS_URL = LEAF_API_BASE_URL + '/inventory_adjustments'

LEAF_INVENTORY_URL = LEAF_API_BASE_URL + '/inventories'
LEAF_INVENTORY_UPDATE_URL = LEAF_API_BASE_URL + '/inventories/update'
LEAF_INVENTORY_DELETE_URL = LEAF_API_BASE_URL + '/inventories/%s'
LEAF_INVENTORY_SPLIT_URL = LEAF_API_BASE_URL + '/split_inventory'
LEAF_INVENTORY_CONVERT_URL = LEAF_API_BASE_URL + '/conversions/create'
LEAF_INVENTORY_MOVE_URL = LEAF_API_BASE_URL + '/move_inventory_to_plants'

LEAF_INVENTORY_TRANSFERS_URL = LEAF_API_BASE_URL + '/inventory_transfers'
LEAF_INVENTORY_TRANSFERS_UPDATE_URL = LEAF_API_BASE_URL + '/inventory_transfers/update'
LEAF_INVENTORY_TRANSFERS_TRANSIT_URL = LEAF_API_BASE_URL + '/inventory_transfers/api_in_transit'
LEAF_INVENTORY_TRANSFERS_RECEIVE_URL = LEAF_API_BASE_URL + '/inventory_transfers/api_receive'
LEAF_INVENTORY_TRANSFERS_VOID_URL = LEAF_API_BASE_URL + '/inventory_transfers/void'

LEAF_INVENTORY_TYPES_URL = LEAF_API_BASE_URL + '/inventory_types'
LEAF_INVENTORY_TYPES_UPDATE_URL = LEAF_API_BASE_URL + '/inventory_types/update'
LEAF_INVENTORY_TYPES_DELETE_URL = LEAF_API_BASE_URL + '/inventory_types/%s'

LEAF_LAB_RESULTS_URL = LEAF_API_BASE_URL + '/lab_results'
LEAF_LAB_RESULTS_UPDATE_URL = LEAF_API_BASE_URL + '/lab_results/update'
LEAF_LAB_RESULTS_DELETE_URL = LEAF_API_BASE_URL + '/lab_results/%s'

LEAF_SALES_URL = LEAF_API_BASE_URL + '/sales'
LEAF_SALES_UPDATE_URL = LEAF_API_BASE_URL + '/sales/update'
LEAF_SALES_DELETE_URL = LEAF_API_BASE_URL + '/sales/%s'

LEAF_STRAINS_URL = LEAF_API_BASE_URL + '/strains'
LEAF_STRAINS_UPDATE_URL = LEAF_API_BASE_URL + '/strains/update'
LEAF_STRAINS_DELETE_URL = LEAF_API_BASE_URL + '/strains/%s'

LEAF_LICENSEES_URL = LEAF_API_BASE_URL + '/mmes'
LEAF_LICENSEE_URL = LEAF_API_BASE_URL + '/mmes/%s'
LEAF_USERS_URL = LEAF_API_BASE_URL + '/users'

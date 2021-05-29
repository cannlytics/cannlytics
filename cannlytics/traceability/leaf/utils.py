# -*- coding: utf-8 -*-
"""
cannlytics.traceability.leaf.utils
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains functions that are useful
when interfacing with the Leaf Data Systems API.
"""

from datetime import datetime, timedelta


def format_time_filter(start, stop, field):
    """Formats a time filter for a given endpoint type.
    Args:
        start (str): An ISO date string, e.g. 2020-04-20.
        stop (str): An ISO date string, e.g. 2021-04-20.
        field (str): The time field to filter by.
    """
    start_date = start.split('-')
    end_date = stop.split('-')
    y1, m1, d1 = start_date[0], start_date[1], start_date[2]
    y2, m2, d2 = end_date[0], end_date[1], end_date[2]
    return f'?f_{field}1={m1}%2F{d1}%2F{y1}&f_{field}2={m2}%2F{d2}%2F{y2}'


def get_time_string(past=0, future=0, tz='local'):
    """Get a human readable time.
    Args:
        past (int): Number of minutes in the past to get a timestamp.
        future (int): Number of minutes into the future to get a timestamp.
        # TODO: Set time in timezone of state (e.g. {'state': 'OK'} -> CDT)
    """
    now = datetime.now()
    now += timedelta(minutes=future)
    now -= timedelta(minutes=past)
    return now.strftime('%m/%d/%Y %I:%M%p').lower()


# TODO: Import / export data to and from the API.

def import_csv(self, file_id, data):
    """Imports data from a .csv to the Leaf Data Systems API.

    :param str data: A CSV string of data.

    Example:

    .. code::

        # Read CSV file contents
        content = open('file_to_import.csv', 'r').read()
        gc.import_csv(spreadsheet.id, content)

    .. note::

        This method removes all other worksheets and then entirely
        replaces the contents of the first worksheet.

    """
    return NotImplementedError
    # headers = {'Content-Type': 'text/csv'}
    # url = '{0}/{1}'.format(DRIVE_FILES_UPLOAD_API_V2_URL, file_id)

    # self.request(
    #     'put',
    #     url,
    #     data=data,
    #     params={
    #         'uploadType': 'media',
    #         'convert': True,
    #         'supportsAllDrives': True,
    #     },
    #     headers=headers,
    # )


def export_csv(self, file_id, data):
    """Exports data to a .csv from the Leaf Data Systems API.

    :param str data: A CSV string of data.

    Example:

    .. code::

        # Read CSV file contents
        content = open('file_to_import.csv', 'r').read()
        gc.import_csv(spreadsheet.id, content)

    .. note::

        This method removes all other worksheets and then entirely
        replaces the contents of the first worksheet.

    """
    return NotImplementedError
    # headers = {'Content-Type': 'text/csv'}
    # url = '{0}/{1}'.format(DRIVE_FILES_UPLOAD_API_V2_URL, file_id)

    # self.request(
    #     'put',
    #     url,
    #     data=data,
    #     params={
    #         'uploadType': 'media',
    #         'convert': True,
    #         'supportsAllDrives': True,
    #     },
    #     headers=headers,
    # )


#------------------------------------------------------------------
# Constants
#------------------------------------------------------------------

adjustment_reasons = [
    'reconciliation',
    'theft',
    'seizure', 
    'member_left_the_cooperative', 
    'internal_qa_sample', 
    'budtender_sample', 
    'vendor_sample',
]

# TODO: Add analyses by sample type
analyses = {}

analysis_statuses = [
    'not_started',
    'in_progress', 
    'completed',
]

batch_types = [
    'propagation material',
    'plant',
    'harvest', 
    'intermediate/ end product',
]

inventory_types = [
    'immature_plant',
    'mature_plant', 
    'harvest_materials',
    'intermediate_product', 
    'end_product',
    'waste',
]

intermediate_types = {
    'intermediate_product': [
        'marijuana_mix',
        'non-solvent_based_concentrate', 
        'hydrocarbon_concentrate', 
        'co2_concentrate', 
        'ethanol_concentrate', 
        'food_grade_solvent_concentrate', 
        'infused_cooking_medium',
    ],
    'end_product': [
        'liquid_edible', 
        'solid_edible', 
        'concentrate_for_inhalation',
        'topical', 
        'infused_mix', 
        'packaged_marijuana_mix', 
        'sample_jar',
        'usable_marijuana', 
        'capsules',
        'tinctures', 
        'transdermal_patches',
        'suppositories',
    ],
    'immature_plant': [
        'seeds',
        'clones',
        'plant_tissue',
    ],
    'mature_plant': [
        'non_mandatory_plant_sample',
    ],
    'harvest_materials': [
        'flower',
        'other_material',
        'flower_lots', 
        'other_material_lots',
    ],
    'waste': ['waste']
}


plant_origins = [
    'seed',
    'clone',
    'plant',
    'tissue',
]

plant_stages = [
    'propagation source',
    'growing', 
    'harvested',
    'packaged',
    'destroyed',
]

sample_types = [
    'lab_sample', 
    'non_mandatory_sample', 
    'product_sample',
]

product_sample_types = [
    'budtender_sample', 
    'vendor_sample',
]

waste_reasons = {
    'harvest': [
        'failed qa',
        'infestation',
        'quality control',
        'returned',
        'spoilage',
        'unhealthy',
        'mandated',
        'waste', 
        'other',
    ],
    'daily_plant_waste': [
        'pruning',
        'infestation',
        'quality control',
        'unhealthy',
        'mandated',
    ],
    'inventory': [
        'failed qa', 
        'quality control',
        'returned', 
        'spoilage',
        'mandated',
        'other',
    ],
}

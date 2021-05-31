# -*- coding: utf-8 -*-
"""
cannlytics.traceability.metrc.utils
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains common Metrc utility functions
and constants.
"""

from base64 import b64encode, decodebytes
from datetime import datetime, timedelta
from re import sub
from pandas import read_excel

#------------------------------------------------------------------
# Utility functions
#------------------------------------------------------------------

def camel_to_snake(s):
    """Turn a camel-case string to a snake-case string.
    Args:
        s (str): The string to convert to snake-case.
    """
    return sub(r'(?<!^)(?=[A-Z])', '_', s).lower()


def snake_to_camel(s):
    """Turn a snake-case string to a camel-case string.
    Args:
        s (str): The string to convert to camel-case.
    """
    return ''.join([*map(str.title, s.split('_'))])


def clean_dictionary(d, function=camel_to_snake):
    """Format dictionary keys with given function, snake case by default.
    Args:
        d (dict): A dictionary to clean.
        function (function): A function to apply to each key.
    """
    return {function(k): v for k, v in d.items()}


def clean_nested_dictionary(d, function=camel_to_snake):
    """Format nested (at most 2 levels) dictionary keys with a given function,
    snake case by default.
    Args:
        d (dict): A dictionary to clean, allowing dictionaries as values.
        function (function): A function to apply to each key.
    """
    clean = clean_dictionary(d, function)
    for k, v in clean.items():
        # if isinstance(v, dict):
        try:
            clean[k] = clean_dictionary(v, function)
        except AttributeError:
            pass
    return clean


def decode_pdf(data: str, destination: str):
    """Save an base-64 encoded string as a PDF.
    Args:
        data (str): Base-64 encoded string representing a PDF.
        destination (str): The destination for the PDF file.
    """
    bits = decodebytes(data)
    with open(destination, 'wb') as pdf:
        pdf.write(bits)


def encode_pdf(filename):
    """Open a PDF file in binary mode.
    Args:
        filename (str): The full file path of a PDF to encode.
    Returns:
        A string encoded in base-64.
    """
    with open(filename, 'rb') as pdf:
        return b64encode(pdf.read())


def format_params(**kwargs):
    """Format Metrc request parameters."""
    params = {}
    for param in kwargs:
        if kwargs[param]:
            key = PARAMETERS[param]
            params[key] = kwargs[param]
    return params


def get_timestamp(past=0, future=0, tz='local'):
    """Get an ISO formatted timestamp.
    Args:
        past (int): Number of minutes in the past to get a timestamp.
        future (int): Number of minutes into the future to get a timestamp.

    # TODO: Set time in timezone of state (e.g. {'state': 'OK'} -> CDT)
    """
    now = datetime.now()
    now += timedelta(minutes=future)
    now -= timedelta(minutes=past)
    if tz is None:
        return now.isoformat()[:19]
    else:
        return now.isoformat()


def remove_dict_fields(d, fields):
    """Remove multiple keys from a dictionary.
    Args:
        d (dict): The dictionary to clean.
        fields (list): A list of keys (str) to remove.
    """
    for key in fields:
        if key in d:
            del d[key]
    return d


def remove_dict_nulls(d):
    """Return a shallow copy of a dictionary with all `None` values excluded.
    Args:
        d (dict): The dictionary to reduce.
    """
    return {k: v for k, v in d.items() if v is not None}


def update_context(context, function=snake_to_camel, **kwargs):
    """Update context with keyword arguments.
    Args:
        function (function): Function to apply to final dictionary keys.
    """
    entry = {}
    for key in kwargs:
        entry[key] = kwargs[key]
    data = {
        **clean_nested_dictionary(context, function),
        **clean_nested_dictionary(entry, function)
    }
    return data

#------------------------------------------------------------------
# Optional: Add data import / export functionality.
#------------------------------------------------------------------

def import_tags(file_path):
    """Import plant and package tags."""
    df = read_excel(file_path, sep=',')
    data = df.to_dict('records')
    return clean_dictionary(data)

# Data import
# 1. Create Plantings / Plantings from Plants / Plantings from Packages
# 2. Immature Plants Growth Phase
# 3. Record Immature Plants Waste
# 4. Immature Plants Packages
# 5. Destroy Immature Plants
# 6. Plants Location
# 7. Plants Growth Phase
# 8. Record Plants Waste
# 9. Manicure Plants
# 10.Harvest Plants
# 11.Destroy Plants
# 12.Packages from Harvest
# 13.Lab Results
# 14.Package Adjustment
# 15.Sales (new)
# 16.Sales (update)
# If uploading multiple types of CSV files, it is recommended that they be uploaded in the
# order listed above to avoid data collisions. For instance, if uploading a CSV to
# Manicure Plants and another to Destroy Plants and the same plant is included on both
# files, the manicure must be recorded prior to the destruction of the plant.
# Except for Lab Results, all CSV files are limited to 500 rows per file. When adding
# plants to the same harvest or manicure batch using multiple CSV files, it is
# recommended that they be uploaded one file at a time.
# Please reference the CA CSV Guide available under the Metrc Support menu for
# additional Data Import assistance.

#------------------------------------------------------------------
# Constants TODO: Clean up constants
#------------------------------------------------------------------

PARAMETERS = {
    'license_number': 'licenseNumber',
    'start': 'lastModifiedStart',
    'end': 'lastModifiedEnd',
    'sales_start': 'salesDateStart',
    'sales_end': 'salesDateEnd',
    'package_id': 'packageId',
    'from_mother': 'isFromMotherPlant',
    'source': 'source'
}

categories = [
    'Flower & Buds',
    'Immature Plants',
# Concentrate (Non-Solvent Based) (Count-Volume)
# Concentrate (Non-Solvent Based) (Count-Weight)
# Concentrate (Weight Based)
# Edibles (Count-Volume)
# Edibles (Count-Weight)
# Extracts (Solvent Based) (Count-Volume)
# Extracts (Solvent Based) (Count-Weight)
# Flower & Buds
# Immature Plants
# Kief
# Mature Plants
# Metered Dose Nasal Spray Products
# MMJ Waste
# Pre-Roll (Flower Only)
# Pre-Roll (Infused)
# Pressurized Metered Dose Inhaler Products
# Rectal/Vaginal Administration Products (Count-Volume)
# Rectal/Vaginal Administration Products (Count-Weight)
# Seeds
# Shake/Trim
# Shake/Trim (by Strain)
# Tinctures (Count-Volume)
# Tinctures (Count-Weight)
# Topicals (Count-Volume)
# Topicals (Count-Weight)
# Transdermal Patches
# Vape Cartridges
# Whole Wet Plant
]

item_types = [
  {
    "Name": "Buds",
    "ProductCategoryType": "Buds",
    "QuantityType": "WeightBased",
    "RequiresStrain": True,
    "RequiresItemBrand": False,
    "RequiresAdministrationMethod": False,
    "RequiresUnitCbdPercent": False,
    "RequiresUnitCbdContent": False,
    "RequiresUnitCbdContentDose": False,
    "RequiresUnitThcPercent": False,
    "RequiresUnitThcContent": False,
    "RequiresUnitThcContentDose": False,
    "RequiresUnitVolume": False,
    "RequiresUnitWeight": False,
    "RequiresServingSize": False,
    "RequiresSupplyDurationDays": False,
    "RequiresNumberOfDoses": False,
    "RequiresPublicIngredients": False,
    "RequiresDescription": False,
    "RequiresProductPhotos": 0,
    "RequiresLabelPhotos": 0,
    "RequiresPackagingPhotos": 0,
    "CanContainSeeds": True,
    "CanBeRemediated": True
  },
  {
    "Name": "Immature Plants",
    "ProductCategoryType": "Plants",
    "QuantityType": "CountBased",
    "RequiresStrain": True,
    "RequiresItemBrand": False,
    "RequiresAdministrationMethod": False,
    "RequiresUnitCbdPercent": False,
    "RequiresUnitCbdContent": False,
    "RequiresUnitCbdContentDose": False,
    "RequiresUnitThcPercent": False,
    "RequiresUnitThcContent": False,
    "RequiresUnitThcContentDose": False,
    "RequiresUnitVolume": False,
    "RequiresUnitWeight": False,
    "RequiresServingSize": False,
    "RequiresSupplyDurationDays": False,
    "RequiresNumberOfDoses": False,
    "RequiresPublicIngredients": False,
    "RequiresDescription": False,
    "RequiresProductPhotos": 0,
    "RequiresLabelPhotos": 0,
    "RequiresPackagingPhotos": 0,
    "CanContainSeeds": True,
    "CanBeRemediated": False
  },
  {
    "Name": "Infused",
    "ProductCategoryType": "InfusedEdible",
    "QuantityType": "CountBased",
    "RequiresStrain": False,
    "RequiresItemBrand": False,
    "RequiresAdministrationMethod": False,
    "RequiresUnitCbdPercent": False,
    "RequiresUnitCbdContent": False,
    "RequiresUnitCbdContentDose": False,
    "RequiresUnitThcPercent": False,
    "RequiresUnitThcContent": True,
    "RequiresUnitThcContentDose": False,
    "RequiresUnitVolume": False,
    "RequiresUnitWeight": True,
    "RequiresServingSize": False,
    "RequiresSupplyDurationDays": False,
    "RequiresNumberOfDoses": False,
    "RequiresPublicIngredients": False,
    "RequiresDescription": False,
    "RequiresProductPhotos": 0,
    "RequiresLabelPhotos": 0,
    "RequiresPackagingPhotos": 0,
    "CanContainSeeds": False,
    "CanBeRemediated": True
  },
  {
    "Name": "Infused Liquid",
    "ProductCategoryType": "InfusedEdible",
    "QuantityType": "CountBased",
    "RequiresStrain": False,
    "RequiresItemBrand": False,
    "RequiresAdministrationMethod": False,
    "RequiresUnitCbdPercent": False,
    "RequiresUnitCbdContent": False,
    "RequiresUnitCbdContentDose": False,
    "RequiresUnitThcPercent": False,
    "RequiresUnitThcContent": True,
    "RequiresUnitThcContentDose": False,
    "RequiresUnitVolume": True,
    "RequiresUnitWeight": False,
    "RequiresServingSize": False,
    "RequiresSupplyDurationDays": False,
    "RequiresNumberOfDoses": False,
    "RequiresPublicIngredients": False,
    "RequiresDescription": False,
    "RequiresProductPhotos": 0,
    "RequiresLabelPhotos": 0,
    "RequiresPackagingPhotos": 0,
    "CanContainSeeds": False,
    "CanBeRemediated": True
  }
]

test_statuses = [
  'NotSubmitted',
  'SubmittedForTesting',
  'TestFailed',
  'TestPassed',
  'TestingInProgress',
  'AwaitingConfirmation',
  'RetestFailed',
  'RetestPassed',
  'Remediated',
  'SelectedForRandomTesting',
  'NotRequired',
  'ProcessValidated',
]


analyses = [
  {
    'Id': 1,
    'Name': 'THC',
    'RequiresTestResult': False,
    'InformationalOnly': False,
    'AlwaysPasses': False,
    'LabTestResultMode': 0,
    'LabTestResultMinimum': None,
    'LabTestResultMaximum': None,
    'DependencyMode': 0
  },
  {
    'Id': 2,
    'Name': 'THCa',
    'RequiresTestResult': False,
    'InformationalOnly': False,
    'AlwaysPasses': False,
    'LabTestResultMode': 0,
    'LabTestResultMinimum': None,
    'LabTestResultMaximum': None,
    'DependencyMode': 0
  },
  {
    'Id': 3,
    'Name': 'CBD',
    'RequiresTestResult': False,
    'InformationalOnly': False,
    'AlwaysPasses': False,
    'LabTestResultMode': 0,
    'LabTestResultMinimum': None,
    'LabTestResultMaximum': None,
    'DependencyMode': 0
  },
  {
    'Id': 4,
    'Name': 'CBDa',
    'RequiresTestResult': False,
    'InformationalOnly': False,
    'AlwaysPasses': False,
    'LabTestResultMode': 0,
    'LabTestResultMinimum': None,
    'LabTestResultMaximum': None,
    'DependencyMode': 0
  },
  {
    'Id': 5,
    'Name': 'Pesticides',
    'RequiresTestResult': False,
    'InformationalOnly': False,
    'AlwaysPasses': False,
    'LabTestResultMode': 0,
    'LabTestResultMinimum': None,
    'LabTestResultMaximum': None,
    'DependencyMode': 'RequiresOne'
  }
]

transfer_statuses = [
  'Shipped',
  'Rejected',
  'Accepted',
  'Returned'
]

transfer_types = [
    {"Name": "Affiliated Transfer", "ForLicensedShipments": True, "ForExternalIncomingShipments": False, "ForExternalOutgoingShipments": False, "RequiresDestinationGrossWeight": False, "RequiresPackagesGrossWeight": False},
    {"Name": "Beginning Inventory Transfer", "ForLicensedShipments": False, "ForExternalIncomingShipments": True, "ForExternalOutgoingShipments": False, "RequiresDestinationGrossWeight": False, "RequiresPackagesGrossWeight": False},
    {"Name": "Lab Sample Transfer", "ForLicensedShipments": True, "ForExternalIncomingShipments": False, "ForExternalOutgoingShipments": False, "RequiresDestinationGrossWeight": False, "RequiresPackagesGrossWeight": False},
    {"Name": "Unaffiliated (Wholesale) Transfer", "ForLicensedShipments": True, "ForExternalIncomingShipments": False, "ForExternalOutgoingShipments": False, "RequiresDestinationGrossWeight": False, "RequiresPackagesGrossWeight": False},
    {"Name": "Waste Disposal", "ForLicensedShipments": True, "ForExternalIncomingShipments": False, "ForExternalOutgoingShipments": False, "RequiresDestinationGrossWeight": False, "RequiresPackagesGrossWeight": False}
]

batch_types = ['Seed', 'Clone']

growth_phases = ['Young', 'Vegetative', 'Flowering']

additive_types = ['Fertilizer', 'Pesticide','Other']

# harvest_waste_types = ['Plant Material', 'Fibrous', 'Root Ball']
harvest_waste_types = ['MMJ Waste', 'Waste']

waste_methods = [{'Name': 'Grinder'}, {'Name': 'Compost'}]

waste_reasons = [
    {"Name": "Disease/Infestation", "RequiresNote": True},
    {"Name": "Mother Plant Destruction", "RequiresNote": True},
    {"Name": "Trimming/Pruning", "RequiresNote": False}
]

customer_types = [
  'Consumer',
  'Patient',
  'Caregiver',
  'ExternalPatient',
]

location_types = [
  {
    'Id': 1,
    'Name': 'Default',
    'ForPlantBatches': True,
    'ForPlants': True,
    'ForHarvests': True,
    'ForPackages': True
  },
  {
    'Id': 2,
    'Name': 'Planting',
    'ForPlantBatches': True,
    'ForPlants': True,
    'ForHarvests': False,
    'ForPackages': False
  },
  {
    'Id': 3,
    'Name': 'Packing',
    'ForPlantBatches': False,
    'ForPlants': False,
    'ForHarvests': False,
    'ForPackages': True
  }
]

package_types = [
  'Product',
  'ImmaturePlant',
  'VegetativePlant',
  'PlantWaste',
  'HarvestWaste'
]

adjustment_reasons = [
  {"Name": "API Related Error", "RequiresNote": True},
  {"Name": "Drying", "RequiresNote": True},
  {"Name": "Mandatory State Destruction", "RequiresNote": True},
  {"Name": "Theft", "RequiresNote": True},
  {"Name": "Typing/Entry Error", "RequiresNote": True}
]

units = [
  {
    "QuantityType": "CountBased",
    "Name": "Each",
    "Abbreviation": "ea"
  },
  {
    "QuantityType": "WeightBased",
    "Name": "Ounces",
    "Abbreviation": "oz"
  },
  {
    "QuantityType": "WeightBased",
    "Name": "Pounds",
    "Abbreviation": "lb"
  },
  {
    "QuantityType": "WeightBased",
    "Name": "Grams",
    "Abbreviation": "g"
  },
  {
    "QuantityType": "WeightBased",
    "Name": "Milligrams",
    "Abbreviation": "mg"
  },
  {
    "QuantityType": "WeightBased",
    "Name": "Kilograms",
    "Abbreviation": "kg"
  }
]

#------------------------------------------------------------------
# Scrap constants
#------------------------------------------------------------------

# waste_types = {
#     'Contamination': 'Degradation of plant(s) by environmental elements such as pests, filth/foreign material, mold/mildew.',
#     'Contamination (BCC)': 'Degradation of plant(s) by environmental elements such as pests, filth/foreign material, mold/mildew. Displays for BCC licensees only.',
#     'Damage': 'Damage to the plant(s).',
#     Damage (BCC) Damage to the plant(s). Displays for BCC licensees only.
#     Failure to Thrive Failure to grow or develop vigorously.
#     Failure to Thrive
#     (BCC)
#     Failure to grow or develop vigorously. Displays for BCC licensees
#     only.
#     Male Plants The plant(s) is male.
#     Male Plants (BCC) The plant(s) is male. Displays for BCC licensees only.
#     Mandated
#     Destruction
#     Cannabis plant(s) is destroyed as a result of a State– or local
#     authority–mandated or –supervised process.
#     Pesticides Improper usage and application of pesticides on plant(s).
#     64
#     Industry User’s Guide – CA Supplemental Rev 20.4
#     Waste Reason Reason Usage
#     Pruning Cannabis byproduct produced during pruning of plant(s).    
# }

# transfer_types = {
# Transfer Used for all transfers except transfers requiring the use of a
# Wholesale Manifest or Return manifest.
# Return A Return transfer is used only for the transfer of defective
# manufactured products back to the originating licensee.
# Wholesale Manifest A Wholesale Manifest transfer is used when transferring products
# to a Retailer licensee.
# When a Wholesale Manifest is used, the originator is required to
# record the wholesale price of each package in the transfer.
# A Microbusiness functioning as a Distributor with a transfer that
# includes a Retailer licensee, or another Microbusiness licensee
# functioning as a Retailer, shall follow the process above.
# It is recommended that Nurseries utilize a Wholesale Manifest
# when transferring seeds or immature plants to a Retailer.    
# }

# rejection_types = {
# Damage There has been damage to the plant or package.
# Damage (BCC) There has been damage to the package. Notes section should be used
# to explain the damage. Displays for BCC licensees only.
# Data Entry Error A package(s) cannot be accepted by the receiving licensee due to a
# data entry error that occurred when the manifest was created.
# Incorrect Item
# (Transfer)
# A manifest was created with the incorrect item and must be rejected.
# Incorrect Quantity Package received via transfer that was not correctly weighed or
# counted. This should NOT be used to correct sales. If the package
# quantity varies significantly, it should be rejected.
# Notes section should be used to explain the error.
# Non-Compliant
# Label
# Package received via transfer that contains non-compliant label.
# 126
# Industry User’s Guide – CA Supplemental Rev 20.4
# Spoilage Deterioration of packaged product.
# Theft Rejection of a package when product has been stolen in transit.
# Licensing Authority must be notified. Notes section should be used to    
# }


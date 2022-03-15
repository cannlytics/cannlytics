"""
Metrc Constants | Cannlytics
Copyright (c) 2021-2022 Cannlytics and Cannlytics Contributors

Authors: Keegan Skeate <keegan@cannlytics.com>
Created: 11/5/2021
Updated: 12/10/2021
License: <https://github.com/cannlytics/cannlytics-engine/blob/main/LICENSE>

This module contains Metrc variables that are constant.
"""

# The number of minutes in the past to check the Metrc API
# when creating and updating objects and returning observations.
DEFAULT_HISTORY = 5

additive_types = [
    'Fertilizer',
    'Pesticide',
    'Other',
]

adjustment_reasons = [
    {
        'Name': 'API Related Error',
        'RequiresNote': True,
    },
    {
        'Name': 'Drying',
        'RequiresNote': True,
    },
    {
        'Name': 'Mandatory State Destruction',
        'RequiresNote': True,
    },
    {
        'Name': 'Theft',
        'RequiresNote': True,
    },
    {
        'Name': 'Typing/Entry Error',
        'RequiresNote': True,
    }
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

batch_types = [
    'Seed',
    'Clone',
]

categories = [
    'Flower & Buds',
    'Immature Plants',
    'Concentrate (Non-Solvent Based) (Count-Volume)',
    'Concentrate (Non-Solvent Based) (Count-Weight)',
    'Concentrate (Weight Based)',
    'Edibles (Count-Volume)',
    'Edibles (Count-Weight)',
    'Extracts (Solvent Based) (Count-Volume)',
    'Extracts (Solvent Based) (Count-Weight)',
    'Flower & Buds',
    'Immature Plants',
    'Kief',
    'Mature Plants',
    'Metered Dose Nasal Spray Products',
    'MMJ Waste',
    'Pre-Roll (Flower Only)',
    'Pre-Roll (Infused)',
    'Pressurized Metered Dose Inhaler Products',
    'Rectal/Vaginal Administration Products (Count-Volume)',
    'Rectal/Vaginal Administration Products (Count-Weight)',
    'Seeds',
    'Shake/Trim',
    'Shake/Trim (by Strain)',
    'Tinctures (Count-Volume)',
    'Tinctures (Count-Weight)',
    'Topicals (Count-Volume)',
    'Topicals (Count-Weight)',
    'Transdermal Patches',
    'Vape Cartridges',
    'Whole Wet Plant',
]

customer_types = [
    'Consumer',
    'Patient',
    'Caregiver',
    'ExternalPatient',
]

item_types = [
    {
        'Name': 'Buds',
        'ProductCategoryType': 'Buds',
        'QuantityType': 'WeightBased',
        'RequiresStrain': True,
        'RequiresItemBrand': False,
        'RequiresAdministrationMethod': False,
        'RequiresUnitCbdPercent': False,
        'RequiresUnitCbdContent': False,
        'RequiresUnitCbdContentDose': False,
        'RequiresUnitThcPercent': False,
        'RequiresUnitThcContent': False,
        'RequiresUnitThcContentDose': False,
        'RequiresUnitVolume': False,
        'RequiresUnitWeight': False,
        'RequiresServingSize': False,
        'RequiresSupplyDurationDays': False,
        'RequiresNumberOfDoses': False,
        'RequiresPublicIngredients': False,
        'RequiresDescription': False,
        'RequiresProductPhotos': 0,
        'RequiresLabelPhotos': 0,
        'RequiresPackagingPhotos': 0,
        'CanContainSeeds': True,
        'CanBeRemediated': True
    },
    {
        'Name': 'Immature Plants',
        'ProductCategoryType': 'Plants',
        'QuantityType': 'CountBased',
        'RequiresStrain': True,
        'RequiresItemBrand': False,
        'RequiresAdministrationMethod': False,
        'RequiresUnitCbdPercent': False,
        'RequiresUnitCbdContent': False,
        'RequiresUnitCbdContentDose': False,
        'RequiresUnitThcPercent': False,
        'RequiresUnitThcContent': False,
        'RequiresUnitThcContentDose': False,
        'RequiresUnitVolume': False,
        'RequiresUnitWeight': False,
        'RequiresServingSize': False,
        'RequiresSupplyDurationDays': False,
        'RequiresNumberOfDoses': False,
        'RequiresPublicIngredients': False,
        'RequiresDescription': False,
        'RequiresProductPhotos': 0,
        'RequiresLabelPhotos': 0,
        'RequiresPackagingPhotos': 0,
        'CanContainSeeds': True,
        'CanBeRemediated': False
    },
    {
        'Name': 'Infused',
        'ProductCategoryType': 'InfusedEdible',
        'QuantityType': 'CountBased',
        'RequiresStrain': False,
        'RequiresItemBrand': False,
        'RequiresAdministrationMethod': False,
        'RequiresUnitCbdPercent': False,
        'RequiresUnitCbdContent': False,
        'RequiresUnitCbdContentDose': False,
        'RequiresUnitThcPercent': False,
        'RequiresUnitThcContent': True,
        'RequiresUnitThcContentDose': False,
        'RequiresUnitVolume': False,
        'RequiresUnitWeight': True,
        'RequiresServingSize': False,
        'RequiresSupplyDurationDays': False,
        'RequiresNumberOfDoses': False,
        'RequiresPublicIngredients': False,
        'RequiresDescription': False,
        'RequiresProductPhotos': 0,
        'RequiresLabelPhotos': 0,
        'RequiresPackagingPhotos': 0,
        'CanContainSeeds': False,
        'CanBeRemediated': True
    },
    {
        'Name': 'Infused Liquid',
        'ProductCategoryType': 'InfusedEdible',
        'QuantityType': 'CountBased',
        'RequiresStrain': False,
        'RequiresItemBrand': False,
        'RequiresAdministrationMethod': False,
        'RequiresUnitCbdPercent': False,
        'RequiresUnitCbdContent': False,
        'RequiresUnitCbdContentDose': False,
        'RequiresUnitThcPercent': False,
        'RequiresUnitThcContent': True,
        'RequiresUnitThcContentDose': False,
        'RequiresUnitVolume': True,
        'RequiresUnitWeight': False,
        'RequiresServingSize': False,
        'RequiresSupplyDurationDays': False,
        'RequiresNumberOfDoses': False,
        'RequiresPublicIngredients': False,
        'RequiresDescription': False,
        'RequiresProductPhotos': 0,
        'RequiresLabelPhotos': 0,
        'RequiresPackagingPhotos': 0,
        'CanContainSeeds': False,
        'CanBeRemediated': True
    }
]

growth_phases = [
    'Young',
    'Vegetative',
    'Flowering',
]

# TODO: Waste types vary by state...
# harvest_waste_types = [
#     'Plant Material',
#     'Fibrous',
#     'Root Ball',
# ]
# harvest_waste_types = [
#     'MMJ Waste',
#     'Waste',
# ]
waste_types = {
    'ca': ['Plant Material'],
}

location_types = [
    {
        'Id': 1,
        'Name': 'Default',
        'ForPlantBatches': True,
        'ForPlants': True,
        'ForHarvests': True,
        'ForPackages': True,
    },
    {
        'Id': 2,
        'Name': 'Planting',
        'ForPlantBatches': True,
        'ForPlants': True,
        'ForHarvests': False,
        'ForPackages': False,
    },
    {
        'Id': 3,
        'Name': 'Packing',
        'ForPlantBatches': False,
        'ForPlants': False,
        'ForHarvests': False,
        'ForPackages': True,
    },
]

package_types = [
    'Product',
    'ImmaturePlant',
    'VegetativePlant',
    'PlantWaste',
    'HarvestWaste',
]

parameters = {
    'license_number': 'licenseNumber',
    'start': 'lastModifiedStart',
    'end': 'lastModifiedEnd',
    'sales_start': 'salesDateStart',
    'sales_end': 'salesDateEnd',
    'package_id': 'packageId',
    'from_mother': 'isFromMotherPlant',
    'source': 'source',
}

# TODO: Rejection reasons vary by state...
# rejection_types = {}

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

transfer_statuses = [
    'Shipped',
    'Rejected',
    'Accepted',
    'Returned',
]

# TODO: Transfer types vary by state...
transfer_types = [
    {
        'Name': 'Affiliated Transfer',
        'ForLicensedShipments': True,
        'ForExternalIncomingShipments': False,
        'ForExternalOutgoingShipments': False,
        'RequiresDestinationGrossWeight': False,
        'RequiresPackagesGrossWeight': False,
    },
    {
        'Name': 'Beginning Inventory Transfer',
        'ForLicensedShipments': False,
        'ForExternalIncomingShipments': True,
        'ForExternalOutgoingShipments': False,
        'RequiresDestinationGrossWeight': False,
        'RequiresPackagesGrossWeight': False,
    },
    {
        'Name': 'Lab Sample Transfer',
        'ForLicensedShipments': True,
        'ForExternalIncomingShipments': False,
        'ForExternalOutgoingShipments': False,
        'RequiresDestinationGrossWeight': False,
        'RequiresPackagesGrossWeight': False,
    },
    {
        'Name': 'Unaffiliated (Wholesale) Transfer',
        'ForLicensedShipments': True,
        'ForExternalIncomingShipments': False,
        'ForExternalOutgoingShipments': False,
        'RequiresDestinationGrossWeight': False,
        'RequiresPackagesGrossWeight': False,
    },
    {
        'Name': 'Waste Disposal',
        'ForLicensedShipments': True,
        'ForExternalIncomingShipments': False,
        'ForExternalOutgoingShipments': False,
        'RequiresDestinationGrossWeight': False,
        'RequiresPackagesGrossWeight': False,
    }
]

units = [
    {
        'QuantityType': 'CountBased',
        'Name': 'Each',
        'Abbreviation': 'ea',
    },
    {
        'QuantityType': 'WeightBased',
        'Name': 'Ounces',
        'Abbreviation': 'oz',
    },
    {
        'QuantityType': 'WeightBased',
        'Name': 'Pounds',
        'Abbreviation': 'lb',
    },
    {
        'QuantityType': 'WeightBased',
        'Name': 'Grams',
        'Abbreviation': 'g',
    },
    {
        'QuantityType': 'WeightBased',
        'Name': 'Milligrams',
        'Abbreviation': 'mg',
    },
    {
        'QuantityType': 'WeightBased',
        'Name': 'Kilograms',
        'Abbreviation': 'kg',
    },
]

waste_methods = [
    {'Name': 'Grinder'},
    {'Name': 'Compost'},
]

waste_reasons = [
    {
        'Name': 'Disease/Infestation',
        'RequiresNote': True,
    },
    {
        'Name': 'Mother Plant Destruction',
        'RequiresNote': True,
    },
    {
        'Name': 'Trimming/Pruning',
        'RequiresNote': False,
    }
]

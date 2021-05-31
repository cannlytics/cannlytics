"""
Inventory Views | Cannlytics API
Created: 4/21/2021

API to interface with inventory.
"""

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response


@api_view(['GET', 'POST'])
def inventory(request, format=None):
    """Get, create, or update inventory."""

    if request.method == 'GET':
        return Response({'error': 'not_implemented'}, content_type='application/json')

    elif request.method == 'POST':

        return Response({'error': 'not_implemented'}, content_type='application/json')

        # Return an error if no author is specified.
        # error_message = 'Unknown error, please notify <support@cannlytics.com>'
        # return Response(
        #     {'error': error_message},
        #     content_type='application/json',
        #     status=status.HTTP_400_BAD_REQUEST
        # )


#------------------------------------------------------------------
# Items ✓
#------------------------------------------------------------------

# # Create an item using: POST /items/v1/create
# item_name = 'New Old-Time Moonshine Teenth'
# item = Item.create_from_json(track, cultivator.license_number, {
#     'ItemCategory': 'Flower & Buds',
#     'Name': item_name,
#     'UnitOfMeasure': 'Ounces',
#     'Strain': strain_name,
# })

# # Create additional products for future use.
# item = Item.create_from_json(track, cultivator.license_number, {
#     'ItemCategory': 'Shake/Trim',
#     'Name': 'New Old-Time Moonshine Shake',
#     'UnitOfMeasure': 'Grams',
#     'Strain': strain_name,
# })


# # Get the item's UID.
# new_item = None
# items = track.get_items(license_number=cultivator.license_number)
# for i in items:
#     print(i.name, '|', i.product_category_name)
#     if i.name == item_name:
#         new_item = i

# # Change the Unit Of Measure Type using: POST /items/v1/update
# new_item.update(unit_of_measure='Grams')

# # View the item using: GET /Items/v1/{id}
# traced_item = track.get_items(uid=new_item.id, license_number=cultivator.license_number)
# print('Successfully created, updated, and retrieved item:')
# print(traced_item.id, '|', traced_item.unit_of_measure)

# # Create items used for batches.
# clone = Item.create_from_json(track, cultivator.license_number, {
#     'ItemCategory': 'Seeds',
#     'Name': 'New Old-Time Moonshine Mature Plants',
#     'UnitOfMeasure': 'Each',
#     'Strain': strain_name,
# })

# # Get the clone for future use.
# clone_uid = '12324'
# clone_item = track.get_items(uid=clone_uid, license_number=cultivator.license_number)

#------------------------------------------------------------------
# Packages ✓
#------------------------------------------------------------------

# Step 1 Using the Package created in Harvest Step 1 OR create a
# package from an existing package that you have found.
# Create a package from another package using: POST /packages/v1/create

# Get the package created earlier.
# packs = track.get_packages(license_number=cultivator.license_number)
# package_id = '13801'
# traced_package = track.get_packages(
#     uid=package_id,
#     license_number=cultivator.license_number
# )

# new_package_tag = 'YOUR_SECOND_PACKAGE_TAG'
# new_package_data = {
#     'Tag': new_package_tag,
#     'Location': 'Warehouse',
#     'Item': 'New Old-Time Moonshine Teenth',
#     'Quantity': 1.75,
#     'UnitOfMeasure': 'Grams',
#     # 'PatientLicenseNumber': 'X00001',
#     'Note': '1st teenth for sale.',
#     # 'IsProductionBatch': False,
#     # 'ProductionBatchNumber': None,
#     # 'IsDonation': False,
#     # 'ProductRequiresRemediation': False,
#     # 'UseSameItem': True,
#     'ActualDate': today,
#     'Ingredients': [
#         {
#             'Package': traced_package.label,
#             'Quantity': 1.75,
#             'UnitOfMeasure': 'Grams'
#         }
#     ]
# }
# traced_package.create_package(new_package_data)
# new_package = track.get_packages(label=new_package_tag, license_number=cultivator.license_number)
# print(new_package.last_modified)

# # Step 2 Using the new package created in Packages Step 1
# # change the item of a package using: POST/packages/v1/change/item
# new_package.change_item(item_name='New Old-Time Moonshine Kief')
# new_package = track.get_packages(uid=new_package.id, license_number=cultivator.license_number)
# print(new_package.last_modified)

# # Step 3 Using the new package created in Packages Step 1
# # adjust the weight to 0 using: POST/packages/v1/adjust
# adjustment = {
#     'Label': new_package_tag,
#     'Quantity': -1.75,
#     'UnitOfMeasure': 'Grams',
#     'AdjustmentReason': 'Drying',
#     'AdjustmentDate': today,
#     'ReasonNote': None
# }
# new_package.adjust(weight=-1.75, note='Look ma, no weight!')
# new_package = track.get_packages(uid=new_package.id, license_number=cultivator.license_number)
# print(new_package.last_modified)

# # Step 4 Using the new package created in Packages Step 1
# #  Finish a package using: POST/packages/v1/finish
# new_package.finish()
# new_package = track.get_packages(uid=new_package.id, license_number=cultivator.license_number)
# print(new_package.last_modified)

# # Step 5 Using the new package created in Packages Step 1
# # Unfinish a package using: POST/packages/v1/unfinish
# new_package.unfinish()
# new_package = track.get_packages(uid=new_package.id, license_number=cultivator.license_number)
# print(new_package.last_modified)

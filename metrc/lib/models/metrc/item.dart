// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 2/27/2023
// Updated: 3/18/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

/// Model representing an item.
class Item {
  // Initialization.
  const Item({
    this.id,
    this.name,
    this.productCategoryName,
    this.productCategoryType,
    this.quantityType,
    this.unitOfMeasureName,
    this.approvalStatus,
    this.approvalStatusDateTime,
    this.defaultLabTestingState,
    this.isUsed,
    this.strainId,
    this.strainName,
    this.administrationMethod = '',
    this.description = '',
    this.numberOfDoses = 0,
    this.publicIngredients,
    this.servingSize = 0,
    this.supplyDurationDays = 0,
    this.unitCbdContent = 0,
    this.unitCbdContentDose = 0,
    this.unitCbdContentDoseUnitOfMeasureName = '',
    this.unitCbdContentUnitOfMeasureName = '',
    this.unitCbdPercent = 0,
    this.unitQuantity = 0,
    this.unitQuantityUnitOfMeasureName = '',
    this.unitThcContent = 0,
    this.unitThcContentDose = 0,
    this.unitThcContentDoseUnitOfMeasureName = '',
    this.unitThcContentUnitOfMeasureName = '',
    this.unitThcPercent = 0,
    this.unitVolume = 0,
    this.unitVolumeUnitOfMeasureName = '',
    this.unitWeight = 0,
    this.unitWeightUnitOfMeasureName = '',
  });
  // Properties.
  final String? id;
  final String? name;
  final String? productCategoryName;
  final String? productCategoryType;
  final String? quantityType;
  final String? unitOfMeasureName;
  final String? approvalStatus;
  final String? approvalStatusDateTime;
  final String? defaultLabTestingState;
  final bool? isUsed;
  final String? strainId;
  final String? strainName;
  final String? administrationMethod;
  final String? description;
  final int? numberOfDoses;
  final List<String>? publicIngredients;
  final int? servingSize;
  final int? supplyDurationDays;
  final double? unitCbdContent;
  final double? unitCbdContentDose;
  final String? unitCbdContentDoseUnitOfMeasureName;
  final String? unitCbdContentUnitOfMeasureName;
  final double? unitCbdPercent;
  final int? unitQuantity;
  final String unitQuantityUnitOfMeasureName;
  final double? unitThcContent;
  final double? unitThcContentDose;
  final String? unitThcContentDoseUnitOfMeasureName;
  final String? unitThcContentUnitOfMeasureName;
  final double? unitThcPercent;
  final double? unitVolume;
  final String? unitVolumeUnitOfMeasureName;
  final double? unitWeight;
  final String? unitWeightUnitOfMeasureName;
  // Create model.
  factory Item.fromMap(Map<String, dynamic> data) {
    return Item(
      id: data['id'].toString(),
      name: data['name'] ?? '',
      productCategoryName: data['product_category_name'] ?? '',
      productCategoryType: data['product_category_type'] ?? '',
      quantityType: data['quantity_type'] ?? '',
      unitOfMeasureName: data['unit_of_measure_name'] ?? '',
      approvalStatus: data['approval_status'] ?? '',
      approvalStatusDateTime: data['approval_status_date_time'] ?? '',
      defaultLabTestingState: data['default_lab_testing_state'] ?? '',
      isUsed: data['is_used'] as bool,
      strainId: data['strain_id'].toString(),
      strainName: data['strain_name'] ?? '',
      administrationMethod: data['administration_method'] ?? '',
      description: data['description'] ?? '',
      numberOfDoses: data['number_of_doses'] ?? 0,
      publicIngredients: (data['public_ingredients'] as List).cast<String>(),
      servingSize: data['serving_size'] ?? 0,
      supplyDurationDays: data['supply_duration_days'] ?? 0,
      unitCbdContent: data['unit_cbd_content'] ?? 0.0,
      unitCbdContentDose: data['unit_cbd_content_dose'] ?? 0.0,
      unitCbdContentDoseUnitOfMeasureName:
          data['unit_cbd_content_dose_unit_of_measure_name'] ?? '',
      unitCbdContentUnitOfMeasureName:
          data['unit_cbd_content_unit_of_measure_name'] ?? '',
      unitCbdPercent: data['unit_cbd_percent'] ?? 0.0,
      unitQuantity: data['unit_quantity'] ?? 0,
      unitQuantityUnitOfMeasureName:
          data['unit_quantity_unit_of_measure_name'] ?? '',
      unitThcContent: data['unit_thc_content'] ?? 0.0,
      unitThcContentDose: data['unit_thc_content_dose'] ?? 0.0,
      unitThcContentDoseUnitOfMeasureName:
          data['unit_thc_content_dose_unit_of_measure_name'] ?? '',
      unitThcContentUnitOfMeasureName:
          data['unit_thc_content_unit_of_measure_name'] ?? '',
      unitThcPercent: data['unit_thc_percent'] ?? 0.0,
      unitVolume: data['unit_volume'] ?? 0.0,
      unitVolumeUnitOfMeasureName:
          data['unit_volume_unit_of_measure_name'] ?? '',
      unitWeight: data['unit_weight'] ?? 0.0,
      unitWeightUnitOfMeasureName:
          data['unit_weight_unit_of_measure_name'] ?? '',
    );
  }
  // Create JSON.
  Map<String, dynamic> toMap() {
    return <String, dynamic>{
      'id': id,
      'name': name,
      'product_category_name': productCategoryName,
      'product_category_type': productCategoryType,
      'quantity_type': quantityType,
      'unit_of_measure_name': unitOfMeasureName,
      'approval_status': approvalStatus,
      'approval_status_date_time': approvalStatusDateTime,
      'default_lab_testing_state': defaultLabTestingState,
      'is_used': isUsed,
      'strain_id': strainId,
      'strain_name': strainName,
      'administration_method': administrationMethod,
      'description': description,
      'number_of_doses': numberOfDoses,
      'public_ingredients': publicIngredients,
      'serving_size': servingSize,
      'supply_duration_days': supplyDurationDays,
      'unit_cbd_content': unitCbdContent,
      'unit_cbd_content_dose': unitCbdContentDose,
      'unit_cbd_content_dose_unit_of_measure_name':
          unitCbdContentDoseUnitOfMeasureName,
      'unit_cbd_content_unit_of_measure_name': unitCbdContentUnitOfMeasureName,
      'unit_cbd_percent': unitCbdPercent,
      'unit_quantity': unitQuantity,
      'unit_quantity_unit_of_measure_name': unitQuantityUnitOfMeasureName,
      'unit_thc_content': unitThcContent,
      'unit_thc_content_dose': unitThcContentDose,
      'unit_thc_content_dose_unit_of_measure_name':
          unitThcContentDoseUnitOfMeasureName,
      'unit_thc_content_unit_of_measure_name': unitThcContentUnitOfMeasureName,
      'unit_thc_percent': unitThcPercent,
      'unit_volume': unitVolume,
      'unit_volume_unit_of_measure_name': unitVolumeUnitOfMeasureName,
      'unit_weight': unitWeight,
      'unit_weight_unit_of_measure_name': unitWeightUnitOfMeasureName,
    };
  }

  // // Create Item.
  // Future<void> create() async {
  //   // Call an API or database to create a new item.
  //   // await MetrcService.createItem(this.toMap());
  // }
  // // Update Item.
  // Future<void> update() async {
  //   // Call an API or database to update the existing item.
  //   // await MetrcService.updateItem(this.id, this.toMap());
  // }
  // // Delete Item.
  // Future<void> delete() async {
  //   // Call an API or database to delete the existing item.
  //   // await MetrcService.deleteItem(this.id);
  // }
}

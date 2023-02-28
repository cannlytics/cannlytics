// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 2/27/2023
// Updated: 2/27/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

import 'package:cannlytics_app/services/metrc_service.dart';

/// Model representing an item.
class Item {
  // Initialization.
  const Item({
    required this.id,
    required this.name,
    required this.productCategoryName,
    required this.productCategoryType,
    required this.quantityType,
    required this.unitOfMeasureName,
    required this.approvalStatus,
    required this.approvalStatusDateTime,
    required this.defaultLabTestingState,
    required this.isUsed,
    required this.strainId,
    required this.strainName,
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
  final int id;
  final String name;
  final String productCategoryName;
  final String productCategoryType;
  final String quantityType;
  final String unitOfMeasureName;
  final String approvalStatus;
  final DateTime approvalStatusDateTime;
  final String defaultLabTestingState;
  final bool isUsed;
  final int strainId;
  final String strainName;
  final String administrationMethod;
  final String description;
  final int numberOfDoses;
  final List<String>? publicIngredients;
  final int servingSize;
  final int supplyDurationDays;
  final double unitCbdContent;
  final double unitCbdContentDose;
  final String unitCbdContentDoseUnitOfMeasureName;
  final String unitCbdContentUnitOfMeasureName;
  final double unitCbdPercent;
  final int unitQuantity;
  final String unitQuantityUnitOfMeasureName;
  final double unitThcContent;
  final double unitThcContentDose;
  final String unitThcContentDoseUnitOfMeasureName;
  final String unitThcContentUnitOfMeasureName;
  final double unitThcPercent;
  final double unitVolume;
  final String unitVolumeUnitOfMeasureName;
  final double unitWeight;
  final String unitWeightUnitOfMeasureName;
  // Create model.
  factory Item.fromMap(Map<String, dynamic> data, int uid) {
    return Item(
      id: uid,
      name: data['name'] as String,
      productCategoryName: data['product_category_name'] as String,
      productCategoryType: data['product_category_type'] as String,
      quantityType: data['quantity_type'] as String,
      unitOfMeasureName: data['unit_of_measure_name'] as String,
      approvalStatus: data['approval_status'] as String,
      approvalStatusDateTime:
          DateTime.parse(data['approval_status_date_time'] as String),
      defaultLabTestingState: data['default_lab_testing_state'] as String,
      isUsed: data['is_used'] as bool,
      strainId: data['strain_id'] as int,
      strainName: data['strain_name'] as String,
      administrationMethod: data['administration_method'] as String,
      description: data['description'] as String,
      numberOfDoses: data['number_of_doses'] as int,
      publicIngredients: (data['public_ingredients'] as List)?.cast<String>(),
      servingSize: data['serving_size'] as int,
      supplyDurationDays: data['supply_duration_days'] as int,
      unitCbdContent: data['unit_cbd_content'] as double,
      unitCbdContentDose: data['unit_cbd_content_dose'] as double,
      unitCbdContentDoseUnitOfMeasureName:
          data['unit_cbd_content_dose_unit_of_measure_name'] as String,
      unitCbdContentUnitOfMeasureName:
          data['unit_cbd_content_unit_of_measure_name'] as String,
      unitCbdPercent: data['unit_cbd_percent'] as double,
      unitQuantity: data['unit_quantity'] as int,
      unitQuantityUnitOfMeasureName:
          data['unit_quantity_unit_of_measure_name'] as String,
      unitThcContent: data['unit_thc_content'] as double,
      unitThcContentDose: data['unit_thc_content_dose'] as double,
      unitThcContentDoseUnitOfMeasureName:
          data['unit_thc_content_dose_unit_of_measure_name'] as String,
      unitThcContentUnitOfMeasureName:
          data['unit_thc_content_unit_of_measure_name'] as String,
      unitThcPercent: data['unit_thc_percent'] as double,
      unitVolume: data['unit_volume'] as double,
      unitVolumeUnitOfMeasureName:
          data['unit_volume_unit_of_measure_name'] as String,
      unitWeight: data['unit_weight'] as double,
      unitWeightUnitOfMeasureName:
          data['unit_weight_unit_of_measure_name'] as String,
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
      'approval_status_date_time': approvalStatusDateTime.toIso8601String(),
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

  // Create Item.
  Future<void> create() async {
    // Call an API or database to create a new item.
    // await MetrcService.createItem(this.toMap());
  }
  // Update Item.
  Future<void> update() async {
    // Call an API or database to update the existing item.
    // await MetrcService.updateItem(this.id, this.toMap());
  }
  // Delete Item.
  Future<void> delete() async {
    // Call an API or database to delete the existing item.
    // await MetrcService.deleteItem(this.id);
  }
}

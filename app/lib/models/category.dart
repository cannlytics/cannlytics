// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 2/25/2023
// Updated: 2/25/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

typedef CategoryId = String;

// Model representing a product category.
class Category {
  const Category({
    required this.name,
    required this.productCategoryType,
    required this.quantityType,
    required this.requiresStrain,
    required this.requiresItemBrand,
    required this.requiresAdministrationMethod,
    required this.requiresUnitCbdPercent,
    required this.requiresUnitCbdContent,
    required this.requiresUnitCbdContentDose,
    required this.requiresUnitThcPercent,
    required this.requiresUnitThcContent,
    required this.requiresUnitThcContentDose,
    required this.requiresUnitVolume,
    required this.requiresUnitWeight,
    required this.requiresServingSize,
    required this.requiresSupplyDurationDays,
    required this.requiresNumberOfDoses,
    required this.requiresPublicIngredients,
    required this.requiresDescription,
    required this.requiresProductPhotos,
    required this.requiresLabelPhotos,
    required this.requiresPackagingPhotos,
    required this.canContainSeeds,
    required this.canBeRemediated,
    required this.canBeDestroyed,
  });

  // Properties.
  final String name;
  final String productCategoryType;
  final String quantityType;
  final bool requiresStrain;
  final bool requiresItemBrand;
  final bool requiresAdministrationMethod;
  final bool requiresUnitCbdPercent;
  final bool requiresUnitCbdContent;
  final bool requiresUnitCbdContentDose;
  final bool requiresUnitThcPercent;
  final bool requiresUnitThcContent;
  final bool requiresUnitThcContentDose;
  final bool requiresUnitVolume;
  final bool requiresUnitWeight;
  final bool requiresServingSize;
  final bool requiresSupplyDurationDays;
  final bool requiresNumberOfDoses;
  final bool requiresPublicIngredients;
  final bool requiresDescription;
  final int requiresProductPhotos;
  final int requiresLabelPhotos;
  final int requiresPackagingPhotos;
  final bool canContainSeeds;
  final bool canBeRemediated;
  final bool canBeDestroyed;

  factory Category.fromMap(Map<String, dynamic> data) {
    return Category(
      name: data['name'] as String,
      productCategoryType: data['product_category_type'] as String,
      quantityType: data['quantity_type'] as String,
      requiresStrain: data['requires_strain'] as bool,
      requiresItemBrand: data['requires_item_brand'] as bool,
      requiresAdministrationMethod:
          data['requires_administration_method'] as bool,
      requiresUnitCbdPercent: data['requires_unit_cbd_percent'] as bool,
      requiresUnitCbdContent: data['requires_unit_cbd_content'] as bool,
      requiresUnitCbdContentDose:
          data['requires_unit_cbd_content_dose'] as bool,
      requiresUnitThcPercent: data['requires_unit_thc_percent'] as bool,
      requiresUnitThcContent: data['requires_unit_thc_content'] as bool,
      requiresUnitThcContentDose:
          data['requires_unit_thc_content_dose'] as bool,
      requiresUnitVolume: data['requires_unit_volume'] as bool,
      requiresUnitWeight: data['requires_unit_weight'] as bool,
      requiresServingSize: data['requires_serving_size'] as bool,
      requiresSupplyDurationDays: data['requires_supply_duration_days'] as bool,
      requiresNumberOfDoses: data['requires_number_of_doses'] as bool,
      requiresPublicIngredients: data['requires_public_ingredients'] as bool,
      requiresDescription: data['requires_description'] as bool,
      requiresProductPhotos: data['requires_product_photos'] as int,
      requiresLabelPhotos: data['requires_label_photos'] as int,
      requiresPackagingPhotos: data['requires_packaging_photos'] as int,
      canContainSeeds: data['can_contain_seeds'] as bool,
      canBeRemediated: data['can_be_remediated'] as bool,
      canBeDestroyed: data['can_be_destroyed'] as bool,
    );
  }

  Map<String, dynamic> toMap() {
    return <String, dynamic>{
      'name': name,
      'product_category_type': productCategoryType,
      'quantity_type': quantityType,
      'requires_strain': requiresStrain,
      'requires_item_brand': requiresItemBrand,
      'requires_administration_method': requiresAdministrationMethod,
      'requires_unit_cbd_percent': requiresUnitCbdPercent,
      'requires_unit_cbd_content': requiresUnitCbdContent,
      'requires_unit_cbd_content_dose': requiresUnitCbdContentDose,
      'requires_unit_thc_percent': requiresUnitThcPercent,
      'requires_unit_thc_content': requiresUnitThcContent,
      'requires_unit_thc_content_dose': requiresUnitThcContentDose,
      'requires_unit_volume': requiresUnitVolume,
      'requires_unit_weight': requiresUnitWeight,
      'requires_serving_size': requiresServingSize,
      'requires_supply_duration_days': requiresSupplyDurationDays,
      'requires_number_of_doses': requiresNumberOfDoses,
      'requires_public_ingredients': requiresPublicIngredients,
      'requires_description': requiresDescription,
      'requires_product_photos': requiresProductPhotos,
      'requires_label_photos': requiresLabelPhotos,
      'requires_packaging_photos': requiresPackagingPhotos,
      'can_contain_seeds': canContainSeeds,
      'can_be_remediated': canBeRemediated,
      'can_be_destroyed': canBeDestroyed,
    };
  }
}

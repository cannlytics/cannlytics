// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 2/26/2023
// Updated: 2/26/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Project imports:
import 'package:cannlytics_app/models/metrc/strain.dart';

typedef PlantId = String;

/// Model representing a plant.
class Plant {
// Initialization.
  const Plant({
    required this.id,
    required this.destroyedByUserName,
    required this.destroyedDate,
    required this.destroyedNote,
    required this.floweringDate,
    required this.growthPhase,
    required this.harvestCount,
    required this.harvestedDate,
    required this.harvestedUnitOfWeightAbbreviation,
    required this.harvestedUnitOfWeightName,
    required this.harvestedWetWeight,
    required this.harvestId,
    required this.isOnHold,
    required this.isOnTrip,
    required this.label,
    required this.lastModified,
    required this.locationId,
    required this.locationName,
    required this.locationTypeName,
    required this.patientLicenseNumber,
    required this.plantBatchId,
    required this.plantBatchName,
    required this.plantBatchTypeId,
    required this.plantBatchTypeName,
    required this.plantedDate,
    required this.state,
    required this.strainId,
    required this.strainName,
    required this.vegetativeDate,
  });

// Properties.
  final PlantId id;
  final String destroyedByUserName;
  final String destroyedDate;
  final String? destroyedNote;
  final String? floweringDate;
  final String growthPhase;
  final int harvestCount;
  final String? harvestedDate;
  final String? harvestedUnitOfWeightAbbreviation;
  final String? harvestedUnitOfWeightName;
  final double? harvestedWetWeight;
  final int? harvestId;
  final bool isOnHold;
  final bool isOnTrip;
  final String label;
  final String lastModified;
  final int locationId;
  final String locationName;
  final String? locationTypeName;
  final String? patientLicenseNumber;
  final int plantBatchId;
  final String plantBatchName;
  final int plantBatchTypeId;
  final String plantBatchTypeName;
  final String plantedDate;
  final String state;
  final StrainId strainId;
  final String strainName;
  final String? vegetativeDate;

// Create model.
  factory Plant.fromMap(Map<String, dynamic> data) {
    return Plant(
      id: data['id'] as PlantId,
      destroyedByUserName: data['destroyed_by_user_name'] as String,
      destroyedDate: data['destroyed_date'] as String,
      destroyedNote: data['destroyed_note'] as String?,
      floweringDate: data['flowering_date'] as String?,
      growthPhase: data['growth_phase'] as String,
      harvestCount: data['harvest_count'] as int,
      harvestedDate: data['harvested_date'] as String?,
      harvestedUnitOfWeightAbbreviation:
          data['harvested_unit_of_weight_abbreviation'] as String?,
      harvestedUnitOfWeightName:
          data['harvested_unit_of_weight_name'] as String?,
      harvestedWetWeight: data['harvested_wet_weight'] as double?,
      harvestId: data['harvest_id'] as int?,
      isOnHold: data['is_on_hold'] as bool,
      isOnTrip: data['is_on_trip'] as bool,
      label: data['label'] as String,
      lastModified: data['last_modified'] as String,
      locationId: data['location_id'] as int,
      locationName: data['location_name'] as String,
      locationTypeName: data['location_type_name'] as String?,
      patientLicenseNumber: data['patient_license_number'] as String?,
      plantBatchId: data['plant_batch_id'] as int,
      plantBatchName: data['plant_batch_name'] as String,
      plantBatchTypeId: data['plant_batch_type_id'] as int,
      plantBatchTypeName: data['plant_batch_type_name'] as String,
      plantedDate: data['planted_date'] as String,
      state: data['state'] as String,
      strainId: data['strain_id'] as StrainId,
      strainName: data['strain_name'] as String,
      vegetativeDate: data['vegetative_date'] as String?,
    );
  }

  Map<String, dynamic> toMap() {
    return <String, dynamic>{
      'destroyed_by_user_name': destroyedByUserName,
      'destroyed_date': destroyedDate,
      'destroyed_note': destroyedNote,
      'flowering_date': floweringDate,
      'growth_phase': growthPhase,
      'harvest_count': harvestCount,
      'harvest_id': harvestId,
      'harvested_date': harvestedDate,
      'harvested_unit_of_weight_abbreviation':
          harvestedUnitOfWeightAbbreviation,
      'harvested_unit_of_weight_name': harvestedUnitOfWeightName,
      'harvested_wet_weight': harvestedWetWeight,
      'id': id.toString(),
      'is_on_hold': isOnHold,
      'is_on_trip': isOnTrip,
      'label': label,
      'last_modified': lastModified,
      'location_id': locationId,
      'location_name': locationName,
      'location_type_name': locationTypeName,
      'patient_license_number': patientLicenseNumber,
      'plant_batch_id': plantBatchId,
      'plant_batch_name': plantBatchName,
      'plant_batch_type_id': plantBatchTypeId,
      'plant_batch_type_name': plantBatchTypeName,
      'planted_date': plantedDate,
      'state': state,
      'strain_id': strainId.toString(),
      'strain_name': strainName,
      'vegetative_date': vegetativeDate
    };
  }

  // TODO: Create planting.

  // TODO: Create plant package.

  // TODO: Flower plant.

  // TODO: Move plant.

  // TODO: Destroy plant.

  // TODO: Manicure plant.

  // TODO: Harvest plant.
}

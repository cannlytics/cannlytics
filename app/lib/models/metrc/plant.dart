// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 2/26/2023
// Updated: 3/16/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Project imports:
import 'package:cannlytics_app/models/metrc/strain.dart';

typedef PlantId = String;

/// Model representing a plant.
class Plant {
// Initialization.
  const Plant({
    required this.id,
    this.destroyedByUserName,
    this.destroyedDate,
    this.destroyedNote,
    this.floweringDate,
    this.growthPhase,
    this.harvestCount,
    this.harvestedDate,
    this.harvestedUnitOfWeightAbbreviation,
    this.harvestedUnitOfWeightName,
    this.harvestedWetWeight,
    this.harvestId,
    this.isOnHold,
    this.isOnTrip,
    this.label,
    this.lastModified,
    this.locationId,
    this.locationName,
    this.locationTypeName,
    this.patientLicenseNumber,
    this.plantBatchId,
    this.plantBatchName,
    this.plantBatchTypeId,
    this.plantBatchTypeName,
    this.plantedDate,
    this.state,
    this.strainId,
    this.strainName,
    this.vegetativeDate,
  });

// Properties.
  final PlantId id;
  final String? destroyedByUserName;
  final String? destroyedDate;
  final String? destroyedNote;
  final String? floweringDate;
  final String? growthPhase;
  final int? harvestCount;
  final String? harvestedDate;
  final String? harvestedUnitOfWeightAbbreviation;
  final String? harvestedUnitOfWeightName;
  final double? harvestedWetWeight;
  final String? harvestId;
  final bool? isOnHold;
  final bool? isOnTrip;
  final String? label;
  final String? lastModified;
  final String? locationId;
  final String? locationName;
  final String? locationTypeName;
  final String? patientLicenseNumber;
  final String? plantBatchId;
  final String? plantBatchName;
  final String? plantBatchTypeId;
  final String? plantBatchTypeName;
  final String? plantedDate;
  final String? state;
  final StrainId? strainId;
  final String? strainName;
  final String? vegetativeDate;

// Create model.
  factory Plant.fromMap(Map<String, dynamic> data) {
    return Plant(
      id: data['id'].toString(),
      destroyedByUserName: data['destroyed_by_user_name'] ?? '',
      destroyedDate: data['destroyed_date'] ?? '',
      destroyedNote: data['destroyed_note'] ?? '',
      floweringDate: data['flowering_date'] ?? '',
      growthPhase: data['growth_phase'] ?? '',
      harvestCount: data['harvest_count'] ?? 0,
      harvestedDate: data['harvested_date'] ?? '',
      harvestedUnitOfWeightAbbreviation:
          data['harvested_unit_of_weight_abbreviation'] ?? '',
      harvestedUnitOfWeightName: data['harvested_unit_of_weight_name'] ?? '',
      harvestedWetWeight: data['harvested_wet_weight'] ?? 0.0,
      harvestId: data['harvest_id'].toString(),
      isOnHold: data['is_on_hold'] ?? false,
      isOnTrip: data['is_on_trip'] ?? false,
      label: data['label'] ?? '',
      lastModified: data['last_modified'] ?? '',
      locationId: data['location_id'].toString(),
      locationName: data['location_name'] ?? '',
      locationTypeName: data['location_type_name'] ?? '',
      patientLicenseNumber: data['patient_license_number'] ?? '',
      plantBatchId: data['plant_batch_id'] ?? 0,
      plantBatchName: data['plant_batch_name'] ?? '',
      plantBatchTypeId: data['plant_batch_type_id'] ?? 0,
      plantBatchTypeName: data['plant_batch_type_name'] ?? '',
      plantedDate: data['planted_date'] ?? '',
      state: data['state'] ?? '',
      strainId: data['strain_id'].toString(),
      strainName: data['strain_name'] ?? '',
      vegetativeDate: data['vegetative_date'] ?? '',
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

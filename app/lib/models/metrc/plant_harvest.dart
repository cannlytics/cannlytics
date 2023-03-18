// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 2/27/2023
// Updated: 3/18/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Project imports:
import 'package:cannlytics_app/models/metrc/strain.dart';
import 'package:cannlytics_app/services/metrc_service.dart';

typedef PlantHarvestId = String;

/// Model representing a harvest of cannabis.
class PlantHarvest {
  // Initialization.
  const PlantHarvest({
    this.id,
    this.archivedDate,
    this.currentWeight,
    this.dryingLocationId,
    this.dryingLocationName,
    this.dryingLocationTypeName,
    this.finishedDate,
    this.harvestStartDate,
    this.harvestType,
    this.isOnHold,
    this.isOnTrip,
    this.labTestingState,
    this.labTestingStateDate,
    this.lastModified,
    this.name,
    this.packageCount,
    this.patientLicenseNumber,
    this.plantCount,
    this.sourceStrainCount,
    this.sourceStrainNames,
    this.strains,
    this.totalPackagedWeight,
    this.totalRestoredWeight,
    this.totalWasteWeight,
    this.totalWetWeight,
    this.unitOfWeightName,
  });

  // Properties.
  final PlantHarvestId? id;
  final String? archivedDate;
  final double? currentWeight;
  final int? dryingLocationId;
  final String? dryingLocationName;
  final String? dryingLocationTypeName;
  final String? finishedDate;
  final String? harvestStartDate;
  final String? harvestType;
  final bool? isOnHold;
  final bool? isOnTrip;
  final String? labTestingState;
  final String? labTestingStateDate;
  final String? lastModified;
  final String? name;
  final int? packageCount;
  final String? patientLicenseNumber;
  final int? plantCount;
  final int? sourceStrainCount;
  final List<String>? sourceStrainNames;
  final List<Strain>? strains;
  final double? totalPackagedWeight;
  final double? totalRestoredWeight;
  final double? totalWasteWeight;
  final double? totalWetWeight;
  final String? unitOfWeightName;

  // Create model.
  factory PlantHarvest.fromMap(Map<String, dynamic> data) {
    return PlantHarvest(
      id: data['id'] ?? '',
      archivedDate: data['archived_date'] ?? '',
      currentWeight: data['current_weight'] ?? 0.0,
      dryingLocationId: data['drying_location_id'] ?? 0,
      dryingLocationName: data['drying_location_name'] ?? '',
      dryingLocationTypeName: data['drying_location_type_name'] ?? '',
      finishedDate: data['finished_date'] ?? '',
      harvestStartDate: data['harvest_start_date'] ?? '',
      harvestType: data['harvest_type'] ?? '',
      isOnHold: data['is_on_hold'] ?? false,
      isOnTrip: data['is_on_trip'] ?? false,
      labTestingState: data['lab_testing_state'] ?? '',
      labTestingStateDate: data['lab_testing_state_date'] ?? '',
      lastModified: data['last_modified'] ?? '',
      name: data['name'] ?? '',
      packageCount: data['package_count'] ?? 0,
      patientLicenseNumber: data['patient_license_number'] ?? '',
      plantCount: data['plant_count'] ?? 0,
      sourceStrainCount: data['source_strain_count'] ?? 0,
      sourceStrainNames: data['source_strain_names'] as List<String>,
      strains: data['strains'] as List<Strain>,
      totalPackagedWeight: data['total_packaged_weight'] ?? 0.0,
      totalRestoredWeight: data['total_restored_weight'] ?? 0.0,
      totalWasteWeight: data['total_waste_weight'] ?? 0.0,
      totalWetWeight: data['total_wet_weight'] ?? 0.0,
      unitOfWeightName: data['unit_of_weight_name'] ?? '',
    );
  }

  // Create JSON.
  Map<String, dynamic> toMap() {
    return <String, dynamic>{
      'id': id,
      'archived_date': archivedDate,
      'current_weight': currentWeight,
      'drying_location_id': dryingLocationId,
      'drying_location_name': dryingLocationName,
      'drying_location_type_name': dryingLocationTypeName,
      'finished_date': finishedDate,
      'harvest_start_date': harvestStartDate,
      'harvest_type': harvestType,
      'is_on_hold': isOnHold,
      'is_on_trip': isOnTrip,
      'lab_testing_state': labTestingState,
      'lab_testing_state_date': labTestingStateDate,
      'last_modified': lastModified,
      'name': name,
      'package_count': packageCount,
      'patient_license_number': patientLicenseNumber,
      'plant_count': plantCount,
      'source_strain_count': sourceStrainCount,
      'source_strain_names': sourceStrainNames,
      'strains': strains,
      'total_packaged_weight': totalPackagedWeight,
      'total_restored_weight': totalRestoredWeight,
      'total_waste_weight': totalWasteWeight,
      'total_wet_weight': totalWetWeight,
      'unit_of_weight_name': unitOfWeightName,
    };
  }

  // // Create Harvest.
  // Future<void> create() async {
  //   // Call an API or database to create a new harvest.
  //   // await MetrcService.createHarvest(this.toMap());
  // }

  // // Update Harvest.
  // Future<void> update() async {
  //   // Call an API or database to update the existing harvest.
  //   // await MetrcService.updateHarvest(this.id, this.toMap());
  // }

  // // Delete Harvest.
  // Future<void> delete() async {
  //   // Call an API or database to delete the existing harvest.
  //   // await MetrcService.deleteHarvest(this.id);
  // }
}

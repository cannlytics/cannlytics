// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 2/27/2023
// Updated: 3/9/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Project imports:
import 'package:cannlytics_app/models/metrc/strain.dart';
import 'package:cannlytics_app/services/metrc_service.dart';

typedef HarvestId = String;

/// Model representing a harvest of cannabis.
class Harvest {
  // Initialization.
  const Harvest({
    required this.id,
    required this.archivedDate,
    required this.currentWeight,
    required this.dryingLocationId,
    required this.dryingLocationName,
    required this.dryingLocationTypeName,
    required this.finishedDate,
    required this.harvestStartDate,
    required this.harvestType,
    required this.isOnHold,
    required this.isOnTrip,
    required this.labTestingState,
    required this.labTestingStateDate,
    required this.lastModified,
    required this.name,
    required this.packageCount,
    required this.patientLicenseNumber,
    required this.plantCount,
    required this.sourceStrainCount,
    required this.sourceStrainNames,
    required this.strains,
    required this.totalPackagedWeight,
    required this.totalRestoredWeight,
    required this.totalWasteWeight,
    required this.totalWetWeight,
    required this.unitOfWeightName,
  });

  // Properties.
  final HarvestId id;
  final DateTime archivedDate;
  final double currentWeight;
  final int dryingLocationId;
  final String dryingLocationName;
  final String dryingLocationTypeName;
  final DateTime finishedDate;
  final DateTime harvestStartDate;
  final String harvestType;
  final bool isOnHold;
  final bool isOnTrip;
  final String labTestingState;
  final DateTime labTestingStateDate;
  final DateTime lastModified;
  final String name;
  final int packageCount;
  final String patientLicenseNumber;
  final int plantCount;
  final int sourceStrainCount;
  final List<String> sourceStrainNames;
  final List<Strain> strains;
  final double totalPackagedWeight;
  final double totalRestoredWeight;
  final double totalWasteWeight;
  final double totalWetWeight;
  final String unitOfWeightName;

  // Create model.
  factory Harvest.fromMap(Map<String, dynamic> data) {
    return Harvest(
      id: data['id'] ?? '',
      archivedDate: data['archived_date'] as DateTime,
      currentWeight: data['current_weight'] as double,
      dryingLocationId: data['drying_location_id'] as int,
      dryingLocationName: data['drying_location_name'] as String,
      dryingLocationTypeName: data['drying_location_type_name'] as String,
      finishedDate: data['finished_date'] as DateTime,
      harvestStartDate: data['harvest_start_date'] as DateTime,
      harvestType: data['harvest_type'] as String,
      isOnHold: data['is_on_hold'] as bool,
      isOnTrip: data['is_on_trip'] as bool,
      labTestingState: data['lab_testing_state'] as String,
      labTestingStateDate: data['lab_testing_state_date'] as DateTime,
      lastModified: data['last_modified'] as DateTime,
      name: data['name'] as String,
      packageCount: data['package_count'] as int,
      patientLicenseNumber: data['patient_license_number'] as String,
      plantCount: data['plant_count'] as int,
      sourceStrainCount: data['source_strain_count'] as int,
      sourceStrainNames: data['source_strain_names'] as List<String>,
      strains: data['strains'] as List<Strain>,
      totalPackagedWeight: data['total_packaged_weight'] as double,
      totalRestoredWeight: data['total_restored_weight'] as double,
      totalWasteWeight: data['total_waste_weight'] as double,
      totalWetWeight: data['total_wet_weight'] as double,
      unitOfWeightName: data['unit_of_weight_name'] as String,
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

  // Create Harvest.
  Future<void> create() async {
    // Call an API or database to create a new harvest.
    // await MetrcService.createHarvest(this.toMap());
  }

  // Update Harvest.
  Future<void> update() async {
    // Call an API or database to update the existing harvest.
    // await MetrcService.updateHarvest(this.id, this.toMap());
  }

  // Delete Harvest.
  Future<void> delete() async {
    // Call an API or database to delete the existing harvest.
    // await MetrcService.deleteHarvest(this.id);
  }
}

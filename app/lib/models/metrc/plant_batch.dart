// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 2/27/2023
// Updated: 2/27/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

import 'package:cannlytics_app/models/metrc/strain.dart';

typedef PlantBatchId = int;

/// Model representing a plant batch.
class PlantBatch {
  // Initialization.
  const PlantBatch({
    required this.id,
    required this.name,
    required this.type,
    required this.locationId,
    required this.locationName,
    required this.locationTypeName,
    required this.strainId,
    required this.strainName,
    required this.patientLicenseNumber,
    required this.untrackedCount,
    required this.trackedCount,
    required this.packagedCount,
    required this.harvestedCount,
    required this.destroyedCount,
    required this.sourcePackageId,
    required this.sourcePackageLabel,
    required this.sourcePlantId,
    required this.sourcePlantLabel,
    required this.sourcePlantBatchId,
    required this.sourcePlantBatchName,
    required this.plantedDate,
    required this.lastModified,
  });

  // Properties.
  final PlantBatchId id;
  final String name;
  final String type;
  final int locationId;
  final String locationName;
  final String locationTypeName;
  final StrainId strainId;
  final String strainName;
  final String patientLicenseNumber;
  final int untrackedCount;
  final int trackedCount;
  final int packagedCount;
  final int harvestedCount;
  final int destroyedCount;
  final int sourcePackageId;
  final String sourcePackageLabel;
  final int sourcePlantId;
  final String sourcePlantLabel;
  final int sourcePlantBatchId;
  final String sourcePlantBatchName;
  final DateTime plantedDate;
  final DateTime lastModified;

  // Create model.
  factory PlantBatch.fromMap(Map<String, dynamic> data, int uid) {
    return PlantBatch(
      id: uid,
      name: data['name'] as String,
      type: data['type'] as String,
      locationId: data['location_id'] as int,
      locationName: data['location_name'] as String,
      locationTypeName: data['location_type_name'] as String,
      strainId: data['strain_id'] as StrainId,
      strainName: data['strain_name'] as String,
      patientLicenseNumber: data['patient_license_number'] as String,
      untrackedCount: data['untracked_count'] as int,
      trackedCount: data['tracked_count'] as int,
      packagedCount: data['packaged_count'] as int,
      harvestedCount: data['harvested_count'] as int,
      destroyedCount: data['destroyed_count'] as int,
      sourcePackageId: data['source_package_id'] as int,
      sourcePackageLabel: data['source_package_label'] as String,
      sourcePlantId: data['source_plant_id'] as int,
      sourcePlantLabel: data['source_plant_label'] as String,
      sourcePlantBatchId: data['source_plant_batch_id'] as int,
      sourcePlantBatchName: data['source_plant_batch_name'] as String,
      plantedDate: DateTime.parse(data['planted_date'] as String),
      lastModified: DateTime.parse(data['last_modified'] as String),
    );
  }

  // Create JSON.
  Map<String, dynamic> toMap() {
    return <String, dynamic>{
      'id': id,
      'name': name,
      'type': type,
      'location_id': locationId,
      'location_name': locationName,
      'location_type_name': locationTypeName,
      'strain_id': strainId,
      'strain_name': strainName,
      'patient_license_number': patientLicenseNumber,
      'untracked_count': untrackedCount,
      'tracked_count': trackedCount,
      'packaged_count': packagedCount,
      'harvested_count': harvestedCount,
      'destroyed_count': destroyedCount,
      'source_package_id': sourcePackageId,
      'source_package_label': sourcePackageLabel,
      'source_plant_id': sourcePlantId,
      'source_plant_label': sourcePlantLabel,
      'source_plant_batch_id': sourcePlantBatchId,
      'source_plant_batch_name': sourcePlantBatchName,
      'planted_date': plantedDate.toIso8601String(),
      'last_modified': lastModified.toIso8601String(),
    };
  }

  // Create PlantBatch.
  Future<void> create() async {
    // Call an API or database to create a new plant batch.
    // await MetrcService.createPlantBatch(this.toMap());
  }

  // Update PlantBatch.
  Future<void> update() async {
    // Call an API or database to update the existing plant batch.
    // await MetrcService.updatePlantBatch(this.id, this.toMap());
  }

  // Delete PlantBatch.
  Future<void> delete() async {
    // Call an API or database to delete the existing plant batch.
    // await MetrcService.deletePlantBatch(this.id);
  }
}

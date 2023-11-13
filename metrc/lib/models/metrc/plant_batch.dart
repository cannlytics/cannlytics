// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 2/27/2023
// Updated: 3/18/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Project imports:
import 'package:cannlytics_app/models/metrc/strain.dart';

typedef PlantBatchId = String;

/// Model representing a plant batch.
class PlantBatch {
  // Initialization.
  const PlantBatch({
    this.id,
    this.name,
    this.type,
    this.locationId,
    this.locationName,
    this.locationTypeName,
    this.strainId,
    this.strainName,
    this.patientLicenseNumber,
    this.untrackedCount,
    this.trackedCount,
    this.packagedCount,
    this.harvestedCount,
    this.destroyedCount,
    this.sourcePackageId,
    this.sourcePackageLabel,
    this.sourcePlantId,
    this.sourcePlantLabel,
    this.sourcePlantBatchId,
    this.sourcePlantBatchName,
    this.plantedDate,
    this.lastModified,
  });

  // Properties.
  final PlantBatchId? id;
  final String? name;
  final String? type;
  final int? locationId;
  final String? locationName;
  final String? locationTypeName;
  final StrainId? strainId;
  final String? strainName;
  final String? patientLicenseNumber;
  final int? untrackedCount;
  final int? trackedCount;
  final int? packagedCount;
  final int? harvestedCount;
  final int? destroyedCount;
  final int? sourcePackageId;
  final String? sourcePackageLabel;
  final int? sourcePlantId;
  final String? sourcePlantLabel;
  final int? sourcePlantBatchId;
  final String? sourcePlantBatchName;
  final String? plantedDate;
  final String? lastModified;

  // Create model.
  factory PlantBatch.fromMap(Map<String, dynamic> data) {
    return PlantBatch(
      id: data['id'] ?? '',
      name: data['name'] ?? '',
      type: data['type'] ?? '',
      locationId: data['location_id'] ?? 0,
      locationName: data['location_name'] ?? '',
      locationTypeName: data['location_type_name'] ?? '',
      strainId: data['strain_id'] as StrainId,
      strainName: data['strain_name'] ?? '',
      patientLicenseNumber: data['patient_license_number'] ?? '',
      untrackedCount: data['untracked_count'] ?? 0,
      trackedCount: data['tracked_count'] ?? 0,
      packagedCount: data['packaged_count'] ?? 0,
      harvestedCount: data['harvested_count'] ?? 0,
      destroyedCount: data['destroyed_count'] ?? 0,
      sourcePackageId: data['source_package_id'] ?? 0,
      sourcePackageLabel: data['source_package_label'] ?? '',
      sourcePlantId: data['source_plant_id'] ?? 0,
      sourcePlantLabel: data['source_plant_label'] ?? '',
      sourcePlantBatchId: data['source_plant_batch_id'] ?? 0,
      sourcePlantBatchName: data['source_plant_batch_name'] ?? '',
      plantedDate: data['planted_date'] ?? '',
      lastModified: data['last_modified'] ?? '',
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
      'planted_date': plantedDate,
      'last_modified': lastModified,
    };
  }

  // // Create PlantBatch.
  // Future<void> create() async {
  //   // Call an API or database to create a new plant batch.
  //   // await MetrcService.createPlantBatch(this.toMap());
  // }

  // // Update PlantBatch.
  // Future<void> update() async {
  //   // Call an API or database to update the existing plant batch.
  //   // await MetrcService.updatePlantBatch(this.id, this.toMap());
  // }

  // // Delete PlantBatch.
  // Future<void> delete() async {
  //   // Call an API or database to delete the existing plant batch.
  //   // await MetrcService.deletePlantBatch(this.id);
  // }
}

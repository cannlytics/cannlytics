// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 2/27/2023
// Updated: 2/27/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

import 'package:cannlytics_app/services/metrc_service.dart';

class Package {
  // Initialization.
  const Package({
    required this.id,
    required this.archivedDate,
    required this.containsRemediatedProduct,
    required this.finishedDate,
    required this.initialLabTestingState,
    required this.isDonation,
    required this.isDonationPersistent,
    required this.isOnHold,
    required this.isOnTrip,
    required this.isProcessValidationTestingSample,
    required this.isProductionBatch,
    required this.isTestingSample,
    required this.isTradeSample,
    required this.isTradeSamplePersistent,
    required this.itemFromFacilityLicenseNumber,
    required this.itemFromFacilityName,
    required this.label,
    required this.lastModified,
    required this.locationId,
    required this.locationName,
    required this.locationTypeName,
    required this.note,
    required this.packageForProductDestruction,
    required this.packageType,
    required this.patientLicenseNumber,
    required this.productRequiresRemediation,
    required this.quantity,
    required this.receivedDateTime,
    required this.receivedFromFacilityLicenseNumber,
    required this.receivedFromFacilityName,
    required this.receivedFromManifestNumber,
    required this.remediationDate,
    required this.labTestingState,
    required this.labTestingStateDate,
    required this.packagedDate,
    required this.productionBatchNumber,
    required this.sourceHarvestCount,
    required this.sourceHarvestNames,
    required this.sourcePackageCount,
    required this.sourcePackageIsDonation,
    required this.sourcePackageIsTradeSample,
    required this.sourceProductionBatchNumbers,
    required this.sourceProcessingJobCount,
    required this.unitOfMeasureAbbreviation,
    required this.unitOfMeasureName,
    required this.items,
  });

  // Properties.
  final int id;
  final DateTime archivedDate;
  final bool containsRemediatedProduct;
  final DateTime finishedDate;
  final String initialLabTestingState;
  final bool isDonation;
  final bool isDonationPersistent;
  final bool isOnHold;
  final bool isOnTrip;
  final bool isProcessValidationTestingSample;
  final bool isProductionBatch;
  final bool isTestingSample;
  final bool isTradeSample;
  final bool isTradeSamplePersistent;
  final String itemFromFacilityLicenseNumber;
  final String itemFromFacilityName;
  final String label;
  final DateTime lastModified;
  final int locationId;
  final String locationName;
  final String locationTypeName;
  final String note;
  final String packageForProductDestruction;
  final String packageType;
  final String patientLicenseNumber;
  final bool productRequiresRemediation;
  final double quantity;
  final DateTime receivedDateTime;
  final String receivedFromFacilityLicenseNumber;
  final String receivedFromFacilityName;
  final String receivedFromManifestNumber;
  final DateTime remediationDate;
  final String labTestingState;
  final DateTime labTestingStateDate;
  final DateTime packagedDate;
  final String productionBatchNumber;
  final int sourceHarvestCount;
  final String sourceHarvestNames;
  final int sourcePackageCount;
  final bool sourcePackageIsDonation;
  final bool sourcePackageIsTradeSample;
  final String sourceProductionBatchNumbers;
  final int sourceProcessingJobCount;
  final String unitOfMeasureAbbreviation;
  final String unitOfMeasureName;
  final List<dynamic> items;

  // Create model.
  factory Package.fromMap(Map<String, dynamic> data, int uid) {
    return Package(
      id: uid,
      archivedDate: data['archived_date'] as DateTime,
      containsRemediatedProduct: data['contains_remediated_product'] as bool,
      finishedDate: data['finished_date'] as DateTime,
      initialLabTestingState: data['initial_lab_testing_state'] as String,
      isDonation: data['is_donation'] as bool,
      isDonationPersistent: data['is_donation_persistent'] as bool,
      isOnHold: data['is_on_hold'] as bool,
      isOnTrip: data['is_on_trip'] as bool,
      isProcessValidationTestingSample:
          data['is_process_validation_testing_sample'] as bool,
      isProductionBatch: data['is_production_batch'] as bool,
      isTestingSample: data['is_testing_sample'] as bool,
      isTradeSample: data['is_trade_sample'] as bool,
      isTradeSamplePersistent: data['is_trade_sample_persistent'] as bool,
      itemFromFacilityLicenseNumber:
          data['item_from_facility_license_number'] as String,
      itemFromFacilityName: data['item_from_facility_name'] as String,
      label: data['label'] as String,
      lastModified: data['last_modified'] as DateTime,
      locationId: data['location_id'] as int,
      locationName: data['location_name'] as String,
      locationTypeName: data['location_type_name'] as String,
      note: data['note'] as String,
      packageForProductDestruction:
          data['package_for_product_destruction'] as String,
      packageType: data['package_type'] as String,
      patientLicenseNumber: data['patient_license_number'] as String,
      productRequiresRemediation: data['product_requires_remediation'] as bool,
      quantity: data['quantity'] as double,
      receivedDateTime: data['received_date_time'] as DateTime,
      receivedFromFacilityLicenseNumber:
          data['received_from_facility_license_number'] as String,
      receivedFromFacilityName: data['received_from_facility_name'] as String,
      receivedFromManifestNumber:
          data['received_from_manifest_number'] as String,
      remediationDate: data['remediation_date'] as DateTime,
      labTestingState: data['lab_testing_state'] as String,
      labTestingStateDate: data['lab_testing_state_date'] as DateTime,
      packagedDate: data['packaged_date'] as DateTime,
      productionBatchNumber: data['production_batch_number'] as String,
      sourceHarvestCount: data['source_harvest_count'] as int,
      sourceHarvestNames: data['source_harvest_names'] as String,
      sourcePackageCount: data['source_package_count'] as int,
      sourcePackageIsDonation: data['source_package_is_donation'] as bool,
      sourcePackageIsTradeSample:
          data['source_package_is_trade_sample'] as bool,
      sourceProductionBatchNumbers:
          data['source_production_batch_numbers'] as String,
      sourceProcessingJobCount: data['source_processing_job_count'] as int,
      unitOfMeasureAbbreviation: data['unit_of_measure_abbreviation'] as String,
      unitOfMeasureName: data['unit_of_measure_name'] as String,
      items: data['items'] as List<dynamic>,
    );
  }

  // Create JSON.
  Map<String, dynamic> toMap() {
    return <String, dynamic>{
      'id': id,
      'archived_date': archivedDate,
      'contains_remediated_product': containsRemediatedProduct,
      'finished_date': finishedDate,
      'initial_lab_testing_state': initialLabTestingState,
      'is_donation': isDonation,
      'is_donation_persistent': isDonationPersistent,
      'is_on_hold': isOnHold,
      'is_on_trip': isOnTrip,
      'is_process_validation_testing_sample': isProcessValidationTestingSample,
      'is_production_batch': isProductionBatch,
      'is_testing_sample': isTestingSample,
      'is_trade_sample': isTradeSample,
      'is_trade_sample_persistent': isTradeSamplePersistent,
      'item_from_facility_license_number': itemFromFacilityLicenseNumber,
      'item_from_facility_name': itemFromFacilityName,
      'label': label,
      'last_modified': lastModified,
      'location_id': locationId,
      'location_name': locationName,
      'location_type_name': locationTypeName,
      'note': note,
      'package_for_product_destruction': packageForProductDestruction,
      'package_type': packageType,
      'patient_license_number': patientLicenseNumber,
      'product_requires_remediation': productRequiresRemediation,
      'quantity': quantity,
      'received_date_time': receivedDateTime,
      'received_from_facility_license_number':
          receivedFromFacilityLicenseNumber,
      'received_from_facility_name': receivedFromFacilityName,
      'received_from_manifest_number': receivedFromManifestNumber,
      'remediation_date': remediationDate,
      'lab_testing_state': labTestingState,
      'lab_testing_state_date': labTestingStateDate,
      'packaged_date': packagedDate,
      'production_batch_number': productionBatchNumber,
      'source_harvest_count': sourceHarvestCount,
      'source_harvest_names': sourceHarvestNames,
      'source_package_count': sourcePackageCount,
      'source_package_is_donation': sourcePackageIsDonation,
      'source_package_is_trade_sample': sourcePackageIsTradeSample,
      'source_production_batch_numbers': sourceProductionBatchNumbers,
      'source_processing_job_count': sourceProcessingJobCount,
      'unit_of_measure_abbreviation': unitOfMeasureAbbreviation,
      'unit_of_measure_name': unitOfMeasureName,
      'items': items,
    };
  }

  // Create Package.
  Future<void> create() async {
    // Call an API or database to create a new package.
    // await MetrcService.createPackage(this.toMap());
  }

  // Update Package.
  Future<void> update() async {
    // Call an API or database to update the existing package.
    // await MetrcService.updatePackage(this.id, this.toMap());
  }

  // Delete Package.
  Future<void> delete() async {
    // Call an API or database to delete the existing package.
    // await MetrcService.deletePackage(this.id);
  }
}

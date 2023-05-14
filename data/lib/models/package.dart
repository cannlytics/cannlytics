// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 2/27/2023
// Updated: 3/18/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Project imports:
import 'package:cannlytics_app/services/metrc_service.dart';

class Package {
  // Initialization.
  const Package({
    this.id,
    this.archivedDate,
    this.containsRemediatedProduct,
    this.finishedDate,
    this.initialLabTestingState,
    this.isDonation,
    this.isDonationPersistent,
    this.isOnHold,
    this.isOnTrip,
    this.isProcessValidationTestingSample,
    this.isProductionBatch,
    this.isTestingSample,
    this.isTradeSample,
    this.isTradeSamplePersistent,
    this.itemFromFacilityLicenseNumber,
    this.itemFromFacilityName,
    this.label,
    this.lastModified,
    this.locationId,
    this.locationName,
    this.locationTypeName,
    this.note,
    this.packageForProductDestruction,
    this.packageType,
    this.patientLicenseNumber,
    this.productRequiresRemediation,
    this.quantity,
    this.receivedDateTime,
    this.receivedFromFacilityLicenseNumber,
    this.receivedFromFacilityName,
    this.receivedFromManifestNumber,
    this.remediationDate,
    this.labTestingState,
    this.labTestingStateDate,
    this.packagedDate,
    this.productionBatchNumber,
    this.sourceHarvestCount,
    this.sourceHarvestNames,
    this.sourcePackageCount,
    this.sourcePackageIsDonation,
    this.sourcePackageIsTradeSample,
    this.sourceProductionBatchNumbers,
    this.sourceProcessingJobCount,
    this.unitOfMeasureAbbreviation,
    this.unitOfMeasureName,
    this.items,
  });

  // Properties.
  final String? id;
  final String? archivedDate;
  final bool? containsRemediatedProduct;
  final String? finishedDate;
  final String? initialLabTestingState;
  final bool? isDonation;
  final bool? isDonationPersistent;
  final bool? isOnHold;
  final bool? isOnTrip;
  final bool? isProcessValidationTestingSample;
  final bool? isProductionBatch;
  final bool? isTestingSample;
  final bool? isTradeSample;
  final bool? isTradeSamplePersistent;
  final String? itemFromFacilityLicenseNumber;
  final String? itemFromFacilityName;
  final String? label;
  final String? lastModified;
  final String? locationId;
  final String? locationName;
  final String? locationTypeName;
  final String? note;
  final String? packageForProductDestruction;
  final String? packageType;
  final String? patientLicenseNumber;
  final bool? productRequiresRemediation;
  final double? quantity;
  final String? receivedDateTime;
  final String? receivedFromFacilityLicenseNumber;
  final String? receivedFromFacilityName;
  final String? receivedFromManifestNumber;
  final String? remediationDate;
  final String? labTestingState;
  final String? labTestingStateDate;
  final String? packagedDate;
  final String? productionBatchNumber;
  final int? sourceHarvestCount;
  final String? sourceHarvestNames;
  final int? sourcePackageCount;
  final bool? sourcePackageIsDonation;
  final bool? sourcePackageIsTradeSample;
  final String? sourceProductionBatchNumbers;
  final int? sourceProcessingJobCount;
  final String? unitOfMeasureAbbreviation;
  final String? unitOfMeasureName;
  final List<dynamic>? items;

  // Create model.
  factory Package.fromMap(Map<String, dynamic> data) {
    return Package(
      id: data['id'].toString(),
      archivedDate: data['archived_date'] ?? '',
      containsRemediatedProduct: data['contains_remediated_product'] ?? false,
      finishedDate: data['finished_date'] ?? '',
      initialLabTestingState: data['initial_lab_testing_state'] ?? '',
      isDonation: data['is_donation'] ?? false,
      isDonationPersistent: data['is_donation_persistent'] ?? false,
      isOnHold: data['is_on_hold'] ?? false,
      isOnTrip: data['is_on_trip'] ?? false,
      isProcessValidationTestingSample:
          data['is_process_validation_testing_sample'] ?? false,
      isProductionBatch: data['is_production_batch'] ?? false,
      isTestingSample: data['is_testing_sample'] ?? false,
      isTradeSample: data['is_trade_sample'] ?? false,
      isTradeSamplePersistent: data['is_trade_sample_persistent'] ?? false,
      itemFromFacilityLicenseNumber:
          data['item_from_facility_license_number'] ?? '',
      itemFromFacilityName: data['item_from_facility_name'] ?? '',
      label: data['label'] ?? '',
      lastModified: data['last_modified'] ?? '',
      locationId: data['location_id'].toString(),
      locationName: data['location_name'] ?? '',
      locationTypeName: data['location_type_name'] ?? '',
      note: data['note'] ?? '',
      packageForProductDestruction:
          data['package_for_product_destruction'] ?? '',
      packageType: data['package_type'] ?? '',
      patientLicenseNumber: data['patient_license_number'] ?? '',
      productRequiresRemediation: data['product_requires_remediation'] ?? false,
      quantity: data['quantity'] ?? 0.0,
      receivedDateTime: data['received_date_time'] ?? '',
      receivedFromFacilityLicenseNumber:
          data['received_from_facility_license_number'] ?? '',
      receivedFromFacilityName: data['received_from_facility_name'] ?? '',
      receivedFromManifestNumber: data['received_from_manifest_number'] ?? '',
      remediationDate: data['remediation_date'] ?? '',
      labTestingState: data['lab_testing_state'] ?? '',
      labTestingStateDate: data['lab_testing_state_date'] ?? '',
      packagedDate: data['packaged_date'] ?? '',
      productionBatchNumber: data['production_batch_number'] ?? '',
      sourceHarvestCount: data['source_harvest_count'] ?? 0,
      sourceHarvestNames: data['source_harvest_names'] ?? '',
      sourcePackageCount: data['source_package_count'] ?? 0,
      sourcePackageIsDonation: data['source_package_is_donation'] ?? false,
      sourcePackageIsTradeSample:
          data['source_package_is_trade_sample'] ?? false,
      sourceProductionBatchNumbers:
          data['source_production_batch_numbers'] ?? '',
      sourceProcessingJobCount: data['source_processing_job_count'] ?? 0,
      unitOfMeasureAbbreviation: data['unit_of_measure_abbreviation'] ?? '',
      unitOfMeasureName: data['unit_of_measure_name'] ?? '',
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

  // // Create Package.
  // Future<void> create() async {
  //   // Call an API or database to create a new package.
  //   // await MetrcService.createPackage(this.toMap());
  // }

  // // Update Package.
  // Future<void> update() async {
  //   // Call an API or database to update the existing package.
  //   // await MetrcService.updatePackage(this.id, this.toMap());
  // }

  // // Delete Package.
  // Future<void> delete() async {
  //   // Call an API or database to delete the existing package.
  //   // await MetrcService.deletePackage(this.id);
  // }
}

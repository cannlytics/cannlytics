// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 3/2/2023
// Updated: 5/23/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Package imports:
import 'package:equatable/equatable.dart';

typedef LabTestResultId = String;
typedef LabTestId = String;

/// A general lab result class.
class LabResult {
  // Initialization.
  const LabResult({
    this.labId,
    this.batchNumber,
    this.productName,
    this.downloadUrl,
    this.businessDbaName,
    this.producerLicenseNumber,
    this.lims,
    this.lab,
    this.labImageUrl,
    this.labAddress,
    this.labStreet,
    this.labCity,
    this.labCounty,
    this.labState,
    this.labZipcode,
    this.labPhone,
    this.labEmail,
    this.labWebsite,
    this.labLatitude,
    this.labLongitude,
    this.licensingAuthorityId,
    this.licensingAuthority,
  });

  // Properties.
  final String? labId;
  final String? batchNumber;
  final String? productName;
  final String? downloadUrl;
  final String? businessDbaName;
  final String? producerLicenseNumber;
  final String? lims;
  final String? lab;
  final String? labImageUrl;
  final String? labAddress;
  final String? labStreet;
  final String? labCity;
  final String? labCounty;
  final String? labState;
  final String? labZipcode;
  final String? labPhone;
  final String? labEmail;
  final String? labWebsite;
  final double? labLatitude;
  final double? labLongitude;
  final String? licensingAuthorityId;
  final String? licensingAuthority;

  @override
  List<String?> get props => [labId];

  // Create model.
  factory LabResult.fromMap(Map data) {
    return LabResult(
      labId: data['lab_id'] ?? '',
      batchNumber: data['batch_number'] ?? '',
      productName: data['product_name'] ?? '',
      downloadUrl: data['download_url'] ?? '',
      businessDbaName: data['business_dba_name'] ?? '',
      producerLicenseNumber: data['producer_license_number'] ?? '',
      lims: data['lims'] ?? '',
      lab: data['lab'] ?? '',
      labImageUrl: data['lab_image_url'] ?? '',
      labAddress: data['lab_address'] ?? '',
      labStreet: data['lab_street'] ?? '',
      labCity: data['lab_city'] ?? '',
      labCounty: data['lab_county'] ?? '',
      labState: data['lab_state'] ?? '',
      labZipcode: data['lab_zipcode'] ?? '',
      labPhone: data['lab_phone'] ?? '',
      labEmail: data['lab_email'] ?? '',
      labWebsite: data['lab_website'] ?? '',
      labLatitude: data['lab_latitude']?.toDouble() ?? 0.0,
      labLongitude: data['lab_longitude']?.toDouble() ?? 0.0,
      licensingAuthorityId: data['licensing_authority_id'] ?? '',
      licensingAuthority: data['licensing_authority'] ?? '',
    );
  }

  // Create JSON.
  Map<String, dynamic> toMap() {
    return <String, dynamic>{
      'lab_id': labId,
      'batch_number': batchNumber,
      'product_name': productName,
      'download_url': downloadUrl,
      'business_dba_name': businessDbaName,
      'producer_license_number': producerLicenseNumber,
      'lims': lims,
      'lab': lab,
      'lab_image_url': labImageUrl,
      'lab_address': labAddress,
      'lab_street': labStreet,
      'lab_city': labCity,
      'lab_county': labCounty,
      'lab_state': labState,
      'lab_zipcode': labZipcode,
      'lab_phone': labPhone,
      'lab_email': labEmail,
      'lab_website': labWebsite,
      'lab_latitude': labLatitude,
      'lab_longitude': labLongitude,
      'licensing_authority_id': licensingAuthorityId,
      'licensing_authority': licensingAuthority,
    };
  }
}

/// Model representing a lab test for traceability.
class LabTest {
  // Initialization.
  const LabTest({
    required this.id,
    required this.labFacilityLicenseNumber,
    required this.labFacilityName,
    required this.labTestDetailRevokedDate,
    required this.overallPassed,
    required this.packageId,
    required this.productCategoryName,
    required this.productName,
    required this.resultReleaseDateTime,
    required this.resultReleased,
    required this.revokedDate,
    required this.sourcePackageLabel,
    required this.testComment,
    required this.testInformationalOnly,
    required this.testPassed,
    required this.testPerformedDate,
    required this.testResultLevel,
    required this.testTypeName,
  });

  // Properties.
  final LabTestId id;
  final String labFacilityLicenseNumber;
  final String labFacilityName;
  final DateTime labTestDetailRevokedDate;
  final bool overallPassed;
  final int packageId;
  final String productCategoryName;
  final String productName;
  final DateTime resultReleaseDateTime;
  final bool resultReleased;
  final DateTime revokedDate;
  final String sourcePackageLabel;
  final String testComment;
  final bool testInformationalOnly;
  final bool testPassed;
  final DateTime testPerformedDate;
  final double testResultLevel;
  final String testTypeName;

  // Create model.
  factory LabTest.fromMap(Map<String, dynamic> data, String uid) {
    return LabTest(
      id: uid,
      labFacilityLicenseNumber: data['lab_facility_license_number'] as String,
      labFacilityName: data['lab_facility_name'] as String,
      labTestDetailRevokedDate:
          data['lab_test_detail_revoked_date'] as DateTime,
      overallPassed: data['overall_passed'] as bool,
      packageId: data['package_id'] as int,
      productCategoryName: data['product_category_name'] as String,
      productName: data['product_name'] as String,
      resultReleaseDateTime: data['result_release_date_time'] as DateTime,
      resultReleased: data['result_released'] as bool,
      revokedDate: data['revoked_date'] as DateTime,
      sourcePackageLabel: data['source_package_label'] as String,
      testComment: data['test_comment'] as String,
      testInformationalOnly: data['test_informational_only'] as bool,
      testPassed: data['test_passed'] as bool,
      testPerformedDate: data['test_performed_date'] as DateTime,
      testResultLevel: data['test_result_level'] as double,
      testTypeName: data['test_type_name'] as String,
    );
  }

  // Create JSON.
  Map<String, dynamic> toMap() {
    return <String, dynamic>{
      'id': id,
      'lab_facility_license_number': labFacilityLicenseNumber,
      'lab_facility_name': labFacilityName,
      'lab_test_detail_revoked_date': labTestDetailRevokedDate,
      'overall_passed': overallPassed,
      'package_id': packageId,
      'product_category_name': productCategoryName,
      'product_name': productName,
      'result_release_date_time': resultReleaseDateTime,
      'result_released': resultReleased,
      'revoked_date': revokedDate,
      'source_package_label': sourcePackageLabel,
      'test_comment': testComment,
      'test_informational_only': testInformationalOnly,
      'test_passed': testPassed,
      'test_performed_date': testPerformedDate,
      'test_result_level': testResultLevel,
      'test_type_name': testTypeName,
    };
  }
}

/// Model representing a singular lab test result for traceability.
class LabTestResult {
  // Initialization.
  const LabTestResult({
    this.id,
    this.labTestTypeName,
    this.notes,
    this.passed,
    this.quantity,
  });

  // Properties.
  final LabTestResultId? id;
  final String? labTestTypeName;
  final String? notes;
  final bool? passed;
  final double? quantity;

  // Create model.
  factory LabTestResult.fromMap(Map<String, dynamic> data) {
    return LabTestResult(
      id: data['id'].toString(),
      labTestTypeName: data['lab_test_type_name'] ?? '',
      notes: data['notes'] ?? '',
      passed: data['passed'] ?? false,
      quantity: data['quantity'] ?? 0.0,
    );
  }

  // Create JSON.
  Map<String, dynamic> toMap() {
    return <String, dynamic>{
      'id': id,
      'lab_test_type_name': labTestTypeName,
      'notes': notes,
      'passed': passed,
      'quantity': quantity,
    };
  }
}

// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 3/2/2023
// Updated: 6/24/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Package imports:
// import 'package:equatable/equatable.dart';

import 'dart:convert';

typedef LabTestResultId = String;
typedef LabTestId = String;

/// A general lab result model for users.
class LabResult {
  // Initialization.
  const LabResult({
    this.labId,
    this.batchNumber,
    this.productName,
    this.businessDbaName,
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
    this.analyses,
    this.analysisStatus,
    this.methods,
    this.dateCollected,
    this.dateTested,
    this.dateReceived,
    this.distributor,
    this.distributorAddress,
    this.distributorStreet,
    this.distributorCity,
    this.distributorState,
    this.distributorZipcode,
    this.distributorLicenseNumber,
    this.producer,
    this.producerLicenseNumber,
    this.producerAddress,
    this.producerStreet,
    this.producerCity,
    this.producerState,
    this.producerZipcode,
    this.productType,
    this.traceabilityIds,
    this.productSize,
    this.servingSize,
    this.servingsPerPackage,
    this.sampleWeight,
    this.status,
    this.totalCannabinoids,
    this.totalThc,
    this.totalCbd,
    this.totalTerpenes,
    this.sampleId,
    this.strainName,
    this.results,
    this.coaAlgorithm,
    this.coaAlgorithmVersion,
    this.coaParsedAt,
    this.resultsHash,
    this.sampleHash,
    this.warning,
    this.fileRef,
    this.downloadUrl,
    this.shortUrl,
  });

  // Properties.
  final String? labId;
  final String? batchNumber;
  final String? productName;
  final String? businessDbaName;
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
  final dynamic analyses;
  final String? analysisStatus;
  final dynamic methods;
  final String? dateCollected;
  final String? dateTested;
  final String? dateReceived;
  final String? distributor;
  final String? distributorAddress;
  final String? distributorStreet;
  final String? distributorCity;
  final String? distributorState;
  final String? distributorZipcode;
  final String? distributorLicenseNumber;
  final String? producer;
  final String? producerLicenseNumber;
  final String? producerAddress;
  final String? producerStreet;
  final String? producerCity;
  final String? producerState;
  final String? producerZipcode;
  final String? productType;
  final dynamic traceabilityIds;
  final int? productSize;
  final int? servingSize;
  final int? servingsPerPackage;
  final double? sampleWeight;
  final String? status;
  final double? totalCannabinoids;
  final double? totalThc;
  final double? totalCbd;
  final double? totalTerpenes;
  final String? sampleId;
  final String? strainName;
  // final List<Result?>? results;
  final dynamic results;
  final String? coaAlgorithm;
  final String? coaAlgorithmVersion;
  final String? coaParsedAt;
  final String? resultsHash;
  final String? sampleHash;
  final String? warning;
  final String? fileRef;
  final String? downloadUrl;
  final String? shortUrl;

  // @override
  // List<String?> get props => [labId];

  // Create model.
  factory LabResult.fromMap(Map data) {
    // Standardize results.
    var results = null;
    try {
      results = jsonDecode(data['results']) as List<dynamic>;
    } catch (error) {
      try {
        results = data['results'] as List<dynamic>;
      } catch (error) {
        results = null;
      }
      results = data['results'] as List<dynamic>;
    }

    return LabResult(
      labId: data['lab_id'] ?? '',
      batchNumber: data['batch_number'] ?? '',
      productName: data['product_name'] ?? '',
      businessDbaName: data['business_dba_name'] ?? '',
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
      labLatitude:
          data['lab_latitude'] != null ? data['lab_latitude'].toDouble() : null,
      labLongitude: data['lab_longitude'] != null
          ? data['lab_longitude'].toDouble()
          : null,
      licensingAuthorityId: data['licensing_authority_id'] ?? '',
      licensingAuthority: data['licensing_authority'] ?? '',
      analyses: data['analyses'] is List<dynamic>
          ? data['analyses']
          : (data['analyses'] != null
              ? jsonDecode(data['analyses']) as List<dynamic>
              : null),
      analysisStatus: data['analysis_status'],
      methods: data['methods'] is List<dynamic>
          ? (data['methods'] as List)
              .map((method) => (method as Map).cast<String, dynamic>())
              .toList()
          : (data['methods'] != null
              ? (jsonDecode(data['methods']) as List)
                  .map((method) => (method as Map).cast<String, dynamic>())
                  .toList()
              : null),
      dateCollected: data['date_collected'],
      dateTested: data['date_tested'],
      dateReceived: data['date_received'],
      distributor: data['distributor'],
      distributorAddress: data['distributor_address'],
      distributorStreet: data['distributor_street'],
      distributorCity: data['distributor_city'],
      distributorState: data['distributor_state'],
      distributorZipcode: data['distributor_zipcode'],
      distributorLicenseNumber: data['distributor_license_number'],
      producer: data['producer'] ?? '',
      producerLicenseNumber: data['producer_license_number'] ?? '',
      producerAddress: data['producer_address'],
      producerStreet: data['producer_street'],
      producerCity: data['producer_city'],
      producerState: data['producer_state'],
      producerZipcode: data['producer_zipcode'],
      productType: data['product_type'],
      traceabilityIds: data['traceability_ids'] is List<dynamic>
          ? data['traceability_ids'] as List<dynamic>
          : (data['traceability_ids'] != null
              ? jsonDecode(data['traceability_ids']) as List<dynamic>
              : null),
      productSize: data['product_size'] is String
          ? int.tryParse(data['product_size'] as String)
          : data['product_size'] as int?,
      servingSize: data['serving_size'] is String
          ? int.tryParse(data['serving_size'] as String)
          : data['serving_size'] as int?,
      servingsPerPackage: data['servings_per_package'] is String
          ? int.tryParse(data['servings_per_package'] as String)
          : data['servings_per_package'] as int?,
      sampleWeight: (data['sample_weight'] is String)
          ? double.tryParse(data['sample_weight'] as String)
          : (data['sample_weight'] as num?)?.toDouble(),
      totalCannabinoids: (data['total_cannabinoids'] is String)
          ? double.tryParse(data['total_cannabinoids'] as String)
          : (data['total_cannabinoids'] as num?)?.toDouble(),
      totalThc: (data['total_thc'] is String)
          ? double.tryParse(data['total_thc'] as String)
          : (data['total_thc'] as num?)?.toDouble(),
      totalCbd: (data['total_cbd'] is String)
          ? double.tryParse(data['total_cbd'] as String)
          : (data['total_cbd'] as num?)?.toDouble(),
      totalTerpenes: (data['total_terpenes'] is String)
          ? double.tryParse(data['total_terpenes'] as String)
          : (data['total_terpenes'] as num?)?.toDouble(),
      status: data['status'],
      sampleId: data['sample_id'],
      strainName: data['strain_name'],
      results: results,
      coaAlgorithm: data['coa_algorithm'],
      coaAlgorithmVersion: data['coa_algorithm_version'],
      coaParsedAt: data['coa_parsed_at'],
      resultsHash: data['results_hash'],
      sampleHash: data['sample_hash'],
      warning: data['warning'],
      fileRef: data['file_ref'] as String?,
      downloadUrl: data['download_url'] as String?,
      shortUrl: data['short_url'] as String?,
    );
  }

  // Create JSON.
  Map<String, dynamic> toMap() {
    return <String, dynamic>{
      'lab_id': labId,
      'batch_number': batchNumber,
      'product_name': productName,
      'business_dba_name': businessDbaName,
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
      'analyses': analyses,
      'analysis_status': analysisStatus,
      'methods': methods,
      'date_collected': dateCollected,
      'date_tested': dateTested,
      'date_received': dateReceived,
      'distributor': distributor,
      'distributor_address': distributorAddress,
      'distributor_street': distributorStreet,
      'distributor_city': distributorCity,
      'distributor_state': distributorState,
      'distributor_zipcode': distributorZipcode,
      'distributor_license_number': distributorLicenseNumber,
      'producer': producer,
      'producer_license_number': producerLicenseNumber,
      'producer_address': producerAddress,
      'producer_street': producerStreet,
      'producer_city': producerCity,
      'producer_state': producerState,
      'producer_zipcode': producerZipcode,
      'product_type': productType,
      'traceability_ids': traceabilityIds,
      'product_size': productSize,
      'serving_size': servingSize,
      'servings_per_package': servingsPerPackage,
      'sample_weight': sampleWeight,
      'status': status,
      'total_cannabinoids': totalCannabinoids,
      'total_thc': totalThc,
      'total_cbd': totalCbd,
      'total_terpenes': totalTerpenes,
      'sample_id': sampleId,
      'strain_name': strainName,
      'results': results,
      'coa_algorithm': coaAlgorithm,
      'coa_algorithm_version': coaAlgorithmVersion,
      'coa_parsed_at': coaParsedAt,
      'results_hash': resultsHash,
      'sample_hash': sampleHash,
      'warning': warning,
      'file_ref': fileRef,
      'download_url': downloadUrl,
      'short_url': shortUrl,
    };
  }
}

/// Model representing a singular lab test result for users.
class Result {
  // Initialization.
  const Result({
    this.analysis,
    this.key,
    this.name,
    this.value,
    this.mg_g,
    this.units,
    this.limit,
    this.lod,
    this.loq,
    this.status,
  });

  // Properties.
  final String? analysis;
  final String? key;
  final String? name;
  final double? value;
  final double? mg_g;
  final String? units;
  final double? limit;
  final double? lod;
  final double? loq;
  final String? status;

  // Create model.
  factory Result.fromMap(Map<String, dynamic> data) {
    return Result(
      analysis: data['analysis'] as String?,
      key: data['key'] as String?,
      name: data['name'] as String?,
      value: data['value'] as double?,
      mg_g: data['mg_g'] as double?,
      units: data['units'] as String?,
      limit: data['limit'] as double?,
      lod: data['lod'] as double?,
      loq: data['loq'] as double?,
      status: data['status'] as String?,
    );
  }

  // Create JSON.
  Map<String, dynamic> toMap() {
    return <String, dynamic>{
      'analysis': analysis,
      'key': key,
      'name': name,
      'value': value,
      'mg_g': mg_g,
      'units': units,
      'limit': limit,
      'lod': lod,
      'loq': loq,
      'status': status,
    };
  }
}

/* === Metrc Lab Result Models === */

// /// Model representing a lab test for traceability.
// class LabTest {
//   // Initialization.
//   const LabTest({
//     required this.id,
//     required this.labFacilityLicenseNumber,
//     required this.labFacilityName,
//     required this.labTestDetailRevokedDate,
//     required this.overallPassed,
//     required this.packageId,
//     required this.productCategoryName,
//     required this.productName,
//     required this.resultReleaseDateTime,
//     required this.resultReleased,
//     required this.revokedDate,
//     required this.sourcePackageLabel,
//     required this.testComment,
//     required this.testInformationalOnly,
//     required this.testPassed,
//     required this.testPerformedDate,
//     required this.testResultLevel,
//     required this.testTypeName,
//   });

//   // Properties.
//   final LabTestId id;
//   final String labFacilityLicenseNumber;
//   final String labFacilityName;
//   final DateTime labTestDetailRevokedDate;
//   final bool overallPassed;
//   final int packageId;
//   final String productCategoryName;
//   final String productName;
//   final DateTime resultReleaseDateTime;
//   final bool resultReleased;
//   final DateTime revokedDate;
//   final String sourcePackageLabel;
//   final String testComment;
//   final bool testInformationalOnly;
//   final bool testPassed;
//   final DateTime testPerformedDate;
//   final double testResultLevel;
//   final String testTypeName;

//   // Create model.
//   factory LabTest.fromMap(Map<String, dynamic> data, String uid) {
//     return LabTest(
//       id: uid,
//       labFacilityLicenseNumber: data['lab_facility_license_number'] as String,
//       labFacilityName: data['lab_facility_name'] as String,
//       labTestDetailRevokedDate:
//           data['lab_test_detail_revoked_date'] as DateTime,
//       overallPassed: data['overall_passed'] as bool,
//       packageId: data['package_id'] as int,
//       productCategoryName: data['product_category_name'] as String,
//       productName: data['product_name'] as String,
//       resultReleaseDateTime: data['result_release_date_time'] as DateTime,
//       resultReleased: data['result_released'] as bool,
//       revokedDate: data['revoked_date'] as DateTime,
//       sourcePackageLabel: data['source_package_label'] as String,
//       testComment: data['test_comment'] as String,
//       testInformationalOnly: data['test_informational_only'] as bool,
//       testPassed: data['test_passed'] as bool,
//       testPerformedDate: data['test_performed_date'] as DateTime,
//       testResultLevel: data['test_result_level'] as double,
//       testTypeName: data['test_type_name'] as String,
//     );
//   }

//   // Create JSON.
//   Map<String, dynamic> toMap() {
//     return <String, dynamic>{
//       'id': id,
//       'lab_facility_license_number': labFacilityLicenseNumber,
//       'lab_facility_name': labFacilityName,
//       'lab_test_detail_revoked_date': labTestDetailRevokedDate,
//       'overall_passed': overallPassed,
//       'package_id': packageId,
//       'product_category_name': productCategoryName,
//       'product_name': productName,
//       'result_release_date_time': resultReleaseDateTime,
//       'result_released': resultReleased,
//       'revoked_date': revokedDate,
//       'source_package_label': sourcePackageLabel,
//       'test_comment': testComment,
//       'test_informational_only': testInformationalOnly,
//       'test_passed': testPassed,
//       'test_performed_date': testPerformedDate,
//       'test_result_level': testResultLevel,
//       'test_type_name': testTypeName,
//     };
//   }
// }

// /// Model representing a singular lab test result for traceability.
// class LabTestResult {
//   // Initialization.
//   const LabTestResult({
//     this.id,
//     this.labTestTypeName,
//     this.notes,
//     this.passed,
//     this.quantity,
//   });

//   // Properties.
//   final LabTestResultId? id;
//   final String? labTestTypeName;
//   final String? notes;
//   final bool? passed;
//   final double? quantity;

//   // Create model.
//   factory LabTestResult.fromMap(Map<String, dynamic> data) {
//     return LabTestResult(
//       id: data['id'].toString(),
//       labTestTypeName: data['lab_test_type_name'] ?? '',
//       notes: data['notes'] ?? '',
//       passed: data['passed'] ?? false,
//       quantity: data['quantity'] ?? 0.0,
//     );
//   }

//   // Create JSON.
//   Map<String, dynamic> toMap() {
//     return <String, dynamic>{
//       'id': id,
//       'lab_test_type_name': labTestTypeName,
//       'notes': notes,
//       'passed': passed,
//       'quantity': quantity,
//     };
//   }
// }

// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 3/2/2023
// Updated: 9/12/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Package imports:
// import 'package:equatable/equatable.dart';

// Dart imports:
import 'dart:convert';

// Project imports:
import 'package:cannlytics_data/utils/utils.dart';

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
    this.labLicenseNumber,
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
    this.dateHarvested,
    this.datePackaged,
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
    this.coaUrls,
    this.labResultsUrl,
    this.jobFileUrl,
    this.public,
    this.labelColor,
    this.cannabinoidType,
  });

  // Properties.
  final String? labId;
  final String? batchNumber;
  final String? productName;
  final String? businessDbaName;
  final String? lims;
  final String? lab;
  final String? labLicenseNumber;
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
  final String? dateHarvested;
  final String? datePackaged;
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
  final List<Result?>? results;
  final String? coaAlgorithm;
  final String? coaAlgorithmVersion;
  final String? coaParsedAt;
  final String? resultsHash;
  final String? sampleHash;
  final String? warning;
  final String? fileRef;
  final String? downloadUrl;
  final String? shortUrl;
  final dynamic coaUrls;
  final String? labResultsUrl;
  final String? jobFileUrl;
  final bool? public;
  final String? labelColor;
  final String? cannabinoidType;

  // @override
  // List<String?> get props => [labId];

  // Create model.
  factory LabResult.fromMap(Map data) {
// Standardize results.
    List<Result?>? results;

    List<dynamic>? cleanAndDecode(String resultsJson) {
      dynamic decodedData = resultsJson;

      // Try decoding up to 3 times.
      for (int i = 0; i < 3; i++) {
        try {
          decodedData = jsonDecode(decodedData);
          if (decodedData is List<dynamic>) {
            return decodedData;
          }
        } catch (e) {
          print("Error decoding at level ${i + 1}: $e");
          break;
        }
      }

      print("Failed to parse the data.");
      return null;
    }

// Parse results.
    final resultsData = cleanAndDecode(data['results']);
    if (resultsData != null) {
      results = resultsData
          .map((result) => Result.fromMap(result as Map<String, dynamic>))
          .toList();
    } else {
      print("Failed to parse the data.");
    }
    // print('\n\nLAB RESULT DATA:');
    // print(data);

    return LabResult(
      labId: data['lab_id'],
      batchNumber: data['batch_number'],
      productName: data['product_name'],
      businessDbaName: data['business_dba_name'],
      lims: data['lims'],
      lab: data['lab'],
      labLicenseNumber: data['lab_license_number'],
      labImageUrl: data['lab_image_url'],
      labAddress: data['lab_address'],
      labStreet: data['lab_street'],
      labCity: data['lab_city'],
      labCounty: data['lab_county'],
      labState: data['lab_state'],
      labZipcode: data['lab_zipcode']?.toString(),
      labPhone: data['lab_phone'],
      labEmail: data['lab_email'],
      labWebsite: data['lab_website'],
      labLatitude: DataUtils.formatNumber(data['lab_latitude']),
      labLongitude: DataUtils.formatNumber(data['lab_longitude']),
      licensingAuthorityId: data['licensing_authority_id'],
      licensingAuthority: data['licensing_authority'],
      analyses: DataUtils.formatList(data['analyses']),
      analysisStatus: data['analysis_status'],
      methods: DataUtils.formatList(data['methods']),
      dateCollected: data['date_collected'],
      dateTested: data['date_tested'],
      dateReceived: data['date_received'],
      dateHarvested: data['date_harvested'],
      datePackaged: data['date_packaged'],
      distributor: data['distributor'],
      distributorAddress: data['distributor_address'],
      distributorStreet: data['distributor_street'],
      distributorCity: data['distributor_city'],
      distributorState: data['distributor_state'],
      distributorZipcode: data['distributor_zipcode'],
      distributorLicenseNumber: data['distributor_license_number'],
      producer: data['producer'],
      producerLicenseNumber: data['producer_license_number'],
      producerAddress: data['producer_address'],
      producerStreet: data['producer_street'],
      producerCity: data['producer_city'],
      producerState: data['producer_state'],
      producerZipcode: data['producer_zipcode'],
      productType: data['product_type'],
      traceabilityIds: DataUtils.formatList(data['traceability_ids']),
      productSize: DataUtils.formatInt(data['product_size']),
      servingSize: DataUtils.formatInt(data['serving_size']),
      servingsPerPackage: DataUtils.formatInt(data['servings_per_package']),
      sampleWeight: DataUtils.formatNumber(data['sample_weight']),
      totalCannabinoids: DataUtils.formatNumber(data['total_cannabinoids']),
      totalThc: DataUtils.formatNumber(data['total_thc']),
      totalCbd: DataUtils.formatNumber(data['total_cbd']),
      totalTerpenes: DataUtils.formatNumber(data['total_terpenes']),
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
      fileRef: data['file_ref'],
      downloadUrl: data['download_url'],
      shortUrl: data['short_url'],
      coaUrls: DataUtils.formatListOfMaps(data['coa_urls']),
      labResultsUrl: data['lab_results_url'],
      jobFileUrl: data['job_file_url'],
      public: data['public'] == true || data['public'] == 1 ? true : false,
      labelColor: data['label_color'],
      cannabinoidType: data['cannabinoid_type'],
    );
  }

  // Create JSON.
  Map<String, dynamic> toMap() {
    // Convert results to JSON.
    List<Map<String, dynamic>> mapResults =
        results?.map((result) => result!.toMap()).toList() ?? [];
    String jsonEncodedResults = jsonEncode(mapResults);

    return <String, dynamic>{
      'lab_id': labId,
      'batch_number': batchNumber,
      'product_name': productName,
      'business_dba_name': businessDbaName,
      'lims': lims,
      'lab': lab,
      'lab_license_number': labLicenseNumber,
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
      'date_harvested': dateHarvested,
      'date_packaged': datePackaged,
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
      'coa_algorithm': coaAlgorithm,
      'coa_algorithm_version': coaAlgorithmVersion,
      'coa_parsed_at': coaParsedAt,
      'results_hash': resultsHash,
      'sample_hash': sampleHash,
      'warning': warning,
      'file_ref': fileRef,
      'download_url': downloadUrl,
      'short_url': shortUrl,
      'coa_urls': coaUrls,
      'lab_results_url': labResultsUrl,
      'job_file_url': jobFileUrl,
      'public': public,
      'label_color': labelColor,
      'cannabinoid_type': cannabinoidType,
      'results': jsonEncodedResults,
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
  final dynamic value;
  final dynamic mg_g;
  final String? units;
  final double? limit;
  final double? lod;
  final double? loq;
  final String? status;

  // Create model.
  factory Result.fromMap(Map<dynamic, dynamic> data) {
    return Result(
      analysis: data['analysis'] as String?,
      key: data['key'] as String?,
      name: data['name'] as String?,
      value: DataUtils.formatNumber(data['value']),
      mg_g: DataUtils.formatNumber(data['mg_g']),
      units: data['units'] as String?,
      limit: DataUtils.formatNumber(data['limit']),
      lod: DataUtils.formatNumber(data['lod']),
      loq: DataUtils.formatNumber(data['loq']),
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

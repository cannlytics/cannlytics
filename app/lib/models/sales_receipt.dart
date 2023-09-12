// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 3/2/2023
// Updated: 9/12/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

import 'package:cannlytics_data/utils/utils.dart';

/// A sales receipt model.
class SalesReceipt {
  // Initialization.
  const SalesReceipt({
    this.hash,
    this.receiptNumber,
    this.salesDateTime,
    this.salesCustomerType,
    this.patientLicenseNumber,
    this.caregiverLicenseNumber,
    this.identificationMethod,
    this.patientRegistrationLocationId,
    this.totalPackages,
    this.totalPrice,
    this.transactions,
    this.isFinal,
    this.archivedDate,
    this.recordedDateTime,
    this.recordedByUserName,
    this.lastModified,
    this.dateSold,
    this.strainNames,
    this.productNames,
    this.productTypes,
    this.productQuantities,
    this.productPrices,
    this.productIds,
    this.totalAmount,
    this.subtotal,
    this.totalDiscount,
    this.totalPaid,
    this.changeDue,
    this.rewardsEarned,
    this.rewardsSpent,
    this.totalRewards,
    this.cityTax,
    this.countyTax,
    this.stateTax,
    this.exciseTax,
    this.retailer,
    this.retailerLicenseNumber,
    this.retailerAddress,
    this.retailerStreet,
    this.retailerCity,
    this.retailerState,
    this.retailerZipcode,
    this.budtender,
    this.totalTax,
    this.totalTransactions,
    this.parsedAt,
    this.algorithm,
    this.algorithmVersion,
    this.warning,
    this.fileRef,
    this.downloadUrl,
    this.shortUrl,
  });

  // Properties.
  final String? hash;
  final String? receiptNumber;
  final String? salesDateTime;
  final String? salesCustomerType;
  final String? patientLicenseNumber;
  final String? caregiverLicenseNumber;
  final String? identificationMethod;
  final String? patientRegistrationLocationId;
  final int? totalPackages;
  final double? totalPrice;
  final List<dynamic>? transactions;
  final bool? isFinal;
  final String? archivedDate;
  final String? recordedDateTime;
  final String? recordedByUserName;
  final String? lastModified;
  final DateTime? dateSold;
  final List<dynamic>? strainNames;
  final List<dynamic>? productNames;
  final List<dynamic>? productTypes;
  final List<int>? productQuantities;
  final List<double>? productPrices;
  final List<dynamic>? productIds;
  final double? totalAmount;
  final double? subtotal;
  final double? totalDiscount;
  final double? totalPaid;
  final double? changeDue;
  final double? rewardsEarned;
  final double? rewardsSpent;
  final double? totalRewards;
  final double? cityTax;
  final double? countyTax;
  final double? stateTax;
  final double? exciseTax;
  final String? retailer;
  final String? retailerLicenseNumber;
  final String? retailerAddress;
  final String? retailerStreet;
  final String? retailerCity;
  final String? retailerState;
  final String? retailerZipcode;
  final String? budtender;
  final double? totalTax;
  final double? totalTransactions;
  final DateTime? parsedAt;
  final String? algorithm;
  final String? algorithmVersion;
  final String? warning;
  final String? fileRef;
  final String? downloadUrl;
  final String? shortUrl;

  // Create model.
  factory SalesReceipt.fromMap(Map<dynamic, dynamic> data) {
    return SalesReceipt(
      hash: data['hash'] ?? '',
      receiptNumber: data['receipt_number'] as String?,
      salesDateTime: data['sales_date_time'] as String?,
      salesCustomerType: data['sales_customer_type'] as String?,
      patientLicenseNumber: data['patient_license_number'] as String?,
      caregiverLicenseNumber: data['caregiver_license_number'] as String?,
      identificationMethod: data['identification_method'] as String?,
      patientRegistrationLocationId:
          data['patient_registration_location_id'] as String?,
      totalPackages: DataUtils.formatInt(data['total_packages']),
      totalPrice: DataUtils.formatNumber(data['total_price']),
      transactions: data['transactions'] as List<dynamic>?,
      isFinal: data['is_final'] as bool?,
      archivedDate: data['archived_date'] as String?,
      recordedDateTime: data['recorded_date_time'] as String?,
      recordedByUserName: data['recorded_by_user_name'] as String?,
      lastModified: data['last_modified'] as String?,
      dateSold: DateTime.parse(data['date_sold'] as String? ?? ''),
      strainNames:
          List<String>.from(data['strain_names'] as List<dynamic>? ?? []),
      productNames:
          List<String>.from(data['product_names'] as List<dynamic>? ?? []),
      productTypes:
          List<String>.from(data['product_types'] as List<dynamic>? ?? []),
      productQuantities:
          List<int>.from(data['product_quantities'] as List<dynamic>? ?? []),
      productPrices:
          List<double>.from(data['product_prices'] as List<dynamic>? ?? []),
      productIds:
          List<String>.from(data['product_ids'] as List<dynamic>? ?? []),
      totalAmount: DataUtils.formatNumber(data['total_amount']),
      subtotal: DataUtils.formatNumber(data['subtotal']),
      totalDiscount: DataUtils.formatNumber(data['total_discount']),
      totalPaid: DataUtils.formatNumber(data['total_paid']),
      changeDue: DataUtils.formatNumber(data['change_due']),
      rewardsEarned: DataUtils.formatNumber(data['rewards_earned']),
      rewardsSpent: DataUtils.formatNumber(data['rewards_spent']),
      totalRewards: DataUtils.formatNumber(data['total_rewards']),
      cityTax: DataUtils.formatNumber(data['city_tax']),
      countyTax: DataUtils.formatNumber(data['county_tax']),
      stateTax: DataUtils.formatNumber(data['state_tax']),
      exciseTax: DataUtils.formatNumber(data['excise_tax']),
      retailer: data['retailer'] as String?,
      retailerLicenseNumber: data['retailer_license_number'] as String?,
      retailerAddress: data['retailer_address'],
      retailerStreet: data['retailer_street'],
      retailerCity: data['retailer_city'],
      retailerState: data['retailer_state'],
      retailerZipcode: data['retailer_zipcode'],
      budtender: data['budtender'] as String?,
      totalTax: DataUtils.formatNumber(data['total_tax']),
      totalTransactions: DataUtils.formatNumber(data['total_transactions']),
      parsedAt: DateTime.parse(data['parsed_at'] as String? ?? ''),
      algorithm: data['algorithm'] as String?,
      algorithmVersion: data['algorithm_version'] as String?,
      warning: data['warning'] as String?,
      fileRef: data['file_ref'] as String?,
      downloadUrl: data['download_url'] as String?,
      shortUrl: data['short_url'] as String?,
    );
  }

  // Create JSON.
  Map<String, dynamic> toMap() {
    return <String, dynamic>{
      'hash': hash,
      'receipt_number': receiptNumber,
      'sales_date_time': salesDateTime,
      'sales_customer_type': salesCustomerType,
      'patient_license_number': patientLicenseNumber,
      'caregiver_license_number': caregiverLicenseNumber,
      'identification_method': identificationMethod,
      'patient_registration_location_id': patientRegistrationLocationId,
      'total_packages': totalPackages,
      'total_price': totalPrice,
      'transactions': transactions,
      'is_final': isFinal,
      'archived_date': archivedDate,
      'recorded_date_time': recordedDateTime,
      'recorded_by_user_name': recordedByUserName,
      'last_modified': lastModified,
      'date_sold': dateSold?.toIso8601String(),
      'strain_names': strainNames,
      'product_names': productNames,
      'product_types': productTypes,
      'product_quantities': productQuantities,
      'product_prices': productPrices,
      'product_ids': productIds,
      'total_amount': totalAmount,
      'subtotal': subtotal,
      'total_discount': totalDiscount,
      'total_paid': totalPaid,
      'change_due': changeDue,
      'rewards_earned': rewardsEarned,
      'rewards_spent': rewardsSpent,
      'total_rewards': totalRewards,
      'city_tax': cityTax,
      'county_tax': countyTax,
      'state_tax': stateTax,
      'excise_tax': exciseTax,
      'retailer': retailer,
      'retailer_license_number': retailerLicenseNumber,
      'retailer_address': retailerAddress,
      'retailer_street': retailerStreet,
      'retailer_city': retailerCity,
      'retailer_state': retailerState,
      'retailer_zipcode': retailerZipcode,
      'budtender': budtender,
      'total_tax': totalTax,
      'total_transactions': totalTransactions,
      'parsed_at': parsedAt?.toIso8601String(),
      'algorithm': algorithm,
      'algorithm_version': algorithmVersion,
      'warning': warning,
      'file_ref': fileRef,
      'download_url': downloadUrl,
      'short_url': shortUrl,
    };
  }
}

// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 3/2/2023
// Updated: 3/17/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

typedef SalesReceiptId = String;

class SalesReceipt {
  // Initialization.
  const SalesReceipt({
    this.id,
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
  });

  // Properties.
  final SalesReceiptId? id;
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

  // Create model.
  factory SalesReceipt.fromMap(Map<String, dynamic> data) {
    return SalesReceipt(
      id: data['id'] ?? '',
      receiptNumber: data['receipt_number'] as String?,
      salesDateTime: data['sales_date_time'] as String?,
      salesCustomerType: data['sales_customer_type'] as String?,
      patientLicenseNumber: data['patient_license_number'] as String?,
      caregiverLicenseNumber: data['caregiver_license_number'] as String?,
      identificationMethod: data['identification_method'] as String?,
      patientRegistrationLocationId:
          data['patient_registration_location_id'] as String?,
      totalPackages: data['total_packages'] as int?,
      totalPrice: data['total_price'] as double?,
      transactions: data['transactions'] as List<dynamic>?,
      isFinal: data['is_final'] as bool?,
      archivedDate: data['archived_date'] as String?,
      recordedDateTime: data['recorded_date_time'] as String?,
      recordedByUserName: data['recorded_by_user_name'] as String?,
      lastModified: data['last_modified'] as String?,
    );
  }

  // Create JSON.
  Map<String, dynamic> toMap() {
    return <String, dynamic>{
      'id': id,
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
    };
  }

  // // Create Sales Receipt.
  // Future<void> create() async {
  //   // Call an API or database to create a new sales receipt.
  //   // await MetrcService.createSalesReceipt(this.toMap());
  // }

  // // Update Sales Receipt.
  // Future<void> update() async {
  //   // Call an API or database to update the existing sales receipt.
  //   // await MetrcService.updateSalesReceipt(this.toMap());
  // }

  // // Delete Sales Receipt.
  // Future<void> delete() async {
  //   // Call an API or database to delete the existing sales receipt.
  //   // await MetrcService.deleteSalesReceipt(this.toMap());
  // }
}

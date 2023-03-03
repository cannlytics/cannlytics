// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 3/2/2023
// Updated: 3/2/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Project imports:
import 'package:cannlytics_app/services/metrc_service.dart';

typedef SalesReceiptId = String;

class SalesReceipt {
  // Initialization.
  const SalesReceipt({
    required this.caregiverLicenseNumber,
    required this.identificationMethod,
    required this.patientLicenseNumber,
    required this.patientRegistrationLocationId,
    required this.salesCustomerType,
    required this.salesDateTime,
    required this.transactions,
  });
  // Properties.
  final String caregiverLicenseNumber;
  final String identificationMethod;
  final String patientLicenseNumber;
  final String patientRegistrationLocationId;
  final String salesCustomerType;
  final DateTime salesDateTime;
  final List<dynamic> transactions;
  // Create model.
  factory SalesReceipt.fromMap(Map<String, dynamic> data) {
    return SalesReceipt(
      caregiverLicenseNumber: data['caregiver_license_number'] as String,
      identificationMethod: data['identification_method'] as String,
      patientLicenseNumber: data['patient_license_number'] as String,
      patientRegistrationLocationId:
          data['patient_registration_location_id'] as String,
      salesCustomerType: data['sales_customer_type'] as String,
      salesDateTime: data['sales_date_time'] as DateTime,
      transactions: data['transactions'] as List<dynamic>,
    );
  }
  // Create JSON.
  Map<String, dynamic> toMap() {
    return <String, dynamic>{
      'caregiver_license_number': caregiverLicenseNumber,
      'identification_method': identificationMethod,
      'patient_license_number': patientLicenseNumber,
      'patient_registration_location_id': patientRegistrationLocationId,
      'sales_customer_type': salesCustomerType,
      'sales_date_time': salesDateTime,
      'transactions': transactions,
    };
  }

  // Create Sales Receipt.
  Future<void> create() async {
    // Call an API or database to create a new sales receipt.
    // await MetrcService.createSalesReceipt(this.toMap());
  }

  // Update Sales Receipt.
  Future<void> update() async {
    // Call an API or database to update the existing sales receipt.
    // await MetrcService.updateSalesReceipt(this.toMap());
  }

  // Delete Sales Receipt.
  Future<void> delete() async {
    // Call an API or database to delete the existing sales receipt.
    // await MetrcService.deleteSalesReceipt(this.toMap());
  }
}

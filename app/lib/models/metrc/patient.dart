// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 2/27/2023
// Updated: 3/8/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Project imports:
import 'package:cannlytics_app/services/metrc_service.dart';

typedef PatientId = String;

/// Model representing a patient.
class Patient {
  // Initialization.
  const Patient({
    required this.id,
    required this.licenseNumber,
    required this.registrationDate,
    required this.licenseEffectiveStartDate,
    required this.licenseEffectiveEndDate,
    required this.recommendedPlants,
    required this.recommendedSmokableQuantity,
    required this.hasSalesLimitExemption,
    required this.otherFacilitiesCount,
  });

  // Properties.
  final PatientId id;
  final String licenseNumber;
  final DateTime registrationDate;
  final DateTime licenseEffectiveStartDate;
  final DateTime licenseEffectiveEndDate;
  final int recommendedPlants;
  final double recommendedSmokableQuantity;
  final bool hasSalesLimitExemption;
  final int otherFacilitiesCount;

  // Create model.
  factory Patient.fromMap(Map<String, dynamic> data) {
    return Patient(
      id: data['id'] ?? '',
      licenseNumber: data['license_number'] as String,
      registrationDate: DateTime.parse(data['registration_date'] as String),
      licenseEffectiveStartDate:
          DateTime.parse(data['license_effective_start_date'] as String),
      licenseEffectiveEndDate:
          DateTime.parse(data['license_effective_end_date'] as String),
      recommendedPlants: data['recommended_plants'] as int,
      recommendedSmokableQuantity:
          data['recommended_smokable_quantity'] as double,
      hasSalesLimitExemption: data['has_sales_limit_exemption'] as bool,
      otherFacilitiesCount: data['other_facilities_count'] as int,
    );
  }

  // Create JSON.
  Map<String, dynamic> toMap() {
    return <String, dynamic>{
      'id': id,
      'license_number': licenseNumber,
      'registration_date': registrationDate.toIso8601String(),
      'license_effective_start_date':
          licenseEffectiveStartDate.toIso8601String(),
      'license_effective_end_date': licenseEffectiveEndDate.toIso8601String(),
      'recommended_plants': recommendedPlants,
      'recommended_smokable_quantity': recommendedSmokableQuantity,
      'has_sales_limit_exemption': hasSalesLimitExemption,
      'other_facilities_count': otherFacilitiesCount,
    };
  }

  // Create Patient.
  Future<void> create() async {
    // Call an API or database to create a new patient.
    // await MetrcService.createPatient(this.toMap());
  }

  // Update Patient.
  Future<void> update() async {
    // Call an API or database to update the existing patient.
    // await MetrcService.updatePatient(this.id, this.toMap());
  }

  // Delete Patient.
  Future<void> delete() async {
    // Call an API or database to delete the existing patient.
    // await MetrcService.deletePatient(this.id);
  }
}

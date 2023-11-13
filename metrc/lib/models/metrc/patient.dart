// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 2/27/2023
// Updated: 3/8/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

typedef PatientId = String?;

/// Model representing a patient.
class Patient {
  // Initialization.
  const Patient({
    this.id,
    this.licenseNumber,
    this.registrationDate,
    this.licenseEffectiveStartDate,
    this.licenseEffectiveEndDate,
    this.recommendedPlants,
    this.recommendedSmokableQuantity,
    this.hasSalesLimitExemption,
    this.otherFacilitiesCount,
  });

  // Properties.
  final PatientId id;
  final String? licenseNumber;
  final String? registrationDate;
  final String? licenseEffectiveStartDate;
  final String? licenseEffectiveEndDate;
  final int? recommendedPlants;
  final double? recommendedSmokableQuantity;
  final bool? hasSalesLimitExemption;
  final int? otherFacilitiesCount;

  // Create model.
  factory Patient.fromMap(Map<String, dynamic> data) {
    return Patient(
      id: data['id'].toString(),
      licenseNumber: data['license_number'] ?? '',
      registrationDate: data['registration_date'] ?? '',
      licenseEffectiveStartDate: data['license_effective_start_date'] ?? '',
      licenseEffectiveEndDate: data['license_effective_end_date'] ?? '',
      recommendedPlants: data['recommended_plants'] ?? 0,
      recommendedSmokableQuantity: data['recommended_smokable_quantity'] ?? 0,
      hasSalesLimitExemption: data['has_sales_limit_exemption'] ?? false,
      otherFacilitiesCount: data['other_facilities_count'] ?? 0,
    );
  }

  // Create JSON.
  Map<String, dynamic> toMap() {
    return <String, dynamic>{
      'id': id,
      'license_number': licenseNumber,
      'registration_date': registrationDate,
      'license_effective_start_date': licenseEffectiveStartDate,
      'license_effective_end_date': licenseEffectiveEndDate,
      'recommended_plants': recommendedPlants,
      'recommended_smokable_quantity': recommendedSmokableQuantity,
      'has_sales_limit_exemption': hasSalesLimitExemption,
      'other_facilities_count': otherFacilitiesCount,
    };
  }

  // // Create Patient.
  // Future<void> create() async {
  //   // Call an API or database to create a new patient.
  //   // await MetrcService.createPatient(this.toMap());
  // }

  // // Update Patient.
  // Future<void> update() async {
  //   // Call an API or database to update the existing patient.
  //   // await MetrcService.updatePatient(this.id, this.toMap());
  // }

  // // Delete Patient.
  // Future<void> delete() async {
  //   // Call an API or database to delete the existing patient.
  //   // await MetrcService.deletePatient(this.id);
  // }
}

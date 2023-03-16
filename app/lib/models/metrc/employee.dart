// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 2/27/2023
// Updated: 3/16/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

/// Model representing an employee.
class Employee {
  // Initialization.
  const Employee({
    required this.fullName,
    this.licenseNumber,
    this.licenseStartDate,
    this.licenseEndDate,
    this.licenseType,
  });

  // Properties.
  final String? fullName;
  final String? licenseNumber;
  final String? licenseStartDate;
  final String? licenseEndDate;
  final String? licenseType;

  // Create model.
  factory Employee.fromMap(Map<String, dynamic> data) {
    return Employee(
      fullName: data['full_name'] ?? '',
      licenseNumber: data['license']['number'] ?? '',
      licenseStartDate: data['license']['start_date'] ?? '',
      licenseEndDate: data['license']['end_date'] ?? '',
      licenseType: data['license']['license_type'] ?? '',
    );
  }

  // Create JSON.
  Map<String, dynamic> toMap() {
    return <String, dynamic>{
      'full_name': fullName,
      'license': {
        'number': licenseNumber,
        'start_date': licenseStartDate,
        'end_date': licenseEndDate,
        'license_type': licenseType,
      },
    };
  }
}

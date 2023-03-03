// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 2/27/2023
// Updated: 2/27/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Project imports:
import 'package:cannlytics_app/services/metrc_service.dart';

typedef EmployeeId = String;

/// Model representing an employee.
class Employee {
  // Initialization.
  const Employee({
    required this.id,
    required this.fullName,
    required this.license,
  });

  // Properties.
  final EmployeeId id;
  final String fullName;
  final String license;

  // Create model.
  factory Employee.fromMap(Map<String, dynamic> data, String uid) {
    return Employee(
      id: uid,
      fullName: data['full_name'] as String,
      license: data['license'] as String,
    );
  }

  // Create JSON.
  Map<String, dynamic> toMap() {
    return <String, dynamic>{
      'id': id,
      'full_name': fullName,
      'license': license,
    };
  }

  // Create Employee.
  Future<void> create() async {
    // Call an API or database to create a new employee.
    // await MetrcService.createEmployee(this.toMap());
  }

  // Update Employee.
  Future<void> update() async {
    // Call an API or database to update the existing employee.
    // await MetrcService.updateEmployee(this.id, this.toMap());
  }

  // Delete Employee.
  Future<void> delete() async {
    // Call an API or database to delete the existing employee.
    // await MetrcService.deleteEmployee(this.id);
  }
}

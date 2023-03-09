// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 3/8/2023
// Updated: 3/8/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Project imports:
import 'package:cannlytics_app/services/metrc_service.dart';

typedef TransferId = String;

/// Model representing an employee.
class Transfer {
  // Initialization.
  const Transfer({
    required this.id,
    required this.fullName,
    required this.license,
  });

  // Properties.
  final TransferId id;
  final String fullName;
  final String license;

  // Create model.
  factory Transfer.fromMap(Map<String, dynamic> data) {
    return Transfer(
      id: data['id'] ?? '',
      fullName: data['full_name'] ?? '',
      license: data['license'] ?? '',
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

  // Create Transfer.
  Future<void> create() async {
    // Call an API or database to create a new employee.
    // await MetrcService.createTransfer(this.toMap());
  }

  // Update Transfer.
  Future<void> update() async {
    // Call an API or database to update the existing employee.
    // await MetrcService.updateTransfer(this.id, this.toMap());
  }

  // Delete Transfer.
  Future<void> delete() async {
    // Call an API or database to delete the existing employee.
    // await MetrcService.deleteTransfer(this.id);
  }
}

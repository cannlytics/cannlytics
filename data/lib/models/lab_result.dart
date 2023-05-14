// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 3/2/2023
// Updated: 3/18/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Project imports:
import 'package:cannlytics_app/services/metrc_service.dart';

typedef LabResultId = String;

/// Model representing a lab result.
class LabResult {
  // Initialization.
  const LabResult({
    this.id,
    this.labTestTypeName,
    this.notes,
    this.passed,
    this.quantity,
  });

  // Properties.
  final LabResultId? id;
  final String? labTestTypeName;
  final String? notes;
  final bool? passed;
  final double? quantity;

  // Create model.
  factory LabResult.fromMap(Map<String, dynamic> data) {
    return LabResult(
      id: data['id'].toString(),
      labTestTypeName: data['lab_test_type_name'] ?? '',
      notes: data['notes'] ?? '',
      passed: data['passed'] ?? false,
      quantity: data['quantity'] ?? 0.0,
    );
  }

  // Create JSON.
  Map<String, dynamic> toMap() {
    return <String, dynamic>{
      'id': id,
      'lab_test_type_name': labTestTypeName,
      'notes': notes,
      'passed': passed,
      'quantity': quantity,
    };
  }

  // // Create LabResult.
  // Future<void> create() async {
  //   // Call an API or database to create a new lab result.
  //   // await Metrc.createLabResult(this.toMap());
  // }

  // // Update LabResult.
  // Future<void> update() async {
  //   // Call an API or database to update the existing lab result.
  //   // await Metrc.updateLabResult(this.id, this.toMap());
  // }

  // // Delete LabResult.
  // Future<void> delete() async {
  //   // Call an API or database to delete the existing lab result.
  //   // await Metrc.deleteLabResult(this.id);
  // }
}

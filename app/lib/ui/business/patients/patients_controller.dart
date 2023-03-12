// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 3/8/2023
// Updated: 3/8/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Package imports:
import 'package:flutter_riverpod/flutter_riverpod.dart';

// Project imports:
import 'package:cannlytics_app/models/metrc/patient.dart';
import 'package:cannlytics_app/services/metrc_service.dart';
import 'package:cannlytics_app/ui/main/app_controller.dart';

// Patients rows per page provider.
final patientsRowsPerPageProvider = StateProvider<int>((ref) => 5);

// Patients provider.
final patientsProvider =
    AsyncNotifierProvider<PatientsController, List<Patient>>(() {
  return PatientsController();
});

/// Patients controller.
class PatientsController extends AsyncNotifier<List<Patient>> {
  @override
  Future<List<Patient>> build() async {
    // Load initial data from Metrc.
    return _getPatients();
  }

  /// Get patients.
  Future<List<Patient>> _getPatients() async {
    // final licenseNumber = ref.watch(primaryLicenseProvider);
    final licenseNumber = '010-X0001';
    final orgId = ref.watch(primaryOrganizationProvider);
    final state = ref.watch(primaryStateProvider);
    try {
      // FIXME:
      // return await MetrcPatients.getPatients(
      //   licenseNumber: licenseNumber,
      //   orgId: orgId,
      //   state: state,
      // );
      return [];
    } catch (error, stack) {
      print(stack);
      throw Exception("Error decoding JSON: [error=${error.toString()}]");
    }
  }

  // TODO: Get patient.

  // TODO: Create patient.

  // TODO: Update patient.

  // TODO: Delete patient.
}

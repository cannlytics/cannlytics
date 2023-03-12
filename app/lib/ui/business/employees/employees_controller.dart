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
import 'package:cannlytics_app/models/metrc/employee.dart';
import 'package:cannlytics_app/services/metrc_service.dart';
import 'package:cannlytics_app/ui/main/app_controller.dart';

// Employees rows per page provider.
final employeesRowsPerPageProvider = StateProvider<int>((ref) => 5);

// Employees provider.
final employeesProvider =
    AsyncNotifierProvider<EmployeesController, List<Employee>>(() {
  return EmployeesController();
});

/// Employees controller.
class EmployeesController extends AsyncNotifier<List<Employee>> {
  @override
  Future<List<Employee>> build() async {
    // Load initial data from Metrc.
    return _getEmployees();
  }

  /// Get employees.
  Future<List<Employee>> _getEmployees() async {
    // final licenseNumber = ref.watch(primaryLicenseProvider);
    final licenseNumber = '010-X0001';
    final orgId = ref.watch(primaryOrganizationProvider);
    final state = ref.watch(primaryStateProvider);
    try {
      // FIXME:
      // return await MetrcEmployees.getEmployees(
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

  // TODO: Get delivery.

  // TODO: Create delivery.

  // TODO: Update delivery.

  // TODO: Delete delivery.
}

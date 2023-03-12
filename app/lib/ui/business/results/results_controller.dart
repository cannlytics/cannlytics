// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 3/9/2023
// Updated: 3/9/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Package imports:
import 'package:flutter_riverpod/flutter_riverpod.dart';

// Project imports:
import 'package:cannlytics_app/models/metrc/lab_result.dart';
import 'package:cannlytics_app/services/metrc_service.dart';
import 'package:cannlytics_app/ui/main/app_controller.dart';

// Results rows per page provider.
final resultsRowsPerPageProvider = StateProvider<int>((ref) => 5);

// Results provider.
final resultsProvider =
    AsyncNotifierProvider<ResultsController, List<LabResult>>(() {
  return ResultsController();
});

/// Results controller.
class ResultsController extends AsyncNotifier<List<LabResult>> {
  @override
  Future<List<LabResult>> build() async {
    // Load initial data from Metrc.
    return _getResults();
  }

  /// Get results.
  Future<List<LabResult>> _getResults() async {
    // final licenseNumber = ref.watch(primaryLicenseProvider);
    final licenseNumber = '010-X0001';
    final orgId = ref.watch(primaryOrganizationProvider);
    final state = ref.watch(primaryStateProvider);
    try {
      // FIXME:
      // return await MetrcResults.getResults(
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

  // TODO: Get strain.

  // TODO: Create strain.

  // TODO: Update strain.

  // TODO: Delete strain.
}

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
import 'package:cannlytics_app/models/metrc/transfer.dart';
import 'package:cannlytics_app/services/metrc_service.dart';
import 'package:cannlytics_app/ui/general/app_controller.dart';

// Transfers rows per page provider.
final transfersRowsPerPageProvider = StateProvider<int>((ref) => 5);

// Transfers provider.
final transfersProvider =
    AsyncNotifierProvider<TransfersController, List<Transfer>>(() {
  return TransfersController();
});

/// Transfers controller.
class TransfersController extends AsyncNotifier<List<Transfer>> {
  @override
  Future<List<Transfer>> build() async {
    // Load initial data from Metrc.
    return _getTransfers();
  }

  /// Get transfers.
  Future<List<Transfer>> _getTransfers() async {
    // final licenseNumber = ref.watch(primaryLicenseProvider);
    final licenseNumber = '010-X0001';
    final orgId = ref.watch(primaryOrganizationProvider);
    final state = ref.watch(primaryStateProvider);
    try {
      // FIXME:
      // return await MetrcTransfers.getTransfers(
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

  // TODO: Get transfer.

  // TODO: Create transfer.

  // TODO: Update transfer.

  // TODO: Delete transfer.
}

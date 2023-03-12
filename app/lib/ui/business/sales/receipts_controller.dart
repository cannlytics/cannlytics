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
import 'package:cannlytics_app/models/metrc/sales_receipt.dart';
import 'package:cannlytics_app/services/metrc_service.dart';
import 'package:cannlytics_app/ui/main/app_controller.dart';

// Receipts rows per page provider.
final receiptsRowsPerPageProvider = StateProvider<int>((ref) => 5);

// Receipts provider.
final receiptsProvider =
    AsyncNotifierProvider<ReceiptsController, List<SalesReceipt>>(() {
  return ReceiptsController();
});

/// Receipts controller.
class ReceiptsController extends AsyncNotifier<List<SalesReceipt>> {
  @override
  Future<List<SalesReceipt>> build() async {
    // Load initial data from Metrc.
    return _getReceipts();
  }

  /// Get receipts.
  Future<List<SalesReceipt>> _getReceipts() async {
    // final licenseNumber = ref.watch(primaryLicenseProvider);
    final licenseNumber = '010-X0001';
    final orgId = ref.watch(primaryOrganizationProvider);
    final state = ref.watch(primaryStateProvider);
    try {
      // FIXME:
      // return await MetrcReceipts.getReceipts(
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

  // TODO: Get receipt.

  // TODO: Create receipt.

  // TODO: Update receipt.

  // TODO: Delete receipt.
}

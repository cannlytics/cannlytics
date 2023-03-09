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
import 'package:cannlytics_app/models/metrc/sales_transaction.dart';
import 'package:cannlytics_app/services/metrc_service.dart';
import 'package:cannlytics_app/ui/general/app_controller.dart';

// Transactions rows per page provider.
final transactionsRowsPerPageProvider = StateProvider<int>((ref) => 5);

// Transactions provider.
final transactionsProvider =
    AsyncNotifierProvider<TransactionsController, List<SalesTransaction>>(() {
  return TransactionsController();
});

/// Transactions controller.
class TransactionsController extends AsyncNotifier<List<SalesTransaction>> {
  @override
  Future<List<SalesTransaction>> build() async {
    // Load initial data from Metrc.
    return _getTransactions();
  }

  /// Get transactions.
  Future<List<SalesTransaction>> _getTransactions() async {
    // final licenseNumber = ref.watch(primaryLicenseProvider);
    final licenseNumber = '010-X0001';
    final orgId = ref.watch(primaryOrganizationProvider);
    final state = ref.watch(primaryStateProvider);
    try {
      // FIXME:
      // return await MetrcTransactions.getTransactions(
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

  // TODO: Get transaction.

  // TODO: Create transaction.

  // TODO: Update transaction.

  // TODO: Delete transaction.
}

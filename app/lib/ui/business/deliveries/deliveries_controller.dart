// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 3/7/2023
// Updated: 3/8/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Package imports:
import 'package:cannlytics_app/models/metrc/delivery.dart';
import 'package:cannlytics_app/services/metrc_service.dart';
import 'package:cannlytics_app/ui/general/app_controller.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

// Deliveries rows per page provider.
final deliveriesRowsPerPageProvider = StateProvider<int>((ref) => 5);

// Deliveries provider.
final deliveriesProvider =
    AsyncNotifierProvider<DeliveriesController, List<Delivery>>(() {
  return DeliveriesController();
});

/// Deliveries controller.
class DeliveriesController extends AsyncNotifier<List<Delivery>> {
  @override
  Future<List<Delivery>> build() async {
    // Load initial data from Metrc.
    return _getDeliveries();
  }

  /// Get deliveries.
  Future<List<Delivery>> _getDeliveries() async {
    // final licenseNumber = ref.watch(primaryLicenseProvider);
    final licenseNumber = '010-X0001';
    final orgId = ref.watch(primaryOrganizationProvider);
    final state = ref.watch(primaryStateProvider);
    try {
      // FIXME:
      // return await MetrcDeliveries.getDeliveries(
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

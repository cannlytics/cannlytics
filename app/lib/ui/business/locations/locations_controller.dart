// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 3/7/2023
// Updated: 3/7/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Package imports:
import 'package:flutter_riverpod/flutter_riverpod.dart';

// Project imports:
import 'package:cannlytics_app/models/metrc/location.dart';
import 'package:cannlytics_app/services/metrc_service.dart';
import 'package:cannlytics_app/ui/general/app_controller.dart';

// Locations rows per page provider.
final locationsRowsPerPageProvider = StateProvider<int>((ref) => 5);

// Locations provider.
final locationsProvider =
    AsyncNotifierProvider<LocationsController, List<Location>>(() {
  return LocationsController();
});

/// Locations controller.
class LocationsController extends AsyncNotifier<List<Location>> {
  @override
  Future<List<Location>> build() async {
    // Load initial data from Metrc.
    return _getLocations();
  }

  /// Get locations.
  Future<List<Location>> _getLocations() async {
    // final licenseNumber = ref.watch(primaryLicenseProvider);
    final licenseNumber = '010-X0001';
    final orgId = ref.watch(primaryOrganizationProvider);
    final state = ref.watch(primaryStateProvider);
    try {
      return await MetrcLocations.getLocations(
        licenseNumber: licenseNumber,
        orgId: orgId,
        state: state,
      );
    } catch (error, stack) {
      print(stack);
      throw Exception("Error decoding JSON: [error=${error.toString()}]");
    }
  }

  // TODO: Get location.

  // TODO: Create location.

  // TODO: Update location.

  // TODO: Delete location.
}

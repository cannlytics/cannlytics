// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 3/7/2023
// Updated: 3/9/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Package imports:
import 'package:flutter_riverpod/flutter_riverpod.dart';

// Project imports:
import 'package:cannlytics_app/models/metrc/location.dart';
import 'package:cannlytics_app/services/metrc_service.dart';
import 'package:cannlytics_app/ui/general/app_controller.dart';

/* Locations */

// Locations rows per page provider.
final locationsRowsPerPageProvider = StateProvider<int>((ref) => 5);

// Locations sorting.
final locationsSortColumnIndex = StateProvider<int>((ref) => 0);
final locationsSortAscending = StateProvider<bool>((ref) => true);

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
    final licenseNumber = ref.watch(primaryLicenseProvider);
    final orgId = ref.watch(primaryOrganizationProvider);
    final state = ref.watch(primaryStateProvider);
    if (licenseNumber == null) return [];
    try {
      return await MetrcLocations.getLocations(
        licenseNumber: licenseNumber,
        orgId: orgId,
        state: state,
      );
    } catch (error, stack) {
      // print(stack);
      print("Error decoding JSON: [error=${error.toString()}]");
      return [];
    }
  }

  /// Set the location.
  Future<void> setLocations(List<Location> items) async {
    state = const AsyncValue.loading();
    state = await AsyncValue.guard(() async => items);
  }

  // TODO: Get location.

  // TODO: Create locations.

  // TODO: Update locations.

  // TODO: Delete locations.
}

// TODO: Implement locations search.

/* Locations Management  */

// Location selection provider.
final selectedLocationsProvider =
    NotifierProvider<SelectedLocationsNotifier, List<Location>>(() {
  return SelectedLocationsNotifier();
});

// Location selection.
class SelectedLocationsNotifier extends Notifier<List<Location>> {
  // Initialize with an empty list.
  @override
  List<Location> build() {
    return [];
  }

  // Select a location.
  void selectLocation(Location item) {
    state = [...state, item];
  }

  // Unselect a location
  void unselectLocation(Location item) {
    state = [
      for (final obj in state)
        if (obj.id != item.id) item,
    ];
  }
}

/* Location Management */

// Location provider.
final locationProvider =
    AsyncNotifierProvider<LocationController, Location?>(() {
  return LocationController();
});

/// Locations controller.
class LocationController extends AsyncNotifier<Location?> {
  @override
  Future<Location?> build() async {
    // // Load initial data from Metrc.
    // return _getLocations();
  }

  /// Get location.
  /// TODO: Implement if navigating directly to the detail screen.
  Future<Location> _getLocation(String id) async {
    final licenseNumber = ref.watch(primaryLicenseProvider);
    final orgId = ref.watch(primaryOrganizationProvider);
    final state = ref.watch(primaryStateProvider);
    try {
      return await MetrcLocations.getLocation(
        licenseNumber: licenseNumber,
        orgId: orgId,
        state: state,
        id: id,
      );
    } catch (error, stack) {
      print(stack);
      throw Exception("Error decoding JSON: [error=${error.toString()}]");
    }
  }

  /// Set the location.
  Future<void> setLocation(Location item) async {
    state = const AsyncValue.loading();
    state = await AsyncValue.guard(() async => item);
  }

  // TODO: Create location.

  // TODO: Update location.

  // TODO: Delete location.
}

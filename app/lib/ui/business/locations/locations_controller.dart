// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 3/7/2023
// Updated: 3/11/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Package imports:
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

// Project imports:
import 'package:cannlytics_app/models/metrc/location.dart';
import 'package:cannlytics_app/services/metrc_service.dart';
import 'package:cannlytics_app/ui/general/app_controller.dart';

/* Locations data */

// Locations provider.
final locationsProvider =
    AsyncNotifierProvider<LocationsController, List<Location>>(() {
  return LocationsController();
});

/// Locations controller.
class LocationsController extends AsyncNotifier<List<Location>> {
  // Load initial data from Metrc.
  @override
  Future<List<Location>> build() async {
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

/* Table */

// Rows per page provider.
final locationsRowsPerPageProvider = StateProvider<int>((ref) => 5);

// Sorting providers.
final locationsSortColumnIndex = StateProvider<int>((ref) => 0);
final locationsSortAscending = StateProvider<bool>((ref) => true);

/* Search */

// Search term provider.
final searchTermProvider = StateProvider<String>((ref) => '');

/// Filtered locations provider.
final filteredLocationsProvider =
    StateNotifierProvider<FilteredLocationsNotifier, List<Location>>(
  (ref) {
    // Listen to both data and search term.
    final data = ref.watch(locationsProvider).value;
    final searchTerm = ref.watch(searchTermProvider);
    return FilteredLocationsNotifier(ref, data ?? [], searchTerm);
  },
);

/// Filtered locations.
class FilteredLocationsNotifier extends StateNotifier<List<Location>> {
  // Properties.
  final StateNotifierProviderRef<dynamic, dynamic> ref;
  final List<Location> items;
  final String searchTerm;

  // Initialization.
  FilteredLocationsNotifier(
    this.ref,
    this.items,
    this.searchTerm,
  ) : super([]) {
    // Search function.
    if (searchTerm.isEmpty) {
      state = items;
      return;
    }
    String keyword = searchTerm.toLowerCase();
    List<Location> matched = [];
    items.forEach((x) {
      // Matching logic.
      if (x.name.toLowerCase().contains(keyword) || x.id.contains(keyword)) {
        matched.add(x);
      }
    });
    state = matched;
  }
}

// Search TextEditingController provider.
final searchControllerProvider =
    StateNotifierProvider<SearchController, TextEditingController>((ref) {
  return SearchController();
});

// Search TextEditingController.
class SearchController extends StateNotifier<TextEditingController> {
  SearchController() : super(TextEditingController());
  @override
  void dispose() {
    state.dispose();
    super.dispose();
  }
}

/* Selection  */

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

  // Unselect a location.
  void unselectLocation(Location item) {
    state = [
      for (final obj in state)
        if (obj.id != item.id) item,
    ];
  }
}

/* Location Details */

// Location provider.
final locationProvider =
    AsyncNotifierProvider<LocationController, Location?>(() {
  return LocationController();
});

/// Locations controller.
class LocationController extends AsyncNotifier<Location?> {
  @override
  Future<Location?> build() async {
    // FIXME: Load initial data from Metrc if data not already loaded.
    // TODO: Persist location data when a user clicks on a location.
    // return _getLocation();
  }

  /// Get location.
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

// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 3/7/2023
// Updated: 3/13/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Package imports:
import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

// Project imports:
import 'package:cannlytics_app/models/metrc/location.dart';
import 'package:cannlytics_app/services/metrc_service.dart';
import 'package:cannlytics_app/ui/main/app_controller.dart';

/* Locations data */

// Locations provider.
final locationsProvider =
    AsyncNotifierProvider<LocationsController, List<Location>>(
        () => LocationsController());

/// Locations controller.
class LocationsController extends AsyncNotifier<List<Location>> {
  // Load initial data from Metrc.
  @override
  Future<List<Location>> build() async => getLocations();

  /// Get locations.
  Future<List<Location>> getLocations() async {
    final licenseNumber = ref.watch(primaryLicenseProvider);
    final orgId = ref.watch(primaryOrganizationProvider);
    final state = ref.watch(primaryStateProvider);
    if (licenseNumber == null) return [];
    try {
      return await MetrcLocations.getLocations(
        license: licenseNumber,
        orgId: orgId,
        state: state,
      );
    } catch (error) {
      print("Error decoding JSON: [error=${error.toString()}]");
      return [];
    }
  }

  /// Set the location.
  Future<void> setLocations(List<Location> items) async {
    state = const AsyncValue.loading();
    state = await AsyncValue.guard(() async => items);
  }

  // TODO: Create locations.
  Future<void> createLocations(List<Location> items) async {
    state = const AsyncValue.loading();
    state = await AsyncValue.guard(() async => items);
  }

  // TODO: Update locations.
  Future<void> updateLocations(List<Location> items) async {
    state = const AsyncValue.loading();
    state = await AsyncValue.guard(() async => items);
  }

  // TODO: Delete locations.
  Future<void> deleteLocations(List<Location> items) async {
    state = const AsyncValue.loading();
    state = await AsyncValue.guard(() async => items);
  }
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

// Search input.
final searchController =
    StateNotifierProvider<SearchController, TextEditingController>(
        (ref) => SearchController());

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
    NotifierProvider<SelectedLocationsNotifier, List<Location>>(
        () => SelectedLocationsNotifier());

// Location selection.
class SelectedLocationsNotifier extends Notifier<List<Location>> {
  // Initialize with an empty list.
  @override
  List<Location> build() => [];

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

// Location ID.
final locationId = StateProvider<String?>((ref) => null);

// Location provider.
final locationProvider =
    AsyncNotifierProvider.family<LocationController, Location?, String?>(
  ({id}) {
    return LocationController(id: id);
  },
);

/// Locations controller.
class LocationController extends FamilyAsyncNotifier<Location?, String?> {
  LocationController({required this.id}) : super();

  // Properties.
  final String? id;

  // Initialization.
  @override
  FutureOr<Location?> build(String? id) async {
    if (id == null) return null;
    return await this.get(id);
  }

  /// Get location.
  Future<Location?> get(String id) async {
    final licenseNumber = ref.watch(primaryLicenseProvider);
    final orgId = ref.watch(primaryOrganizationProvider);
    final licenseState = ref.watch(primaryStateProvider);
    if (licenseNumber == null) return null;
    if (id == 'new') return Location(id: '', name: '');
    try {
      return await MetrcLocations.getLocation(
        id: id,
        license: licenseNumber,
        orgId: orgId,
        state: licenseState,
      );
    } catch (error) {
      throw Exception("Error decoding JSON: [error=${error.toString()}]");
    }
  }

  /// Set the location.
  Future<bool> set(Location item) async {
    state = const AsyncValue.loading();
    state = await AsyncValue.guard(() async => item);
    ref.read(nameController).value = TextEditingValue(text: item.name);
    return state.hasError == false;
  }

  // TODO: Create location.
  Future<bool> create(Location item) async {
    state = const AsyncValue.loading();
    state = await AsyncValue.guard(() async => item);
    return state.hasError == false;
  }

  // TODO: Update location.

  // TODO: Delete location.
}

/* Location Form */

// Name field.
final nameController =
    StateNotifierProvider<NameController, TextEditingController>(
  (ref) => NameController(),
);

class NameController extends StateNotifier<TextEditingController> {
  NameController() : super(TextEditingController());

  @override
  void dispose() {
    state.dispose();
    super.dispose();
  }

  void change(String value) => state.value = TextEditingValue(text: value);
}

/* Location Types */

// Location types provider.
final locationTypesProvider =
    AsyncNotifierProvider<LocationTypesNotifier, List<dynamic>>(() {
  return LocationTypesNotifier();
});

// Location types controller.
class LocationTypesNotifier extends AsyncNotifier<List<dynamic>> {
  // Initialization.
  @override
  Future<List<dynamic>> build() async => getLocationTypes();

  // Get location types from Metrc.
  Future<List<dynamic>> getLocationTypes() async {
    final licenseNumber = ref.watch(primaryLicenseProvider);
    final orgId = ref.watch(primaryOrganizationProvider);
    final licenseState = ref.watch(primaryStateProvider);
    List<dynamic> data;
    try {
      data = await MetrcLocations.getLocationTypes(
        license: licenseNumber,
        orgId: orgId,
        state: licenseState,
      );
    } catch (error) {
      return [];
    }

    final value = ref.read(locationType);
    // Set initial location type and permissions.
    if (value == null && data.isNotEmpty) {
      Map initialValue = data[0];
      ref.read(locationType.notifier).state = initialValue['name'];
      ref.read(forPlants.notifier).state = initialValue['for_plants'];
      ref.read(forPlantBatches.notifier).state =
          initialValue['for_plant_batches'];
      ref.read(forHarvests.notifier).state = initialValue['for_harvests'];
      ref.read(forPackages.notifier).state = initialValue['for_packages'];
    }
    return data;
  }
}

// Location name field.
final locationType = StateProvider<String?>((ref) => null);

// Boolean fields.
final forPlants = StateProvider<bool?>((ref) => null);
final forPlantBatches = StateProvider<bool?>((ref) => null);
final forHarvests = StateProvider<bool?>((ref) => null);
final forPackages = StateProvider<bool?>((ref) => null);

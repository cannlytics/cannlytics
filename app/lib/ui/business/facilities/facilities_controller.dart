// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 2/18/2023
// Updated: 3/7/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Package imports:
import 'dart:async';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

// Project imports:
import 'package:cannlytics_app/models/metrc/facility.dart';
import 'package:cannlytics_app/services/metrc_service.dart';
import 'package:cannlytics_app/ui/main/app_controller.dart';

// Facilities provider.
final facilitiesProvider =
    AsyncNotifierProvider<FacilitiesController, List<Facility>>(
        () => FacilitiesController());

/// Facilities controller.
class FacilitiesController extends AsyncNotifier<List<Facility>> {
  // Load initial facilities list from Metrc.
  @override
  Future<List<Facility>> build() async => _getFacilities();

  /// Get facilities.
  Future<List<Facility>> _getFacilities() async {
    final orgId = ref.watch(primaryOrganizationProvider);
    final state = ref.read(primaryStateProvider);
    final primaryFacility = ref.read(primaryFacilityProvider);
    try {
      var data = await MetrcFacilities.getFacilities(
        orgId: orgId,
        state: state,
      );
      // Set primary facility.
      if (data.isNotEmpty && primaryFacility == null) {
        ref.read(primaryFacilityProvider.notifier).state = data[0].id;
      }
      return data;
    } catch (error, stack) {
      print(stack);
      throw Exception("Error decoding JSON: [error=${error.toString()}]");
    }
  }

  /// Set the facilities.
  Future<void> setFacilities(List<Facility> items) async {
    state = const AsyncValue.loading();
    state = await AsyncValue.guard(() async => items);
  }
}

/* Table */

// Rows per page provider.
final facilitiesRowsPerPageProvider = StateProvider<int>((ref) => 5);

// Sorting providers.
final facilitiesSortColumnIndex = StateProvider<int>((ref) => 0);
final facilitiesSortAscending = StateProvider<bool>((ref) => true);

/* Search */

// Search term provider.
final searchTermProvider = StateProvider<String>((ref) => '');

/// Filtered facilities provider.
final filteredFacilitiesProvider =
    StateNotifierProvider<FilteredFacilitiesNotifier, List<Facility>>(
  (ref) {
    // Listen to both data and search term.
    final data = ref.watch(facilitiesProvider).value;
    final searchTerm = ref.watch(searchTermProvider);
    return FilteredFacilitiesNotifier(ref, data ?? [], searchTerm);
  },
);

/// Filtered facilities.
class FilteredFacilitiesNotifier extends StateNotifier<List<Facility>> {
  // Properties.
  final StateNotifierProviderRef<dynamic, dynamic> ref;
  final List<Facility> items;
  final String searchTerm;

  // Initialization.
  FilteredFacilitiesNotifier(
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
    List<Facility> matched = [];
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

// Facility selection provider.
final selectedFacilitiesProvider =
    NotifierProvider<SelectedFacilitiesNotifier, List<Facility>>(
        () => SelectedFacilitiesNotifier());

// Facility selection.
class SelectedFacilitiesNotifier extends Notifier<List<Facility>> {
  // Initialize with an empty list.
  @override
  List<Facility> build() => [];

  // Select a facility.
  void selectFacility(Facility item) {
    state = [...state, item];
  }

  // Unselect a facility.
  void unselectFacility(Facility item) {
    state = [
      for (final obj in state)
        if (obj.id != item.id) item,
    ];
  }
}

/* Facility Details */

// Facility ID.
final facilityId = StateProvider<String?>((ref) => null);

// Facility provider.
final facilityProvider =
    AsyncNotifierProvider.family<FacilityController, Facility?, String?>(
  ({id}) => FacilityController(id: id),
);

/// Facilities controller.
class FacilityController extends FamilyAsyncNotifier<Facility?, String?> {
  FacilityController({required this.id}) : super();

  // Properties.
  final String? id;

  // Initialization.
  @override
  FutureOr<Facility?> build(String? id) async {
    if (id == null) return null;
    return await this.get(id);
  }

  /// Get facility.
  Future<Facility?> get(String id) async {
    final items = ref.read(facilitiesProvider).value ?? [];
    for (Facility item in items) {
      if (item.id == id) {
        return item;
      }
    }
    return null;
  }

  /// Set the facility.
  Future<bool> set(Facility item) async {
    state = const AsyncValue.loading();
    state = await AsyncValue.guard(() async => item);
    ref.read(nameController).value = TextEditingValue(text: item.name);
    return state.hasError == false;
  }
}

/* Facility Form */

// Name field.
final nameController =
    StateNotifierProvider<NameController, TextEditingController>(
        (ref) => NameController());

class NameController extends StateNotifier<TextEditingController> {
  NameController() : super(TextEditingController());

  @override
  void dispose() {
    state.dispose();
    super.dispose();
  }

  void change(String value) => state.value = TextEditingValue(text: value);
}

/* Facility Types */

// // Facility types provider.
// final facilityTypesProvider =
//     AsyncNotifierProvider<FacilityTypesNotifier, List<dynamic>>(
//         () => FacilityTypesNotifier());

// // Facility types controller.
// class FacilityTypesNotifier extends AsyncNotifier<List<dynamic>> {
//   // Initialization.
//   @override
//   Future<List<dynamic>> build() async => getFacilityTypes();

//   // Get facility types from Metrc.
//   Future<List<dynamic>> getFacilityTypes() async {
//     final licenseNumber = ref.watch(primaryLicenseProvider);
//     final orgId = ref.watch(primaryOrganizationProvider);
//     final licenseState = ref.watch(primaryStateProvider);
//     List<dynamic> data;
//     try {
//       data = await MetrcFacilities.getFacilityTypes(
//         license: licenseNumber,
//         orgId: orgId,
//         state: licenseState,
//       );
//     } catch (error) {
//       return [];
//     }

//     // Set initial facility type and permissions.
//     final value = ref.read(facilityType);
//     if (value == null && data.isNotEmpty) {
//       Map initialValue = data[0];
//       ref.read(facilityType.notifier).state = initialValue['name'];
//       ref.read(forPlants.notifier).state = initialValue['for_plants'];
//       ref.read(forPlantBatches.notifier).state =
//           initialValue['for_plant_batches'];
//       ref.read(forHarvests.notifier).state = initialValue['for_harvests'];
//       ref.read(forPackages.notifier).state = initialValue['for_packages'];
//     }
//     return data;
//   }
// }

// // Facility name field.
// final facilityType = StateProvider<String?>((ref) => null);

// // Boolean fields.
// final forPlants = StateProvider<bool?>((ref) => null);
// final forPlantBatches = StateProvider<bool?>((ref) => null);
// final forHarvests = StateProvider<bool?>((ref) => null);
// final forPackages = StateProvider<bool?>((ref) => null);

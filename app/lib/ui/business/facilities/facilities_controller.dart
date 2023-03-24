// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 2/18/2023
// Updated: 3/23/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Dart imports:
import 'dart:async';

// Flutter imports:
import 'package:cannlytics_app/widgets/inputs/string_controller.dart';
import 'package:flutter/material.dart';

// Package imports:
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
    final currentFacility = ref.read(primaryFacility);
    try {
      var data = await MetrcFacilities.getFacilities(
        orgId: orgId,
        state: state,
      );
      // Set primary facility.
      if (data.isNotEmpty && currentFacility == null) {
        ref.read(primaryFacility.notifier).state = data[0];
      }
      print('FOUND FACILITIES!');
      return data;
    } catch (error, stack) {
      // print(stack);
      // throw Exception("Error decoding JSON: [error=${error.toString()}]");
      print("Error decoding JSON: [error=${error.toString()}]");
      return [];
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
final facilitiesSearchController =
    StateNotifierProvider<StringController, TextEditingController>(
        (ref) => StringController());

// class SearchController extends StateNotifier<TextEditingController> {
//   SearchController() : super(TextEditingController());
//   @override
//   void dispose() {
//     state.dispose();
//     super.dispose();
//   }
// }

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
final facilityId = StateProvider<String?>((ref) => 'new');

// Facility provider.
final facilityProvider =
    AsyncNotifierProvider.family<FacilityController, Facility, String?>(
        ({id}) => FacilityController(id: id));

/// Facilities controller.
class FacilityController extends FamilyAsyncNotifier<Facility, String?> {
  FacilityController({required this.id}) : super();

  // Properties.
  final String? id;

  // Initialization.
  @override
  FutureOr<Facility> build(String? id) async {
    if (id == null || id == 'new') return Facility(id: 'new');
    return await this.get(id);
  }

  /// Get facility.
  Future<Facility> get(String id) async {
    final items = ref.read(facilitiesProvider).value ?? [];
    for (Facility item in items) {
      if (item.id == id) {
        return item;
      }
    }
    return Facility(id: id);
  }

  /// Set the facility.
  Future<bool> set(Facility item) async {
    state = const AsyncValue.loading();
    state = await AsyncValue.guard(() async => item);
    // TODO: Set all of the initial values.
    ref.read(nameController).value = TextEditingValue(text: item.name);
    ref.read(aliasController).value = TextEditingValue(text: item.alias);
    return state.hasError == false;
  }
}

/* Facility Form */

// Name field.
final nameController =
    StateNotifierProvider<StringController, TextEditingController>(
        (ref) => StringController());

// Alias field.
final aliasController =
    StateNotifierProvider<StringController, TextEditingController>(
        (ref) => StringController());

// TODO: Add remaining facility fields!
// final credentialDateProvider = StateProvider<String?>((ref) => null);
// final displayNameProvider = StateProvider<String?>((ref) => null);
// final hireDateProvider = StateProvider<String?>((ref) => null);
// final isManagerProvider = StateProvider<bool?>((ref) => null);
// final isOwnerProvider = StateProvider<bool?>((ref) => null);
// final licenseEndDateProvider = StateProvider<String?>((ref) => null);
// final licenseNumberProvider = StateProvider<String?>((ref) => null);
// final licenseStartDateProvider = StateProvider<String?>((ref) => null);
// final licenseTypeProvider = StateProvider<String?>((ref) => null);
// final supportActivationDateProvider = StateProvider<String?>((ref) => null);
// final supportExpirationDateProvider = StateProvider<String?>((ref) => null);
// final supportLastPaidDateProvider = StateProvider<String?>((ref) => null);

// TODO: Facility type
// final facilityTypeProvider = StateProvider<String?>((ref) => null);

// TODO: Occupation
// final occupationProvider = StateProvider<String?>((ref) => null);

// TODO: Permissions
// final permissionsProvider = StateProvider<List<String>?>((ref) => null);

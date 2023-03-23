// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 3/8/2023
// Updated: 3/22/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Dart imports:
import 'dart:async';

// Flutter imports:
import 'package:flutter/material.dart';

// Package imports:
import 'package:flutter_riverpod/flutter_riverpod.dart';

// Project imports:
import 'package:cannlytics_app/models/metrc/strain.dart';
import 'package:cannlytics_app/services/metrc_service.dart';
import 'package:cannlytics_app/ui/main/app_controller.dart';

/* Strains data */

// Strains provider.
final strainsProvider = AsyncNotifierProvider<StrainsController, List<Strain>>(
    () => StrainsController());

/// Strains controller.
class StrainsController extends AsyncNotifier<List<Strain>> {
  // Load initial data from Metrc.
  @override
  Future<List<Strain>> build() async => getStrains();

  /// Get strains.
  Future<List<Strain>> getStrains() async {
    final licenseNumber = ref.watch(primaryLicenseProvider);
    final orgId = ref.watch(primaryOrganizationProvider);
    final state = ref.watch(primaryStateProvider);
    if (licenseNumber == null) return [];
    try {
      return await MetrcStrains.getStrains(
        license: licenseNumber,
        orgId: orgId,
        state: state,
      );
    } catch (error) {
      print("Error decoding JSON: [error=${error.toString()}]");
      return [];
    }
  }

  /// Set the strain.
  Future<void> setStrains(List<Strain> items) async {
    state = const AsyncValue.loading();
    state = await AsyncValue.guard(() async => items);
  }

  /// Create strains.
  Future<void> createStrains(List<Strain> items) async {
    state = const AsyncValue.loading();
    state = await AsyncValue.guard(() async {
      final licenseNumber = ref.read(primaryLicenseProvider);
      final licenseState = ref.read(primaryStateProvider);
      final orgId = ref.read(primaryOrganizationProvider);
      for (Strain item in items) {
        await MetrcStrains.createStrain(
          name: item.name,
          testingStatus: item.testingStatus!,
          cbdLevel: item.cbdLevel ?? 0.0,
          indicaPercentage: item.indicaPercentage ?? 50.0,
          sativaPercentage: item.sativaPercentage ?? 50.0,
          thcLevel: item.thcLevel ?? 0.0,
          license: licenseNumber,
          orgId: orgId,
          state: licenseState,
        );
      }
      return await getStrains();
    });
  }

  // Update strains.
  Future<void> updateStrains(List<Strain> items) async {
    state = const AsyncValue.loading();
    state = await AsyncValue.guard(() async {
      final licenseNumber = ref.read(primaryLicenseProvider);
      final licenseState = ref.read(primaryStateProvider);
      final orgId = ref.read(primaryOrganizationProvider);
      for (Strain item in items) {
        await MetrcStrains.updateStrain(
          id: item.id,
          name: item.name,
          testingStatus: item.testingStatus!,
          cbdLevel: item.cbdLevel ?? 0.0,
          indicaPercentage: item.indicaPercentage ?? 50.0,
          sativaPercentage: item.sativaPercentage ?? 50.0,
          thcLevel: item.thcLevel ?? 0.0,
          license: licenseNumber,
          orgId: orgId,
          state: licenseState,
        );
      }
      return await getStrains();
    });
  }

  // Delete strains.
  Future<void> deleteStrains(List<Strain> items) async {
    state = const AsyncValue.loading();
    state = await AsyncValue.guard(() async {
      final licenseNumber = ref.read(primaryLicenseProvider);
      final licenseState = ref.read(primaryStateProvider);
      final orgId = ref.read(primaryOrganizationProvider);
      for (Strain item in items) {
        await MetrcStrains.deleteStrain(
          id: item.id,
          license: licenseNumber,
          orgId: orgId,
          state: licenseState,
        );
      }
      return await getStrains();
    });
  }
}

/* Table */

// Rows per page provider.
final strainsRowsPerPageProvider = StateProvider<int>((ref) => 5);

// Sorting providers.
final strainsSortColumnIndex = StateProvider<int>((ref) => 0);
final strainsSortAscending = StateProvider<bool>((ref) => true);

/* Search */

// Search term provider.
final searchTermProvider = StateProvider<String>((ref) => '');

/// Filtered strains provider.
final filteredStrainsProvider =
    StateNotifierProvider<FilteredStrainsNotifier, List<Strain>>(
  (ref) {
    // Listen to both data and search term.
    final data = ref.watch(strainsProvider).value;
    final searchTerm = ref.watch(searchTermProvider);
    return FilteredStrainsNotifier(ref, data ?? [], searchTerm);
  },
);

/// Filtered strains.
class FilteredStrainsNotifier extends StateNotifier<List<Strain>> {
  // Properties.
  final StateNotifierProviderRef<dynamic, dynamic> ref;
  final List<Strain> items;
  final String searchTerm;

  // Initialization.
  FilteredStrainsNotifier(
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
    List<Strain> matched = [];
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

// Strain selection provider.
final selectedStrainsProvider =
    NotifierProvider<SelectedStrainsNotifier, List<Strain>>(
        () => SelectedStrainsNotifier());

// Strain selection.
class SelectedStrainsNotifier extends Notifier<List<Strain>> {
  // Initialize with an empty list.
  @override
  List<Strain> build() => [];

  // Select a strain.
  void selectStrain(Strain item) {
    state = [...state, item];
  }

  // Unselect a strain.
  void unselectStrain(Strain item) {
    state = [
      for (final obj in state)
        if (obj.id != item.id) item,
    ];
  }
}

/* Strain Details */

// Strain ID.
final strainId = StateProvider<String?>((ref) => null);

// Strain provider.
final strainProvider =
    AsyncNotifierProvider.family<StrainController, Strain?, String?>(
  ({id}) {
    return StrainController(id: id);
  },
);

/// Strains controller.
class StrainController extends FamilyAsyncNotifier<Strain?, String?> {
  StrainController({required this.id}) : super();

  // Properties.
  final String? id;

  // Initialization.
  @override
  FutureOr<Strain?> build(String? id) async {
    if (id == null) return null;
    return await this.get(id);
  }

  /// Get strain.
  Future<Strain?> get(String id) async {
    final licenseNumber = ref.watch(primaryLicenseProvider);
    final orgId = ref.watch(primaryOrganizationProvider);
    final licenseState = ref.watch(primaryStateProvider);
    if (licenseNumber == null) return null;
    if (id == 'new') return Strain(id: '', name: '');
    try {
      return await MetrcStrains.getStrain(
        license: licenseNumber,
        orgId: orgId,
        state: licenseState,
        id: id,
      );
    } catch (error) {
      throw Exception("Error decoding JSON: [error=${error.toString()}]");
    }
  }

  /// Set the strain.
  Future<bool> set(Strain item) async {
    state = const AsyncValue.loading();
    state = await AsyncValue.guard(() async => item);
    ref.read(nameController).value = TextEditingValue(text: item.name);
    return state.hasError == false;
  }

  // TODO: Create strain.
  Future<bool> create(Strain item) async {
    state = const AsyncValue.loading();
    state = await AsyncValue.guard(() async => item);
    return state.hasError == false;
  }

  // TODO: Update strain.

  // TODO: Delete strain.
}

/* Strain Form */

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

// TODO: Convert to testing statuses.

// Strain types provider.
final testingStatusesProvider =
    AsyncNotifierProvider<StrainTypesNotifier, List<dynamic>>(
        () => StrainTypesNotifier());

// Strain types controller.
class StrainTypesNotifier extends AsyncNotifier<List<dynamic>> {
  // Initialization.
  @override
  Future<List<dynamic>> build() async => getTestingStatuses();

  // Get strain types from Metrc.
  Future<List<dynamic>> getTestingStatuses() async {
    final licenseNumber = ref.watch(primaryLicenseProvider);
    final orgId = ref.watch(primaryOrganizationProvider);
    final licenseState = ref.watch(primaryStateProvider);
    // FIXME:
    return [];
    // List<dynamic> data = await MetrcStrains.getTestStatuses(
    //   license: licenseNumber,
    //   orgId: orgId,
    //   state: licenseState,
    // );
    // final value = ref.read(strainName);
    // return data;
  }
}

// Strain fields.
final strainName = StateProvider<String?>((ref) => null);
final testingStatus = StateProvider<String?>((ref) => null);
final cbdLevel = StateProvider<double>((ref) => 0.0);
final thcLevel = StateProvider<double>((ref) => 0.0);
final indicaPercentage = StateProvider<double>((ref) => 50.0);
final sativaPercentage = StateProvider<double>((ref) => 50.0);

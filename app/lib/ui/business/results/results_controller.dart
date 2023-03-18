// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 3/9/2023
// Updated: 3/9/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Package imports:
import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

// Project imports:
import 'package:cannlytics_app/models/metrc/lab_result.dart';
import 'package:cannlytics_app/services/metrc_service.dart';
import 'package:cannlytics_app/ui/main/app_controller.dart';

/* LabResults data */

// LabResults provider.
final labResultsProvider =
    AsyncNotifierProvider<LabResultsController, List<LabResult>>(
        () => LabResultsController());

/// LabResults controller.
class LabResultsController extends AsyncNotifier<List<LabResult>> {
  // Load initial data from Metrc.
  @override
  Future<List<LabResult>> build() async => getLabResults();

  /// Get labResults.
  Future<List<LabResult>> getLabResults() async {
    final licenseNumber = ref.watch(primaryLicenseProvider);
    final licenseState = ref.read(primaryStateProvider);
    final orgId = ref.read(primaryOrganizationProvider);
    if (licenseNumber == null) return [];
    try {
      // FIXME:
      // return await MetrcLabResults.getLabResults(
      //   license: licenseNumber,
      //   orgId: orgId,
      //   state: licenseState,
      // );
      return [];
    } catch (error) {
      print("Error decoding JSON: [error=${error.toString()}]");
      return [];
    }
  }

  /// Set the labResult.
  Future<void> setLabResults(List<LabResult> items) async {
    state = const AsyncValue.loading();
    state = await AsyncValue.guard(() async => items);
  }

  // Create labResults.
  Future<void> createLabResults(List<LabResult> items) async {
    state = const AsyncValue.loading();
    state = await AsyncValue.guard(() async {
      final licenseNumber = ref.read(primaryLicenseProvider);
      final licenseState = ref.read(primaryStateProvider);
      final orgId = ref.read(primaryOrganizationProvider);
      for (LabResult item in items) {
        // FIXME:
        // await MetrcLabResults.createLabResult(
        //   name: item.name,
        //   labResultTypeName: item.labResultTypeName,
        //   license: licenseNumber,
        //   orgId: orgId,
        //   state: licenseState,
        // );
      }
      return await getLabResults();
    });
  }

  // Update labResults.
  Future<void> updateLabResults(List<LabResult> items) async {
    state = const AsyncValue.loading();
    state = await AsyncValue.guard(() async {
      final licenseNumber = ref.read(primaryLicenseProvider);
      final licenseState = ref.read(primaryStateProvider);
      final orgId = ref.read(primaryOrganizationProvider);
      for (LabResult item in items) {
        // FIXME:
        // await MetrcLabResults.updateLabResult(
        //   id: item.id,
        //   name: item.name,
        //   labResultTypeName: item.labResultTypeName ?? 'Default LabResult Type',
        //   license: licenseNumber,
        //   orgId: orgId,
        //   state: licenseState,
        // );
      }
      return await getLabResults();
    });
  }

  // Delete labResults.
  Future<void> deleteLabResults(List<LabResult> items) async {
    state = const AsyncValue.loading();
    state = await AsyncValue.guard(() async {
      final licenseNumber = ref.read(primaryLicenseProvider);
      final licenseState = ref.read(primaryStateProvider);
      final orgId = ref.read(primaryOrganizationProvider);
      for (LabResult item in items) {
        // FIXME:
        // await MetrcLabResults.deleteLabResult(
        //   id: item.id,
        //   license: licenseNumber,
        //   orgId: orgId,
        //   state: licenseState,
        // );
      }
      return await getLabResults();
    });
  }
}

/* Table */

// Rows per page provider.
final labResultsRowsPerPageProvider = StateProvider<int>((ref) => 5);

// Sorting providers.
final labResultsSortColumnIndex = StateProvider<int>((ref) => 0);
final labResultsSortAscending = StateProvider<bool>((ref) => true);

/* Search */

// Search term provider.
final searchTermProvider = StateProvider<String>((ref) => '');

/// Filtered labResults provider.
final filteredLabResultsProvider =
    StateNotifierProvider<FilteredLabResultsNotifier, List<LabResult>>(
  (ref) {
    // Listen to both data and search term.
    final data = ref.watch(labResultsProvider).value;
    final searchTerm = ref.watch(searchTermProvider);
    return FilteredLabResultsNotifier(ref, data ?? [], searchTerm);
  },
);

/// Filtered labResults.
class FilteredLabResultsNotifier extends StateNotifier<List<LabResult>> {
  // Properties.
  final StateNotifierProviderRef<dynamic, dynamic> ref;
  final List<LabResult> items;
  final String searchTerm;

  // Initialization.
  FilteredLabResultsNotifier(
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
    List<LabResult> matched = [];
    items.forEach((x) {
      // Matching logic.
      // FIXME:
      if (x.id!.contains(keyword)) {
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

// LabResult selection provider.
final selectedLabResultsProvider =
    NotifierProvider<SelectedLabResultsNotifier, List<LabResult>>(
        () => SelectedLabResultsNotifier());

// LabResult selection.
class SelectedLabResultsNotifier extends Notifier<List<LabResult>> {
  // Initialize with an empty list.
  @override
  List<LabResult> build() => [];

  // Select a labResult.
  void selectLabResult(LabResult item) {
    state = [...state, item];
  }

  // Unselect a labResult.
  void unselectLabResult(LabResult item) {
    state = [
      for (final obj in state)
        if (obj.id != item.id) item,
    ];
  }
}

/* LabResult Details */

// LabResult ID.
final labResultId = StateProvider<String?>((ref) => null);

// LabResult provider.
final labResultProvider =
    AsyncNotifierProvider.family<LabResultController, LabResult?, String?>(
  ({id}) => LabResultController(id: id),
);

/// LabResults controller.
class LabResultController extends FamilyAsyncNotifier<LabResult?, String?> {
  LabResultController({required this.id}) : super();

  // Properties.
  final String? id;

  // Initialization.
  @override
  FutureOr<LabResult?> build(String? id) async {
    if (id == null) return null;
    return await this.get(id);
  }

  /// Get labResult.
  Future<LabResult?> get(String id) async {
    print('GETTING LOCATION...');
    final items = ref.read(labResultsProvider).value ?? [];
    for (LabResult item in items) {
      if (item.id == id) {
        print('Returning item:');
        print(item);
        return item;
      }
    }
    final licenseNumber = ref.watch(primaryLicenseProvider);
    final orgId = ref.read(primaryOrganizationProvider);
    final licenseState = ref.read(primaryStateProvider);
    if (licenseNumber == null) return null;
    if (id == 'new') return LabResult();
    print('GETTING LOCATION...');
    try {
      // FIXME:
      // return await MetrcLabResults.getLabResult(
      //   id: id,
      //   license: licenseNumber,
      //   orgId: orgId,
      //   state: licenseState,
      // );
    } catch (error) {
      throw Exception("Error decoding JSON: [error=${error.toString()}]");
    }
  }

  /// Set the labResult.
  Future<bool> set(LabResult item) async {
    state = const AsyncValue.loading();
    state = await AsyncValue.guard(() async => item);
    // FIXME:
    // ref.read(nameController).value = TextEditingValue(text: item.name);
    return state.hasError == false;
  }

  // TODO: Create labResult.
  Future<bool> create(LabResult item) async {
    state = const AsyncValue.loading();
    state = await AsyncValue.guard(() async => item);
    return state.hasError == false;
  }

  // TODO: Update labResult.

  // TODO: Delete labResult.
}

/* LabResult Form */

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

/* LabResult Types */

// LabResult types provider.
final labResultTypesProvider =
    AsyncNotifierProvider<LabResultTypesNotifier, List<dynamic>>(
        () => LabResultTypesNotifier());

// LabResult types controller.
class LabResultTypesNotifier extends AsyncNotifier<List<dynamic>> {
  // Initialization.
  @override
  Future<List<dynamic>> build() async => getLabResultTypes();

  // Get labResult types from Metrc.
  Future<List<dynamic>> getLabResultTypes() async {
    final licenseNumber = ref.watch(primaryLicenseProvider);
    final orgId = ref.watch(primaryOrganizationProvider);
    final licenseState = ref.watch(primaryStateProvider);
    List<dynamic> data;
    try {
      // FIXME:
      // data = await MetrcLabResults.getLabResultTypes(
      //   license: licenseNumber,
      //   orgId: orgId,
      //   state: licenseState,
      // );
      data = [];
    } catch (error) {
      return [];
    }

    // Set initial labResult type and permissions.
    final value = ref.read(labResultType);
    if (value == null && data.isNotEmpty) {
      Map initialValue = data[0];
      ref.read(labResultType.notifier).state = initialValue['name'];
      ref.read(forPlants.notifier).state = initialValue['for_plants'];
      ref.read(forPlantBatches.notifier).state =
          initialValue['for_plant_batches'];
      ref.read(forHarvests.notifier).state = initialValue['for_harvests'];
      ref.read(forPackages.notifier).state = initialValue['for_packages'];
    }
    return data;
  }
}

// LabResult name field.
final labResultType = StateProvider<String?>((ref) => null);

// Boolean fields.
final forPlants = StateProvider<bool?>((ref) => null);
final forPlantBatches = StateProvider<bool?>((ref) => null);
final forHarvests = StateProvider<bool?>((ref) => null);
final forPackages = StateProvider<bool?>((ref) => null);

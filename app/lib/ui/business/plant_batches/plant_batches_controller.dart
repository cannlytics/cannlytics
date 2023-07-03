// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 3/9/2023
// Updated: 3/18/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// ignore_for_file: unused_local_variable

// Dart imports:
import 'dart:async';

// Flutter imports:
import 'package:flutter/material.dart';

// Package imports:
import 'package:flutter_riverpod/flutter_riverpod.dart';

// Project imports:
import 'package:cannlytics_app/models/metrc/plant_batch.dart';
import 'package:cannlytics_app/ui/main/app_controller.dart';

/* PlantBatches data */

// PlantBatches provider.
final plantBatchesProvider =
    AsyncNotifierProvider<PlantBatchesController, List<PlantBatch>>(
        () => PlantBatchesController());

/// PlantBatches controller.
class PlantBatchesController extends AsyncNotifier<List<PlantBatch>> {
  // Load initial data from Metrc.
  @override
  Future<List<PlantBatch>> build() async => getPlantBatches();

  /// Get plantBatches.
  Future<List<PlantBatch>> getPlantBatches() async {
    final licenseNumber = ref.watch(primaryLicenseProvider);
    final licenseState = ref.read(primaryStateProvider);
    final orgId = ref.read(primaryOrganizationProvider);
    if (licenseNumber == null) return [];
    try {
      // FIXME:
      // return await MetrcPlantBatches.getPlantBatches(
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

  /// Set the plantBatch.
  Future<void> setPlantBatches(List<PlantBatch> items) async {
    state = const AsyncValue.loading();
    state = await AsyncValue.guard(() async => items);
  }

  // Create plantBatches.
  Future<void> createPlantBatches(List<PlantBatch> items) async {
    state = const AsyncValue.loading();
    state = await AsyncValue.guard(() async {
      final licenseNumber = ref.read(primaryLicenseProvider);
      final licenseState = ref.read(primaryStateProvider);
      final orgId = ref.read(primaryOrganizationProvider);
      for (PlantBatch item in items) {
        // FIXME:
        // await MetrcPlantBatches.createPlantBatch(
        //   name: item.name,
        //   plantBatchTypeName: item.plantBatchTypeName,
        //   license: licenseNumber,
        //   orgId: orgId,
        //   state: licenseState,
        // );
      }
      return await getPlantBatches();
    });
  }

  // Update plantBatches.
  Future<void> updatePlantBatches(List<PlantBatch> items) async {
    state = const AsyncValue.loading();
    state = await AsyncValue.guard(() async {
      final licenseNumber = ref.read(primaryLicenseProvider);
      final licenseState = ref.read(primaryStateProvider);
      final orgId = ref.read(primaryOrganizationProvider);
      for (PlantBatch item in items) {
        // FIXME:
        // await MetrcPlantBatches.updatePlantBatch(
        //   id: item.id,
        //   name: item.name,
        //   plantBatchTypeName:
        //       item.plantBatchTypeName ?? 'Default PlantBatch Type',
        //   license: licenseNumber,
        //   orgId: orgId,
        //   state: licenseState,
        // );
      }
      return await getPlantBatches();
    });
  }

  // Delete plantBatches.
  Future<void> deletePlantBatches(List<PlantBatch> items) async {
    state = const AsyncValue.loading();
    state = await AsyncValue.guard(() async {
      final licenseNumber = ref.read(primaryLicenseProvider);
      final licenseState = ref.read(primaryStateProvider);
      final orgId = ref.read(primaryOrganizationProvider);
      for (PlantBatch item in items) {
        // FIXME:
        // await MetrcPlantBatches.deletePlantBatch(
        //   id: item.id,
        //   license: licenseNumber,
        //   orgId: orgId,
        //   state: licenseState,
        // );
      }
      return await getPlantBatches();
    });
  }
}

/* Table */

// Rows per page provider.
final plantBatchesRowsPerPageProvider = StateProvider<int>((ref) => 5);

// Sorting providers.
final plantBatchesSortColumnIndex = StateProvider<int>((ref) => 0);
final plantBatchesSortAscending = StateProvider<bool>((ref) => true);

/* Search */

// Search term provider.
final searchTermProvider = StateProvider<String>((ref) => '');

/// Filtered plantBatches provider.
final filteredPlantBatchesProvider =
    StateNotifierProvider<FilteredPlantBatchesNotifier, List<PlantBatch>>(
  (ref) {
    // Listen to both data and search term.
    final data = ref.watch(plantBatchesProvider).value;
    final searchTerm = ref.watch(searchTermProvider);
    return FilteredPlantBatchesNotifier(ref, data ?? [], searchTerm);
  },
);

/// Filtered plantBatches.
class FilteredPlantBatchesNotifier extends StateNotifier<List<PlantBatch>> {
  // Properties.
  final StateNotifierProviderRef<dynamic, dynamic> ref;
  final List<PlantBatch> items;
  final String searchTerm;

  // Initialization.
  FilteredPlantBatchesNotifier(
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
    List<PlantBatch> matched = [];
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

// PlantBatch selection provider.
final selectedPlantBatchesProvider =
    NotifierProvider<SelectedPlantBatchesNotifier, List<PlantBatch>>(
        () => SelectedPlantBatchesNotifier());

// PlantBatch selection.
class SelectedPlantBatchesNotifier extends Notifier<List<PlantBatch>> {
  // Initialize with an empty list.
  @override
  List<PlantBatch> build() => [];

  // Select a plantBatch.
  void selectPlantBatch(PlantBatch item) {
    state = [...state, item];
  }

  // Unselect a plantBatch.
  void unselectPlantBatch(PlantBatch item) {
    state = [
      for (final obj in state)
        if (obj.id != item.id) item,
    ];
  }
}

/* PlantBatch Details */

// PlantBatch ID.
final plantBatchId = StateProvider<String?>((ref) => null);

// PlantBatch provider.
final plantBatchProvider =
    AsyncNotifierProvider.family<PlantBatchController, PlantBatch?, String?>(
  ({id}) => PlantBatchController(id: id),
);

/// PlantBatches controller.
class PlantBatchController extends FamilyAsyncNotifier<PlantBatch?, String?> {
  PlantBatchController({required this.id}) : super();

  // Properties.
  final String? id;

  // Initialization.
  @override
  FutureOr<PlantBatch?> build(String? id) async {
    if (id == null) return null;
    return await this.get(id);
  }

  /// Get plantBatch.
  Future<PlantBatch?> get(String id) async {
    print('GETTING LOCATION...');
    final items = ref.read(plantBatchesProvider).value ?? [];
    for (PlantBatch item in items) {
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
    if (id == 'new') return PlantBatch(id: '', name: '');
    print('GETTING LOCATION...');
    try {
      // FIXME:
      // return await MetrcPlantBatches.getPlantBatch(
      //   id: id,
      //   license: licenseNumber,
      //   orgId: orgId,
      //   state: licenseState,
      // );
      return null;
    } catch (error) {
      throw Exception("Error decoding JSON: [error=${error.toString()}]");
    }
  }

  /// Set the plantBatch.
  Future<bool> set(PlantBatch item) async {
    state = const AsyncValue.loading();
    state = await AsyncValue.guard(() async => item);
    // FIXME:
    // ref.read(nameController).value = TextEditingValue(text: item.name);
    return state.hasError == false;
  }

  // TODO: Create plantBatch.
  Future<bool> create(PlantBatch item) async {
    state = const AsyncValue.loading();
    state = await AsyncValue.guard(() async => item);
    return state.hasError == false;
  }

  // TODO: Update plantBatch.

  // TODO: Delete plantBatch.
}

/* PlantBatch Form */

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

/* PlantBatch Types */

// PlantBatch types provider.
final plantBatchTypesProvider =
    AsyncNotifierProvider<PlantBatchTypesNotifier, List<dynamic>>(
        () => PlantBatchTypesNotifier());

// PlantBatch types controller.
class PlantBatchTypesNotifier extends AsyncNotifier<List<dynamic>> {
  // Initialization.
  @override
  Future<List<dynamic>> build() async => getPlantBatchTypes();

  // Get plantBatch types from Metrc.
  Future<List<dynamic>> getPlantBatchTypes() async {
    final licenseNumber = ref.watch(primaryLicenseProvider);
    final orgId = ref.watch(primaryOrganizationProvider);
    final licenseState = ref.watch(primaryStateProvider);
    List<dynamic> data;
    try {
      // FIXME:
      // data = await MetrcPlantBatches.getPlantBatchTypes(
      //   license: licenseNumber,
      //   orgId: orgId,
      //   state: licenseState,
      // );
      data = [];
    } catch (error) {
      return [];
    }

    // Set initial plantBatch type and permissions.
    final value = ref.read(plantBatchType);
    if (value == null && data.isNotEmpty) {
      Map initialValue = data[0];
      ref.read(plantBatchType.notifier).state = initialValue['name'];
      ref.read(forPlants.notifier).state = initialValue['for_plants'];
      ref.read(forPlantBatches.notifier).state =
          initialValue['for_plant_batches'];
      ref.read(forHarvests.notifier).state = initialValue['for_harvests'];
      ref.read(forPackages.notifier).state = initialValue['for_packages'];
    }
    return data;
  }
}

// PlantBatch name field.
final plantBatchType = StateProvider<String?>((ref) => null);

// Boolean fields.
final forPlants = StateProvider<bool?>((ref) => null);
final forPlantBatches = StateProvider<bool?>((ref) => null);
final forHarvests = StateProvider<bool?>((ref) => null);
final forPackages = StateProvider<bool?>((ref) => null);

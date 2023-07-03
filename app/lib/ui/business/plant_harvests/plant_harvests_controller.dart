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
import 'package:cannlytics_app/models/metrc/plant_harvest.dart';
import 'package:cannlytics_app/ui/main/app_controller.dart';

/* PlantHarvests data */

// PlantHarvests provider.
final plantHarvestsProvider =
    AsyncNotifierProvider<PlantHarvestsController, List<PlantHarvest>>(
        () => PlantHarvestsController());

/// PlantHarvests controller.
class PlantHarvestsController extends AsyncNotifier<List<PlantHarvest>> {
  // Load initial data from Metrc.
  @override
  Future<List<PlantHarvest>> build() async => getPlantHarvests();

  /// Get plantHarvests.
  Future<List<PlantHarvest>> getPlantHarvests() async {
    final licenseNumber = ref.watch(primaryLicenseProvider);
    final licenseState = ref.read(primaryStateProvider);
    final orgId = ref.read(primaryOrganizationProvider);
    if (licenseNumber == null) return [];
    try {
      // FIXME:
      // return await MetrcPlantHarvests.getPlantHarvests(
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

  /// Set the plantHarvest.
  Future<void> setPlantHarvests(List<PlantHarvest> items) async {
    state = const AsyncValue.loading();
    state = await AsyncValue.guard(() async => items);
  }

  // Create plantHarvests.
  Future<void> createPlantHarvests(List<PlantHarvest> items) async {
    state = const AsyncValue.loading();
    state = await AsyncValue.guard(() async {
      final licenseNumber = ref.read(primaryLicenseProvider);
      final licenseState = ref.read(primaryStateProvider);
      final orgId = ref.read(primaryOrganizationProvider);
      for (PlantHarvest item in items) {
        // FIXME:
        // await MetrcPlantHarvests.createPlantHarvest(
        //   name: item.name,
        //   plantHarvestTypeName: item.plantHarvestTypeName,
        //   license: licenseNumber,
        //   orgId: orgId,
        //   state: licenseState,
        // );
      }
      return await getPlantHarvests();
    });
  }

  // Update plantHarvests.
  Future<void> updatePlantHarvests(List<PlantHarvest> items) async {
    state = const AsyncValue.loading();
    state = await AsyncValue.guard(() async {
      final licenseNumber = ref.read(primaryLicenseProvider);
      final licenseState = ref.read(primaryStateProvider);
      final orgId = ref.read(primaryOrganizationProvider);
      for (PlantHarvest item in items) {
        // FIXME:
        // await MetrcPlantHarvests.updatePlantHarvest(
        //   id: item.id,
        //   name: item.name,
        //   plantHarvestTypeName:
        //       item.plantHarvestTypeName ?? 'Default PlantHarvest Type',
        //   license: licenseNumber,
        //   orgId: orgId,
        //   state: licenseState,
        // );
      }
      return await getPlantHarvests();
    });
  }

  // Delete plantHarvests.
  Future<void> deletePlantHarvests(List<PlantHarvest> items) async {
    state = const AsyncValue.loading();
    state = await AsyncValue.guard(() async {
      final licenseNumber = ref.read(primaryLicenseProvider);
      final licenseState = ref.read(primaryStateProvider);
      final orgId = ref.read(primaryOrganizationProvider);
      for (PlantHarvest item in items) {
        // FIXME:
        // await MetrcPlantHarvests.deletePlantHarvest(
        //   id: item.id,
        //   license: licenseNumber,
        //   orgId: orgId,
        //   state: licenseState,
        // );
      }
      return await getPlantHarvests();
    });
  }
}

/* Table */

// Rows per page provider.
final plantHarvestsRowsPerPageProvider = StateProvider<int>((ref) => 5);

// Sorting providers.
final plantHarvestsSortColumnIndex = StateProvider<int>((ref) => 0);
final plantHarvestsSortAscending = StateProvider<bool>((ref) => true);

/* Search */

// Search term provider.
final searchTermProvider = StateProvider<String>((ref) => '');

/// Filtered plantHarvests provider.
final filteredPlantHarvestsProvider =
    StateNotifierProvider<FilteredPlantHarvestsNotifier, List<PlantHarvest>>(
  (ref) {
    // Listen to both data and search term.
    final data = ref.watch(plantHarvestsProvider).value;
    final searchTerm = ref.watch(searchTermProvider);
    return FilteredPlantHarvestsNotifier(ref, data ?? [], searchTerm);
  },
);

/// Filtered plantHarvests.
class FilteredPlantHarvestsNotifier extends StateNotifier<List<PlantHarvest>> {
  // Properties.
  final StateNotifierProviderRef<dynamic, dynamic> ref;
  final List<PlantHarvest> items;
  final String searchTerm;

  // Initialization.
  FilteredPlantHarvestsNotifier(
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
    List<PlantHarvest> matched = [];
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

// PlantHarvest selection provider.
final selectedPlantHarvestsProvider =
    NotifierProvider<SelectedPlantHarvestsNotifier, List<PlantHarvest>>(
        () => SelectedPlantHarvestsNotifier());

// PlantHarvest selection.
class SelectedPlantHarvestsNotifier extends Notifier<List<PlantHarvest>> {
  // Initialize with an empty list.
  @override
  List<PlantHarvest> build() => [];

  // Select a plantHarvest.
  void selectPlantHarvest(PlantHarvest item) {
    state = [...state, item];
  }

  // Unselect a plantHarvest.
  void unselectPlantHarvest(PlantHarvest item) {
    state = [
      for (final obj in state)
        if (obj.id != item.id) item,
    ];
  }
}

/* PlantHarvest Details */

// PlantHarvest ID.
final plantHarvestId = StateProvider<String?>((ref) => null);

// PlantHarvest provider.
final plantHarvestProvider = AsyncNotifierProvider.family<
    PlantHarvestController, PlantHarvest?, String?>(
  ({id}) => PlantHarvestController(id: id),
);

/// PlantHarvests controller.
class PlantHarvestController
    extends FamilyAsyncNotifier<PlantHarvest?, String?> {
  PlantHarvestController({required this.id}) : super();

  // Properties.
  final String? id;

  // Initialization.
  @override
  FutureOr<PlantHarvest?> build(String? id) async {
    if (id == null) return null;
    return await this.get(id);
  }

  /// Get plantHarvest.
  Future<PlantHarvest?> get(String id) async {
    print('GETTING...');
    final items = ref.read(plantHarvestsProvider).value ?? [];
    for (PlantHarvest item in items) {
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
    if (id == 'new') return PlantHarvest(id: '', name: '');
    print('GETTING...');
    try {
      // FIXME:
      // return await MetrcPlantHarvests.getPlantHarvest(
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

  /// Set the plantHarvest.
  Future<bool> set(PlantHarvest item) async {
    state = const AsyncValue.loading();
    state = await AsyncValue.guard(() async => item);
    // FIXME:
    // ref.read(nameController).value = TextEditingValue(text: item.name);
    return state.hasError == false;
  }

  // TODO: Create plantHarvest.
  Future<bool> create(PlantHarvest item) async {
    state = const AsyncValue.loading();
    state = await AsyncValue.guard(() async => item);
    return state.hasError == false;
  }

  // TODO: Update plantHarvest.

  // TODO: Delete plantHarvest.
}

/* Plant Harvest Form */

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

/* Plant Harvest Types */

// Plant Harvest types provider.
final plantHarvestTypesProvider =
    AsyncNotifierProvider<PlantHarvestTypesNotifier, List<dynamic>>(
        () => PlantHarvestTypesNotifier());

// PlantHarvest types controller.
class PlantHarvestTypesNotifier extends AsyncNotifier<List<dynamic>> {
  // Initialization.
  @override
  Future<List<dynamic>> build() async => getPlantHarvestTypes();

  // Get plantHarvest types from Metrc.
  Future<List<dynamic>> getPlantHarvestTypes() async {
    final licenseNumber = ref.watch(primaryLicenseProvider);
    final orgId = ref.watch(primaryOrganizationProvider);
    final licenseState = ref.watch(primaryStateProvider);
    List<dynamic> data;
    try {
      // FIXME:
      // data = await MetrcPlantHarvests.getPlantHarvestTypes(
      //   license: licenseNumber,
      //   orgId: orgId,
      //   state: licenseState,
      // );
      data = [];
    } catch (error) {
      return [];
    }

    // Set initial plantHarvest type and permissions.
    final value = ref.read(plantHarvestType);
    if (value == null && data.isNotEmpty) {
      Map initialValue = data[0];
      ref.read(plantHarvestType.notifier).state = initialValue['name'];
      ref.read(forPlants.notifier).state = initialValue['for_plants'];
      ref.read(forPlantBatches.notifier).state =
          initialValue['for_plant_batches'];
      ref.read(forHarvests.notifier).state = initialValue['for_harvests'];
      ref.read(forPackages.notifier).state = initialValue['for_packages'];
    }
    return data;
  }
}

// PlantHarvest name field.
final plantHarvestType = StateProvider<String?>((ref) => null);

// Boolean fields.
final forPlants = StateProvider<bool?>((ref) => null);
final forPlantBatches = StateProvider<bool?>((ref) => null);
final forHarvests = StateProvider<bool?>((ref) => null);
final forPackages = StateProvider<bool?>((ref) => null);

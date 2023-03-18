// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 3/9/2023
// Updated: 3/16/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Dart imports:
import 'dart:async';

// Flutter imports:
import 'package:flutter/material.dart';

// Package imports:
import 'package:flutter_riverpod/flutter_riverpod.dart';

// Project imports:
import 'package:cannlytics_app/models/metrc/plant.dart';
import 'package:cannlytics_app/services/metrc_service.dart';
import 'package:cannlytics_app/ui/main/app_controller.dart';

/* Plants data */

// Plants provider.
final plantsProvider = AsyncNotifierProvider<PlantsController, List<Plant>>(
    () => PlantsController());

/// Plants controller.
class PlantsController extends AsyncNotifier<List<Plant>> {
  // Load initial data from Metrc.
  @override
  Future<List<Plant>> build() async => getPlants();

  /// Get plants.
  Future<List<Plant>> getPlants() async {
    final licenseNumber = ref.watch(primaryLicenseProvider);
    final orgId = ref.watch(primaryOrganizationProvider);
    final state = ref.watch(primaryStateProvider);
    if (licenseNumber == null) return [];
    try {
      // FIXME:
      // return await MetrcPlants.getPlants(
      //   license: licenseNumber,
      //   orgId: orgId,
      //   state: state,
      // );
      return [];
    } catch (error) {
      print("Error decoding JSON: [error=${error.toString()}]");
      return [];
    }
  }

  /// Set the plant.
  Future<void> setPlants(List<Plant> items) async {
    state = const AsyncValue.loading();
    state = await AsyncValue.guard(() async => items);
  }

  // TODO: Create plants.
  Future<void> createPlants(List<Plant> items) async {
    state = const AsyncValue.loading();
    state = await AsyncValue.guard(() async => items);
  }

  // TODO: Update plants.
  Future<void> updatePlants(List<Plant> items) async {
    state = const AsyncValue.loading();
    state = await AsyncValue.guard(() async => items);
  }

  // TODO: Delete plants.
  Future<void> deletePlants(List<Plant> items) async {
    state = const AsyncValue.loading();
    state = await AsyncValue.guard(() async => items);
  }
}

/* Table */

// Rows per page provider.
final plantsRowsPerPageProvider = StateProvider<int>((ref) => 5);

// Sorting providers.
final plantsSortColumnIndex = StateProvider<int>((ref) => 0);
final plantsSortAscending = StateProvider<bool>((ref) => true);

/* Search */

// Search term provider.
final searchTermProvider = StateProvider<String>((ref) => '');

/// Filtered plants provider.
final filteredPlantsProvider =
    StateNotifierProvider<FilteredPlantsNotifier, List<Plant>>(
  (ref) {
    // Listen to both data and search term.
    final data = ref.watch(plantsProvider).value;
    final searchTerm = ref.watch(searchTermProvider);
    return FilteredPlantsNotifier(ref, data ?? [], searchTerm);
  },
);

/// Filtered plants.
class FilteredPlantsNotifier extends StateNotifier<List<Plant>> {
  // Properties.
  final StateNotifierProviderRef<dynamic, dynamic> ref;
  final List<Plant> items;
  final String searchTerm;

  // Initialization.
  FilteredPlantsNotifier(
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
    List<Plant> matched = [];
    items.forEach((x) {
      // Matching logic.
      if (x.strainName!.toLowerCase().contains(keyword) ||
          x.id.contains(keyword)) {
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

// Plant selection provider.
final selectedPlantsProvider =
    NotifierProvider<SelectedPlantsNotifier, List<Plant>>(
        () => SelectedPlantsNotifier());

// Plant selection.
class SelectedPlantsNotifier extends Notifier<List<Plant>> {
  // Initialize with an empty list.
  @override
  List<Plant> build() => [];

  // Select a plant.
  void selectPlant(Plant item) {
    state = [...state, item];
  }

  // Unselect a plant.
  void unselectPlant(Plant item) {
    state = [
      for (final obj in state)
        if (obj.id != item.id) item,
    ];
  }
}

/* Plant Details */

// Plant ID.
final plantId = StateProvider<String?>((ref) => null);

// Plant provider.
final plantProvider =
    AsyncNotifierProvider.family<PlantController, Plant?, String?>(
  ({id}) {
    return PlantController(id: id);
  },
);

/// Plants controller.
class PlantController extends FamilyAsyncNotifier<Plant?, String?> {
  PlantController({required this.id}) : super();

  // Properties.
  final String? id;

  // Initialization.
  @override
  FutureOr<Plant?> build(String? id) async {
    if (id == null) return null;
    return await this.get(id);
  }

  /// Get plant.
  Future<Plant?> get(String id) async {
    final licenseNumber = ref.watch(primaryLicenseProvider);
    final orgId = ref.watch(primaryOrganizationProvider);
    final licenseState = ref.watch(primaryStateProvider);
    if (licenseNumber == null) return null;
    if (id == 'new') return Plant(id: '');
    try {
      return await MetrcPlants.getPlant(
        id: id,
        license: licenseNumber,
        orgId: orgId,
        state: licenseState,
      );
    } catch (error) {
      throw Exception("Error decoding JSON: [error=${error.toString()}]");
    }
  }

  /// Set the plant.
  Future<bool> set(Plant item) async {
    state = const AsyncValue.loading();
    state = await AsyncValue.guard(() async => item);
    ref.read(nameController).value =
        TextEditingValue(text: item.strainName ?? '');
    return state.hasError == false;
  }

  // TODO: Create plant.
  Future<bool> create(Plant item) async {
    state = const AsyncValue.loading();
    state = await AsyncValue.guard(() async => item);
    return state.hasError == false;
  }

  // TODO: Update plant.

  // TODO: Delete plant.
}

/* Plant Form */

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

/* Plant Types */

// // Plant types provider.
// final plantTypesProvider =
//     AsyncNotifierProvider<PlantTypesNotifier, List<dynamic>>(() {
//   return PlantTypesNotifier();
// });

// // Plant types controller.
// class PlantTypesNotifier extends AsyncNotifier<List<dynamic>> {
//   // Initialization.
//   @override
//   Future<List<dynamic>> build() async => getPlantTypes();

//   // Get plant types from Metrc.
//   Future<List<dynamic>> getPlantTypes() async {
//     final licenseNumber = ref.watch(primaryLicenseProvider);
//     final orgId = ref.watch(primaryOrganizationProvider);
//     final licenseState = ref.watch(primaryStateProvider);
//     List<dynamic> data;
//     try {
//       data = await MetrcPlants.getPlantTypes(
//         license: licenseNumber,
//         orgId: orgId,
//         state: licenseState,
//       );
//     } catch (error) {
//       return [];
//     }

//     final value = ref.read(plantType);
//     // Set initial plant type and permissions.
//     if (value == null && data.isNotEmpty) {
//       Map initialValue = data[0];
//       ref.read(plantType.notifier).state = initialValue['name'];
//       ref.read(forPlants.notifier).state = initialValue['for_plants'];
//       ref.read(forPlantBatches.notifier).state =
//           initialValue['for_plant_batches'];
//       ref.read(forHarvests.notifier).state = initialValue['for_harvests'];
//       ref.read(forPackages.notifier).state = initialValue['for_packages'];
//     }
//     return data;
//   }
// }

// // Plant name field.
// final plantType = StateProvider<String?>((ref) => null);

// // Boolean fields.
// final forPlants = StateProvider<bool?>((ref) => null);
// final forPlantBatches = StateProvider<bool?>((ref) => null);
// final forHarvests = StateProvider<bool?>((ref) => null);
// final forPackages = StateProvider<bool?>((ref) => null);

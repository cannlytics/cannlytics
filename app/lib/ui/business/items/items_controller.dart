// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 2/18/2023
// Updated: 3/18/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Package imports:
import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

// Project imports:
import 'package:cannlytics_app/models/metrc/item.dart';
import 'package:cannlytics_app/services/metrc_service.dart';
import 'package:cannlytics_app/ui/main/app_controller.dart';

/* Items data */

// Items provider.
final itemsProvider =
    AsyncNotifierProvider<ItemsController, List<Item>>(() => ItemsController());

/// Items controller.
class ItemsController extends AsyncNotifier<List<Item>> {
  // Load initial data from Metrc.
  @override
  Future<List<Item>> build() async => getItems();

  /// Get items.
  Future<List<Item>> getItems() async {
    final licenseNumber = ref.watch(primaryLicenseProvider);
    final licenseState = ref.read(primaryStateProvider);
    final orgId = ref.read(primaryOrganizationProvider);
    if (licenseNumber == null) return [];
    try {
      return await MetrcItems.getItems(
        license: licenseNumber,
        orgId: orgId,
        state: licenseState,
      );
    } catch (error) {
      print("Error decoding JSON: [error=${error.toString()}]");
      return [];
    }
  }

  /// Set the item.
  Future<void> setItems(List<Item> items) async {
    state = const AsyncValue.loading();
    state = await AsyncValue.guard(() async => items);
  }

  // Create items.
  Future<void> createItems(List<Item> items) async {
    state = const AsyncValue.loading();
    state = await AsyncValue.guard(() async {
      final licenseNumber = ref.read(primaryLicenseProvider);
      final licenseState = ref.read(primaryStateProvider);
      final orgId = ref.read(primaryOrganizationProvider);
      for (Item item in items) {
        // FIXME:
        // await MetrcItems.createItem(
        //   name: item.name,
        //   itemTypeName: item.itemTypeName,
        //   license: licenseNumber,
        //   orgId: orgId,
        //   state: licenseState,
        // );
      }
      return await getItems();
    });
  }

  // Update items.
  Future<void> updateItems(List<Item> items) async {
    state = const AsyncValue.loading();
    state = await AsyncValue.guard(() async {
      final licenseNumber = ref.read(primaryLicenseProvider);
      final licenseState = ref.read(primaryStateProvider);
      final orgId = ref.read(primaryOrganizationProvider);
      for (Item item in items) {
        // FIXME:
        // await MetrcItems.updateItem(
        //   id: item.id,
        //   name: item.name,
        //   itemTypeName: item.itemTypeName ?? 'Default Item Type',
        //   license: licenseNumber,
        //   orgId: orgId,
        //   state: licenseState,
        // );
      }
      return await getItems();
    });
  }

  // Delete items.
  Future<void> deleteItems(List<Item> items) async {
    state = const AsyncValue.loading();
    state = await AsyncValue.guard(() async {
      final licenseNumber = ref.read(primaryLicenseProvider);
      final licenseState = ref.read(primaryStateProvider);
      final orgId = ref.read(primaryOrganizationProvider);
      for (Item item in items) {
        // FIXME:
        // await MetrcItems.deleteItem(
        //   id: item.id,
        //   license: licenseNumber,
        //   orgId: orgId,
        //   state: licenseState,
        // );
      }
      return await getItems();
    });
  }
}

/* Table */

// Rows per page provider.
final itemsRowsPerPageProvider = StateProvider<int>((ref) => 5);

// Sorting providers.
final itemsSortColumnIndex = StateProvider<int>((ref) => 0);
final itemsSortAscending = StateProvider<bool>((ref) => true);

/* Search */

// Search term provider.
final searchTermProvider = StateProvider<String>((ref) => '');

/// Filtered items provider.
final filteredItemsProvider =
    StateNotifierProvider<FilteredItemsNotifier, List<Item>>(
  (ref) {
    // Listen to both data and search term.
    final data = ref.watch(itemsProvider).value;
    final searchTerm = ref.watch(searchTermProvider);
    return FilteredItemsNotifier(ref, data ?? [], searchTerm);
  },
);

/// Filtered items.
class FilteredItemsNotifier extends StateNotifier<List<Item>> {
  // Properties.
  final StateNotifierProviderRef<dynamic, dynamic> ref;
  final List<Item> items;
  final String searchTerm;

  // Initialization.
  FilteredItemsNotifier(
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
    List<Item> matched = [];
    items.forEach((x) {
      // TODO: Matching logic.
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

// Item selection provider.
final selectedItemsProvider =
    NotifierProvider<SelectedItemsNotifier, List<Item>>(
        () => SelectedItemsNotifier());

// Item selection.
class SelectedItemsNotifier extends Notifier<List<Item>> {
  // Initialize with an empty list.
  @override
  List<Item> build() => [];

  // Select a item.
  void selectItem(Item item) {
    state = [...state, item];
  }

  // Unselect a item.
  void unselectItem(Item item) {
    state = [
      for (final obj in state)
        if (obj.id != item.id) item,
    ];
  }
}

/* Item Details */

// Item ID.
final itemId = StateProvider<String?>((ref) => null);

// Item provider.
final itemProvider =
    AsyncNotifierProvider.family<ItemController, Item?, String?>(
  ({id}) => ItemController(id: id),
);

/// Items controller.
class ItemController extends FamilyAsyncNotifier<Item?, String?> {
  ItemController({required this.id}) : super();

  // Properties.
  final String? id;

  // Initialization.
  @override
  FutureOr<Item?> build(String? id) async {
    if (id == null) return null;
    return await this.get(id);
  }

  /// Get item.
  Future<Item?> get(String id) async {
    print('GETTING ITEM...');
    final items = ref.read(itemsProvider).value ?? [];
    for (Item item in items) {
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
    if (id == 'new') return Item();
    print('GETTING ITEM...');
    try {
      // FIXME:
      // return await MetrcItems.getItem(
      //   id: id,
      //   license: licenseNumber,
      //   orgId: orgId,
      //   state: licenseState,
      // );
    } catch (error) {
      throw Exception("Error decoding JSON: [error=${error.toString()}]");
    }
  }

  /// Set the item.
  Future<bool> set(Item item) async {
    state = const AsyncValue.loading();
    state = await AsyncValue.guard(() async => item);
    ref.read(nameController).value = TextEditingValue(text: item.name ?? '');
    return state.hasError == false;
  }

  // TODO: Create item.
  Future<bool> create(Item item) async {
    state = const AsyncValue.loading();
    state = await AsyncValue.guard(() async => item);
    return state.hasError == false;
  }

  // TODO: Update item.

  // TODO: Delete item.
}

/* Item Form */

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

/* Item Types */

// Item types provider.
final itemTypesProvider =
    AsyncNotifierProvider<ItemTypesNotifier, List<dynamic>>(
        () => ItemTypesNotifier());

// Item types controller.
class ItemTypesNotifier extends AsyncNotifier<List<dynamic>> {
  // Initialization.
  @override
  Future<List<dynamic>> build() async => getItemTypes();

  // Get item types from Metrc.
  Future<List<dynamic>> getItemTypes() async {
    final licenseNumber = ref.watch(primaryLicenseProvider);
    final orgId = ref.watch(primaryOrganizationProvider);
    final licenseState = ref.watch(primaryStateProvider);
    List<dynamic> data;
    try {
      // FIXME:
      // data = await MetrcItems.getItemTypes(
      //   license: licenseNumber,
      //   orgId: orgId,
      //   state: licenseState,
      // );
      data = [];
    } catch (error) {
      return [];
    }

    // Set initial item type and permissions.
    final value = ref.read(itemType);
    if (value == null && data.isNotEmpty) {
      Map initialValue = data[0];
      ref.read(itemType.notifier).state = initialValue['name'];
      ref.read(forPlants.notifier).state = initialValue['for_plants'];
      ref.read(forPlantBatches.notifier).state =
          initialValue['for_plant_batches'];
      ref.read(forHarvests.notifier).state = initialValue['for_harvests'];
      ref.read(forPackages.notifier).state = initialValue['for_packages'];
    }
    return data;
  }
}

// Item name field.
final itemType = StateProvider<String?>((ref) => null);

// Boolean fields.
final forPlants = StateProvider<bool?>((ref) => null);
final forPlantBatches = StateProvider<bool?>((ref) => null);
final forHarvests = StateProvider<bool?>((ref) => null);
final forPackages = StateProvider<bool?>((ref) => null);

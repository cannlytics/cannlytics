// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 3/8/2023
// Updated: 3/18/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Package imports:
import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

// Project imports:
import 'package:cannlytics_app/models/metrc/transfer.dart';
import 'package:cannlytics_app/services/metrc_service.dart';
import 'package:cannlytics_app/ui/main/app_controller.dart';

/* Transfers data */

// Transfers provider.
final transfersProvider =
    AsyncNotifierProvider<TransfersController, List<Transfer>>(
        () => TransfersController());

/// Transfers controller.
class TransfersController extends AsyncNotifier<List<Transfer>> {
  // Load initial data from Metrc.
  @override
  Future<List<Transfer>> build() async => getTransfers();

  /// Get transfers.
  Future<List<Transfer>> getTransfers() async {
    final licenseNumber = ref.watch(primaryLicenseProvider);
    final licenseState = ref.read(primaryStateProvider);
    final orgId = ref.read(primaryOrganizationProvider);
    if (licenseNumber == null) return [];
    try {
      // FIXME:
      // return await MetrcTransfers.getTransfers(
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

  /// Set the transfer.
  Future<void> setTransfers(List<Transfer> items) async {
    state = const AsyncValue.loading();
    state = await AsyncValue.guard(() async => items);
  }

  // Create transfers.
  Future<void> createTransfers(List<Transfer> items) async {
    state = const AsyncValue.loading();
    state = await AsyncValue.guard(() async {
      final licenseNumber = ref.read(primaryLicenseProvider);
      final licenseState = ref.read(primaryStateProvider);
      final orgId = ref.read(primaryOrganizationProvider);
      for (Transfer item in items) {
        // FIXME:
        // await MetrcTransfers.createTransfer(
        //   name: item.name,
        //   transferTypeName: item.transferTypeName,
        //   license: licenseNumber,
        //   orgId: orgId,
        //   state: licenseState,
        // );
      }
      return await getTransfers();
    });
  }

  // Update transfers.
  Future<void> updateTransfers(List<Transfer> items) async {
    state = const AsyncValue.loading();
    state = await AsyncValue.guard(() async {
      final licenseNumber = ref.read(primaryLicenseProvider);
      final licenseState = ref.read(primaryStateProvider);
      final orgId = ref.read(primaryOrganizationProvider);
      for (Transfer item in items) {
        // FIXME:
        // await MetrcTransfers.updateTransfer(
        //   id: item.id,
        //   name: item.name,
        //   transferTypeName: item.transferTypeName ?? 'Default Transfer Type',
        //   license: licenseNumber,
        //   orgId: orgId,
        //   state: licenseState,
        // );
      }
      return await getTransfers();
    });
  }

  // Delete transfers.
  Future<void> deleteTransfers(List<Transfer> items) async {
    state = const AsyncValue.loading();
    state = await AsyncValue.guard(() async {
      final licenseNumber = ref.read(primaryLicenseProvider);
      final licenseState = ref.read(primaryStateProvider);
      final orgId = ref.read(primaryOrganizationProvider);
      for (Transfer item in items) {
        // FIXME:
        // await MetrcTransfers.deleteTransfer(
        //   id: item.id,
        //   license: licenseNumber,
        //   orgId: orgId,
        //   state: licenseState,
        // );
      }
      return await getTransfers();
    });
  }
}

/* Table */

// Rows per page provider.
final transfersRowsPerPageProvider = StateProvider<int>((ref) => 5);

// Sorting providers.
final transfersSortColumnIndex = StateProvider<int>((ref) => 0);
final transfersSortAscending = StateProvider<bool>((ref) => true);

/* Search */

// Search term provider.
final searchTermProvider = StateProvider<String>((ref) => '');

/// Filtered transfers provider.
final filteredTransfersProvider =
    StateNotifierProvider<FilteredTransfersNotifier, List<Transfer>>(
  (ref) {
    // Listen to both data and search term.
    final data = ref.watch(transfersProvider).value;
    final searchTerm = ref.watch(searchTermProvider);
    return FilteredTransfersNotifier(ref, data ?? [], searchTerm);
  },
);

/// Filtered transfers.
class FilteredTransfersNotifier extends StateNotifier<List<Transfer>> {
  // Properties.
  final StateNotifierProviderRef<dynamic, dynamic> ref;
  final List<Transfer> items;
  final String searchTerm;

  // Initialization.
  FilteredTransfersNotifier(
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
    List<Transfer> matched = [];
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

// Transfer selection provider.
final selectedTransfersProvider =
    NotifierProvider<SelectedTransfersNotifier, List<Transfer>>(
        () => SelectedTransfersNotifier());

// Transfer selection.
class SelectedTransfersNotifier extends Notifier<List<Transfer>> {
  // Initialize with an empty list.
  @override
  List<Transfer> build() => [];

  // Select a transfer.
  void selectTransfer(Transfer item) {
    state = [...state, item];
  }

  // Unselect a transfer.
  void unselectTransfer(Transfer item) {
    state = [
      for (final obj in state)
        if (obj.id != item.id) item,
    ];
  }
}

/* Transfer Details */

// Transfer ID.
final transferId = StateProvider<String?>((ref) => null);

// Transfer provider.
final transferProvider =
    AsyncNotifierProvider.family<TransferController, Transfer?, String?>(
  ({id}) => TransferController(id: id),
);

/// Transfers controller.
class TransferController extends FamilyAsyncNotifier<Transfer?, String?> {
  TransferController({required this.id}) : super();

  // Properties.
  final String? id;

  // Initialization.
  @override
  FutureOr<Transfer?> build(String? id) async {
    if (id == null) return null;
    return await this.get(id);
  }

  /// Get transfer.
  Future<Transfer?> get(String id) async {
    final items = ref.read(transfersProvider).value ?? [];
    for (Transfer item in items) {
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
    if (id == 'new') return Transfer(id: '', name: '');
    print('GETTING TRANSFER...');
    try {
      // FIXME:
      // return await MetrcTransfers.getTransfer(
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

  /// Set the transfer.
  Future<bool> set(Transfer item) async {
    state = const AsyncValue.loading();
    state = await AsyncValue.guard(() async => item);
    // FIXME:
    // ref.read(nameController).value = TextEditingValue(text: item.name);
    return state.hasError == false;
  }

  // TODO: Create transfer.
  Future<bool> create(Transfer item) async {
    state = const AsyncValue.loading();
    state = await AsyncValue.guard(() async => item);
    return state.hasError == false;
  }

  // TODO: Update transfer.

  // TODO: Delete transfer.
}

/* Transfer Form */

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

/* Transfer Types */

// Transfer types provider.
final transferTypesProvider =
    AsyncNotifierProvider<TransferTypesNotifier, List<dynamic>>(
        () => TransferTypesNotifier());

// Transfer types controller.
class TransferTypesNotifier extends AsyncNotifier<List<dynamic>> {
  // Initialization.
  @override
  Future<List<dynamic>> build() async => getTransferTypes();

  // Get transfer types from Metrc.
  Future<List<dynamic>> getTransferTypes() async {
    final licenseNumber = ref.watch(primaryLicenseProvider);
    final orgId = ref.watch(primaryOrganizationProvider);
    final licenseState = ref.watch(primaryStateProvider);
    List<dynamic> data;
    try {
      // FIXME:
      // data = await MetrcTransfers.getTransferTypes(
      //   license: licenseNumber,
      //   orgId: orgId,
      //   state: licenseState,
      // );
      data = [];
    } catch (error) {
      return [];
    }

    // Set initial transfer type and permissions.
    final value = ref.read(transferType);
    if (value == null && data.isNotEmpty) {
      Map initialValue = data[0];
      ref.read(transferType.notifier).state = initialValue['name'];
      ref.read(forPlants.notifier).state = initialValue['for_plants'];
      ref.read(forPlantBatches.notifier).state =
          initialValue['for_plant_batches'];
      ref.read(forHarvests.notifier).state = initialValue['for_harvests'];
      ref.read(forPackages.notifier).state = initialValue['for_packages'];
    }
    return data;
  }
}

// Transfer name field.
final transferType = StateProvider<String?>((ref) => null);

// Boolean fields.
final forPlants = StateProvider<bool?>((ref) => null);
final forPlantBatches = StateProvider<bool?>((ref) => null);
final forHarvests = StateProvider<bool?>((ref) => null);
final forPackages = StateProvider<bool?>((ref) => null);

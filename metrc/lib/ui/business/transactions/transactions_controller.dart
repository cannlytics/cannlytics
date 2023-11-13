// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 3/9/2023
// Updated: 3/17/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// ignore_for_file: unused_local_variable, body_might_complete_normally_nullable

// Dart imports:
import 'dart:async';

// Flutter imports:
import 'package:flutter/material.dart';

// Package imports:
import 'package:flutter_riverpod/flutter_riverpod.dart';

// Project imports:
import 'package:cannlytics_app/models/metrc/sales_transaction.dart';
import 'package:cannlytics_app/services/metrc_service.dart';
import 'package:cannlytics_app/ui/main/app_controller.dart';

/* SalesTransactions data */

// SalesTransactions provider.
final salesTransactionsProvider =
    AsyncNotifierProvider<SalesTransactionsController, List<SalesTransaction>>(
        () => SalesTransactionsController());

/// SalesTransactions controller.
class SalesTransactionsController
    extends AsyncNotifier<List<SalesTransaction>> {
  // Load initial data from Metrc.
  @override
  Future<List<SalesTransaction>> build() async => getSalesTransactions();

  /// Get salesTransactions.
  Future<List<SalesTransaction>> getSalesTransactions() async {
    final licenseNumber = ref.watch(primaryLicenseProvider);
    final licenseState = ref.read(primaryStateProvider);
    final orgId = ref.read(primaryOrganizationProvider);
    if (licenseNumber == null) return [];
    try {
      return await MetrcSalesTransactions.getTransactions(
        license: licenseNumber,
        orgId: orgId,
        state: licenseState,
      );
    } catch (error) {
      print("Error decoding JSON: [error=${error.toString()}]");
      return [];
    }
  }

  /// Set the salesTransaction.
  Future<void> setSalesTransactions(List<SalesTransaction> items) async {
    state = const AsyncValue.loading();
    state = await AsyncValue.guard(() async => items);
  }

  // Create salesTransactions.
  Future<void> createSalesTransactions(List<SalesTransaction> items) async {
    state = const AsyncValue.loading();
    state = await AsyncValue.guard(() async {
      final licenseNumber = ref.read(primaryLicenseProvider);
      final licenseState = ref.read(primaryStateProvider);
      final orgId = ref.read(primaryOrganizationProvider);
      for (SalesTransaction item in items) {
        // FIXME:
        print('CREATE: $item');
        // await MetrcSalesTransactions.createSalesTransaction(
        //   name: item.name,
        //   salesTransactionTypeName: item.salesTransactionTypeName,
        //   license: licenseNumber,
        //   orgId: orgId,
        //   state: licenseState,
        // );
      }
      return await getSalesTransactions();
    });
  }

  // Update salesTransactions.
  Future<void> updateSalesTransactions(List<SalesTransaction> items) async {
    state = const AsyncValue.loading();
    state = await AsyncValue.guard(() async {
      final licenseNumber = ref.read(primaryLicenseProvider);
      final licenseState = ref.read(primaryStateProvider);
      final orgId = ref.read(primaryOrganizationProvider);
      for (SalesTransaction item in items) {
        // FIXME:
        print('UPDATE: $item');
        // await MetrcSalesTransactions.updateSalesTransaction(
        //   id: item.id,
        //   name: item.name,
        //   salesTransactionTypeName: item.salesTransactionTypeName ?? 'Default SalesTransaction Type',
        //   license: licenseNumber,
        //   orgId: orgId,
        //   state: licenseState,
        // );
      }
      return await getSalesTransactions();
    });
  }

  // Delete salesTransactions.
  Future<void> deleteSalesTransactions(List<SalesTransaction> items) async {
    state = const AsyncValue.loading();
    state = await AsyncValue.guard(() async {
      final licenseNumber = ref.read(primaryLicenseProvider);
      final licenseState = ref.read(primaryStateProvider);
      final orgId = ref.read(primaryOrganizationProvider);
      for (SalesTransaction item in items) {
        // FIXME:
        print('DELETE: $item');
        // await MetrcSalesTransactions.deleteSalesTransaction(
        //   id: item.id,
        //   license: licenseNumber,
        //   orgId: orgId,
        //   state: licenseState,
        // );
      }
      return await getSalesTransactions();
    });
  }
}

/* Table */

// Rows per page provider.
final salesTransactionsRowsPerPageProvider = StateProvider<int>((ref) => 5);

// Sorting providers.
final salesTransactionsSortColumnIndex = StateProvider<int>((ref) => 0);
final salesTransactionsSortAscending = StateProvider<bool>((ref) => true);

/* Search */

// Search term provider.
final searchTermProvider = StateProvider<String>((ref) => '');

/// Filtered salesTransactions provider.
final filteredSalesTransactionsProvider = StateNotifierProvider<
    FilteredSalesTransactionsNotifier, List<SalesTransaction>>(
  (ref) {
    // Listen to both data and search term.
    final data = ref.watch(salesTransactionsProvider).value;
    final searchTerm = ref.watch(searchTermProvider);
    return FilteredSalesTransactionsNotifier(ref, data ?? [], searchTerm);
  },
);

/// Filtered salesTransactions.
class FilteredSalesTransactionsNotifier
    extends StateNotifier<List<SalesTransaction>> {
  // Properties.
  final StateNotifierProviderRef<dynamic, dynamic> ref;
  final List<SalesTransaction> items;
  final String searchTerm;

  // Initialization.
  FilteredSalesTransactionsNotifier(
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
    List<SalesTransaction> matched = [];
    items.forEach((x) {
      // FIXME: Matching logic.
      // if (x.name.toLowerCase().contains(keyword) || x.id.contains(keyword)) {
      //   matched.add(x);
      // }
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

// SalesTransaction selection provider.
final selectedSalesTransactionsProvider =
    NotifierProvider<SelectedSalesTransactionsNotifier, List<SalesTransaction>>(
        () => SelectedSalesTransactionsNotifier());

// SalesTransaction selection.
class SelectedSalesTransactionsNotifier
    extends Notifier<List<SalesTransaction>> {
  // Initialize with an empty list.
  @override
  List<SalesTransaction> build() => [];

  // Select a salesTransaction.
  void selectSalesTransaction(SalesTransaction item) {
    state = [...state, item];
  }

  // Unselect a salesTransaction.
  void unselectSalesTransaction(SalesTransaction item) {
    state = [
      for (final obj in state)
        if (obj.salesDate != item.salesDate) item,
    ];
  }
}

/* SalesTransaction Details */

// SalesTransaction ID.
final salesTransactionId = StateProvider<String?>((ref) => null);

// SalesTransaction provider.
final salesTransactionProvider = AsyncNotifierProvider.family<
    SalesTransactionController, SalesTransaction?, String?>(
  ({id}) => SalesTransactionController(id: id),
);

/// SalesTransactions controller.
class SalesTransactionController
    extends FamilyAsyncNotifier<SalesTransaction?, String?> {
  SalesTransactionController({required this.id}) : super();

  // Properties.
  final String? id;

  // Initialization.
  @override
  FutureOr<SalesTransaction?> build(String? id) async {
    if (id == null) return null;
    return await this.get(id);
  }

  /// Get salesTransaction.
  Future<SalesTransaction?> get(String id) async {
    print('GETTING...');
    final items = ref.read(salesTransactionsProvider).value ?? [];
    for (SalesTransaction item in items) {
      if (item.salesDate == id) {
        print('Returning item:');
        print(item);
        return item;
      }
    }
    final licenseNumber = ref.watch(primaryLicenseProvider);
    final orgId = ref.read(primaryOrganizationProvider);
    final licenseState = ref.read(primaryStateProvider);
    if (licenseNumber == null) return null;
    if (id == 'new') return SalesTransaction();
    print('GETTING...');
    try {
      // FIXME:
      // return await MetrcSalesTransactions.getSalesTransaction(
      //   id: id,
      //   license: licenseNumber,
      //   orgId: orgId,
      //   state: licenseState,
      // );
    } catch (error) {
      throw Exception("Error decoding JSON: [error=${error.toString()}]");
    }
  }

  /// Set the salesTransaction.
  Future<bool> set(SalesTransaction item) async {
    state = const AsyncValue.loading();
    state = await AsyncValue.guard(() async => item);
    // FIXME:
    // ref.read(nameController).value = TextEditingValue(text: item.name);
    return state.hasError == false;
  }

  // TODO: Create salesTransaction.
  Future<bool> create(SalesTransaction item) async {
    state = const AsyncValue.loading();
    state = await AsyncValue.guard(() async => item);
    return state.hasError == false;
  }

  // TODO: Update salesTransaction.

  // TODO: Delete salesTransaction.
}

/* SalesTransaction Form */

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

/* SalesTransaction Types */

// SalesTransaction types provider.
final salesTransactionTypesProvider =
    AsyncNotifierProvider<SalesTransactionTypesNotifier, List<dynamic>>(
        () => SalesTransactionTypesNotifier());

// SalesTransaction types controller.
class SalesTransactionTypesNotifier extends AsyncNotifier<List<dynamic>> {
  // Initialization.
  @override
  Future<List<dynamic>> build() async => getSalesTransactionTypes();

  // Get salesTransaction types from Metrc.
  Future<List<dynamic>> getSalesTransactionTypes() async {
    final licenseNumber = ref.watch(primaryLicenseProvider);
    final orgId = ref.watch(primaryOrganizationProvider);
    final licenseState = ref.watch(primaryStateProvider);
    List<dynamic> data;
    try {
      // FIXME:
      // data = await MetrcSalesTransactions.getSalesTransactionTypes(
      //   license: licenseNumber,
      //   orgId: orgId,
      //   state: licenseState,
      // );
      data = [];
    } catch (error) {
      return [];
    }

    // Set initial salesTransaction type and permissions.
    final value = ref.read(salesTransactionType);
    if (value == null && data.isNotEmpty) {
      Map initialValue = data[0];
      ref.read(salesTransactionType.notifier).state = initialValue['name'];
      ref.read(forPlants.notifier).state = initialValue['for_plants'];
      ref.read(forPlantBatches.notifier).state =
          initialValue['for_plant_batches'];
      ref.read(forHarvests.notifier).state = initialValue['for_harvests'];
      ref.read(forPackages.notifier).state = initialValue['for_packages'];
    }
    return data;
  }
}

// SalesTransaction name field.
final salesTransactionType = StateProvider<String?>((ref) => null);

// Boolean fields.
final forPlants = StateProvider<bool?>((ref) => null);
final forPlantBatches = StateProvider<bool?>((ref) => null);
final forHarvests = StateProvider<bool?>((ref) => null);
final forPackages = StateProvider<bool?>((ref) => null);

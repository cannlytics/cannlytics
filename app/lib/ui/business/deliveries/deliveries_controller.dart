// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 3/7/2023
// Updated: 3/17/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Dart imports:
import 'dart:async';

// Flutter imports:
import 'package:flutter/material.dart';

// Package imports:
import 'package:flutter_riverpod/flutter_riverpod.dart';

// Project imports:
import 'package:cannlytics_app/models/metrc/delivery.dart';
import 'package:cannlytics_app/services/metrc_service.dart';
import 'package:cannlytics_app/ui/main/app_controller.dart';

/* Deliveries data */

// Deliveries provider.
final deliveriesProvider =
    AsyncNotifierProvider<DeliveriesController, List<Delivery>>(
        () => DeliveriesController());

/// Deliveries controller.
class DeliveriesController extends AsyncNotifier<List<Delivery>> {
  // Load initial data from Metrc.
  @override
  Future<List<Delivery>> build() async => getDeliveries();

  /// Get deliveries.
  Future<List<Delivery>> getDeliveries() async {
    final licenseNumber = ref.watch(primaryLicenseProvider);
    final licenseState = ref.read(primaryStateProvider);
    final orgId = ref.read(primaryOrganizationProvider);
    if (licenseNumber == null) return [];
    try {
      return await MetrcDeliveries.getDeliveries(
        license: licenseNumber,
        orgId: orgId,
        state: licenseState,
      );
    } catch (error) {
      print("Error decoding JSON: [error=${error.toString()}]");
      return [];
    }
  }

  /// Set the delivery.
  Future<void> setDeliveries(List<Delivery> items) async {
    state = const AsyncValue.loading();
    state = await AsyncValue.guard(() async => items);
  }

  // Create deliveries.
  Future<void> createDeliveries(List<Delivery> items) async {
    state = const AsyncValue.loading();
    state = await AsyncValue.guard(() async {
      final licenseNumber = ref.read(primaryLicenseProvider);
      final licenseState = ref.read(primaryStateProvider);
      final orgId = ref.read(primaryOrganizationProvider);
      // ignore: unused_local_variable
      for (Delivery item in items) {
        await MetrcDeliveries.createDelivery(
          data: {}, // FIXME:
          license: licenseNumber,
          orgId: orgId,
          state: licenseState,
        );
      }
      return await getDeliveries();
    });
  }

  // Update deliveries.
  Future<void> updateDeliveries(List<Delivery> items) async {
    state = const AsyncValue.loading();
    state = await AsyncValue.guard(() async {
      final licenseNumber = ref.read(primaryLicenseProvider);
      final licenseState = ref.read(primaryStateProvider);
      final orgId = ref.read(primaryOrganizationProvider);
      // ignore: unused_local_variable
      for (Delivery item in items) {
        await MetrcDeliveries.updateDelivery(
          data: {}, // FIXME:
          license: licenseNumber,
          orgId: orgId,
          state: licenseState,
        );
      }
      return await getDeliveries();
    });
  }

  // Delete deliveries.
  Future<void> deleteDeliveries(List<Delivery> items) async {
    state = const AsyncValue.loading();
    state = await AsyncValue.guard(() async {
      final licenseNumber = ref.read(primaryLicenseProvider);
      final licenseState = ref.read(primaryStateProvider);
      final orgId = ref.read(primaryOrganizationProvider);
      for (Delivery item in items) {
        await MetrcDeliveries.deleteDelivery(
          id: item.consumerId ?? '',
          license: licenseNumber,
          orgId: orgId,
          state: licenseState,
        );
      }
      return await getDeliveries();
    });
  }
}

/* Table */

// Rows per page provider.
final deliveriesRowsPerPageProvider = StateProvider<int>((ref) => 5);

// Sorting providers.
final deliveriesSortColumnIndex = StateProvider<int>((ref) => 0);
final deliveriesSortAscending = StateProvider<bool>((ref) => true);

/* Search */

// Search term provider.
final searchTermProvider = StateProvider<String>((ref) => '');

/// Filtered deliveries provider.
final filteredDeliveriesProvider =
    StateNotifierProvider<FilteredDeliveriesNotifier, List<Delivery>>(
  (ref) {
    // Listen to both data and search term.
    final data = ref.watch(deliveriesProvider).value;
    final searchTerm = ref.watch(searchTermProvider);
    return FilteredDeliveriesNotifier(ref, data ?? [], searchTerm);
  },
);

/// Filtered deliveries.
class FilteredDeliveriesNotifier extends StateNotifier<List<Delivery>> {
  // Properties.
  final StateNotifierProviderRef<dynamic, dynamic> ref;
  final List<Delivery> items;
  final String searchTerm;

  // Initialization.
  FilteredDeliveriesNotifier(
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
    List<Delivery> matched = [];
    items.forEach((x) {
      // Matching logic.
      if (x.driverName!.toLowerCase().contains(keyword) ||
          x.consumerId!.contains(keyword)) {
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

// Delivery selection provider.
final selectedDeliveriesProvider =
    NotifierProvider<SelectedDeliveriesNotifier, List<Delivery>>(
        () => SelectedDeliveriesNotifier());

// Delivery selection.
class SelectedDeliveriesNotifier extends Notifier<List<Delivery>> {
  // Initialize with an empty list.
  @override
  List<Delivery> build() => [];

  // Select a delivery.
  void selectDelivery(Delivery item) {
    state = [...state, item];
  }

  // Unselect a delivery.
  void unselectDelivery(Delivery item) {
    state = [
      for (final obj in state)
        if (obj.consumerId != item.consumerId) item,
    ];
  }
}

/* Delivery Details */

// Delivery ID.
final deliveryId = StateProvider<String?>((ref) => null);

// Delivery provider.
final deliveryProvider =
    AsyncNotifierProvider.family<DeliveryController, Delivery?, String?>(
  ({id}) => DeliveryController(id: id),
);

/// Deliveries controller.
class DeliveryController extends FamilyAsyncNotifier<Delivery?, String?> {
  DeliveryController({required this.id}) : super();

  // Properties.
  final String? id;

  // Initialization.
  @override
  FutureOr<Delivery?> build(String? id) async {
    if (id == null) return null;
    return await this.get(id);
  }

  /// Get delivery.
  Future<Delivery?> get(String id) async {
    final items = ref.read(deliveriesProvider).value ?? [];
    for (Delivery item in items) {
      if (item.consumerId == id) {
        print('Returning item:');
        print(item);
        return item;
      }
    }
    final licenseNumber = ref.watch(primaryLicenseProvider);
    final orgId = ref.read(primaryOrganizationProvider);
    final licenseState = ref.read(primaryStateProvider);
    if (licenseNumber == null) return null;
    if (id == 'new') return Delivery();
    try {
      return await MetrcDeliveries.getDelivery(
        id: id,
        license: licenseNumber,
        orgId: orgId,
        state: licenseState,
      );
    } catch (error) {
      throw Exception("Error decoding JSON: [error=${error.toString()}]");
    }
  }

  /// Set the delivery.
  Future<bool> set(Delivery item) async {
    state = const AsyncValue.loading();
    state = await AsyncValue.guard(() async => item);
    ref.read(nameController).value =
        TextEditingValue(text: item.driverName ?? '');
    return state.hasError == false;
  }

  // TODO: Create delivery.
  Future<bool> create(Delivery item) async {
    state = const AsyncValue.loading();
    state = await AsyncValue.guard(() async => item);
    return state.hasError == false;
  }

  // TODO: Update delivery.

  // TODO: Delete delivery.
}

/* Delivery Form */

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

// /* Delivery Types */

// // Delivery types provider.
// final deliveryTypesProvider =
//     AsyncNotifierProvider<DeliveryTypesNotifier, List<dynamic>>(
//         () => DeliveryTypesNotifier());

// // Delivery types controller.
// class DeliveryTypesNotifier extends AsyncNotifier<List<dynamic>> {
//   // Initialization.
//   @override
//   Future<List<dynamic>> build() async => getDeliveryTypes();

//   // Get delivery types from Metrc.
//   Future<List<dynamic>> getDeliveryTypes() async {
//     final licenseNumber = ref.watch(primaryLicenseProvider);
//     final orgId = ref.watch(primaryOrganizationProvider);
//     final licenseState = ref.watch(primaryStateProvider);
//     List<dynamic> data;
//     try {
//       data = await MetrcDeliveries.getDeliveryTypes(
//         license: licenseNumber,
//         orgId: orgId,
//         state: licenseState,
//       );
//     } catch (error) {
//       return [];
//     }

//     // Set initial delivery type and permissions.
//     final value = ref.read(deliveryType);
//     if (value == null && data.isNotEmpty) {
//       Map initialValue = data[0];
//       ref.read(deliveryType.notifier).state = initialValue['name'];
//       ref.read(forPlants.notifier).state = initialValue['for_plants'];
//       ref.read(forPlantBatches.notifier).state =
//           initialValue['for_plant_batches'];
//       ref.read(forHarvests.notifier).state = initialValue['for_harvests'];
//       ref.read(forPackages.notifier).state = initialValue['for_packages'];
//     }
//     return data;
//   }
// }

// // Delivery name field.
// final deliveryType = StateProvider<String?>((ref) => null);

// // Boolean fields.
// final forPlants = StateProvider<bool?>((ref) => null);
// final forPlantBatches = StateProvider<bool?>((ref) => null);
// final forHarvests = StateProvider<bool?>((ref) => null);
// final forPackages = StateProvider<bool?>((ref) => null);

// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 2/18/2023
// Updated: 3/18/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// ignore_for_file: body_might_complete_normally_nullable

// Dart imports:
import 'dart:async';

// Flutter imports:
import 'package:flutter/material.dart';

// Package imports:
import 'package:flutter_riverpod/flutter_riverpod.dart';

// Project imports:
import 'package:cannlytics_app/models/metrc/package.dart';
import 'package:cannlytics_app/services/metrc_service.dart';
import 'package:cannlytics_app/ui/main/app_controller.dart';

/* Packages data */

// Packages provider.
final packagesProvider =
    AsyncNotifierProvider<PackagesController, List<Package>>(
        () => PackagesController());

/// Packages controller.
class PackagesController extends AsyncNotifier<List<Package>> {
  // Load initial data from Metrc.
  @override
  Future<List<Package>> build() async => getPackages();

  /// Get packages.
  Future<List<Package>> getPackages() async {
    final licenseNumber = ref.watch(primaryLicenseProvider);
    final licenseState = ref.read(primaryStateProvider);
    final orgId = ref.read(primaryOrganizationProvider);
    if (licenseNumber == null) return [];
    try {
      return await MetrcPackages.getPackages(
        license: licenseNumber,
        orgId: orgId,
        state: licenseState,
      );
    } catch (error) {
      print("Error decoding JSON: [error=${error.toString()}]");
      return [];
    }
  }

  /// Set the package.
  Future<void> setPackages(List<Package> items) async {
    state = const AsyncValue.loading();
    state = await AsyncValue.guard(() async => items);
  }

  // Create packages.
  Future<void> createPackages(List<Package> items) async {
    state = const AsyncValue.loading();
    state = await AsyncValue.guard(() async {
      // final licenseNumber = ref.read(primaryLicenseProvider);
      // final licenseState = ref.read(primaryStateProvider);
      // final orgId = ref.read(primaryOrganizationProvider);
      // for (Package item in items) {
      //   // FIXME:
      //   // await MetrcPackages.createPackage(
      //   //   name: item.name,
      //   //   packageTypeName: item.packageTypeName,
      //   //   license: licenseNumber,
      //   //   orgId: orgId,
      //   //   state: licenseState,
      //   // );
      // }
      return await getPackages();
    });
  }

  // Update packages.
  Future<void> updatePackages(List<Package> items) async {
    state = const AsyncValue.loading();
    state = await AsyncValue.guard(() async {
      // final licenseNumber = ref.read(primaryLicenseProvider);
      // final licenseState = ref.read(primaryStateProvider);
      // final orgId = ref.read(primaryOrganizationProvider);
      // for (Package item in items) {
      //   // FIXME:
      //   // await MetrcPackages.updatePackage(
      //   //   id: item.id,
      //   //   name: item.name,
      //   //   packageTypeName: item.packageTypeName ?? 'Default Package Type',
      //   //   license: licenseNumber,
      //   //   orgId: orgId,
      //   //   state: licenseState,
      //   // );
      // }
      return await getPackages();
    });
  }

  // Delete packages.
  Future<void> deletePackages(List<Package> items) async {
    state = const AsyncValue.loading();
    state = await AsyncValue.guard(() async {
      // final licenseNumber = ref.read(primaryLicenseProvider);
      // final licenseState = ref.read(primaryStateProvider);
      // final orgId = ref.read(primaryOrganizationProvider);
      // for (Package item in items) {
      //   // FIXME:
      //   // await MetrcPackages.deletePackage(
      //   //   id: item.id,
      //   //   license: licenseNumber,
      //   //   orgId: orgId,
      //   //   state: licenseState,
      //   // );
      // }
      return await getPackages();
    });
  }
}

/* Table */

// Rows per page provider.
final packagesRowsPerPageProvider = StateProvider<int>((ref) => 5);

// Sorting providers.
final packagesSortColumnIndex = StateProvider<int>((ref) => 0);
final packagesSortAscending = StateProvider<bool>((ref) => true);

/* Search */

// Search term provider.
final searchTermProvider = StateProvider<String>((ref) => '');

/// Filtered packages provider.
final filteredPackagesProvider =
    StateNotifierProvider<FilteredPackagesNotifier, List<Package>>(
  (ref) {
    // Listen to both data and search term.
    final data = ref.watch(packagesProvider).value;
    final searchTerm = ref.watch(searchTermProvider);
    return FilteredPackagesNotifier(ref, data ?? [], searchTerm);
  },
);

/// Filtered packages.
class FilteredPackagesNotifier extends StateNotifier<List<Package>> {
  // Properties.
  final StateNotifierProviderRef<dynamic, dynamic> ref;
  final List<Package> items;
  final String searchTerm;

  // Initialization.
  FilteredPackagesNotifier(
    this.ref,
    this.items,
    this.searchTerm,
  ) : super([]) {
    // Search function.
    if (searchTerm.isEmpty) {
      state = items;
      return;
    }
    // String keyword = searchTerm.toLowerCase();
    List<Package> matched = [];
    items.forEach((x) {
      // Matching logic.
      // FIXME:
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

// Package selection provider.
final selectedPackagesProvider =
    NotifierProvider<SelectedPackagesNotifier, List<Package>>(
        () => SelectedPackagesNotifier());

// Package selection.
class SelectedPackagesNotifier extends Notifier<List<Package>> {
  // Initialize with an empty list.
  @override
  List<Package> build() => [];

  // Select a package.
  void selectPackage(Package item) {
    state = [...state, item];
  }

  // Unselect a package.
  void unselectPackage(Package item) {
    state = [
      for (final obj in state)
        if (obj.id != item.id) item,
    ];
  }
}

/* Package Details */

// Package ID.
final packageId = StateProvider<String?>((ref) => null);

// Package provider.
final packageProvider =
    AsyncNotifierProvider.family<PackageController, Package?, String?>(
  ({id}) => PackageController(id: id),
);

/// Packages controller.
class PackageController extends FamilyAsyncNotifier<Package?, String?> {
  PackageController({required this.id}) : super();

  // Properties.
  final String? id;

  // Initialization.
  @override
  FutureOr<Package?> build(String? id) async {
    if (id == null) return null;
    return await this.get(id);
  }

  /// Get package.
  Future<Package?> get(String id) async {
    print('GETTING...');
    final items = ref.read(packagesProvider).value ?? [];
    for (Package item in items) {
      if (item.id == id) {
        print('Returning item:');
        print(item);
        return item;
      }
    }
    final licenseNumber = ref.watch(primaryLicenseProvider);
    // final orgId = ref.read(primaryOrganizationProvider);
    // final licenseState = ref.read(primaryStateProvider);
    if (licenseNumber == null) return null;
    if (id == 'new') return Package();
    print('GETTING...');
    try {
      // FIXME:
      // return await MetrcPackages.getPackage(
      //   id: id,
      //   license: licenseNumber,
      //   orgId: orgId,
      //   state: licenseState,
      // );
    } catch (error) {
      throw Exception("Error decoding JSON: [error=${error.toString()}]");
    }
  }

  /// Set the package.
  Future<bool> set(Package item) async {
    state = const AsyncValue.loading();
    state = await AsyncValue.guard(() async => item);
    // FIXME:
    // ref.read(nameController).value = TextEditingValue(text: item.name);
    return state.hasError == false;
  }

  // TODO: Create package.
  Future<bool> create(Package item) async {
    state = const AsyncValue.loading();
    state = await AsyncValue.guard(() async => item);
    return state.hasError == false;
  }

  // TODO: Update package.

  // TODO: Delete package.
}

/* Package Form */

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

/* Package Types */

// Package types provider.
final packageTypesProvider =
    AsyncNotifierProvider<PackageTypesNotifier, List<dynamic>>(
        () => PackageTypesNotifier());

// Package types controller.
class PackageTypesNotifier extends AsyncNotifier<List<dynamic>> {
  // Initialization.
  @override
  Future<List<dynamic>> build() async => getPackageTypes();

  // Get package types from Metrc.
  Future<List<dynamic>> getPackageTypes() async {
    // final licenseNumber = ref.watch(primaryLicenseProvider);
    // final orgId = ref.watch(primaryOrganizationProvider);
    // final licenseState = ref.watch(primaryStateProvider);
    List<dynamic> data;
    try {
      // FIXME:
      // data = await MetrcPackages.getPackageTypes(
      //   license: licenseNumber,
      //   orgId: orgId,
      //   state: licenseState,
      // );
      data = [];
    } catch (error) {
      return [];
    }

    // Set initial package type and permissions.
    final value = ref.read(packageType);
    if (value == null && data.isNotEmpty) {
      Map initialValue = data[0];
      ref.read(packageType.notifier).state = initialValue['name'];
      ref.read(forPlants.notifier).state = initialValue['for_plants'];
      ref.read(forPlantBatches.notifier).state =
          initialValue['for_plant_batches'];
      ref.read(forHarvests.notifier).state = initialValue['for_harvests'];
      ref.read(forPackages.notifier).state = initialValue['for_packages'];
    }
    return data;
  }
}

// Package name field.
final packageType = StateProvider<String?>((ref) => null);

// Boolean fields.
final forPlants = StateProvider<bool?>((ref) => null);
final forPlantBatches = StateProvider<bool?>((ref) => null);
final forHarvests = StateProvider<bool?>((ref) => null);
final forPackages = StateProvider<bool?>((ref) => null);

// Cannlytics Data
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 5/7/2023
// Updated: 5/16/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Flutter imports:
import 'dart:html';

import 'package:cannlytics_data/services/storage_service.dart';
import 'package:flutter/material.dart';

// Package imports:
import 'package:flutter_riverpod/flutter_riverpod.dart';

// Project imports:
import 'package:cannlytics_data/common/inputs/string_controller.dart';
import 'package:cannlytics_data/models/licensee.dart';
import 'package:cannlytics_data/services/data_service.dart';
import 'package:cannlytics_data/services/firestore_service.dart';

/* === Data === */

// Licenses state.
final activeStateProvider = StateProvider<String?>((ref) => null);

// Licensees provider.
final licenseesProvider = AutoDisposeAsyncNotifierProvider<LicenseesController,
    List<Map<String, dynamic>>>(() => LicenseesController());

/// Licensees controller.
class LicenseesController
    extends AutoDisposeAsyncNotifier<List<Map<String, dynamic>>> {
  // Load initial licensees list.
  @override
  Future<List<Map<String, dynamic>>> build() async => _getLicensees();

  /// Get licensees.
  Future<List<Map<String, dynamic>>> _getLicensees() async {
    var stateId = ref.watch(activeStateProvider);
    if (stateId == null) {
      stateId = window.location.href.split('/').last;
    }
    // TODO: If a user is not signed in, then get a sample instead.
    String? url = await StorageService.getDownloadUrl(
        'data/licenses/$stateId/licenses-$stateId-latest.csv');
    if (url == null) return [];
    return await DataService.fetchCSVFromURL(url);
  }

  /// Set the licensees.
  Future<void> setLicensees(List<Map<String, dynamic>> items) async {
    state = const AsyncValue.loading();
    state = await AsyncValue.guard(() async => items);
  }
}

/* === Table === */

// Rows per page.
final licenseesRowsPerPageProvider = StateProvider<int>((ref) => 10);

// Sorting.
final licenseesSortColumnIndex = StateProvider<int>((ref) => 0);
final licenseesSortAscending = StateProvider<bool>((ref) => true);

/* === Search === */

// Search term.
final searchTermProvider = StateProvider<String>((ref) => '');

// Search input.
final licenseesSearchController =
    StateNotifierProvider<StringController, TextEditingController>(
        (ref) => StringController());

/// Filtered licensees provider.
final filteredLicenseesProvider = StateNotifierProvider.autoDispose<
    FilteredLicenseesNotifier, AsyncValue<List<Map<String, dynamic>>>>(
  (ref) {
    // Listen to search term and read the data.
    final searchTerm = ref.watch(searchTermProvider);
    final data = ref.watch(licenseesProvider).value;
    return FilteredLicenseesNotifier(ref, data ?? [], searchTerm);
  },
);

/// Filtered licensees.
class FilteredLicenseesNotifier
    extends StateNotifier<AsyncValue<List<Map<String, dynamic>>>> {
  // Properties.
  final StateNotifierProviderRef<dynamic, dynamic> ref;
  final List<Map<String, dynamic>> items;
  final String searchTerm;

  // Initialization.
  FilteredLicenseesNotifier(
    this.ref,
    this.items,
    this.searchTerm,
  ) : super(const AsyncLoading()) {
    // Search function.
    if (searchTerm.isEmpty) {
      state = AsyncValue.data(items);
      return;
    }
    String keyword = searchTerm.toLowerCase();
    // FIXME: Fix search logic.
    // List<Map<String, dynamic>> matched = [];
    // items.forEach((x) {
    //   // Matching logic.
    //   if (x['business_legal_name'].toLowerCase().contains(keyword) ||
    //       x['license_number'].toLowerCase().contains(keyword)) {
    //     matched.add(x);
    //   }
    // });
    state = AsyncValue.data(items);
  }
}

/* === Details === */

// Unused: Licensee ID.
// final licenseeId = StateProvider<String?>((ref) => 'new');

/// Licensee provider.
final licenseeProvider =
    AutoDisposeAsyncNotifierProvider<LicenseeController, Map<String, dynamic>?>(
        LicenseeController.new);

/// Licensee controller.
class LicenseeController
    extends AutoDisposeAsyncNotifier<Map<String, dynamic>?> {
  // Constructor.
  LicenseeController();

  /// Get licensee data.
  Future<Map<String, dynamic>> _getLicensee() async {
    var parts = window.location.href.split('/');
    // FIXME: Standardize to lowercase after re-uploading data.
    var stateId = parts[parts.length - 2].toUpperCase();
    var licenseId = parts.last;
    final _dataSource = ref.read(firestoreProvider);
    String path = 'data/licenses/$stateId/$licenseId';
    // FIXME: Path is not correct when coming from state licensees screen.
    print('PATH: $path');
    final data = await _dataSource.getDocument(path: path);
    print('RETRIEVED DATA: $data');
    return data ?? {};
  }

  // Load initial licensee list from Firestore
  @override
  Future<Map<String, dynamic>> build() async {
    return await _getLicensee();
  }
}

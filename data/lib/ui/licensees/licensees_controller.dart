// Cannlytics Data
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 5/7/2023
// Updated: 5/7/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Dart imports:
import 'dart:async';

// Flutter imports:
import 'package:cannlytics_data/common/inputs/string_controller.dart';
import 'package:cannlytics_data/models/licensee.dart';
import 'package:cannlytics_data/services/firestore_service.dart';
import 'package:flutter/material.dart';

// Package imports:
import 'package:flutter_riverpod/flutter_riverpod.dart';

/* Data */

// Active state.
final activeStateProvider = StateProvider<String?>((ref) => null);

// Licenses provider.
final licenseesProvider =
    AsyncNotifierProvider<LicenseesController, List<Licensee?>>(
        () => LicenseesController());

/// Licensees controller.
class LicenseesController extends AsyncNotifier<List<Licensee?>> {
  // Load initial licensees list from Metrc.
  @override
  Future<List<Licensee?>> build() async => _getLicensees();

  /// Get licensees.
  Future<List<Licensee?>> _getLicensees() async {
    // final orgId = ref.watch(primaryOrganizationProvider);
    // final state = ref.read(primaryStateProvider);
    // final currentLicensee = ref.read(primaryLicensee);
    print('GETTING LICENSEES: ${activeStateProvider}');
    return [];
    // try {
    //   var data = await MetrcLicensees.getLicensees(
    //     orgId: orgId,
    //     state: state,
    //   );
    //   // Set primary licensee.
    //   if (data.isNotEmpty && currentLicensee == null) {
    //     ref.read(primaryLicensee.notifier).state = data[0];
    //   }
    //   print('FOUND FACILITIES!');
    //   return data;
    // } catch (error, stack) {
    //   // print(stack);
    //   // throw Exception("Error decoding JSON: [error=${error.toString()}]");
    //   print("Error decoding JSON: [error=${error.toString()}]");
    //   return [];
    // }
  }

  /// Set the licensees.
  Future<void> setLicensees(List<Licensee?> items) async {
    state = const AsyncValue.loading();
    state = await AsyncValue.guard(() async => items);
  }
}

/* Table */

// Rows per page provider.
final licenseesRowsPerPageProvider = StateProvider<int>((ref) => 10);

// Sorting providers.
final licenseesSortColumnIndex = StateProvider<int>((ref) => 0);
final licenseesSortAscending = StateProvider<bool>((ref) => true);

/* Search */

// Search term provider.
final searchTermProvider = StateProvider<String>((ref) => '');

/// Filtered licensees provider.
final filteredLicenseesProvider =
    StateNotifierProvider<FilteredLicenseesNotifier, List<Licensee?>>(
  (ref) {
    final data = ref.watch(licenseesProvider).value;
    final searchTerm = ref.watch(searchTermProvider);
    return FilteredLicenseesNotifier(ref, data ?? [], searchTerm);
  },
);

/// Filtered licensees.
class FilteredLicenseesNotifier extends StateNotifier<List<Licensee?>> {
  // Properties.
  final StateNotifierProviderRef<dynamic, dynamic> ref;
  final List<Licensee?> items;
  final String searchTerm;

  // Initialization.
  FilteredLicenseesNotifier(
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
    List<Licensee> matched = [];
    items.forEach((x) {
      // Matching logic.
      if (x!.licenseType.toLowerCase().contains(keyword) ||
          x.id.contains(keyword)) {
        matched.add(x);
      }
    });
    state = matched;
  }
}

// Search input.
final licenseesSearchController =
    StateNotifierProvider<StringController, TextEditingController>(
        (ref) => StringController());

/* Licensee Details */

// Licensee ID.
final licenseeId = StateProvider<String?>((ref) => 'new');

// Licensee provider.
final licenseeProvider =
    AsyncNotifierProvider.family<LicenseeController, Licensee?, String?>(
        ({id}) => LicenseeController(id: id));

/// Facilities controller.
class LicenseeController extends FamilyAsyncNotifier<Licensee?, String?> {
  LicenseeController({required this.id}) : super();

  // Properties.
  final String? id;

  // Initialization.
  @override
  FutureOr<Licensee?> build(String? id) async {
    if (id == null || id == 'new') return null;
    return await this.get(id);
  }

  /// Get licensee.
  Future<Licensee?> get(String id) async {
    final items = ref.read(licenseesProvider).value ?? [];
    for (Licensee? item in items) {
      if (item!.id == id) {
        return item;
      }
    }
    return null;
  }

  /// Set the licensee.
  // Future<bool> set(Licensee item) async {
  //   state = const AsyncValue.loading();
  //   state = await AsyncValue.guard(() async => item);
  //   // TODO: Set all of the initial values.
  //   ref.read(nameController).value = TextEditingValue(text: item.name);
  //   ref.read(aliasController).value = TextEditingValue(text: item.alias);
  //   return state.hasError == false;
  // }
}

/* Service */

final stateLicensesProvider =
    StreamProvider<List<Map<String, dynamic>>>((ref) async* {
  // Connect to an API using sockets, and decode the output
  // final socket = await Socket.connect('my-api', 4242);
  // ref.onDispose(socket.close);

  // var allMessages = const <String>[];
  // await for (final message in socket.map(utf8.decode)) {
  //   // A new message has been received. Let's add it to the list of all messages.
  //   allMessages = [...allMessages, message];
  //   yield allMessages;
  // }
  // FIXME:
  final String activeState = 'wa';
  final FirestoreService _dataSource = ref.watch(firestoreProvider);
  yield* _dataSource.watchCollection(
    path: 'public/data/licenses',
    builder: (data, documentId) => data!,
    queryBuilder: (query) => query
        .where('premise_state', isEqualTo: activeState.toUpperCase())
        .limit(10),
  );
});

// Licenses service provider.
final licensesFirestoreProvider = Provider<LicensesService>((ref) {
  return LicensesService(ref.watch(firestoreProvider));
});

/// Licenses service.
class LicensesService {
  const LicensesService(this._dataSource);
  final FirestoreService _dataSource;

  // Set license data.
  // Future<void> setFacility({
  //   required UserID uid,
  //   required License values,
  // }) async {
  //   print('TODO: Save license!');
  //   // return _dataSource.setData(
  //   //   path: FirestorePath.facility(uid, facility.id),
  //   //   data: facility.toMap(),
  //   // );
  // }

  // Stream a license.
  // Stream<License> watchFacility({
  //   required UserID uid,
  //   required FacilityId facilityId,
  // }) async {
  //   return _dataSource.watchDocument(
  //     path: FirestorePath.facility(uid, facilityId),
  //     builder: (data, documentId) => Facility.fromMap(data, documentId),
  //   );
  // }

  // Stream licenses.
  Stream<List<Map>> watchLicenses({required String state}) {
    return _dataSource.watchCollection(
      path: 'public/data/licensees',
      builder: (data, documentId) => data!,
      queryBuilder: (query) =>
          query.where('state', isEqualTo: state.toUpperCase()),
    );
  }

  // // Get all licenses.
  // Future<List<License>> fetchFacilities({required UserID uid}) {
  //   return _dataSource.fetchCollection(
  //     path: FirestorePath.facilities(uid),
  //     builder: (data, documentId) => License.fromMap(data!),
  //   );
  // }
}

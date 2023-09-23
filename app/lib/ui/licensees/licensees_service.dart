// Cannlytics Data
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 5/7/2023
// Updated: 7/3/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Flutter imports:
import 'package:flutter/material.dart';

// Package imports:
import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

// Project imports:
import 'package:cannlytics_data/common/inputs/string_controller.dart';
import 'package:cannlytics_data/models/licensee.dart';
import 'package:cannlytics_data/services/firestore_service.dart';
import 'package:cannlytics_data/ui/account/account_controller.dart';

// TODO: Add the ability for user's to upload images for licenses.
// TODO: Add the ability for users to write reviews of licenses.
// TODO: Associate lab results and strains to licenses / labs.

/* === Data === */

// Licenses state.
final activeStateProvider = StateProvider<String?>((ref) => null);

// Licensees provider.
final licenseesProvider =
    AutoDisposeAsyncNotifierProvider<LicenseesController, List<Licensee?>>(
        () => LicenseesController());

/// Licensees controller.
class LicenseesController extends AutoDisposeAsyncNotifier<List<Licensee?>> {
  // Load initial licensees list.
  @override
  Future<List<Licensee?>> build() async => _getLicensees();

  /// Get licensees.
  Future<List<Licensee?>> _getLicensees() async {
    var stateId = ref.watch(activeStateProvider);
    if (stateId == null) {
      // FIXME:
      // stateId = window.location.href.split('/').last;
    }
    final _dataSource = ref.read(firestoreProvider);
    var data = await _dataSource.getCollection(
      path: 'data/licenses/$stateId',
      builder: (data, id) => Licensee.fromMap(data ?? {}),
      queryBuilder: (query) => query.orderBy('business_legal_name'),
    );
    return data;
  }

  /// Set the licensees.
  Future<void> setLicensees(List<Licensee?> items) async {
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
final licenseeSearchTerm = StateProvider<String>((ref) => '');

// Search input.
final licenseesSearchController =
    StateNotifierProvider<StringController, TextEditingController>(
        (ref) => StringController());

/* === Filter === */

/// Filtered licensees provider.
final filteredLicenseesProvider = StateNotifierProvider.autoDispose<
    FilteredLicenseesNotifier, AsyncValue<List<Licensee?>>>(
  (ref) {
    // Listen to search term and read the data.
    final searchTerm = ref.watch(licenseeSearchTerm);
    final data = ref.watch(licenseesProvider).value;
    return FilteredLicenseesNotifier(ref, data ?? [], searchTerm);
  },
);

/// Filtered licensees.
class FilteredLicenseesNotifier
    extends StateNotifier<AsyncValue<List<Licensee?>>> {
  // Properties.
  final StateNotifierProviderRef<dynamic, dynamic> ref;
  final List<Licensee?> items;
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
    List<Licensee?> matched = [];
    items.forEach((x) {
      // Create a new map that only contains the fields you are interested in.
      Map<String, dynamic> itemMap = {
        'businessDbaName': x?.businessDbaName,
        'businessLegalName': x?.businessLegalName,
        'licenseNumber': x?.licenseNumber,
        'licenseType': x?.licenseType,
        // 'premiseStreetAddress': x?.premiseStreetAddress,
        // 'businessEmail': x?.businessEmail,
        // 'businessPhone': x?.businessPhone,
      };

      // Now loop over this new map's values
      for (var value in itemMap.values) {
        if (value != null && value.toString().toLowerCase().contains(keyword)) {
          matched.add(x);
          break;
        }
      }
    });
    state = AsyncValue.data(matched);
  }
}

/* === Details === */

/// Stream a licensee from Firebase.
final licenseeProvider =
    StreamProvider.autoDispose.family<Licensee?, String>((ref, licenseNumber) {
  final _database = ref.watch(firestoreProvider);
  // FIXME:
  // var pathSegments = window.location.href.split('/');
  var pathSegments = [];
  var stateId = ref.watch(activeStateProvider);
  if (stateId == null) {
    if (pathSegments.length > 2) {
      stateId = pathSegments[pathSegments.length - 2];
    }
  }
  return _database.streamDocument(
    path: 'data/licenses/$stateId/$licenseNumber',
    builder: (data, documentId) => Licensee.fromMap(data ?? {}),
  );
});

// Also stream any data the user has saved for the licensee.
final userLicenseeData =
    StreamProvider.autoDispose.family<Map?, String>((ref, id) {
  final _database = ref.watch(firestoreProvider);
  final user = ref.watch(userProvider).value;
  if (user == null) return Stream.value(null);
  return _database.streamDocument(
    path: 'users/${user.uid}/licenses/$id',
    builder: (data, documentId) => data ?? {},
  );
});

// Current values.
final updatedLicensee = StateProvider<Licensee?>((ref) => null);

// Licensee service provider.
final licenseeService = Provider<LicenseeService>((ref) {
  return LicenseeService(ref.watch(firestoreProvider));
});

/// Licensee service.
class LicenseeService {
  const LicenseeService(this._dataSource);

  // Parameters.
  final FirestoreService _dataSource;

  // Update licensee.
  Future<void> updateLicensee(
    String stateId,
    String licenseNumber,
    Map<String, dynamic> data,
  ) async {
    await _dataSource.updateDocument(
      path: 'data/licenses/$stateId/$licenseNumber',
      data: data,
    );
  }

  // Upload image.
  // FIXME:
  // Future<void> uploadImage(File imageFile) async {
  //   // TODO: Implement your image upload logic here. You can use Firebase Storage if you want.
  // }

  // // Get gallery images.
  // Stream<List<String>> getGalleryImages(String stateId, String licenseNumber) {
  //   // TODO: Implement your gallery image retrieval logic here. You can use Firebase Storage if you want.
  //   // The method should return a stream of a list of image URLs.
  // }

  // Create / update comments.
  Future<void> updateComment(String stateId, String licenseNumber,
      String commentId, String comment) async {
    // TODO: Implement your comment update logic here.
  }
}

/* === Logs === */

// Licensee edit history logs.
final licenseeLogs =
    StateProvider.family<Query<Map<dynamic, dynamic>?>, List<String>>((
  ref,
  ids,
) {
  return FirebaseFirestore.instance
      .collection('data/licenses/${ids[0]}/${ids[1]}/licensee_logs')
      .orderBy('created_at', descending: true)
      .withConverter(
        fromFirestore: (snapshot, _) => snapshot.data()!,
        toFirestore: (item, _) => item as Map<String, Object?>,
      );
});

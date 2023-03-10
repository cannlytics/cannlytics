// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 2/18/2023
// Updated: 2/18/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Dart imports:
import 'dart:async';

// Package imports:
import 'package:flutter_riverpod/flutter_riverpod.dart';

// Project imports:
import 'package:cannlytics_app/models/metrc/license.dart';
import 'package:cannlytics_app/models/common/user.dart';
import 'package:cannlytics_app/services/auth_service.dart';
import 'package:cannlytics_app/services/firestore_service.dart';

// Licenses provider.
final licensesProvider =
    AutoDisposeAsyncNotifierProvider<LicensesController, void>(
        LicensesController.new);

/// Licenses controller.
class LicensesController extends AutoDisposeAsyncNotifier<void> {
  @override
  FutureOr<void> build() {}

  /// Save a license.
  Future<bool> addLicense(License data) async {
    final currentUser = ref.read(authProvider).currentUser;
    // final database = ref.read(licensesFirestoreProvider);
    state = const AsyncLoading();
    state = await AsyncValue.guard(() async {
      // return database.setFacility(
      //   uid: currentUser!.uid,
      //   values: entry,
      // );
      print('TODO: Add license!');
      print(data);
    });
    return state.hasError == false;
  }
}

// // Licenses service provider.
// final licensesFirestoreProvider = Provider<LicensesService>((ref) {
//   return LicensesService(ref.watch(firestoreProvider));
// });

// /// Licenses service.
// class LicensesService {
//   const LicensesService(this._dataSource);
//   final FirestoreService _dataSource;

//   // Set license data.
//   Future<void> setFacility({
//     required UserID uid,
//     required License values,
//   }) async {
//     print('TODO: Save license!');
//     // return _dataSource.setData(
//     //   path: FirestorePath.facility(uid, facility.id),
//     //   data: facility.toMap(),
//     // );
//   }

//   // Stream a license.
//   // Stream<License> watchFacility({
//   //   required UserID uid,
//   //   required FacilityId facilityId,
//   // }) async {
//   //   return _dataSource.watchDocument(
//   //     path: FirestorePath.facility(uid, facilityId),
//   //     builder: (data, documentId) => Facility.fromMap(data, documentId),
//   //   );
//   // }

//   // Stream all licenses.
//   Stream<List<License>> watchLicenses({required UserID uid}) {
//     return _dataSource.watchCollection(
//       path: FirestorePath.facilities(uid),
//       builder: (data, documentId) => License.fromMap(data!),
//     );
//   }

//   // Get all licenses.
//   Future<List<License>> fetchFacilities({required UserID uid}) {
//     return _dataSource.fetchCollection(
//       path: FirestorePath.facilities(uid),
//       builder: (data, documentId) => License.fromMap(data!),
//     );
//   }
// }

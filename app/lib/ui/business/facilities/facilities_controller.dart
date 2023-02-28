// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 2/18/2023
// Updated: 2/26/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Package imports:
import 'package:cannlytics_app/models/metrc/facility.dart';
import 'package:cannlytics_app/services/firestore_service.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

// Project imports:
import 'package:cannlytics_app/models/user.dart';
import 'package:cannlytics_app/services/auth_service.dart';

class FirestorePath {
  // TODO: Make paths revolve around organizations.
  static String facility(String uid, String facilityId) =>
      'users/$uid/facilities/$facilityId';
  static String facilities(String uid) => 'users/$uid/facilities';
}

/// Class to display facilities.
class FacilitiesListTileModel {
  const FacilitiesListTileModel({
    required this.leadingText,
    required this.trailingText,
    this.middleText,
    this.isHeader = false,
  });
  final String leadingText;
  final String trailingText;
  final String? middleText;
  final bool isHeader;
}

/// Service to manage facilities.
class FacilitiesService {
  const FacilitiesService(this._dataSource);
  final FirestoreService _dataSource;

  // Set facility data.
  Future<void> setFacility({required UserID uid, required Facility facility}) =>
      _dataSource.setData(
        path: FirestorePath.facility(uid, facility.id),
        data: facility.toMap(),
      );

  // Stream a facility.
  Stream<Facility> watchFacility(
          {required UserID uid, required FacilityId facilityId}) =>
      _dataSource.watchDocument(
        path: FirestorePath.facility(uid, facilityId),
        builder: (data, documentId) => Facility.fromMap(data, documentId),
      );

  // Stream all facilities.
  Stream<List<Facility>> watchFacilities({required UserID uid}) =>
      _dataSource.watchCollection(
        path: FirestorePath.facilities(uid),
        builder: (data, documentId) => Facility.fromMap(data, documentId),
      );

  // Get all facilities.
  Future<List<Facility>> fetchFacilities({required UserID uid}) =>
      _dataSource.fetchCollection(
        path: FirestorePath.facilities(uid),
        builder: (data, documentId) => Facility.fromMap(data, documentId),
      );
}

// The database provider.
final databaseProvider = Provider<FacilitiesService>((ref) {
  return FacilitiesService(ref.watch(firestoreDataSourceProvider));
});

// The facilities stream provider.
final facilitiesStreamProvider =
    StreamProvider.autoDispose<List<Facility>>((ref) {
  final user = ref.watch(authStateChangesProvider).value;
  if (user == null) {
    throw AssertionError('User can\'t be null');
  }
  final database = ref.watch(databaseProvider);
  return database.watchFacilities(uid: user.uid);
});

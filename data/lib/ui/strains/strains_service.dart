// Cannlytics Data
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 5/11/2023
// Updated: 7/4/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// TODO:
// - [ ] Variety Identification Prediction (V.I.P.) model
// - [ ] Patented strains dataset
// - [ ] Connecticut strains dataset
// - [ ] Washington strains dataset

// Dart imports:
import 'dart:async';

// Flutter imports:
import 'package:flutter/material.dart';

// Package imports:
import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

// Project imports:
import 'package:cannlytics_data/common/inputs/string_controller.dart';
import 'package:cannlytics_data/models/strain.dart';
import 'package:cannlytics_data/services/api_service.dart';
import 'package:cannlytics_data/services/firestore_service.dart';
import 'package:cannlytics_data/ui/account/account_controller.dart';
import 'package:cannlytics_data/utils/utils.dart';

/* === Search === */

// Search term.
final strainSearchTerm = StateProvider<String>((ref) => '');

// Lab results search input.
final strainsSearchController =
    StateNotifierProvider<StringController, TextEditingController>(
        (ref) => StringController());

// Strains keywords-only query.
final strainsQuery = StateProvider.family<Query<Strain>, String>((
  ref,
  orderBy,
) {
  // Get a list of keywords from the search term.
  /// FIXME: Implement search based on keywords.
  String searchTerm = ref.watch(strainSearchTerm);
  // List<String> keywords = searchTerm.toLowerCase().split(' ');

  // Query by search term.
  if (searchTerm.isNotEmpty) {
    return FirebaseFirestore.instance
        .collection('public/data/strains')
        .where('strain_name', isEqualTo: searchTerm)
        .withConverter(
          fromFirestore: (snapshot, _) => Strain.fromMap(snapshot.data()!),
          toFirestore: (Strain item, _) => item.toMap(),
        );
  }

  // TODO: Allow the user to sort by name, time, etc.

  // Query by time.
  return FirebaseFirestore.instance
      .collection('public/data/strains')
      .orderBy('strain_name', descending: false)
      .withConverter(
        fromFirestore: (snapshot, _) => Strain.fromMap(snapshot.data()!),
        toFirestore: (Strain item, _) => item.toMap(),
      );
});

/// Query by popularity.
final popularityQuery = StateProvider.family<Query<Strain>, String>((
  ref,
  orderBy,
) {
  /// FIXME: Implement search based on keywords.
  String searchTerm = ref.watch(strainSearchTerm);
  // List<String> keywords = searchTerm.toLowerCase().split(' ');

  // Query by search term and total favorites.
  if (searchTerm.isNotEmpty) {
    return FirebaseFirestore.instance
        .collection('public/data/strains')
        .where('strain_name', isEqualTo: searchTerm)
        .orderBy('total_favorites', descending: true)
        .withConverter(
          fromFirestore: (snapshot, _) => Strain.fromMap(snapshot.data()!),
          toFirestore: (Strain item, _) => item.toMap(),
        );
  }

  // Query by time.
  return FirebaseFirestore.instance
      .collection('public/data/strains')
      .orderBy('total_favorites', descending: true)
      .withConverter(
        fromFirestore: (snapshot, _) => Strain.fromMap(snapshot.data()!),
        toFirestore: (Strain item, _) => item.toMap(),
      );
});

/// Stream a user's favorite strains from Firebase.
/// FIXME: Ensure that the statistics are consistent with the user's data.
final userFavoriteStrains = StateProvider.family<Query<Strain>, String>((
  ref,
  uid,
) {
  return FirebaseFirestore.instance
      .collection('users/$uid/strains')
      .where('favorite', isEqualTo: true)
      .orderBy('updated_at', descending: true)
      .withConverter(
        fromFirestore: (snapshot, _) => Strain.fromMap(snapshot.data()!),
        toFirestore: (Strain item, _) => item.toMap(),
      );
});

/* === Data === */

/// Stream a strain from Firebase.
final strainProvider =
    StreamProvider.autoDispose.family<Strain?, String>((ref, id) {
  final _database = ref.watch(firestoreProvider);
  // FIXME: Move to hashes of the strain name.
  String strainId = Uri.decodeComponent(id);
  return _database.streamDocument(
    path: 'public/data/strains/$strainId',
    builder: (data, documentId) => Strain.fromMap(data ?? {}),
  );
});

// TODO: Also stream the strain's lab results.

// Also stream any data the user has saved for the strain.
final userStrainData =
    StreamProvider.autoDispose.family<Map?, String>((ref, id) {
  final _database = ref.watch(firestoreProvider);
  final user = ref.watch(userProvider).value;
  if (user == null) return Stream.value(null);
  return _database.streamDocument(
    path: 'users/${user.uid}/strains/$id',
    builder: (data, documentId) => data ?? {},
  );
});

// Current receipt values.
final updatedStrain = StateProvider<Strain?>((ref) => null);

// Strain service provider.
final strainService = Provider<StrainService>((ref) {
  return StrainService(ref.watch(firestoreProvider));
});

/// Strain service.
class StrainService {
  const StrainService(this._dataSource);

  // Parameters.
  final FirestoreService _dataSource;

  // Update strain.
  Future<void> updateStrain(String id, Map<String, dynamic> data) async {
    await _dataSource.updateDocument(
      path: 'public/data/strains/$id',
      data: data,
    );
  }

  // Delete strain.
  Future<void> deleteStrain(String id) async {
    await _dataSource.deleteDocument(path: 'public/data/strains/$id');
  }

  // Toggle favorite status of a strain.
  Future<void> toggleFavorite(Strain strain, String uid) async {
    var strainId = DataUtils.createHash(strain.name, privateKey: '');
    final path = 'users/$uid/strains/$strainId';
    final doc = await _dataSource.getDocument(path: path);
    bool isFavorite = doc?['favorite'] ?? false;
    Map<String, dynamic> data = strain.toMap();
    data['favorite'] = !isFavorite;
    data['uid'] = uid;
    data['updated_at'] = DateTime.now().toIso8601String();
    await _dataSource.updateDocument(
      path: path,
      data: data,
    );
  }
}

/* === Extraction === */

/// Generate strain descriptions and art images through the API.
class StrainGenerator extends AsyncNotifier<List<Map?>> {
  /// Initialize the generator.
  @override
  Future<List<Map?>> build() async {
    return [];
  }

  /// Generate descriptions and art images for strains.
  Future<void> generateStrainData(
    List<Strain> strains,
  ) async {
    state = const AsyncValue.loading();
    state = await AsyncValue.guard(() async {
      final items = await APIService.apiRequest(
        '/api/data/strains',
        data: strains.map((strain) => strain.toMap()).toList(),
      );
      return items.cast<Map<dynamic, dynamic>?>();
    });
  }

  // Clear generation results.
  Future<void> clear() async {
    state = const AsyncValue.loading();
    state = await AsyncValue.guard(() async {
      return [];
    });
  }
}

// An instance of the strain generator.
final strainGenerator = AsyncNotifierProvider<StrainGenerator, List<Map?>>(() {
  return StrainGenerator();
});

// Strain photo upload provider.
final strainPhotoUpload =
    StateNotifierProvider<StrainPhotoUpload, String>((ref) {
  return StrainPhotoUpload();
});

/// Strain photo upload.
class StrainPhotoUpload extends StateNotifier<String> {
  StrainPhotoUpload() : super('');

  // Upload photo for a strain.
  Future<void> uploadPhoto(String id, String photoPath) async {
    // TODO: Implement photo upload functionality.
    // You'll need to use a service like Firebase Storage to upload the photo,
    // then get the download URL and save it to the strain's document in Firestore.
  }
}

// Strain comments provider.
final strainCommentsProvider =
    StreamProvider.autoDispose.family<List<dynamic>, String>((ref, id) {
  final _database = ref.watch(firestoreProvider);
  return _database.streamDocument(
    path: 'public/data/strains/$id/comments',
    builder: (data, documentId) => List<dynamic>.from([data]),
  );
});

// Strain comment service provider.
final strainCommentService = Provider<StrainCommentService>((ref) {
  return StrainCommentService(ref.watch(firestoreProvider));
});

/// Strain comment service.
class StrainCommentService {
  const StrainCommentService(this._dataSource);

  // Parameters.
  final FirestoreService _dataSource;

  // Add comment to a strain.
  Future<void> addComment(String id, String comment) async {
    await _dataSource.updateDocument(
      path: 'public/data/strains/$id/comments',
      data: {'new_comment': comment},
      // Note: You'll need to update this to merge the new comment with the existing comments.
    );
  }

  // TODO: Update comment.
  // - Write Firestore rules to allow writing comments with their UID.
}

/* === Logs === */

// Strain edit history logs.
final strainLogs = StateProvider.family<Query<Map<dynamic, dynamic>?>, String>((
  ref,
  strainId,
) {
  return FirebaseFirestore.instance
      .collection('public/data/strains/$strainId/strain_logs')
      .orderBy('created_at', descending: true)
      .withConverter(
        fromFirestore: (snapshot, _) => snapshot.data()!,
        toFirestore: (item, _) => item as Map<String, Object?>,
      );
});

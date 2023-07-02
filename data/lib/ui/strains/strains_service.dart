// Cannlytics Data
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 5/11/2023
// Updated: 7/1/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// TODO:
// - [ ] Searchable database of observed strains
// - [ ] Variety Identification Prediction (V.I.P.) model
// - [ ] Patented strains dataset
// - [ ] Connecticut strains dataset
// - [ ] Washington strains dataset

// Dart imports:
import 'dart:async';

// Flutter imports:
import 'package:cannlytics_data/models/strain.dart';
import 'package:cannlytics_data/services/api_service.dart';
import 'package:cannlytics_data/services/firestore_service.dart';
import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

/* === Search === */

// Search term.
final strainSearchTerm = StateProvider<String>((ref) => '');

// Strains keywords-only query.
final strainsQuery = StateProvider.family<Query<Strain>, String>((
  ref,
  orderBy,
) {
  // Get a list of keywords from the search term.
  String searchTerm = ref.watch(strainSearchTerm);
  List<String> keywords = searchTerm.toLowerCase().split(' ');
  print('STRAIN KEYWORDS:');
  print(keywords);

  // Query by time.
  return FirebaseFirestore.instance
      .collection('public/data/strains')
      // .where('keywords', arrayContainsAny: keywords)
      .orderBy(orderBy, descending: true)
      .withConverter(
        fromFirestore: (snapshot, _) => Strain.fromMap(snapshot.data()!),
        toFirestore: (Strain item, _) => item.toMap(),
      );

  // Query by favorites.

  // Query by popularity.

  // Query by keywords.
  // return FirebaseFirestore.instance
  //     .collection('public/data/strains')
  //     .where('keywords', arrayContainsAny: keywords)
  //     .withConverter(
  //       fromFirestore: (snapshot, _) => Strain.fromMap(snapshot.data()!),
  //       toFirestore: (Strain item, _) => item.toMap(),
  //     );
});
// final keywordsQuery = FirebaseFirestore.instance
//     .collection('public/data/lab_results')
//     .where('keywords', arrayContainsAny: keywords)
//     .withConverter(
//       fromFirestore: (snapshot, _) => LabResult.fromMap(snapshot.data()!),
//       toFirestore: (LabResult item, _) => item.toMap(),
//     );
//

// // Lab results search input.
// final resultsSearchController =
//     StateNotifierProvider<StringController, TextEditingController>(
//         (ref) => StringController());

/* === Data === */

/// Stream strains from Firebase.
// final strainsProvider = StreamProvider<List<Strain>>((ref) async* {
//   final FirestoreService _dataSource = ref.watch(firestoreProvider);
//   yield* _dataSource.streamCollection(
//     path: 'public/data/strains',
//     builder: (data, documentId) => Strain.fromMap(data ?? {}),
//   );
// });

/// Stream a strain from Firebase.
final strainProvider =
    StreamProvider.autoDispose.family<Strain?, String>((ref, id) {
  final _database = ref.watch(firestoreProvider);
  return _database.streamDocument(
    path: 'public/data/strains/$id',
    builder: (data, documentId) => Strain.fromMap(data ?? {}),
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
}

// Dart imports:
// import 'dart:convert';

// Flutter imports:
// import 'package:flutter/material.dart';

// Package imports:
// import 'package:http/http.dart' as http;

// /// Strains service.
// class StrainsService {
//   const StrainsService._();

//   Future<void> getStrains([String query = '']) async {
//     // String url = '/api/data/strains$query';
//     // final response = await AuthRequestService().authRequest(url);
//     // strains = jsonDecode(response.body);
//     // List<String> strainNames = strains.map((x) => x['strain_name'] as String).toList();
//     // // TODO: use strainNames for auto-complete input
//     // setState(() {});
//   }

//   void getStrainResults() {
//     // bool matched = false;
//     // for (var strain in strains) {
//     //   if (strain['strain_name'] == selectedStrain) {
//     //     matched = true;
//     //     renderLabResultsForm(strain);
//     //     renderPredictionForm(strain, strain['model_stats']);
//     //     // TODO: Update the URL so the user can easily copy and return.
//     //   }
//     // }
//     // if (!matched) {
//     //   ScaffoldMessenger.of(context).showSnackBar(
//     //     SnackBar(content: Text('No Strain Records at this moment.')),
//     //   );
//     // }
//   }

//   // Future<void> findSimilarStrains(Map sample) async {
//   //   Map<String, dynamic> candidates = {};

//   //   // TODO: Get strains for each effect and aroma
//   //   for (String effect in sample['predicted_effects']) {
//   //     List<String> strains = await getStrains(effect);
//   //     // TODO: Keep list of predicted effects and aromas for each strain
//   //   }

//   //   // TODO: Return candidates with the most effect and aroma matches
//   // }

//   void renderLabResultsForm(Map<String, dynamic> strain) {
//     // TODO: implement this
//   }

//   void renderPredictionForm(Map<String, dynamic> strain, dynamic modelStats) {
//     // TODO: implement this
//   }
// }

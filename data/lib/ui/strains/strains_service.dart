// Cannlytics Data
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 5/11/2023
// Updated: 7/10/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// TODO:
// - [ ] Variety Identification Prediction (V.I.P.) model
// - [ ] Patented strains dataset
// - [ ] Connecticut strains dataset
// - [ ] Washington strains dataset

// Dart imports:
import 'dart:async';

// Flutter imports:
import 'package:cannlytics_data/services/api_service.dart';
import 'package:flutter/material.dart';

// Package imports:
import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

// Project imports:
import 'package:cannlytics_data/common/inputs/string_controller.dart';
import 'package:cannlytics_data/models/strain.dart';
import 'package:cannlytics_data/services/firestore_service.dart';
import 'package:cannlytics_data/ui/account/account_controller.dart';
import 'package:cannlytics_data/utils/utils.dart';

/* === Search === */

// Search term.
final strainSearchTerm = StateProvider<String>((ref) => '');

final selectedLetterProvider = StateProvider<String>((ref) => 'All');

// Lab results search input.
final strainsSearchController =
    StateNotifierProvider<StringController, TextEditingController>(
        (ref) => StringController());

// Strains keywords-only query.
// TODO: Allow the user to sort by name, time, etc.
final strainsQuery = StateProvider.family<Query<Strain>, String>((
  ref,
  orderBy,
) {
  // Get a list of keywords from the search term.
  String searchTerm = ref.watch(strainSearchTerm);
  List<String> keywords = searchTerm.toLowerCase().split(' ');

  // Query by search term.
  if (searchTerm.isNotEmpty) {
    return FirebaseFirestore.instance
        .collection('public/data/strains')
        .where('keywords', arrayContainsAny: keywords)
        .orderBy('strain_name', descending: false)
        .withConverter(
          fromFirestore: (snapshot, _) => Strain.fromMap(snapshot.data()!),
          toFirestore: (Strain item, _) => item.toMap(),
        );
  }

  // Otherwise, query by time alone.
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
  // Get a list of keywords from the search term.
  String searchTerm = ref.watch(strainSearchTerm);
  List<String> keywords = searchTerm.toLowerCase().split(' ');

  // Query by search term and total favorites.
  if (searchTerm.isNotEmpty) {
    return FirebaseFirestore.instance
        .collection('public/data/strains')
        .where('keywords', arrayContainsAny: keywords)
        .orderBy('total_favorites', descending: true)
        .withConverter(
          fromFirestore: (snapshot, _) => Strain.fromMap(snapshot.data()!),
          toFirestore: (Strain item, _) => item.toMap(),
        );
  }

  // Otherwise, query by time alone.
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
    builder: (data, documentId) {
      data?['id'] = documentId;
      return Strain.fromMap(data ?? {});
    },
  );
});

// TODO: Also stream the strain's lab results.

// Stream any data a user has saved for a strain.
final userStrainData =
    StreamProvider.autoDispose.family<Map?, String>((ref, id) {
  final _database = ref.watch(firestoreProvider);
  final user = ref.watch(userProvider).value;
  if (user == null) return Stream.value(null);
  return _database.streamDocument(
    path: 'users/${user.uid}/strains/$id',
    builder: (data, documentId) {
      data?['id'] = documentId;
      return data ?? {};
    },
  );
});

// Get any data a user has saved for a strain.
final userStrainDataProvider =
    FutureProvider.family.autoDispose<Map?, String>((ref, id) async {
  final _database = ref.watch(firestoreProvider);
  final user = ref.watch(userProvider).value;
  if (user == null) return null;
  return await _database.getDocument(
    path: 'users/${user.uid}/strains/$id',
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
  Future<void> updateStrain(String id, Map<dynamic, dynamic> data) async {
    await _dataSource.updateDocument(
      path: 'public/data/strains/$id',
      data: data as Map<String, dynamic>,
    );
  }

  // Delete strain.
  Future<void> deleteStrain(String id) async {
    await _dataSource.deleteDocument(path: 'public/data/strains/$id');
  }

  // Stream strain data.
  Stream<Strain> streamStrain(String id) {
    return _dataSource.streamDocument(
      path: 'public/data/strains/$id',
      builder: (data, documentId) => Strain.fromMap(data ?? {}),
    );
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

  // Generate a strain description.
  Future<String> generateStrainDescription(
    String name, {
    Map<String, dynamic>? stats,
    String? model,
    int? maxTokens,
    int? wordCount,
    double? temperature,
    String? id,
  }) async {
    final response = await APIService.apiRequest(
      '/api/ai/strains/description',
      data: {
        'id': id,
        'text': name,
        // 'stats': stats,
        // 'model': model,
        // 'max_tokens': maxTokens,
        'word_count': wordCount ?? 60,
        'temperature': temperature ?? 0.042,
      },
    );
    return response['description'];
  }

  // Generate strain art.
  Future<String> generateStrainArt(
    String name, {
    String? artStyle,
    int? n,
    String? size,
    String? id,
  }) async {
    final response = await APIService.apiRequest(
      '/api/ai/strains/art',
      data: {
        'id': id,
        'text': name,
        'art_style': artStyle ?? ' in the style of pixel art',
        'size': size ?? '1024x1024',
        'n': n ?? 1,
      },
    );
    return response['art_url'];
  }

  /// Generate strain descriptions and art images through the API.
  Future<void> generateStrainArtAndDescriptionIfMissing(
    Strain strain,
    WidgetRef ref,
  ) async {
    // Determine if the description or imageUrl are missing.
    bool shouldGenerateDescription = strain.description == null;
    bool shouldGenerateImageUrl = strain.imageUrl == null;

    // If both are present, no need to make any API call.
    if (!shouldGenerateDescription && !shouldGenerateImageUrl) return;

    // FIXME: Strain ID is null.
    print('STRAIN ID:');
    print(strain.id);
    if (strain.id.isEmpty) return;

    // Call your API to generate the description and imageUrl, as needed.
    var updatedFields = {};
    if (shouldGenerateDescription) {
      // Call your API to generate the description.
      String newDescription = await generateStrainDescription(
        strain.name,
        id: strain.id,
      );
      updatedFields['description'] = newDescription;
    }
    if (shouldGenerateImageUrl) {
      // Call your API to generate the imageUrl.
      String newImageUrl = await generateStrainArt(
        strain.name,
        id: strain.id,
      );
      updatedFields['imageUrl'] = newImageUrl;
    }

    // Update the document in Firestore.
    // await ref.read(strainService).updateStrain(strain.id, updatedFields);
  }
}

/// Strain description parameters.
final strainDescriptionParams = StateProvider<StrainDescriptionParams>((ref) {
  return StrainDescriptionParams(
      model: 'gpt-4', wordCount: 50, temperature: 0.42);
});

/// Strain art parameters.
final strainArtParams = StateProvider<StrainArtParams>((ref) {
  return StrainArtParams(
      artStyle: ' in the style of pixel art', n: 1, size: '1024x1024');
});

class StrainDescriptionParams {
  StrainDescriptionParams({
    required this.model,
    required this.wordCount,
    required this.temperature,
    this.description,
  });

  final String model;
  final int wordCount;
  final double temperature;
  final String? description;
}

class StrainArtParams {
  StrainArtParams({
    required this.artStyle,
    required this.n,
    required this.size,
    this.imageUrl,
  });

  final String artStyle;
  final int n;
  final String size;
  final String? imageUrl;
}

/* === Extraction === */

// /// Generate strain descriptions and art images through the API.
// class StrainGenerator extends AsyncNotifier<List<Map?>> {
//   /// Initialize the generator.
//   @override
//   Future<List<Map?>> build() async {
//     return [];
//   }

//   /// Generate descriptions and art images for strains.
//   Future<void> generateStrainData(
//     List<Strain> strains,
//   ) async {
//     state = const AsyncValue.loading();
//     state = await AsyncValue.guard(() async {
//       final items = await APIService.apiRequest(
//         '/api/data/strains',
//         data: strains.map((strain) => strain.toMap()).toList(),
//       );
//       return items.cast<Map<dynamic, dynamic>?>();
//     });
//   }

//   // Clear generation results.
//   Future<void> clear() async {
//     state = const AsyncValue.loading();
//     state = await AsyncValue.guard(() async {
//       return [];
//     });
//   }
// }

// // An instance of the strain generator.
// final strainGenerator = AsyncNotifierProvider<StrainGenerator, List<Map?>>(() {
//   return StrainGenerator();
// });

// // Strain photo upload provider.
// final strainPhotoUpload =
//     StateNotifierProvider<StrainPhotoUpload, String>((ref) {
//   return StrainPhotoUpload();
// });

// /// Strain photo upload.
// class StrainPhotoUpload extends StateNotifier<String> {
//   StrainPhotoUpload() : super('');

//   // Upload photo for a strain.
//   Future<void> uploadPhoto(String id, String photoPath) async {
//     // TODO: Implement photo upload functionality.
//     // You'll need to use a service like Firebase Storage to upload the photo,
//     // then get the download URL and save it to the strain's document in Firestore.
//   }
// }

// // Strain comments provider.
// final strainCommentsProvider =
//     StreamProvider.autoDispose.family<List<dynamic>, String>((ref, id) {
//   final _database = ref.watch(firestoreProvider);
//   return _database.streamDocument(
//     path: 'public/data/strains/$id/comments',
//     builder: (data, documentId) => List<dynamic>.from([data]),
//   );
// });

// // Strain comment service provider.
// final strainCommentService = Provider<StrainCommentService>((ref) {
//   return StrainCommentService(ref.watch(firestoreProvider));
// });

// /// Strain comment service.
// class StrainCommentService {
//   const StrainCommentService(this._dataSource);

//   // Parameters.
//   final FirestoreService _dataSource;

//   // Add comment to a strain.
//   Future<void> addComment(String id, String comment) async {
//     await _dataSource.updateDocument(
//       path: 'public/data/strains/$id/comments',
//       data: {'new_comment': comment},
//       // Note: You'll need to update this to merge the new comment with the existing comments.
//     );
//   }

//   // TODO: Update comment.
//   // - Write Firestore rules to allow writing comments with their UID.
// }

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

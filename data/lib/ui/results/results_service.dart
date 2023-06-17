// Cannlytics Data
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 6/13/2023
// Updated: 6/17/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Dart imports:
import 'dart:async';

// Flutter imports:
import 'package:cannlytics_data/common/inputs/string_controller.dart';
import 'package:cannlytics_data/services/api_service.dart';
import 'package:cannlytics_data/services/auth_service.dart';
import 'package:cannlytics_data/services/firestore_service.dart';
import 'package:cannlytics_data/utils/utils.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

/* === Data === */

/// Stream user results from Firebase.
final userResults = StreamProvider.family<List<Map<String, dynamic>>, String>(
    (ref, stateId) async* {
  final FirestoreService _dataSource = ref.watch(firestoreProvider);
  final user = ref.watch(authProvider).currentUser;
  yield* _dataSource.watchCollection(
    path: 'users/${user!.uid}/lab_results',
    builder: (data, documentId) => data!,
    queryBuilder: (query) =>
        query.orderBy('coa_parsed_at', descending: true).limit(1000),
  );
});

// TODO: Update user receipts.

// TODO: Delete user receipts.

/* === Extraction === */

/// Parse COA data through the API.
class COAParser extends AsyncNotifier<List<Map?>> {
  /// Initialize the parser.
  @override
  Future<List<Map?>> build() async {
    return [];
  }

  /// Parse a COA from a URL.
  /// [✓]: TEST: https://portal.acslabcannabis.com/qr-coa-view?salt=QUFFSTM3N181NzU5NDAwMDQwMzA0NTVfMDQxNzIwMjNfNjQzZDhiOTcyMzE1YQ==
  Future<void> parseUrl(String url) async {
    state = const AsyncValue.loading();
    state = await AsyncValue.guard(() async {
      final items = await APIService.apiRequest('/api/data/coas', data: {
        'urls': [url]
      });
      if (items is List<dynamic>) {
        List<Map<String, dynamic>> mappedItems = items.map((item) {
          return item as Map<String, dynamic>;
        }).toList();

        return mappedItems;
      } else {
        throw Exception(
            'Invalid data format. Expected List<Map<String, dynamic>>.');
      }
    });
  }

  /// Parse COA files (PDFs and images).
  Future<void> parseCOAs(
    List<dynamic> files, {
    List<dynamic>? fileNames,
  }) async {
    state = const AsyncValue.loading();
    state = await AsyncValue.guard(() async {
      var items = await APIService.apiRequest(
        '/api/data/coas',
        files: files,
        fileNames: fileNames,
      );
      return items.cast<Map<dynamic, dynamic>?>();
    });
  }

  // Clear parsing results.
  Future<void> clear() async {
    state = const AsyncValue.loading();
    state = await AsyncValue.guard(() async {
      return [];
    });
  }
}

// An instance of the user results provider.
final coaParser = AsyncNotifierProvider<COAParser, List<Map?>>(() {
  return COAParser();
});

/* === UI === */

// COA URL search input.
final urlSearchController =
    StateNotifierProvider<StringController, TextEditingController>(
        (ref) => StringController());

/* === Downloads === */

/// Data download service.
class DownloadService {
  const DownloadService._();

  /// Download COA data.
  static Future<void> downloadData(List<Map<String, dynamic>> data) async {
    var response = await APIService.apiRequest(
      '/api/data/coas/download',
      data: {'data': data},
    );
    if (kIsWeb) {
      WebUtils.downloadUrl(response['download_url']);
    } else {
      // TODO: Implement mobile download.
    }
  }
}

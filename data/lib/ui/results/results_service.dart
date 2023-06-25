// Cannlytics Data
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 6/13/2023
// Updated: 6/23/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Dart imports:
import 'dart:async';

// Flutter imports:
import 'package:cannlytics_data/common/inputs/string_controller.dart';
import 'package:cannlytics_data/services/api_service.dart';
import 'package:cannlytics_data/services/firestore_service.dart';
import 'package:cannlytics_data/ui/account/account_controller.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

/* === Data === */

/// Stream user results from Firebase.
final userResults = StreamProvider<List<Map?>>((ref) async* {
  final FirestoreService _dataSource = ref.watch(firestoreProvider);
  final user = ref.watch(userProvider).value;
  if (user == null) return;
  yield* _dataSource.watchCollection(
    path: 'users/${user.uid}/lab_results',
    builder: (data, documentId) => data!,
    queryBuilder: (query) => query.orderBy('coa_parsed_at', descending: true),
  );
});

// Result service provider.
final resultService = Provider<ResultService>((ref) {
  return ResultService();
});

/// Result service.
class ResultService {
  const ResultService();

  // Update result.
  Future<void> updateResult(String id, Map data) async {
    String url = '/api/data/coas/$id';
    await APIService.apiRequest(url, data: {'data': data});
  }

  // Delete result.
  Future<void> deleteResult(String id) async {
    String url = '/api/data/coas/$id';
    await APIService.apiRequest(url, options: {'delete': true});
  }
}

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

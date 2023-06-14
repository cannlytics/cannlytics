// Cannlytics Data
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 6/13/2023
// Updated: 6/13/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Dart imports:
import 'dart:async';
import 'dart:convert';
import 'dart:io';

// Flutter imports:
import 'package:cannlytics_data/common/inputs/string_controller.dart';
import 'package:cannlytics_data/services/api_service.dart';
import 'package:cannlytics_data/services/auth_service.dart';
import 'package:cannlytics_data/services/firestore_service.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:path_provider/path_provider.dart';

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

/// Parse COA data through the API.
class COAParser extends AsyncNotifier<List<Map?>> {
  // Future<List<Map?>> _getParsedResults() async {
  //   final json = await APIService.apiRequest('/api/data/coas');
  //   final items = jsonDecode(json) as List<Map<String, dynamic>>;
  //   return items;
  // }

  /// Initialize the parser.
  @override
  Future<List<Map?>> build() async {
    return [];
  }

  /// Parse a COA from a URL.
  /// [ ]: TEST: https://portal.acslabcannabis.com/qr-coa-view?salt=QUFFSTM3N181NzU5NDAwMDQwMzA0NTVfMDQxNzIwMjNfNjQzZDhiOTcyMzE1YQ==
  Future<void> parseUrl(String url) async {
    state = const AsyncValue.loading();
    state = await AsyncValue.guard(() async {
      // FIXME: Implement!!!
      print('PARSING URL: $url');
      final items = await APIService.apiRequest('/api/data/coas', data: {
        'urls': [url]
      });
      print('ITEMS: $items');
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
  Future<void> parseCOAs(List<dynamic> files) async {
    state = const AsyncValue.loading();
    state = await AsyncValue.guard(() async {
      // FIXME: Implement!!!
      final json = await APIService.apiRequest('/api/data/coas', files: files);
      print('JSON: $json');
      final items = jsonDecode(json) as List<Map<String, dynamic>>;
      print('ITEMS: $items');
      return items;
    });
  }

  // Clear parsing results.
  Future<void> clearResults() async {
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

/* === Download Service === */

/// Data download service.
class DownloadService {
  const DownloadService._();

  /// Download COA data.
  static Future<File> downloadData(List<Map<String, dynamic>> data) async {
    var response = await APIService.apiRequest(
      '/api/data/coas/download',
      data: {'data': data},
    );

    if (response.statusCode == 200) {
      var timestamp = DateTime.now()
          .toIso8601String()
          .substring(0, 19)
          .replaceAll(':', '-');
      var filePath = await _localFilePath('coa-data-$timestamp.xlsx');
      return File(filePath).writeAsBytes(response.bodyBytes);
    } else {
      print('Error downloading file: ${response.statusCode}');
      throw Exception('Error downloading file');
    }
  }

  /// Get the local file path.
  static Future<String> _localFilePath(String filename) async {
    var dir = await getApplicationDocumentsDirectory();
    return '${dir.path}/$filename';
  }
}

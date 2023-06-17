// Cannlytics Data
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 6/15/2023
// Updated: 6/16/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Dart imports:
import 'dart:async';
import 'dart:convert';

// Flutter imports:
import 'package:cannlytics_data/services/api_service.dart';
import 'package:cannlytics_data/services/auth_service.dart';
import 'package:cannlytics_data/services/firestore_service.dart';
import 'package:cannlytics_data/utils/utils.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

/* === Data === */

/// Stream user receipts from Firebase.
final userReceipts = StreamProvider.family<List<Map<String, dynamic>>, String>(
    (ref, stateId) async* {
  final FirestoreService _dataSource = ref.watch(firestoreProvider);
  final user = ref.watch(authProvider).currentUser;
  yield* _dataSource.watchCollection(
    path: 'users/${user!.uid}/receipts',
    builder: (data, documentId) => data!,
    queryBuilder: (query) =>
        query.orderBy('parsed_at', descending: true).limit(1000),
  );
});

/// Parse receipt data through the API.
class ReceiptParser extends AsyncNotifier<List<Map?>> {
  /// Initialize the parser.
  @override
  Future<List<Map?>> build() async {
    return [];
  }

  /// Parse receipt images.
  Future<void> parseImages(List<dynamic> files) async {
    state = const AsyncValue.loading();
    state = await AsyncValue.guard(() async {
      final json =
          await APIService.apiRequest('/api/data/receipts', files: files);
      final items = jsonDecode(json) as List<Map<String, dynamic>>;
      return items;
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
final receiptParser = AsyncNotifierProvider<ReceiptParser, List<Map?>>(() {
  return ReceiptParser();
});

/* === Download Service === */

/// Data download service.
class DownloadService {
  const DownloadService._();

  /// Download data.
  static Future<void> downloadData(List<Map<String, dynamic>> data) async {
    var response = await APIService.apiRequest(
      '/api/data/receipts/download',
      data: {'data': data},
    );

    if (response.statusCode == 200) {
      var timestamp = DateTime.now()
          .toIso8601String()
          .substring(0, 19)
          .replaceAll(':', '-');

      // Web download.
      String filename = 'receipt-data-$timestamp.xlsx';
      String base64String = base64Encode(response.bodyBytes);
      WebUtils.downloadBytes([base64String], filename);
    } else {
      throw Exception('Error downloading file');
    }
  }
}

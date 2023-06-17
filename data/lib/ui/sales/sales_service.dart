// Cannlytics Data
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 6/15/2023
// Updated: 6/17/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Dart imports:
import 'dart:async';

// Flutter imports:
import 'package:cannlytics_data/services/api_service.dart';
import 'package:cannlytics_data/services/auth_service.dart';
import 'package:cannlytics_data/services/firestore_service.dart';
import 'package:cannlytics_data/utils/utils.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

/* === Data === */

/// Stream user receipts from Firebase.
final userReceipts = StreamProvider<List<Map?>>((ref) async* {
  final FirestoreService _dataSource = ref.watch(firestoreProvider);
  final user = ref.watch(authProvider).currentUser;
  if (user == null) return;
  print('STREAMING RECEIPTS FOR USER: ${user.uid}');
  yield* _dataSource.watchCollection(
    path: 'users/${user.uid}/receipts',
    builder: (data, documentId) => data!,
    queryBuilder: (query) =>
        query.orderBy('parsed_at', descending: true).limit(1000),
  );
});

// TODO: Update user receipts.

// TODO: Delete user receipts.

/* === Extraction === */

/// Parse receipt data through the API.
class ReceiptParser extends AsyncNotifier<List<Map?>> {
  /// Initialize the parser.
  @override
  Future<List<Map?>> build() async {
    return [];
  }

  /// Parse receipt images.
  Future<void> parseImages(
    List<dynamic> files, {
    List<dynamic>? fileNames,
  }) async {
    state = const AsyncValue.loading();
    state = await AsyncValue.guard(() async {
      final items = await APIService.apiRequest(
        '/api/data/receipts',
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
final receiptParser = AsyncNotifierProvider<ReceiptParser, List<Map?>>(() {
  return ReceiptParser();
});

/* === Downloads === */

/// Data download service.
class DownloadService {
  const DownloadService._();

  /// Download receipt data.
  static Future<void> downloadData(List<Map<String, dynamic>> data) async {
    var response = await APIService.apiRequest(
      '/api/data/receipts/download',
      data: {'data': data},
    );
    if (kIsWeb) {
      WebUtils.downloadUrl(response['download_url']);
    } else {
      // TODO: Implement mobile download.
    }
  }
}

// Cannlytics Data
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 6/15/2023
// Updated: 6/23/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Dart imports:
import 'dart:async';

// Flutter imports:
import 'package:cannlytics_data/services/api_service.dart';
import 'package:cannlytics_data/services/auth_service.dart';
import 'package:cannlytics_data/services/firestore_service.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

/* === Data === */

/// Stream user receipts from Firebase.
final userReceipts = StreamProvider<List<Map?>>((ref) async* {
  final FirestoreService _dataSource = ref.watch(firestoreProvider);
  final user = ref.watch(authProvider).currentUser;
  if (user == null) return;
  yield* _dataSource.watchCollection(
    path: 'users/${user.uid}/receipts',
    builder: (data, documentId) => data!,
    queryBuilder: (query) => query.orderBy('parsed_at', descending: true),
  );
});

// Receipt service provider.
final receiptService = Provider<ReceiptService>((ref) {
  return ReceiptService();
});

/// Receipt service.
class ReceiptService {
  const ReceiptService();

  // Update receipt.
  Future<void> updateReceipt(String id, Map data) async {
    String url = '/api/data/receipts/$id';
    await APIService.apiRequest(url, data: {'data': data});
  }

  // Delete receipt.
  Future<void> deleteReceipt(String id) async {
    String url = '/api/data/receipts/$id';
    await APIService.apiRequest(url, options: {'delete': true});
  }
}

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

// An instance of the receipt parser.
final receiptParser = AsyncNotifierProvider<ReceiptParser, List<Map?>>(() {
  return ReceiptParser();
});

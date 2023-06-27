// Cannlytics Data
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 6/15/2023
// Updated: 6/27/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Dart imports:
import 'dart:async';

// Flutter imports:
import 'package:cannlytics_data/models/sales_receipt.dart';
import 'package:cannlytics_data/services/api_service.dart';
import 'package:cannlytics_data/services/firestore_service.dart';
import 'package:cannlytics_data/ui/account/account_controller.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

/* === Data === */

/// Stream user receipts from Firebase.
final userReceipts = StreamProvider<List<Map?>>((ref) async* {
  final FirestoreService _dataSource = ref.watch(firestoreProvider);
  final user = ref.watch(userProvider).value;
  if (user == null) return;
  yield* _dataSource.streamCollection(
    path: 'users/${user.uid}/receipts',
    builder: (data, documentId) => data!,
    queryBuilder: (query) => query.orderBy('parsed_at', descending: true),
  );
});

/// Stream a receipt from Firebase.
final receiptProvider =
    StreamProvider.autoDispose.family<SalesReceipt?, String>((ref, hash) {
  final _database = ref.watch(firestoreProvider);
  final user = ref.watch(userProvider).value;
  if (user == null) return Stream.value(null);
  return _database.streamDocument(
    path: 'users/${user.uid}/receipts/$hash',
    builder: (data, documentId) {
      // Keep track of current values for editing.
      var obj = SalesReceipt.fromMap(data ?? {});
      ref.read(currentReceipt.notifier).update((state) => data ?? {});
      return obj;
    },
  );
});

// Current receipt values.
final currentReceipt = StateProvider<Map>((ref) => {});

// Receipt service provider.
final receiptService = Provider<ReceiptService>((ref) {
  final uid = ref.read(userProvider).value?.uid ?? 'cannlytics';
  return ReceiptService(ref.watch(firestoreProvider), uid);
});

/// Receipt service.
class ReceiptService {
  const ReceiptService(this._dataSource, this.uid);

  // Parameters.
  final FirestoreService _dataSource;
  final String uid;

  // Update receipt.
  Future<void> updateReceipt(String id, Map<String, dynamic> data) async {
    await _dataSource.updateDocument(
      path: 'users/$uid/receipts/$id',
      data: data,
    );
  }

  // Delete receipt.
  Future<void> deleteReceipt(String id) async {
    await _dataSource.deleteDocument(path: 'users/$uid/receipts/$id');
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

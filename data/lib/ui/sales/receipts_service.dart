// Cannlytics Data
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 6/15/2023
// Updated: 7/8/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Dart imports:
import 'dart:async';

// Flutter imports:
import 'package:cannlytics_data/models/sales_receipt.dart';
import 'package:cannlytics_data/services/api_service.dart';
import 'package:cannlytics_data/services/firestore_service.dart';
import 'package:cannlytics_data/ui/account/account_controller.dart';
import 'package:cloud_firestore/cloud_firestore.dart';
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
      ref.read(updatedReceipt.notifier).update((state) => obj);
      return obj;
    },
  );
});

// Current receipt values.
final updatedReceipt = StateProvider<SalesReceipt?>((ref) => null);

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

/* === Logs === */

// Receipt edit history logs.
final receiptLogs =
    StateProvider.family<Query<Map<dynamic, dynamic>?>, String>((
  ref,
  hash,
) {
  final user = ref.watch(userProvider).value;
  // if (user == null) return Stream.value(<Map<dynamic, dynamic>?>[]);
  return FirebaseFirestore.instance
      .collection('users/${user?.uid}/receipts/$hash/receipt_logs')
      .orderBy('created_at', descending: true)
      .withConverter<Map<dynamic, dynamic>?>(
        fromFirestore: (snapshot, _) => snapshot.data()!,
        toFirestore: (Map<dynamic, dynamic>? item, _) =>
            item as Map<String, Object?>,
      );
});

/* === Analytics === */

/// Stream user receipt statistics from Firestore.
final receiptsStats = StreamProvider<List<Map<String, dynamic>>>((ref) async* {
  final _dataSource = ref.watch(firestoreProvider);
  final user = ref.watch(userProvider).value;
  if (user == null) return;
  DateTime now = DateTime.now();
  yield* _dataSource.streamCollection(
    path: 'users/${user.uid}/receipts_stats',
    builder: (data, documentId) => data!,
    queryBuilder: (query) {
      // TODO: Limit by time range.
      //  .where('date', isGreaterThanOrEqualTo: DateTime(now.year, now.month - 1).toString())
      return query.orderBy('date', descending: true).limit(60);
    },
  );
});

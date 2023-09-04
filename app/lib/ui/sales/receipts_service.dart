// Cannlytics Data
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 6/15/2023
// Updated: 9/3/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Dart imports:
import 'dart:async';

// Package imports:
import 'package:cannlytics_data/services/storage_service.dart';
import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

// Project imports:
import 'package:cannlytics_data/models/sales_receipt.dart';
import 'package:cannlytics_data/services/firestore_service.dart';
import 'package:cannlytics_data/ui/account/account_controller.dart';

/* === Data === */

// Date range.
final receiptsCurrentPageProvider = StateProvider<int>((ref) => 0);
final receiptsStartDateProvider = StateProvider<DateTime?>((ref) {
  DateTime now = DateTime.now();
  return DateTime(now.year, now.month + 1, 0);
});
final receiptsEndDateProvider = StateProvider<DateTime?>((ref) {
  DateTime now = DateTime.now();
  return DateTime(now.year, now.month - 3, 1);
});

/// Stream user receipts from Firebase.
final userReceipts = StreamProvider.autoDispose<List<Map?>>((ref) async* {
  final FirestoreService _dataSource = ref.watch(firestoreProvider);
  final user = ref.watch(userProvider).value;
  if (user == null) return;
  final startDate = ref.watch(receiptsStartDateProvider);
  final endDate = ref.watch(receiptsEndDateProvider);
  yield* _dataSource.streamCollection(
    path: 'users/${user.uid}/receipts',
    builder: (data, documentId) => data,
    queryBuilder: (query) {
      // Filter the receipts based on the start and end dates
      Query<Map<String, dynamic>> filteredQuery = query
          .orderBy('parsed_at', descending: true)
          .startAt([startDate?.toIso8601String()]).endAt(
              [endDate?.toIso8601String()]).limit(2000);
      return filteredQuery;
    },
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

/// Stream user's receipt parsing jobs from Firebase.
final receiptJobsProvider =
    StreamProvider.autoDispose<List<Map?>>((ref) async* {
  final FirestoreService _dataSource = ref.watch(firestoreProvider);
  final user = ref.watch(userProvider).value;
  yield* Stream.value(<Map<dynamic, dynamic>?>[]);
  if (user == null) return;
  yield* _dataSource.streamCollection(
    path: 'users/${user.uid}/parse_receipt_jobs',
    builder: (data, documentId) => data,
    queryBuilder: (query) => query.orderBy('job_created_at', descending: true),
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

  /// Common method to create a job in Firestore and return data for it
  Future<Map<String, dynamic>> _createJob(
    String uid, {
    dynamic file,
    String? fileName,
    String? fileUrl,
  }) async {
    // Create a job document in Firestore.
    DocumentReference docRef = FirebaseFirestore.instance
        .collection('users')
        .doc(uid)
        .collection('parse_receipt_jobs')
        .doc();
    String jobId = docRef.id;
    String fileRef = 'users/$uid/parse_receipt_jobs/$jobId';

    // If there's a file, upload it to Firebase Storage and get the download URL.
    if (file != null) {
      await StorageService.uploadRawData(fileRef, file);
      fileUrl = await StorageService.getDownloadUrl(fileRef);
    }

    // Return the job data.
    return {
      'uid': uid,
      'job_id': jobId,
      'job_created_at': DateTime.now().toIso8601String(),
      'job_finished_at': null,
      'job_error': false,
      'job_error_message': null,
      'job_duration': 0,
      'job_file_ref': fileRef,
      'job_file_url': fileUrl,
      'job_file_name': fileName,
    };
  }

  /// Parse receipt images.
  Future<void> parseImages(
    List<dynamic> files, {
    List<dynamic>? fileNames,
  }) async {
    state = const AsyncValue.loading();
    state = await AsyncValue.guard(() async {
      // Deprecated: API call directly to the backend.
      // final items = await APIService.apiRequest(
      //   '/api/data/receipts',
      //   files: files,
      //   fileNames: fileNames,
      // );
      // return items.cast<Map<dynamic, dynamic>?>();
      var allData = state.value ?? [];
      final user = ref.watch(userProvider).value;
      if (user == null) return [];
      for (var i = 0; i < files.length; i++) {
        var file = files[i];
        var fileName =
            fileNames != null && fileNames.length > i ? fileNames[i] : null;
        Map<String, dynamic> data = await _createJob(
          user.uid,
          file: file,
          fileName: fileName,
        );
        allData.add(data);
        String docRef =
            'users/${user.uid}/parse_receipt_jobs/${data['job_id']}';
        await ref
            .read(firestoreProvider)
            .updateDocument(path: docRef, data: data);
      }
      return allData;
    });
  }

  /// Delete a job.
  Future<void> deleteJob(String uid, String jobId) async {
    String docRef = 'users/$uid/parse_receipt_jobs/$jobId';
    await ref.read(firestoreProvider).deleteDocument(path: docRef);
    state = AsyncValue.data(
        (state.value ?? [])..removeWhere((item) => item?['job_id'] == jobId));
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

// Automatically increment date range.
final autoIncrementProvider = StateProvider<bool>((_) => true);

// Selected date range state provider.
final dateRangeProvider = StateProvider<String>((_) => 'All');

// Selected series state provider.
final seriesProvider = StateProvider<String>((_) => 'total_price');

/// Stream user receipt statistics from Firestore.
final receiptsStats =
    StreamProvider.autoDispose<List<Map<dynamic, dynamic>>>((ref) async* {
  final _dataSource = ref.watch(firestoreProvider);
  final user = ref.watch(userProvider).value;
  if (user == null) return;
  DateTime endDate = DateTime.now();
  DateTime startDate;
  final dateRange = ref.watch(dateRangeProvider);
  print('Toggling date range: ${dateRange}');
  switch (dateRange) {
    case '1M':
      startDate = DateTime(endDate.year, endDate.month - 1, endDate.day);
      break;
    case '3M':
      startDate = DateTime(endDate.year, endDate.month - 3, endDate.day);
      break;
    case 'YTD':
      startDate = DateTime(endDate.year, 1, 1);
      break;
    case '1Y':
      startDate = DateTime(endDate.year - 1, endDate.month, endDate.day);
      break;
    case 'All':
      startDate = DateTime(endDate.year - 1, endDate.month, endDate.day);
      break;
    default:
      startDate = DateTime(2018, 1, 1);
  }
  yield* _dataSource.streamCollection(
    path: 'users/${user.uid}/receipts_stats',
    builder: (data, documentId) => data!,
    queryBuilder: (query) {
      print('Starting after:');
      print(startDate.toIso8601String());
      return query
          .orderBy('date', descending: false)
          .startAfter([startDate.toIso8601String()]);
    },
  );
});

/// Stream a user's spend statistics from Firebase.
final totalSpendProvider = StreamProvider.autoDispose<Map?>((ref) {
  final _database = ref.watch(firestoreProvider);
  final user = ref.watch(userProvider).value;
  if (user == null) return Stream.value(null);
  return _database.streamDocument(
    path: 'users/${user.uid}/stats/spending',
    builder: (data, documentId) => data,
  );
});

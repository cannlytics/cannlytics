// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 2/18/2023
// Updated: 2/18/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Dart imports:
import 'dart:async';

// Package imports:
import 'package:flutter_riverpod/flutter_riverpod.dart';

// Project imports:
import 'package:cannlytics_app/models/entry.dart';
import 'package:cannlytics_app/models/job.dart';
import 'package:cannlytics_app/models/user.dart';
import 'package:cannlytics_app/services/auth_service.dart';
import 'package:cannlytics_app/services/firestore_service.dart';

String documentIdFromCurrentDate() {
  final iso = DateTime.now().toIso8601String();
  return iso.replaceAll(':', '-').replaceAll('.', '-');
}

class FirestorePath {
  static String facility(String uid, String jobId) => 'users/$uid/jobs/$jobId';
  static String facilities(String uid) => 'users/$uid/jobs';
  static String entry(String uid, String entryId) =>
      'users/$uid/entries/$entryId';
  static String entries(String uid) => 'users/$uid/entries';
}

class SpendingService {
  const SpendingService(this._dataSource);
  final FirestoreService _dataSource;

  Future<void> setJob({required UserID uid, required Job job}) =>
      _dataSource.setData(
        path: FirestorePath.facility(uid, job.id),
        data: job.toMap(),
      );

  /// Delete a package given it's ID.
  Future<void> deletePackage({
    required UserID uid,
    required Job job,
  }) async {
    final allEntries = await watchEntries(uid: uid, job: job).first;
    for (final entry in allEntries) {
      if (entry.jobId == job.id) {
        await deleteEntry(uid: uid, entry: entry);
      }
    }
    // delete job
    await _dataSource.deleteData(path: FirestorePath.facility(uid, job.id));
  }

  Stream<Job> watchJob({required UserID uid, required JobID jobId}) =>
      _dataSource.watchDocument(
        path: FirestorePath.facility(uid, jobId),
        builder: (data, documentId) => Job.fromMap(data, documentId),
      );

  Stream<List<Job>> watchJobs({required UserID uid}) =>
      _dataSource.watchCollection(
        path: FirestorePath.facilities(uid),
        builder: (data, documentId) => Job.fromMap(data, documentId),
      );

  Future<List<Job>> fetchJobs({required UserID uid}) =>
      _dataSource.fetchCollection(
        path: FirestorePath.facilities(uid),
        builder: (data, documentId) => Job.fromMap(data, documentId),
      );

  Future<void> setEntry({required UserID uid, required Entry entry}) =>
      _dataSource.setData(
        path: FirestorePath.entry(uid, entry.id),
        data: entry.toMap(),
      );

  Future<void> deleteEntry({required UserID uid, required Entry entry}) =>
      _dataSource.deleteData(path: FirestorePath.entry(uid, entry.id));

  Stream<List<Entry>> watchEntries({required UserID uid, Job? job}) =>
      _dataSource.watchCollection<Entry>(
        path: FirestorePath.entries(uid),
        queryBuilder: job != null
            ? (query) => query.where('jobId', isEqualTo: job.id)
            : null,
        builder: (data, documentID) => Entry.fromMap(data, documentID),
        sort: (lhs, rhs) => rhs.start.compareTo(lhs.start),
      );
}

final databaseProvider = Provider<SpendingService>((ref) {
  return SpendingService(ref.watch(firestoreDataSourceProvider));
});

final jobsStreamProvider = StreamProvider.autoDispose<List<Job>>((ref) {
  final user = ref.watch(authStateChangesProvider).value;
  if (user == null) {
    throw AssertionError('User can\'t be null');
  }
  final database = ref.watch(databaseProvider);
  return database.watchJobs(uid: user.uid);
});

final jobStreamProvider =
    StreamProvider.autoDispose.family<Job, JobID>((ref, jobId) {
  final user = ref.watch(authStateChangesProvider).value;
  if (user == null) {
    throw AssertionError('User can\'t be null');
  }
  final database = ref.watch(databaseProvider);
  return database.watchJob(uid: user.uid, jobId: jobId);
});

final jobEntriesStreamProvider =
    StreamProvider.autoDispose.family<List<Entry>, Job>((ref, job) {
  final user = ref.watch(authStateChangesProvider).value;
  if (user == null) {
    throw AssertionError('User can\'t be null when fetching jobs');
  }
  final database = ref.watch(databaseProvider);
  return database.watchEntries(uid: user.uid, job: job);
});

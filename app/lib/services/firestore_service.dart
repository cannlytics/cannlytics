// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 2/18/2023
// Updated: 3/2/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Package imports:
import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

/// The main Firestore paths.
class FirestorePath {
  // Organizations
  static String organizations() => 'organizations';
  static String organization(String uid) => 'organizations/$uid';

  // Users
  static String users() => 'users';
  static String user(String uid) => 'users/$uid';

  // Facilities
  static String facilities(String uid) => 'organizations/$uid/facilities';
  static String facility(String uid, String id) =>
      'organizations/$uid/facilities/$id';

  // Employees
  static String employees(String uid) => 'organizations/$uid/employees';
  static String employee(String uid, String id) =>
      'organizations/$uid/employee/$id';

  // Deliveries
  static String deliveries(String uid) => 'organizations/$uid/deliveries';
  static String delivery(String uid, String id) =>
      'organizations/$uid/deliveries/$id';

  // Packages
  static String packages(String uid) => 'organizations/$uid/packages';
  static String package(String uid, String id) =>
      'organizations/$uid/packages/$id';

  // Items
  static String items(String uid) => 'organizations/$uid/items';
  static String item(String uid, String id) => 'organizations/$uid/items/$id';

  // Locations
  static String locations(String uid) => 'organizations/$uid/locations';
  static String location(String uid, String id) =>
      'organizations/$uid/locations/$id';

  // Patients
  static String patients(String uid) => 'organizations/$uid/patients';
  static String patient(String uid, String id) =>
      'organizations/$uid/patients/$id';

  // Plants
  static String plants(String uid) => 'organizations/$uid/plants';
  static String plant(String uid, String id) => 'organizations/$uid/plants/$id';

  // Plant batches
  static String batches(String uid) => 'organizations/$uid/batches';
  static String batch(String uid, String id) =>
      'organizations/$uid/batches/$id';

  // Harvests
  static String harvests(String uid) => 'organizations/$uid/harvests';
  static String harvest(String uid, String id) =>
      'organizations/$uid/harvest/$id';

  // Lab Tests
  static String labTests(String uid) => 'organizations/$uid/lab_tests';
  static String lab_test(String uid, String id) =>
      'organizations/$uid/lab_tests/$id';

  // Lab Results
  static String labResults(String uid) => 'organizations/$uid/lab_results';
  static String labResult(String uid, String id) =>
      'organizations/$uid/lab_results/$id';

  // Sales receipts
  static String salesReceipts(String uid) =>
      'organizations/$uid/sales_receipts';
  static String salesReceipt(String uid, String id) =>
      'organizations/$uid/sales_receipts/$id';

  // Sales transactions
  static String salesTransactions(String uid) =>
      'organizations/$uid/sales_transactions';
  static String salesTransaction(String uid, String id) =>
      'organizations/$uid/sales_transactions/$id';

  // Strains
  static String strains(String uid) => 'organizations/$uid/strains';
  static String strain(String uid, String id) =>
      'organizations/$uid/strains/$id';

  // Transfers
  static String transfers(String uid) => 'organizations/$uid/transfers';
  static String transfer(String uid, String id) =>
      'organizations/$uid/transfers/$id';

  // Transfer templates
  static String transferTemplates(String uid) =>
      'organizations/$uid/transfer_templates';
  static String transferTemplate(String uid, String id) =>
      'organizations/$uid/transfer_templates/$id';

  // Types
  static String types(String uid) => 'organizations/$uid/types';
  static String type(String uid, String id) => 'organizations/$uid/types/$id';

  // TODO: Consumer paths.
}

/// The main Firestore client.
class FirestoreService {
  const FirestoreService._();

  /// Set data in Firestore given a path, optionally merging data.
  Future<void> setData({
    required String path,
    required Map<String, dynamic> data,
    bool merge = true,
  }) async {
    final reference = FirebaseFirestore.instance.doc(path);
    await reference.set(data, SetOptions(merge: merge));
  }

  /// Delete a document from Firestore.
  Future<void> deleteData({required String path}) async {
    final reference = FirebaseFirestore.instance.doc(path);
    await reference.delete();
  }

  /// Watch a collection as streams.
  Stream<List<T>> watchCollection<T>({
    required String path,
    required T Function(
      Map<String, dynamic>? data,
      String documentID,
    )
        builder,
    Query<Map<String, dynamic>>? Function(
      Query<Map<String, dynamic>> query,
    )?
        queryBuilder,
    int Function(T lhs, T rhs)? sort,
  }) {
    // Create a references.
    Query<Map<String, dynamic>> query =
        FirebaseFirestore.instance.collection(path);

    // Handle queries.
    if (queryBuilder != null) {
      query = queryBuilder(query)!;
    }

    // Return collection data.
    final snapshots = query.snapshots();
    return snapshots.map((snapshot) {
      final result = snapshot.docs
          .map((snapshot) => builder(
                snapshot.data(),
                snapshot.id,
              ))
          .where((value) => value != null)
          .toList();
      if (sort != null) {
        result.sort(sort);
      }
      return result;
    });
  }

  /// Watch a document as streams.
  Stream<T> watchDocument<T>({
    required String path,
    required T Function(
      Map<String, dynamic>? data,
      String documentID,
    )
        builder,
  }) {
    // Create a reference.
    final reference = FirebaseFirestore.instance.doc(path);

    // Listen to the document.
    final Stream<DocumentSnapshot<Map<String, dynamic>>> snapshots =
        reference.snapshots();

    // Return the document data.
    return snapshots.map((snapshot) => builder(
          snapshot.data(),
          snapshot.id,
        ));
  }

  /// Get documents from a collection.
  Future<List<T>> fetchCollection<T>({
    required String path,
    required T Function(
      Map<String, dynamic>? data,
      String documentID,
    )
        builder,
    Query<Map<String, dynamic>>? Function(
      Query<Map<String, dynamic>> query,
    )?
        queryBuilder,
    int Function(T lhs, T rhs)? sort,
  }) async {
    Query<Map<String, dynamic>> query =
        FirebaseFirestore.instance.collection(path);
    if (queryBuilder != null) {
      query = queryBuilder(query)!;
    }
    final snapshot = await query.get();
    final result = snapshot.docs
        .map((snapshot) => builder(
              snapshot.data(),
              snapshot.id,
            ))
        .where((value) => value != null)
        .toList();
    if (sort != null) {
      result.sort(sort);
    }
    return result;
  }

  /// Get a document.
  Future<T> fetchDocument<T>({
    required String path,
    required T Function(
      Map<String, dynamic>? data,
      String documentID,
    )
        builder,
  }) async {
    final reference = FirebaseFirestore.instance.doc(path);
    final snapshot = await reference.get();
    return builder(snapshot.data(), snapshot.id);
  }
}

// An instance of the Firestore provider.
final firestoreDataSourceProvider = Provider<FirestoreService>((ref) {
  return const FirestoreService._();
});

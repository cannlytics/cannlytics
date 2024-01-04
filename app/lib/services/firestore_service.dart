// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 2/18/2023
// Updated: 5/14/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Package imports:
import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

// Firestore provider.
final firestoreProvider = Provider<FirestoreService>((ref) {
  return const FirestoreService._();
});

/// The main Firestore client.
class FirestoreService {
  const FirestoreService._();

  /// Get a document.
  Future<Map<String, dynamic>?> getDocument({required String path}) async {
    final reference = FirebaseFirestore.instance.doc(path);
    final snapshot = await reference.get();
    var data = snapshot.data();
    if (data == null) return null;
    data['doc_id'] = snapshot.id;
    return data;
  }

  /// Get documents from a collection.
  Future<List<T>> getCollection<T>({
    required String path,
    required T Function(Map? data, String documentID) builder,
    Query<Map>? Function(Query<Map> query)? queryBuilder,
    int Function(T lhs, T rhs)? sort,
  }) async {
    Query<Map> query = FirebaseFirestore.instance.collection(path);
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

  /// Watch a document as streams.
  Stream<T> streamDocument<T>({
    required String path,
    required T Function(
      Map<String, dynamic>? data,
      String documentID,
    ) builder,
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

  /// Watch a collection as streams.
  Stream<List<T>> streamCollection<T>({
    required String path,
    required T Function(
      Map<String, dynamic>? data,
      String documentID,
    ) builder,
    Query<Map<String, dynamic>>? Function(
      Query<Map<String, dynamic>> query,
    )? queryBuilder,
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

  /// Add a document to a given collection.
  Future<String> addDocument({
    required String path,
    required Map<String, dynamic> data,
  }) async {
    final reference = FirebaseFirestore.instance.collection(path);
    DocumentReference<Map<String, dynamic>> doc = await reference.add(data);
    return doc.id;
  }

  /// Set data in Firestore given a path, optionally merging data.
  Future<void> updateDocument({
    required String path,
    required Map<String, dynamic> data,
    bool merge = true,
  }) async {
    final reference = FirebaseFirestore.instance.doc(path);
    await reference.set(data, SetOptions(merge: merge));
  }

  /// Delete a document from Firestore.
  Future<void> deleteDocument({required String path}) async {
    final reference = FirebaseFirestore.instance.doc(path);
    await reference.delete();
  }
}

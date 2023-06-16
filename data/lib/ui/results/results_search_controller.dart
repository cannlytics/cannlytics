// Cannlytics Data
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 5/23/2023
// Updated: 6/13/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Dart imports:
import 'dart:async';

// Flutter imports:
import 'package:flutter/material.dart';

// Package imports:
import 'package:flutter_riverpod/flutter_riverpod.dart';

// Project imports:
import 'package:cannlytics_data/common/inputs/string_controller.dart';
import 'package:cannlytics_data/models/lab_result.dart';
import 'package:cannlytics_data/services/auth_service.dart';
import 'package:cannlytics_data/services/firestore_service.dart';

// Lab results search input.
final resultsSearchController =
    StateNotifierProvider<StringController, TextEditingController>(
        (ref) => StringController());

// Lab results provider.
final asyncLabResultsProvider =
    AsyncNotifierProvider<AsyncLabResultsNotifier, List<LabResult>>(
        () => AsyncLabResultsNotifier());

// Lab results controller.
class AsyncLabResultsNotifier extends AsyncNotifier<List<LabResult>> {
  @override
  List<LabResult> build() => [];

  /// Get lab results.
  Future<List<LabResult>> _getLabResults(String? term) async {
    // Firestore reference.
    final _dataSource = ref.read(firestoreProvider);

    // FIXME: Let the user view lab results in different states.
    final String _dataPath = 'data/lab_results/fl';

    // TODO: Allow the user to change ordered by?
    // final String orderBy = 'updated_at';

    // TODO: Allow the user to change limit?
    final int limit = 1000;

    // Query by product_name.
    var data = await _dataSource.getCollection(
      path: _dataPath,
      builder: (data, id) => LabResult.fromMap(data!),
      queryBuilder: (query) {
        if (term != null) {
          return query
              .orderBy('product_name')
              .startAt([term]).endAt([term + '~']).limit(limit);
          // .where(
          //   'product_name',
          //   isGreaterThanOrEqualTo: term,
          //   isLessThanOrEqualTo: term + '\uf8ff',
          // )
        }
        return query.orderBy('updated_at', descending: true).limit(limit);
      },
    );
    print('FOUND: ${data.length} BY PRODUCT NAME');

    // Query by keywords.
    var supplement = [];
    if (term != null) {
      List<String> keywords = term.toLowerCase().split(' ');
      supplement = await _dataSource.getCollection(
        path: _dataPath,
        builder: (data, id) => LabResult.fromMap(data!),
        queryBuilder: (query) {
          return query
              .where('keywords', arrayContainsAny: keywords)
              .limit(limit);
        },
      );
    }
    print('FOUND: ${supplement.length} BY KEYWORDS');

    // Query by lab_id.
    var supplement2 = [];
    if (term != null) {
      supplement2 = await _dataSource.getCollection(
        path: _dataPath,
        builder: (data, id) => LabResult.fromMap(data!),
        queryBuilder: (query) {
          return query.where('lab_id', isEqualTo: term).limit(limit);
        },
      );
    }
    print('FOUND: ${supplement2.length} BY LAB ID');

    // Query by batch_number.
    var supplement3 = [];
    if (term != null) {
      supplement3 = await _dataSource.getCollection(
        path: _dataPath,
        builder: (data, id) => LabResult.fromMap(data!),
        queryBuilder: (query) {
          return query.where('batch_number', isEqualTo: term).limit(limit);
        },
      );
    }
    print('FOUND: ${supplement2.length} BY LAB ID');

    // Aggregate results from all queries.
    List<LabResult> combinedList = [
      ...data,
      ...supplement,
      ...supplement2,
      ...supplement3
    ];
    Set<LabResult> uniqueSet = Set<LabResult>.from(combinedList);
    List<LabResult> results = uniqueSet.toList();

    // Create a log of the search.
    final _user = ref.read(authProvider).currentUser;
    String timestamp = DateTime.now().toIso8601String();
    String logPath = 'logs/data/coas/${timestamp.replaceAll('.', '-')}';
    Map<String, dynamic> logData = {
      'search_term': term ?? null,
      'search_results': results.length,
      'timestamp': timestamp,
      'user': _user?.uid ?? null,
    };
    _dataSource.setData(path: logPath, data: logData);

    // Return the results.
    return results;
  }

  // Search lab results.
  Future<void> searchLabResults(String term) async {
    state = const AsyncValue.loading();
    state = await AsyncValue.guard(() async {
      return _getLabResults(term);
    });
  }

  // Clear lab results.
  Future<void> clearLabResults() async {
    state = const AsyncValue.loading();
    state = await AsyncValue.guard(() async {
      return [];
    });
  }
}

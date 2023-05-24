// Cannlytics Data
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 5/23/2023
// Updated: 5/23/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Dart imports:
import 'dart:async';

// Flutter imports:
import 'package:cannlytics_data/models/lab_result.dart';
import 'package:cannlytics_data/services/firestore_service.dart';
import 'package:flutter/material.dart';

// Package imports:
import 'package:flutter_riverpod/flutter_riverpod.dart';

// Project imports:
import 'package:cannlytics_data/common/inputs/string_controller.dart';

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

  // Get lab results.
  // FIXME: Let the user view lab results in different states.
  // TODO: Allow the user to change limit?
  // TODO: Allow the user to change ordered by?
  Future<List<LabResult>> _getLabResults(String? term) async {
    final _dataSource = ref.read(firestoreProvider);
    var data = await _dataSource.getCollection(
      path: 'data/lab_results/fl',
      builder: (data, id) => LabResult.fromMap(data!),
      queryBuilder: (query) {
        if (term != null) {
          return query
              .orderBy('product_name')
              .startAt([term]).endAt([term + '~']).limit(10);
          // .where(
          //   'product_name',
          //   isGreaterThanOrEqualTo: term,
          //   isLessThanOrEqualTo: term + '\uf8ff',
          // )
        }
        return query.orderBy('updated_at', descending: true).limit(10);
      },
    );
    print('FOUND: ${data.length} BY PRODUCT NAME');
    var supplement = [];
    if (term != null) {
      supplement = await _dataSource.getCollection(
        path: 'data/lab_results/fl',
        builder: (data, id) => LabResult.fromMap(data!),
        queryBuilder: (query) {
          return query
              .where('keywords', arrayContains: term.toLowerCase())
              .limit(10);
        },
      );
    }
    print('FOUND: ${supplement.length} BY KEYWORDS');
    // FIXME: Allow the user to search by: product_name, batch_number, lab_id, etc.
    // First search each for an exact match. Then search for a partial match.
    // - lab_id
    // - batch_number
    // - product_name
    List<LabResult> combinedList = [...data, ...supplement];
    Set<LabResult> uniqueSet = Set<LabResult>.from(combinedList);
    return uniqueSet.toList();
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

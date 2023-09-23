// Cannlytics Data
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 3/3/2023
// Updated: 7/3/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Flutter imports:
import 'package:flutter/material.dart';

// Package imports:
import 'package:flutter_riverpod/flutter_riverpod.dart';

// Project imports:
import 'package:cannlytics_data/services/firestore_service.dart';

/* Data */

/// Main datasets.
final datasetsProvider =
    FutureProvider<List<Map<dynamic, dynamic>?>>((ref) async {
  final _dataSource = ref.read(firestoreProvider);
  var data = await _dataSource.getCollection(
    path: 'public/ai/datasets',
    builder: (data, id) => data,
    queryBuilder: (query) => query.orderBy('type'),
  );
  return data;
});

/// Main AI models.
final aiModelsProvider =
    FutureProvider<List<Map<dynamic, dynamic>?>>((ref) async {
  final _dataSource = ref.read(firestoreProvider);
  var data = await _dataSource.getCollection(
    path: 'public/ai/models',
    builder: (data, id) => data,
    queryBuilder: (query) => query.orderBy('model_name', descending: true),
  );
  return data;
});

/* Navigation */

// Current page provider.
final currentPageProvider = StateProvider<String>((ref) => 'Data Dashboard');

// Menu controller.
final sideMenuOpen = StateProvider<bool>((ref) => true);

/* Layout */

/// Menu controller.
class MenuAppController extends ChangeNotifier {
  final GlobalKey<ScaffoldState> _scaffoldKey = GlobalKey<ScaffoldState>();

  GlobalKey<ScaffoldState> get scaffoldKey => _scaffoldKey;

  void controlMenu() {
    if (!_scaffoldKey.currentState!.isDrawerOpen) {
      _scaffoldKey.currentState!.openDrawer();
    }
  }
}

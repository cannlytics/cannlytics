// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 2/18/2023
// Updated: 2/20/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>
import 'dart:async';

import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:cannlytics_app/services/auth_service.dart';
import 'package:cannlytics_app/ui/business/inventory/packages/packages_service.dart';
import 'package:cannlytics_app/models/job.dart';

/// Manages packages.
class PackagesController extends AutoDisposeAsyncNotifier<void> {
  @override
  FutureOr<void> build() {}

  /// Deletes a package.
  Future<void> deletePackage(Job job) async {
    final currentUser = ref.read(authServiceProvider).currentUser;
    if (currentUser == null) {
      throw AssertionError('User can\'t be null');
    }
    final database = ref.read(databaseProvider);
    state = const AsyncLoading();
    state = await AsyncValue.guard(
        () => database.deletePackage(uid: currentUser.uid, job: job));
  }
}

final packagesProvider =
    AutoDisposeAsyncNotifierProvider<PackagesController, void>(
        PackagesController.new);

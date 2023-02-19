// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 2/18/2023
// Updated: 2/18/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>
import 'dart:async';

import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:cannlytics_app/services/auth_service.dart';

class AccountScreenController extends AutoDisposeAsyncNotifier<void> {
  @override
  FutureOr<void> build() {
    // ok to leave this empty if the return type is FutureOr<void>
  }

  Future<void> signOut() async {
    final authService = ref.read(authServiceProvider);
    state = const AsyncLoading();
    state = await AsyncValue.guard(authService.signOut);
  }
}

final accountScreenControllerProvider =
    AutoDisposeAsyncNotifierProvider<AccountScreenController, void>(
        AccountScreenController.new);

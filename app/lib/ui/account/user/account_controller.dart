// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 2/18/2023
// Updated: 3/6/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Dart imports:
import 'dart:async';

// Package imports:
import 'package:flutter_riverpod/flutter_riverpod.dart';

// Project imports:
import 'package:cannlytics_app/services/auth_service.dart';

// An instance of the account controller to use as a provider.
final accountProvider =
    AutoDisposeAsyncNotifierProvider<AccountController, void>(
        AccountController.new);

/// Controller that manages the user's account.
class AccountController extends AutoDisposeAsyncNotifier<void> {
  @override
  FutureOr<void> build() {}

  /// Change the user's photo.
  Future<void> changePhoto() async {
    final authService = ref.read(authProvider);
    state = const AsyncLoading();
    state = await AsyncValue.guard(authService.changePhoto);
  }

  /// Send the user a reset password email.
  Future<void> resetPassword(String email) async {
    final authService = ref.read(authProvider);
    state = const AsyncLoading();
    state = await AsyncValue.guard(() => authService.resetPassword(email));
  }

  /// Sign the user out.
  Future<void> signOut() async {
    final authService = ref.read(authProvider);
    state = const AsyncLoading();
    state = await AsyncValue.guard(authService.signOut);
  }
}

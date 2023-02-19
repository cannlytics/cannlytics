// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 2/18/2023
// Updated: 2/18/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>
import 'dart:async';

import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:cannlytics_app/ui/account/sign-in/sign_in_text.dart';
import 'package:cannlytics_app/services/auth_service.dart';

/// [SignInController] manages the sign in, sign up, and reset password screens.
class SignInController extends AutoDisposeAsyncNotifier<void> {
  @override
  FutureOr<void> build() {}

  /// [signIn] signs the user in with their email and password.
  Future<void> signIn({
    required String email,
    required String password,
    required SignInFormType formType,
  }) async {
    state = const AsyncValue.loading();
    state =
        await AsyncValue.guard(() => _authenticate(email, password, formType));
  }

  /// [_authenticate] either signs the user in or creates a new account.
  Future<void> _authenticate(
    String email,
    String password,
    SignInFormType formType,
  ) {
    final authService = ref.read(authServiceProvider);
    switch (formType) {
      case SignInFormType.signIn:
        return authService.signInWithEmailAndPassword(email, password);
      case SignInFormType.register:
        return authService.createUserWithEmailAndPassword(email, password);
    }
  }

  /// [signInAnonymously] allows the user to sign in anonymously.
  Future<void> signInAnonymously() async {
    final authService = ref.read(authServiceProvider);
    state = const AsyncLoading();
    state = await AsyncValue.guard(authService.signInAnonymously);
  }
}

// An instance of the sign-in controller.
final signInProvider = AutoDisposeAsyncNotifierProvider<SignInController, void>(
    SignInController.new);

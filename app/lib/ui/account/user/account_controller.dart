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
import 'package:cannlytics_app/services/firestore_service.dart';
import 'package:cannlytics_app/ui/main/app_controller.dart';
import 'package:firebase_auth/firebase_auth.dart';
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

  /// Update the user's display name and email.
  Future<void> updateUser({
    String? email,
    String? displayName,
    String? phoneNumber,
  }) async {
    // final authService = ref.read(authProvider);
    state = const AsyncLoading();
    state = await AsyncValue.guard(() async {
      final user = ref.read(userProvider).value;
      final _firestore = ref.watch(firestoreProvider);

      if (user != null) {
        if (displayName != null && displayName != user.displayName) {
          await user.updateDisplayName(displayName);
        }

        if (email != null && email != user.email) {
          await user.updateEmail(email);
        }

        if (phoneNumber != null && phoneNumber != user.phoneNumber) {
          // First, create a PhoneAuthCredential with the verification ID and verification code
          // obtained from the user.
          final credential = PhoneAuthProvider.credential(
            verificationId:
                "verificationId", // Replace with your verification ID
            smsCode: "smsCode", // Replace with your verification code
          );

          // Then update the user's phone number with the new phone number.
          await user.updatePhoneNumber(credential);
        }

        // Update the user's data in Firestore.
        await _firestore.setData(
          path: 'users/${user.uid}',
          data: {
            'email': user.email,
            'display_name': user.displayName,
            'phone_number': user.phoneNumber,
          },
        );
      }
    });
  }
}

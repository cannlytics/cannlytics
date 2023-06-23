// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 2/18/2023
// Updated: 6/23/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Dart imports:
import 'dart:async';

// Package imports:
import 'package:flutter_riverpod/flutter_riverpod.dart';

// Project imports:
import 'package:cannlytics_data/services/auth_service.dart';
import 'package:cannlytics_data/services/firestore_service.dart';
import 'package:cannlytics_data/ui/dashboard/dashboard_controller.dart';

/* === User === */

// An instance of the account controller to use as a provider.
final accountProvider =
    AutoDisposeAsyncNotifierProvider<AccountController, void>(
        AccountController.new);

/// Controller that manages the user's account.
class AccountController extends AutoDisposeAsyncNotifier<void> {
  @override
  FutureOr<void> build() {}

  /// Change the user's photo.
  Future<String> changePhoto() async {
    final authService = ref.read(authProvider);
    state = const AsyncLoading();
    var message;
    state = const AsyncLoading();
    state = await AsyncValue.guard(() async {
      message = await authService.changePhoto();
    });
    return message;
  }

  /// Send the user a reset password email.
  Future<String> resetPassword(String email) async {
    final authService = ref.read(authProvider);
    var message;
    state = const AsyncLoading();
    state = await AsyncValue.guard(() async {
      message = await authService.resetPassword(email);
    });
    return message;
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
    state = const AsyncLoading();
    state = await AsyncValue.guard(() async {
      // Get the appropriate providers.
      final user = ref.read(userProvider).value;
      final _firestore = ref.watch(firestoreProvider);

      // Return if there is no user.
      if (user == null) return;

      // Update the user's display name.
      if (displayName != null && displayName != user.displayName) {
        await user.updateDisplayName(displayName);
      }

      // Update the user's email.
      if (email != null && email != user.email) {
        await user.updateEmail(email);
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
    });
  }

  /// Save the user's data.
  Future<void> saveUserData(Map<String, dynamic> data) async {
    final _firestore = ref.watch(firestoreProvider);
    state = const AsyncLoading();
    state = await AsyncValue.guard(() async {
      final user = ref.read(userProvider).value;
      if (user != null) {
        await _firestore.setData(
          path: 'users/${user.uid}',
          data: data,
        );
      }
    });
  }
}

/// Stream a user's subscription data from Firebase.
final userSubscriptionProvider = StreamProvider.autoDispose<Map>((ref) {
  final _database = ref.watch(firestoreProvider);
  final user = ref.watch(userProvider).value;
  return _database.watchDocument(
    path: 'subscribers/${user!.uid}',
    builder: (data, documentId) {
      return data ?? {};
    },
  );
});

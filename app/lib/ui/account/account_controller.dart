// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 2/18/2023
// Updated: 8/6/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Dart imports:
import 'dart:async';

// Flutter imports:
import 'package:flutter/material.dart';

// Package imports:
import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:firebase_auth/firebase_auth.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

// Project imports:
import 'package:cannlytics_data/common/inputs/string_controller.dart';
import 'package:cannlytics_data/services/auth_service.dart';
import 'package:cannlytics_data/services/firestore_service.dart';

/* === User === */

// User type provider.
final userTypeProvider = StateProvider<String>((ref) => 'consumer');

// User provider.
final userProvider = StreamProvider<User?>((ref) {
  return ref.watch(authProvider).authStateChanges();
});

/* === Subscription === */

/// Stream a user's subscription data from Firebase.
final userSubscriptionProvider = StreamProvider.autoDispose<Map?>((ref) {
  final _database = ref.watch(firestoreProvider);
  final user = ref.watch(userProvider).value;
  if (user == null) return Stream.value(null);
  return _database.streamDocument(
    path: 'subscribers/${user.uid}',
    builder: (data, documentId) {
      return data ?? {};
    },
  );
});

/// Get app subscriptions from Firestore.
final subscriptionsProvider =
    FutureProvider<List<Map<dynamic, dynamic>?>>((ref) async {
  final _dataSource = ref.read(firestoreProvider);
  var data = await _dataSource.getCollection(
    path: 'public/subscriptions/subscription_plans',
    builder: (data, id) => data,
    queryBuilder: (query) => query.orderBy('price_usd'),
  );
  return data;
});

///  Get FAQ data from Firestore.
final faqProvider = FutureProvider<Map<dynamic, dynamic>?>((ref) async {
  final _dataSource = ref.read(firestoreProvider);
  var data = await _dataSource.getDocument(
    path: 'public/ai/info/faq',
  );
  return data;
});

/* === User authentication === */

// Email text field.
final emailController =
    StateNotifierProvider<StringController, TextEditingController>(
        (ref) => StringController());

// Password text field.
final passwordController =
    StateNotifierProvider<StringController, TextEditingController>(
        (ref) => StringController());

// Sign-in controller.
final signInProvider = AutoDisposeAsyncNotifierProvider<SignInController, void>(
    SignInController.new);

/// [SignInController] manages the sign in, sign up, and reset password screens.
class SignInController extends AutoDisposeAsyncNotifier<void> {
  @override
  FutureOr<void> build() {}

  /// [signIn] signs the user in with their email and password.
  Future<String> signIn({
    required String email,
    required String password,
  }) async {
    state = const AsyncValue.loading();
    var message;
    state = await AsyncValue.guard(() async {
      message = await ref.read(authProvider).signIn(email, password);
    });
    return message;
  }

  /// [signUp] signs the user up with their email and password.
  Future<String> signUp({
    required String email,
    required String password,
  }) async {
    state = const AsyncValue.loading();
    var message;
    state = await AsyncValue.guard(() async {
      message = await ref.read(authProvider).signUp(email, password);
    });
    return message;
  }
}

/* === User account === */

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
  Future<String> updateUser({
    String? email,
    String? displayName,
    String? phoneNumber,
  }) async {
    var message;
    state = const AsyncLoading();
    state = await AsyncValue.guard(() async {
      // Get the appropriate providers.
      final user = ref.read(userProvider).value;
      final _firestore = ref.watch(firestoreProvider);

      // Return if there is no user.
      if (user == null) {
        message = 'No user found.';
        return;
      }

      // Update the user's display name.
      if (displayName != null && displayName != user.displayName) {
        await user.updateDisplayName(displayName);
      }

      // Update the user's email.
      if (email != null && email != user.email) {
        await user.updateEmail(email);
      }

      // Update the user's data in Firestore.
      await _firestore.updateDocument(
        path: 'users/${user.uid}',
        data: {
          'email': user.email,
          'display_name': user.displayName,
          'phone_number': user.phoneNumber,
        },
      );

      // Update the user's profile.
      await _firestore.updateDocument(
        path: 'users/${user.uid}/public_user_data/profile',
        data: {'display_name': user.displayName},
      );

      // Set the message to success.
      message = 'success';
    });
    return message;
  }

  /// Save the user's data.
  Future<void> saveUserData(Map<String, dynamic> data) async {
    final _firestore = ref.watch(firestoreProvider);
    state = const AsyncLoading();
    state = await AsyncValue.guard(() async {
      final user = ref.read(userProvider).value;
      if (user != null) {
        await _firestore.updateDocument(
          path: 'users/${user.uid}',
          data: data,
        );
      }
    });
  }
}

/* === User profile === */

// User logs provider.
final userLogsProvider =
    StateProvider.family<Query<Map<dynamic, dynamic>?>, String>((ref, uid) {
  return FirebaseFirestore.instance
      .collection('users/$uid/public_logs')
      .orderBy('created_at', descending: true)
      .withConverter(
        fromFirestore: (snapshot, _) => snapshot.data()!,
        toFirestore: (item, _) => item as Map<String, Object?>,
      );
});

// User profile provider.
final userProfileProvider = StreamProvider.autoDispose.family<Map?, String>((
  ref,
  uid,
) {
  final _database = ref.watch(firestoreProvider);
  return _database.streamDocument(
    path: 'users/$uid/public_user_data/profile',
    builder: (data, documentId) => data ?? {},
  );
});

// Cannlytics Data
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 3/3/2023
// Updated: 4/14/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Dart imports:
import 'dart:async';

// Flutter imports:
import 'package:flutter/material.dart';

// Package imports:
import 'package:firebase_auth/firebase_auth.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

// Project imports:
import 'package:cannlytics_data/common/inputs/string_controller.dart';
import 'package:cannlytics_data/services/auth_service.dart';

/* Data */

/// TODO: Get data from Firestore.

final List<Map> mainDatasets = [
  {
    "title": "Cannabis Licenses",
    "image_url":
        "https://firebasestorage.googleapis.com/v0/b/cannlytics.appspot.com/o/public%2Fimages%2Flogos%2Fcannlytics_coa_doc.png?alt=media&token=1871dde9-82db-4342-a29d-d373671491b3",
    "description":
        "A collection of 11,060 cannabis licenses from each state with permitted adult-use cannabis.",
    "tier": "Premium",
    "path": "/licenses",
    "observations": 11060,
    "fields": 28,
  },
];

List<Map> aiModels = [
  {
    "image_url":
        "https://firebasestorage.googleapis.com/v0/b/cannlytics.appspot.com/o/public%2Fimages%2Flogos%2Fcannlytics_coa_doc.png?alt=media&token=1871dde9-82db-4342-a29d-d373671491b3",
    "description": "AI Lab Results Parser",
    "route": "CoADoc"
  },
  {
    "image_url":
        "https://firebasestorage.googleapis.com/v0/b/cannlytics.appspot.com/o/public%2Fimages%2Flogos%2Fskunkfx_logo.png?alt=media&token=1a75b3cc-3230-446c-be7d-5c06012c8e30",
    "description": "Effects & Aromas Predictor",
    "route": "SkunkFx"
  }
];

/* Navigation */

// Current page provider.
final currentPageProvider = StateProvider<String>((ref) => 'Data Dashboard');

// Menu controller.
final sideMenuOpen = StateProvider<bool>((ref) => true);

/* User */

// User type provider.
final userTypeProvider = StateProvider<String>((ref) => 'business');

// User provider.
final userProvider = StreamProvider<User?>((ref) {
  return ref.watch(authProvider).authStateChanges();
});

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

/* Sign in / sign up */

/// Sign up controller.
// final signUpController = StateProvider<bool>((ref) => false);

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

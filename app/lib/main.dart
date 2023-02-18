// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 2/17/2023
// Updated: 2/17/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

import 'package:firebase_core/firebase_core.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:cannlytics_app/firebase_options.dart';
import 'package:cannlytics_app/app.dart';
import 'package:cannlytics_app/services/firebase_auth_repository.dart';
import 'package:cannlytics_app/localization/string_hardcoded.dart';
import 'package:cannlytics_app/services/onboarding_repository.dart';
// ignore:depend_on_referenced_packages
import 'package:flutter_web_plugins/url_strategy.dart';

/// [main] initializes the Cannlytics app.
Future<void> main() async {
  // Initialize Flutter.
  WidgetsFlutterBinding.ensureInitialized();

  // Initialize Firebase.
  await Firebase.initializeApp(
    options: DefaultFirebaseOptions.currentPlatform,
  );

  // turn off the # in the URLs on the web
  usePathUrlStrategy();
  final sharedPreferences = await SharedPreferences.getInstance();
  // * Register error handlers. For more info, see:
  // * https://docs.flutter.dev/testing/errors
  registerErrorHandlers();
  // * Entry point of the app

  final container = ProviderContainer(
    overrides: [
      onboardingRepositoryProvider.overrideWithValue(
        OnboardingRepository(sharedPreferences),
      ),
    ],
  );
  // await until auth state is determined
  // this will prevent unnecessary redirects inside GoRouter when the app starts
  await container.read(authStateChangesProvider.future);
  runApp(UncontrolledProviderScope(
    container: container,
    child: const CannlyticsApp(),
  ));
}

void registerErrorHandlers() {
  // * Show some error UI if any uncaught exception happens
  FlutterError.onError = (FlutterErrorDetails details) {
    FlutterError.presentError(details);
    debugPrint(details.toString());
  };
  // * Handle errors from the underlying platform/OS
  PlatformDispatcher.instance.onError = (Object error, StackTrace stack) {
    debugPrint(error.toString());
    return true;
  };
  // * Show some error UI when any widget in the app fails to build
  ErrorWidget.builder = (FlutterErrorDetails details) {
    return Scaffold(
      appBar: AppBar(
        backgroundColor: Colors.red,
        title: Text('An error occurred'.hardcoded),
      ),
      body: Center(child: Text(details.toString())),
    );
  };
}

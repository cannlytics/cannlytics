// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 2/17/2023
// Updated: 2/20/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>
import 'package:cannlytics_app/constants/colors.dart';
import 'package:cannlytics_app/routing/app_router.dart';
import 'package:firebase_core/firebase_core.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:cannlytics_app/firebase_options.dart';
import 'package:cannlytics_app/services/auth_service.dart';
import 'package:cannlytics_app/utils/strings/string_hardcoded.dart';
import 'package:cannlytics_app/ui/account/onboarding/onboarding_controller.dart';
// ignore:depend_on_referenced_packages
import 'package:flutter_web_plugins/url_strategy.dart';

/// The main application.
class CannlyticsApp extends ConsumerWidget {
  const CannlyticsApp({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final goRouter = ref.watch(goRouterProvider);
    return MaterialApp.router(
      routerConfig: goRouter,
      theme: ThemeData(
        primarySwatch: AppColors.primaryColors,
        unselectedWidgetColor: Colors.grey,
        appBarTheme: const AppBarTheme(
          elevation: 2.0,
          centerTitle: true,
        ),
        scaffoldBackgroundColor: Colors.grey[200],
      ),
      debugShowCheckedModeBanner: false,
    );
  }
}

/// [main] initializes the [CannlyticsApp].
Future<void> main() async {
  // Initialize Flutter.
  WidgetsFlutterBinding.ensureInitialized();

  // Initialize Firebase.
  await Firebase.initializeApp(
    options: DefaultFirebaseOptions.currentPlatform,
  );

  // Remove the hashtag (#) from URLs on the web.
  usePathUrlStrategy();

  // Register error handlers.
  final sharedPreferences = await SharedPreferences.getInstance();
  registerErrorHandlers();

  // App entry point.
  final container = ProviderContainer(
    overrides: [
      onboardingStoreProvider.overrideWithValue(
        OnboardingStore(sharedPreferences),
      ),
    ],
  );

  // Wait for authentication to be determined.
  // Note: This will prevent unnecessary redirects when the app starts.
  await container.read(authStateChangesProvider.future);
  runApp(UncontrolledProviderScope(
    container: container,
    child: const CannlyticsApp(),
  ));
}

/// [registerErrorHandlers] displays notifications if certain errors are thrown.
void registerErrorHandlers() {
  // Show an error notification if any uncaught exception happens.
  FlutterError.onError = (FlutterErrorDetails details) {
    FlutterError.presentError(details);
    debugPrint(details.toString());
  };

  // Handle underlying platform/OS errors.
  PlatformDispatcher.instance.onError = (Object error, StackTrace stack) {
    debugPrint(error.toString());
    return true;
  };

  // Show an error notification when any widget in the app fails to build.
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

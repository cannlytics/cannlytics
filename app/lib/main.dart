// Cannlytics Data
// Copyright (c) 2023 Cannlytics
// Copyright (c) 2021 Coding With Flutter Limited

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 2/17/2023
// Updated: 6/24/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>
// License: MIT License <https://github.com/bizz84/code_with_andrea_flutter/blob/main/LICENSE.md>

// Flutter imports:
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';

// Package imports:
import 'package:firebase_core/firebase_core.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_web_plugins/url_strategy.dart';

// Project imports:
import 'package:cannlytics_data/constants/errors.dart';
import 'package:cannlytics_data/constants/licenses.dart';
import 'package:cannlytics_data/constants/theme.dart';
import 'package:cannlytics_data/firebase_options.dart';
import 'package:cannlytics_data/routing/app_router.dart';
import 'package:cannlytics_data/ui/account/account_controller.dart';

// ignore:depend_on_referenced_packages

/// The main application.
class CannlyticsApp extends ConsumerWidget {
  const CannlyticsApp({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    // Routing provider.
    final goRouter = ref.watch(goRouterProvider);

    // Theme provider.
    final themeMode = ref.watch(themeModeProvider);

    // Material app.
    return MaterialApp.router(
      debugShowCheckedModeBanner: false,
      routerConfig: goRouter,
      theme: AppTheme.toThemeData(),
      darkTheme: AppTheme.toThemeData(isDark: true),
      themeMode: themeMode,
    );
  }
}

/// [main] initializes the [CannlyticsApp].
Future<void> main() async {
  // Initialize Flutter.
  WidgetsFlutterBinding.ensureInitialized();

  // Initialize Firebase.
  await Firebase.initializeApp(options: DefaultFirebaseOptions.currentPlatform);

  // Remove hashtags from URLs on the web.
  usePathUrlStrategy();

  // Register error handlers.
  registerErrorHandlers();

  // Register licenses.
  LicenseRegistry.addLicense(renderAppLicenses);

  // Create a container to serve as the app entry point.
  final container = ProviderContainer();

  // Run the app after authentication is determined.
  // This will prevent unnecessary redirects when the app starts.
  await container.read(userProvider.future);
  runApp(UncontrolledProviderScope(
    container: container,
    child: const CannlyticsApp(),
  ));
}

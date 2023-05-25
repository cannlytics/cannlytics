// Cannlytics App
// Copyright (c) 2023 Cannlytics
// Copyright (c) 2021 Coding With Flutter Limited

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 5/16/2023
// Updated: 5/16/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>
// License: MIT License <https://github.com/bizz84/code_with_andrea_flutter/blob/main/LICENSE.md>

// Flutter imports:
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';

/// [registerErrorHandlers] displays notifications if certain errors are thrown.
void registerErrorHandlers() {
  // Handle underlying platform/OS errors.
  PlatformDispatcher.instance.onError = (Object error, StackTrace stack) {
    debugPrint(error.toString());
    return true;
  };

  // Show an error notification if any uncaught exception happens.
  FlutterError.onError = (FlutterErrorDetails details) {
    // Standard error message:
    // debugPrint(details.exception.toString());

    // Verbose error message:
    // FlutterError.presentError(details);
    // debugPrint(details.toString());

    // Short error message:
    FlutterError.dumpErrorToConsole(details);
    throw details.exception;
  };

  // Show an error notification when any widget in the app fails to build.
  ErrorWidget.builder = (FlutterErrorDetails details) {
    return Scaffold(
      appBar: AppBar(
        backgroundColor: Colors.redAccent,
        // Production error title:
        // title: Text('Error! Please contact support@cannlytics.com'),

        // Dev error title:
        title: Text(
          details.exception.toString().substring(0, 100),
          style: TextStyle(fontSize: 21),
        ),
      ),
      body: Center(
        // TODO: Production error UI:

        // Dev error UI:
        child: Text(
          details.toString(),
          style: TextStyle(fontSize: 18),
        ),
      ),
    );
  };
}

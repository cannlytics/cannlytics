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

  String _lastLoggedErrorMessage = '';

  // Show an error notification if any uncaught exception happens.
  FlutterError.onError = (FlutterErrorDetails details) {
    // Default error message:
    // debugPrint(details.exception.toString());

    // Verbose error message:
    // FlutterError.presentError(details);
    // debugPrint(details.toString());
    // FlutterError.dumpErrorToConsole(details);
    // throw details.exception;

    // Short error message:
    String errorMessage = details.exception.toString();
    if (_lastLoggedErrorMessage != 'error') {
      debugPrint(errorMessage);
      _lastLoggedErrorMessage = 'error';
    }
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
        child: SelectableText(
          details.toString(),
          style: TextStyle(fontSize: 12),
        ),
      ),
    );
  };
}

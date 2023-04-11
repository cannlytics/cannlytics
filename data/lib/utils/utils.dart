// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 2/22/2023
// Updated: 4/9/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Flutter imports:
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';

// Package imports:
import 'package:url_launcher/url_launcher.dart';

/// Utility functions for the web.
class WebUtils {
  /// Launch a website.
  static Future<void> launchURL(String url) async {
    Uri uri = Uri.parse(url);
    if (await canLaunchUrl(uri)) {
      await launchUrl(uri);
    } else {
      throw 'Could not launch $url';
    }
  }
}

/// [registerErrorHandlers] displays notifications if certain errors are thrown.
void registerErrorHandlers() {
  // Handle underlying platform/OS errors.
  PlatformDispatcher.instance.onError = (Object error, StackTrace stack) {
    debugPrint(error.toString());
    return true;
  };

  // Show an error notification if any uncaught exception happens.
  FlutterError.onError = (FlutterErrorDetails details) {
    // debugPrint(details.exception.toString());
    FlutterError.presentError(details);
    debugPrint(details.toString());
    // FlutterError.dumpErrorToConsole(details);
    // throw details.exception;
  };

  // Show an error notification when any widget in the app fails to build.
  ErrorWidget.builder = (FlutterErrorDetails details) {
    return Scaffold(
      appBar: AppBar(
        backgroundColor: Colors.red,
        title: Text('Error! Please contact support@cannlytics.com'),
      ),
      body: Center(child: Text(details.toString())),
    );
  };
}

// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 2/22/2023
// Updated: 4/14/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Dart imports:
import 'dart:io';

// Flutter imports:
import 'package:flutter/cupertino.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';

// Package imports:
import 'package:url_launcher/url_launcher.dart';

// Project imports:
import 'package:cannlytics_data/widgets/buttons/secondary_button.dart';

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

/// Utility functions for the interface.
class InterfaceUtils {
  /// Show an alert dialog.
  static Future<bool?> showAlertDialog({
    required BuildContext context,
    required String title,
    String? content,
    String? cancelActionText,
    required String defaultActionText,
  }) async {
    if (kIsWeb || !Platform.isIOS) {
      return showDialog(
        context: context,
        builder: (context) => AlertDialog(
          // Title.
          title: Text(
            title,
            style: Theme.of(context).textTheme.titleLarge,
          ),

          // Content.
          content: content != null ? Text(content) : null,

          // Actions.
          actions: <Widget>[
            // Cancel action.
            if (cancelActionText != null)
              TextButton(
                child: Text(
                  cancelActionText,
                  style: Theme.of(context).textTheme.titleMedium!.copyWith(
                        color: Theme.of(context).textTheme.titleLarge!.color,
                      ),
                ),
                onPressed: () => Navigator.of(context).pop(false),
              ),

            // Confirm action.
            SecondaryButton(
              text: defaultActionText,
              onPressed: () => Navigator.of(context).pop(true),
            ),
          ],
        ),
      );
    }
    return showCupertinoDialog(
      context: context,
      builder: (context) => CupertinoAlertDialog(
        title: Text(title),
        content: content != null ? Text(content) : null,
        actions: <Widget>[
          if (cancelActionText != null)
            CupertinoDialogAction(
              child: Text(cancelActionText),
              onPressed: () => Navigator.of(context).pop(false),
            ),
          CupertinoDialogAction(
            child: Text(defaultActionText),
            onPressed: () => Navigator.of(context).pop(true),
          ),
        ],
      ),
    );
  }
}

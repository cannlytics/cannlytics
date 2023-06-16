// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 2/22/2023
// Updated: 6/15/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Dart imports:
import 'dart:io';
import 'dart:html' as html;

// Flutter imports:
import 'package:flutter/cupertino.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';

// Package imports:
import 'package:url_launcher/url_launcher.dart';

// Project imports:
import 'package:cannlytics_data/common/buttons/secondary_button.dart';

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

  /// Download a file from bytes.
  static Future<void> downloadBytes(List<String> bytes, String filename) async {
    final blob = html.Blob(bytes);
    final url = html.Url.createObjectUrlFromBlob(blob);
    final anchor = html.document.createElement('a') as html.AnchorElement
      ..href = url
      ..style.display = 'none'
      ..download = filename;
    html.document.body?.children.add(anchor);
    anchor.click();
    html.document.body?.children.remove(anchor);
    html.Url.revokeObjectUrl(url);
  }

  /// Convert a color to a HTML hex code.
  static String colorToHexCode(Color color) {
    return '#' + color.value.toRadixString(16).substring(2).toUpperCase();
  }

  /// Slugify text.
  static String slugify(String input) {
    // Remove leading and trailing whitespace and convert to lowercase.
    String result = input.trim().toLowerCase();

    // Replace special characters with a hyphen.
    result = result.replaceAll(RegExp(r"[^\w\s-]"), "-");

    // Replace consecutive whitespace and hyphens with a single hyphen.
    result = result.replaceAll(RegExp(r"[\s-]+"), "-");

    // Remove leading and trailing hyphens.
    result = result
        .replaceAll(RegExp(r"^[-]+"), "")
        .replaceAll(RegExp(r"[-]+$"), "");

    return result;
  }
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

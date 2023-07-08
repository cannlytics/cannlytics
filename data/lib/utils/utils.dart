// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 2/22/2023
// Updated: 6/24/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Dart imports:
import 'dart:convert';
import 'dart:io';
import 'dart:html' as html;

// Flutter imports:
import 'package:cannlytics_data/common/buttons/primary_button.dart';
import 'package:flutter/cupertino.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import 'package:crypto/crypto.dart';

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

  /// Download a file from a URL.
  static void downloadUrl(String url) {
    html.AnchorElement anchorElement = new html.AnchorElement(href: url);
    anchorElement.download = url;
    anchorElement.click();
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

  /// Convert a HTML hex code to a color.
  static Color hexCodeToColor(String hexCode) {
    return Color(int.parse(hexCode.substring(1, 7), radix: 16) + 0xFF000000);
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
    String? defaultActionText,
    Color? primaryActionColor,
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
          content: content != null
              ? Container(
                  width: 420,
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Text(content),
                    ],
                  ),
                )
              : null,

          // Actions.
          actions: <Widget>[
            // Cancel action.
            if (cancelActionText != null)
              SecondaryButton(
                text: cancelActionText,
                onPressed: () => Navigator.of(context).pop(false),
              ),

            // Confirm action.
            PrimaryButton(
              text: defaultActionText ?? 'Okay',
              onPressed: () => Navigator.of(context).pop(true),
              backgroundColor: primaryActionColor,
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
            child: Text(defaultActionText ?? 'Okay'),
            onPressed: () => Navigator.of(context).pop(true),
          ),
        ],
      ),
    );
  }
}

/// Date and time utility functions.
class TimeUtils {
  /// Format a DateTime as a human readable time.
  static String getReadableTime(DateTime date) {
    return DateFormat('MMMM d, y HH:mm').format(date);
  }
}

/// Data utility functions.
class DataUtils {
  /// Format a list from a dynamic data type.
  static List<String>? formatList(dynamic data) {
    if (data == null) {
      return [];
    } else if (data is String) {
      return data.split(',').map((e) => e.trim()).toList();
    } else if (data is List<dynamic>) {
      return data.cast<String>();
    } else {
      return null;
    }
  }

  // Format a list of Maps from a dynamic data type.
  static List<dynamic>? formatListOfMaps(dynamic data) {
    if (data == null) {
      return [];
    } else if (data is List<dynamic>) {
      return data.cast<Map<String, dynamic>>();
    } else if (data is String) {
      return jsonDecode(data)
          .map((item) => item as Map<String, dynamic>)
          .toList();
    } else {
      return null;
    }
  }

  /// Format a number from a dynamic data type.
  static double? formatNumber(dynamic data) {
    if (data == null) {
      return null;
    } else if (data is String) {
      return double.tryParse(data);
    } else if (data is num) {
      return data.toDouble();
    } else {
      return null;
    }
  }

  /// Format an integer from a dynamic data type.
  static int? formatInt(dynamic data) {
    if (data == null) {
      return null;
    } else if (data is String) {
      return int.tryParse(data);
    } else if (data is int) {
      return data;
    } else {
      return null;
    }
  }

  /// Compute the SHA-256 hash of a string.
  static String sha256hash(String? data) {
    if (data == null) return '';
    var bytes = utf8.encode(data);
    var digest = sha256.convert(bytes);
    return digest.toString();
  }

  /// Create a hash (HMAC-SHA256) that is unique to the provided data.
  static String createHash(
    String? publicKey, {
    String privateKey = 'cannlytics.eth',
  }) {
    if (publicKey == null) return '';
    var key = utf8.encode(privateKey);
    var msg = utf8.encode(publicKey);
    var hmacSha256 = new Hmac(sha256, key); // HMAC-SHA256
    var digest = hmacSha256.convert(msg);
    return digest.toString();
  }
}

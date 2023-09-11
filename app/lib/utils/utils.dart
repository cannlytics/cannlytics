// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 2/22/2023
// Updated: 9/10/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Dart imports:
import 'dart:convert';
import 'dart:io' show Platform;

// Flutter imports:
import 'package:flutter/cupertino.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';

// Package imports:
import 'package:crypto/crypto.dart';
import 'package:intl/intl.dart';

// Project imports:
import 'package:cannlytics_data/common/buttons/primary_button.dart';
import 'package:cannlytics_data/common/buttons/secondary_button.dart';
import 'package:cannlytics_data/constants/colors.dart';

import 'package:cannlytics_data/utils/web_utils.dart'
    if (dart.library.io) 'package:cannlytics_data/utils/mobile_utils.dart';

class PlatformChecker {
  bool get isAndroid => !kIsWeb && Platform.isAndroid;
  bool get isIOS => !kIsWeb && Platform.isIOS;
  bool get isWeb => kIsWeb;
}

// File utility class that will work for web and mobile platforms.
abstract class PlatformFileUtils {
  void downloadUrl(String url, String? filename);
  Future<void> downloadBytes(String fileName, List<dynamic> bytes);
}

/// Utility functions for the file system.
final platformChecker = PlatformChecker();

PlatformFileUtils FileUtils = platformChecker.isWeb
    ? WebUtils()
    : (platformChecker.isAndroid || platformChecker.isIOS
        ? MobileUtils()
        : throw UnsupportedError('Unsupported platform'));

/// API utility functions.
class ApiUtils {
  /// Get the file extension from the mime type.
  static String getExtensionFromMimeType(dynamic mimeType) {
    const Map<String, String> extensionMap = {
      'application/pdf': '.pdf',
      'image/jpeg': '.jpg',
      'image/png': '.png',
      'image/tiff': '.tif',
      'image/webp': '.webp',
    };
    return extensionMap[mimeType] ?? '';
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

  /// Show a date picker.
  static Future<DateTime?> themedDatePicker({
    required BuildContext context,
    required DateTime initialDate,
    required DateTime firstDate,
    required DateTime lastDate,
    required bool isDark,
  }) async {
    return await showDatePicker(
      context: context,
      initialDate: initialDate,
      firstDate: firstDate,
      lastDate: lastDate,
      builder: (BuildContext context, Widget? child) {
        ThemeData baseTheme = isDark ? ThemeData.dark() : ThemeData.light();
        return Theme(
          data: baseTheme.copyWith(
            colorScheme: baseTheme.colorScheme.copyWith(
              primary: isDark ? DarkColors.green : LightColors.green,
              onPrimary: baseTheme.colorScheme.onSurface,
              surface: baseTheme.colorScheme.surface,
              onSurface: baseTheme.colorScheme.onSurface,
            ),
            dialogBackgroundColor: baseTheme.colorScheme.surface,
            textButtonTheme: TextButtonThemeData(
              style: TextButton.styleFrom(
                textStyle: Theme.of(context).textTheme.bodyMedium?.copyWith(
                      color: baseTheme.colorScheme.onSurface,
                    ),
              ),
            ),
            splashFactory: InkRipple.splashFactory,
          ),
          child: child!,
        );
      },
    );
  }
}

/// Date and time utility functions.
class TimeUtils {
  /// Format a DateTime as a human readable time.
  static String getReadableTime(DateTime date) {
    return DateFormat('MMMM d, y HH:mm').format(date);
  }

  /// Convert a string to a DateTime.
  static DateTime? parseDate(String? date) {
    if (date == null) return null;
    try {
      return DateTime.parse(date);
    } catch (e) {
      return null;
    }
  }

  /// Format a DateTime as a string.
  static String formatDate(DateTime? date) {
    if (date == null) return '';
    return '${date.month}/${date.day}/${date.year}';
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
      dynamic decodedData = data;
      int decodeAttempts = 0;

      while (decodedData is String && decodeAttempts < 2) {
        decodedData = jsonDecode(decodedData);
        decodeAttempts++;
      }

      if (decodedData is List<dynamic>) {
        return decodedData.map((item) => item as Map<String, dynamic>).toList();
      } else {
        return [];
      }
    } else {
      return [];
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

/// String utility functions.
class StringUtils {
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

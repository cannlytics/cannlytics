// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 8/6/2023
// Updated: 8/19/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Dart imports:
import 'dart:html' as html if (dart.library.io) 'dart:io';

// Project imports:
import 'package:cannlytics_data/utils/utils.dart';

/// Utility functions for the web.
class MobileUtils implements PlatformFileUtils {
  /// Download a file from a URL.
  @override
  Future<void> downloadUrl(String url, String? filename) async {}

  /// Download a file from bytes.
  @override
  Future<void> downloadBytes(String filename, List<dynamic> bytes) async {}
}

/// Utility functions for the web.
class WebUtils implements PlatformFileUtils {
  /// Download a file from a URL.
  @override
  void downloadUrl(String url, String? filename) {
    html.AnchorElement anchorElement = new html.AnchorElement(href: url);
    anchorElement.download = url;
    anchorElement.click();
  }

  /// Download a file from bytes.
  @override
  Future<void> downloadBytes(String filename, List<dynamic> bytes) async {
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
}

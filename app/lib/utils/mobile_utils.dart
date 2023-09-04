// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 8/6/2023
// Updated: 8/6/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Dart imports:
import 'dart:io';
import 'dart:typed_data';

// Package imports:
import 'package:flutter_file_saver/flutter_file_saver.dart';
import 'package:http/http.dart' as http;
import 'package:path_provider/path_provider.dart';

// Project imports:
import 'package:cannlytics_data/utils/utils.dart';

/// Utility functions for the web.
class MobileUtils implements PlatformFileUtils {
  /// Download a file from a URL.
  @override
  Future<void> downloadUrl(String url, String? filename) async {
    var response = await http.get(Uri.parse(url));
    final directory = (await getApplicationDocumentsDirectory()).path;
    final filePath = '$directory/$filename';
    File file = new File(filePath);
    await file.writeAsBytes(response.bodyBytes);
  }

  /// Download a file from bytes.
  @override
  Future<void> downloadBytes(String filename, List<dynamic> bytes) async {
    Uint8List uint8list = Uint8List.fromList(bytes as List<int>);
    await FlutterFileSaver()
        .writeFileAsBytes(bytes: uint8list, fileName: filename);
  }
}

/// Utility functions for the web.
class WebUtils implements PlatformFileUtils {
  /// Download a file from a URL.
  @override
  Future<void> downloadUrl(String url, String? filename) async {}

  /// Download a file from bytes.
  @override
  Future<void> downloadBytes(String filename, List<dynamic> bytes) async {}
}

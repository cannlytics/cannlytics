// Cannlytics Data
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 6/23/2023
// Updated: 9/9/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Project imports:
import 'package:cannlytics_data/services/api_service.dart';
import 'package:cannlytics_data/services/data_service.dart';
import 'package:cannlytics_data/services/storage_service.dart';
import 'package:cannlytics_data/utils/utils.dart';

/// Data download service.
class DownloadService {
  const DownloadService._();

  /// Download a file.
  static Future<void> downloadFile(String pdfUrl, String filename) async {
    try {
      FileUtils.downloadUrl(pdfUrl, filename);
    } catch (error) {
      String? downloadUrl = await StorageService.getDownloadUrl(pdfUrl);
      DataService.openInANewTab(downloadUrl);
    }
  }

  /// Download data (by sending it to the API to get a datafile).
  static Future<void> downloadData(
    List<Map<dynamic, dynamic>?> data,
    String url,
  ) async {
    var response = await APIService.apiRequest(
      url,
      data: {'data': data},
    );
    try {
      FileUtils.downloadUrl(response['download_url'], response['filename']);
    } catch (error) {
      String? downloadUrl =
          await StorageService.getDownloadUrl(response['file_ref']);
      DataService.openInANewTab(downloadUrl);
    }
  }
}

// Cannlytics Data
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 6/23/2023
// Updated: 8/6/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Project imports:
import 'package:cannlytics_data/services/api_service.dart';
import 'package:cannlytics_data/services/data_service.dart';
import 'package:cannlytics_data/services/storage_service.dart';
// import 'package:cannlytics_data/utils/utils.dart';

/// Data download service.
class DownloadService {
  const DownloadService._();

  /// Download receipt data.
  static Future<void> downloadData(
    List<Map<dynamic, dynamic>?> data,
    String url,
  ) async {
    print('Downloading from URL: $url');
    Map response = await APIService.apiRequest(
      url,
      data: {'data': data},
    );
    print('Download response: $response');
    String? downloadUrl =
        await StorageService.getDownloadUrl(response['file_ref']);
    DataService.openInANewTab(downloadUrl);
    // FileUtils.downloadUrl(response['download_url'], response['filename']);
  }
}

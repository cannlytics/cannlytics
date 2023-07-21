// Cannlytics Data
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 6/23/2023
// Updated: 6/23/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Flutter imports:
import 'package:flutter/foundation.dart';

// Project imports:
import 'package:cannlytics_data/services/api_service.dart';
import 'package:cannlytics_data/utils/utils.dart';

/// Data download service.
class DownloadService {
  const DownloadService._();

  /// Download receipt data.
  static Future<void> downloadData(
    List<Map<dynamic, dynamic>?> data,
    String url,
  ) async {
    var response = await APIService.apiRequest(
      url,
      data: {'data': data},
    );
    if (kIsWeb) {
      WebUtils.downloadUrl(response['download_url']);
    } else {
      // TODO: Implement mobile download.
    }
  }
}

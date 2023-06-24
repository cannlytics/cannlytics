// Cannlytics Data
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 6/23/2023
// Updated: 6/23/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

import 'package:cannlytics_data/common/buttons/secondary_button.dart';
import 'package:cannlytics_data/services/download_service.dart';
import 'package:flutter/material.dart';

/// A download button with a circular progress indicator.
class DownloadButton extends StatefulWidget {
  DownloadButton({required this.items, required this.url});

  // Parameters.
  final List<Map<dynamic, dynamic>?> items;
  final String url;

  @override
  _DownloadButtonState createState() => _DownloadButtonState();
}

/// Download button state
class _DownloadButtonState extends State<DownloadButton> {
  bool _isLoading = false;

  Future<void> _downloadData() async {
    setState(() {
      _isLoading = true;
    });

    await DownloadService.downloadData(widget.items, widget.url);

    setState(() {
      _isLoading = false;
    });
  }

  @override
  Widget build(BuildContext context) {
    return SecondaryButton(
        onPressed: _isLoading ? null : _downloadData,
        text: 'Download All',
        isLoading: _isLoading);
  }
}

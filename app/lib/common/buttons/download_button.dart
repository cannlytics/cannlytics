// Cannlytics Data
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 6/23/2023
// Updated: 8/6/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Flutter imports:
import 'package:flutter/material.dart';

// Project imports:
import 'package:cannlytics_data/common/buttons/secondary_button.dart';
import 'package:cannlytics_data/constants/colors.dart';
import 'package:cannlytics_data/services/download_service.dart';

/// A download button with a circular progress indicator.
class DownloadButton extends StatefulWidget {
  DownloadButton({
    required this.items,
    required this.url,
    this.text,
  });

  // Parameters.
  final List<Map<dynamic, dynamic>?> items;
  final String url;
  final String? text;

  @override
  _DownloadButtonState createState() => _DownloadButtonState();
}

/// Download button state
class _DownloadButtonState extends State<DownloadButton> {
  bool _isLoading = false;

  Future<void> _downloadData() async {
    // Show loading indicator.
    setState(() {
      _isLoading = true;
    });

    // Get the theme.
    bool isDark = Theme.of(context).brightness == Brightness.dark;

    // Show a downloading notification.
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(
          'Preparing your download...',
          style: Theme.of(context).textTheme.bodyMedium,
        ),
        duration: Duration(seconds: 2),
        backgroundColor: isDark ? DarkColors.green : LightColors.lightGreen,
        showCloseIcon: true,
      ),
    );

    // Download the data.
    await DownloadService.downloadData(widget.items, widget.url);

    // Remove loading indicator.
    setState(() {
      _isLoading = false;
    });
  }

  @override
  Widget build(BuildContext context) {
    return SecondaryButton(
        onPressed: _isLoading ? null : _downloadData,
        text: widget.text ?? 'Download All',
        isLoading: _isLoading);
  }
}

// Cannlytics Data
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 6/23/2023
// Updated: 6/25/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

import 'package:cannlytics_data/common/buttons/secondary_button.dart';
import 'package:cannlytics_data/constants/colors.dart';
import 'package:cannlytics_data/services/download_service.dart';
import 'package:flutter/material.dart';
import 'package:fluttertoast/fluttertoast.dart';

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

    // Show a downloading notification.
    Fluttertoast.showToast(
      msg: 'Preparing your download...',
      toastLength: Toast.LENGTH_SHORT,
      gravity: ToastGravity.TOP,
      timeInSecForIosWeb: 2,
      backgroundColor: LightColors.lightGreen.withAlpha(60),
      textColor: Colors.white,
      fontSize: 16.0,
      webPosition: 'center',
      webShowClose: true,
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

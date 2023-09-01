// Cannlytics Data
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 8/29/2023
// Updated: 8/29/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Flutter imports:
import 'dart:async';

import 'package:cannlytics_data/ui/results/results_service.dart';
import 'package:cannlytics_data/utils/utils.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

// Package imports:
// import 'package:url_launcher/url_launcher.dart';

// Project imports:
import 'package:cannlytics_data/constants/colors.dart';
import 'package:cannlytics_data/constants/design.dart';
// import 'package:cannlytics_data/models/lab_result.dart';
import 'package:cannlytics_data/services/download_service.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

/// A results parser job item.
/// Optional: Add image.
class ResultsParserJob extends ConsumerWidget {
  ResultsParserJob({required this.item});

  // Properties
  final Map item;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    // Render.
    return Card(
      margin: EdgeInsets.only(left: 24, right: 24, bottom: 24),
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(3)),
      color: Theme.of(context).scaffoldBackgroundColor,
      surfaceTintColor: Theme.of(context).scaffoldBackgroundColor,
      child: Container(
        margin: EdgeInsets.all(0),
        padding: EdgeInsets.all(16.0),
        decoration: BoxDecoration(borderRadius: BorderRadius.circular(3.0)),
        child: SelectionArea(child: _content(context, ref)),
      ),
    );
  }

  Widget _content(BuildContext context, WidgetRef ref) {
    // Style and theme.
    final screenWidth = MediaQuery.of(context).size.width;
    bool isDark = Theme.of(context).brightness == Brightness.dark;

    // Download logic.
    void handleDownload(BuildContext context, Map data) {
      // Handle malformed results.
      // var data = labResult.toMap();
      // if (data['results'] == null) {
      //   data['results'] = [];
      // }

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
      DownloadService.downloadData(
        [data],
        '/api/data/coas/download',
      );
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // Product name and COA link.
        Row(
          children: [
            if (screenWidth <= Breakpoints.tablet)
              Expanded(
                child: Text(
                  "Job: ${item['job_id']}",
                  style: Theme.of(context).textTheme.titleMedium,
                ),
              ),
            if (screenWidth > Breakpoints.tablet)
              Text(
                "Job: ${item['job_id']}",
                style: Theme.of(context).textTheme.titleMedium,
              ),

            // Download COA data.
            Spacer(),
            if (item['job_finished_at'] != null)
              IconButton(
                icon: Icon(
                  Icons.download_sharp,
                  color: Theme.of(context).textTheme.bodyMedium!.color,
                ),
                onPressed: () {
                  handleDownload(context, item);
                },
              ),

            // Delete a job.
            IconButton(
              icon: Icon(
                Icons.delete,
                color: Theme.of(context).textTheme.bodyMedium!.color,
              ),
              onPressed: () async {
                final delete = await InterfaceUtils.showAlertDialog(
                  context: context,
                  title: 'Are you sure that you want to delete this job?',
                  cancelActionText: 'Cancel',
                  defaultActionText: 'Delete',
                  primaryActionColor:
                      isDark ? DarkColors.orange : LightColors.orange,
                );
                if (delete == true) {
                  await ref
                      .read(coaParser.notifier)
                      .deleteJob(item['uid'], item['job_id']);
                }
              },
            ),

            // FUTURE WORK: Open a job.
          ],
        ),
        Text(
          'Created At: ${item['job_created_at'] != null ? DateTime.parse(item['job_created_at']).toLocal().toString() : 'Parsing...'}',
          style: Theme.of(context).textTheme.labelMedium,
        ),
        Text(
          'Finished At: ${item['job_finished_at'] != null ? DateTime.parse(item['job_finished_at']).toLocal().toString() : 'Parsing...'}',
          style: Theme.of(context).textTheme.labelMedium,
        ),
        gapH8,

        // Progress bar.
        JobProgressBar(
          jobCreatedAt: DateTime.parse(item['job_created_at']),
          jobFinished: item['job_finished'] != null,
          hasError: item['job_error'] ?? false,
        ),

        // Job details.
        if (item['job_error'])
          Text(
            'Job Error: ${item['job_error'] ? 'Yes' : 'No'}',
            style: Theme.of(context).textTheme.labelMedium,
          ),
        if (item['job_error'])
          Text(
            'Job Error Message: ${item['job_error_message'] ?? 'No error message available'}',
            style: Theme.of(context).textTheme.labelMedium,
          ),

        // Copy COA link.
        if (item['job_file_url']?.isNotEmpty ?? false) gapH4,
        if (item['job_file_url']?.isNotEmpty ?? false)
          _coaLink(context, item['job_file_url']!),
      ],
    );
  }

  /// Copy COA link.
  Widget _coaLink(BuildContext context, String url) {
    // Theme.
    bool isDark = Theme.of(context).brightness == Brightness.dark;

    return InkWell(
      onTap: () async {
        await Clipboard.setData(ClipboardData(text: url));
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(
              'Copied link!',
              style: Theme.of(context).textTheme.bodyMedium,
            ),
            duration: Duration(seconds: 2),
            backgroundColor: isDark ? DarkColors.green : LightColors.lightGreen,
            showCloseIcon: true,
          ),
        );
      },
      child: Padding(
        padding: EdgeInsets.symmetric(vertical: 8, horizontal: 12),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          mainAxisAlignment: MainAxisAlignment.start,
          children: <Widget>[
            Icon(Icons.link, size: 12, color: Colors.blueAccent),
            SizedBox(width: 4),
            Text(
              'Copy COA link',
              style: TextStyle(
                fontSize: 12,
                fontWeight: FontWeight.bold,
                color: Colors.blueAccent,
              ),
            ),
          ],
        ),
      ),
    );
  }
}

/// Progress bar for a job.
class JobProgressBar extends StatefulWidget {
  final DateTime jobCreatedAt;
  final bool jobFinished;
  final bool hasError;

  JobProgressBar({
    required this.jobCreatedAt,
    required this.jobFinished,
    required this.hasError,
  });

  @override
  _JobProgressBarState createState() => _JobProgressBarState();
}

class _JobProgressBarState extends State<JobProgressBar> {
  late double _progressValue;
  late Timer _timer;

  @override
  void initState() {
    super.initState();
    _updateProgress();
    _timer =
        Timer.periodic(Duration(seconds: 10), (Timer t) => _updateProgress());
  }

  @override
  void dispose() {
    _timer.cancel();
    super.dispose();
  }

  void _updateProgress() {
    if (!widget.jobFinished) {
      final durationPassed = DateTime.now().difference(widget.jobCreatedAt);
      final maxDuration = Duration(minutes: 5);
      _progressValue = durationPassed.inSeconds / maxDuration.inSeconds;
      // Clamp the value to be between 0 and 0.9.
      _progressValue = _progressValue.clamp(0.0, 0.9);
    } else {
      _progressValue = 1.0; // 100%
    }
    setState(() {});
  }

  @override
  Widget build(BuildContext context) {
    return LinearProgressIndicator(
      value: _progressValue,
      backgroundColor: Colors.grey[200],
      valueColor: widget.hasError
          ? AlwaysStoppedAnimation<Color>(Colors.red)
          : AlwaysStoppedAnimation<Color>(Colors.green),
    );
  }
}

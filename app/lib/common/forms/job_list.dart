// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 9/3/2023
// Updated: 9/5/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Dart imports:
import 'dart:async';

// Flutter imports:
import 'package:cannlytics_data/ui/account/account_controller.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

// Package imports:
import 'package:flutter_riverpod/flutter_riverpod.dart';

// Project imports:
import 'package:cannlytics_data/constants/colors.dart';
import 'package:cannlytics_data/constants/design.dart';
import 'package:cannlytics_data/utils/utils.dart';
import 'package:intl/intl.dart';

/// API job configuration.
class JobConfig {
  final String title;
  final String downloadApiPath;
  final Function deleteJobFunction;
  final Function retryJobFunction;

  JobConfig({
    required this.title,
    required this.downloadApiPath,
    required this.deleteJobFunction,
    required this.retryJobFunction,
  });
}

/// An API job item.
class JobItem extends ConsumerWidget {
  JobItem({required this.item, required this.config});

  // Parameters.
  final Map item;
  final JobConfig config;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    if (item.isEmpty) {
      return SizedBox.shrink();
    }

    // Render.
    return Card(
      margin: EdgeInsets.only(bottom: 24),
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

    String limitErrorMessage(String? message, [int limit = 250]) {
      if (message == null || message.length <= limit) {
        return message ?? 'No error message available';
      }
      return message.substring(0, limit) + '...';
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
            Spacer(),

            // Retry jobs with errors.
            if (item['job_error'] == true)
              Tooltip(
                message: 'Retry',
                child: IconButton(
                  icon: Icon(
                    Icons.refresh,
                    color: Theme.of(context).textTheme.bodyMedium!.color,
                  ),
                  onPressed: () async {
                    String uid = ref.read(userProvider).value?.uid ?? '';
                    await config.retryJobFunction(uid, item['job_id']);
                  },
                ),
              ),

            // Delete a job.
            Tooltip(
              message: 'Delete',
              child: IconButton(
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
                    String uid = ref.read(userProvider).value?.uid ?? '';
                    await config.deleteJobFunction(uid, item['job_id']);
                  }
                },
              ),
            ),

            // FUTURE WORK: Open a job.
          ],
        ),
        Text(
          'Created: ${item['job_created_at'] != null ? DateFormat.yMMMd().add_jm().format(DateTime.parse(item['job_created_at']).toLocal()) : 'Parsing...'}',
          style: Theme.of(context).textTheme.labelMedium,
        ),
        Text(
          item['job_finished_at'] != null
              ? 'Finished: ${DateFormat.yMMMd().add_jm().format(DateTime.parse(item['job_finished_at']).toLocal())}'
              : 'Parsing...',
          style: Theme.of(context).textTheme.labelMedium,
        ),
        gapH8,

        // Progress bar.
        JobProgressBar(
          jobCreatedAt: DateTime.parse(item['job_created_at']),
          jobFinished: item['job_finished'] ?? false,
          hasError: item['job_error'] ?? false,
        ),

        // Job details.
        if (item['job_error']) _errorBadge(),

        // Error message
        if (item['job_error'])
          Text(
            'Job Error Message: ${limitErrorMessage(item['job_error_message'])}',
            style: Theme.of(context).textTheme.labelMedium,
          ),

        // Copy COA link.
        if (item['job_file_url']?.isNotEmpty ?? false) gapH4,
        if (item['job_file_url']?.isNotEmpty ?? false)
          _coaLink(context, item['job_file_url']!),
      ],
    );
  }

  /// Error badge
  Widget _errorBadge() {
    return Padding(
      padding: EdgeInsets.symmetric(vertical: 8),
      child: Container(
        padding: EdgeInsets.symmetric(horizontal: 12.0, vertical: 4.0),
        decoration: BoxDecoration(
          color: Colors.red, // Adjust the color as needed
          borderRadius: BorderRadius.circular(3),
        ),
        child: Text(
          'Error',
          style: TextStyle(
            color: Colors.white,
            fontWeight: FontWeight.bold,
          ),
        ),
      ),
    );
  }

  /// Copy file link.
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
              'Copy file link',
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

/// Progress bar for an API job.
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
  int maxDurationMinutes = 2;
  int updateIntervalSeconds = 3;

  @override
  void initState() {
    super.initState();
    _updateProgress();
    _timer = Timer.periodic(Duration(seconds: updateIntervalSeconds),
        (Timer t) => _updateProgress());
  }

  @override
  void dispose() {
    _timer.cancel();
    super.dispose();
  }

  void _updateProgress() {
    if (!widget.jobFinished) {
      final durationPassed = DateTime.now().difference(widget.jobCreatedAt);
      final maxDuration = Duration(minutes: maxDurationMinutes);
      _progressValue = durationPassed.inSeconds / maxDuration.inSeconds;
      _progressValue = _progressValue.clamp(0.0, 0.9);
    } else {
      _progressValue = 1.0;
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

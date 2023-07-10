// Cannlytics Data
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 7/2/2023
// Updated: 7/2/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Flutter imports:
import 'package:flutter/material.dart';

// Package imports:
import 'package:intl/intl.dart';

// Project imports:
import 'package:cannlytics_data/constants/design.dart';

/// A log item list card.
class LogItem extends StatelessWidget {
  LogItem({required this.log});

  // Properties
  final Map log;

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: EdgeInsets.symmetric(horizontal: 24),
      padding: EdgeInsets.all(16.0),
      child: Row(
        children: [
          // User image.
          if (log['user_photo_url'] != null)
            Padding(
              padding: EdgeInsets.only(right: 16.0),
              child: CircleAvatar(
                radius: 32,
                backgroundImage: NetworkImage(log['user_photo_url']),
              ),
            ),

          // Log details.
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // User name.
                Text(
                  log['user_name'] ?? '',
                  style: Theme.of(context).textTheme.labelLarge,
                ),
                gapH8,

                // Log timestamp.
                Text(
                  'Timestamp: ${DateFormat('yMMMd').add_jm().format(DateTime.parse(log['created_at']))}',
                  style: Theme.of(context).textTheme.labelMedium,
                ),

                // Log action.
                Text(
                  'Action: ${log['action']}',
                  style: Theme.of(context).textTheme.labelMedium,
                ),

                // Log type.
                Text(
                  'Type: ${log['type']}',
                  style: Theme.of(context).textTheme.labelMedium,
                ),

                // Log key.
                Text(
                  'Key: ${log['key']}',
                  style: Theme.of(context).textTheme.labelMedium,
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

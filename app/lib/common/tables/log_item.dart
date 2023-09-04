// Cannlytics Data
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 7/2/2023
// Updated: 7/11/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Flutter imports:
import 'package:flutter/material.dart';

// Package imports:
import 'package:go_router/go_router.dart';
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
      margin: EdgeInsets.only(left: 24, right: 24, bottom: 16),
      padding: EdgeInsets.all(16.0),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // User image.
          Padding(
            padding: EdgeInsets.only(right: 16.0),
            child: Tooltip(
              message: log['user_name'] ?? 'Anonymous',
              child: Material(
                color: Colors.transparent,
                child: InkWell(
                  borderRadius: BorderRadius.circular(50),
                  onTap: () {
                    if (log['user'] == null) return;
                    context.go('/users/${log['user']}');
                  },
                  child: CircleAvatar(
                    radius: 28,
                    backgroundColor: Theme.of(context).dialogBackgroundColor,
                    backgroundImage: NetworkImage(log['user_photo_url'] ??
                        'https://firebasestorage.googleapis.com/v0/b/cannlytics.appspot.com/o/assets%2Fimages%2Fplaceholders%2Fhomegrower-placeholder.png?alt=media&token=29331691-c2ef-4bc5-89e8-cec58a7913e4'),
                  ),
                  splashColor: Colors.blue
                      .withAlpha(30), // Change to your preferred color
                ),
              ),
            ),
          ),

          // Log details.
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Log action.
                Text(
                  log['action'],
                  style: Theme.of(context).textTheme.bodyLarge,
                ),
                gapH4,

                // Log timestamp.
                Text(
                  DateFormat('yMMMd')
                      .add_jm()
                      .format(DateTime.parse(log['created_at'])),
                  style: Theme.of(context).textTheme.bodySmall,
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

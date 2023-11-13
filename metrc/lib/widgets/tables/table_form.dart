// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 3/7/2023
// Updated: 3/12/2023

// Flutter imports:
import 'package:flutter/material.dart';

// Package imports:
import 'package:flutter_riverpod/flutter_riverpod.dart';

// Project imports:
import 'package:cannlytics_app/constants/design.dart';

/// Table form.
class TableForm extends ConsumerWidget {
  const TableForm({
    super.key,
    required this.table,
    this.title,
    this.actions,
  });
  final Widget table;
  final String? title;
  final Widget? actions;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    // Determine the screen size.
    final screenWidth = MediaQuery.of(context).size.width;

    // Build the form.
    return Consumer(
      builder: (context, ref, child) {
        return Container(
          margin: EdgeInsets.only(top: Insets(1).md),
          constraints: BoxConstraints(
            minHeight: 320,
          ),
          child: Center(
            child: SizedBox(
              width: Breakpoints.desktop.toDouble(),
              child: Padding(
                padding: EdgeInsets.symmetric(
                  horizontal: horizontalPadding(screenWidth),
                ),
                child: Column(
                  children: [
                    // Table header.
                    if (title != null)
                      Row(
                        children: [
                          // Title
                          Text(
                            title ?? '',
                            style: Theme.of(context)
                                .textTheme
                                .titleLarge!
                                .copyWith(
                                  color: Theme.of(context)
                                      .textTheme
                                      .titleLarge!
                                      .color,
                                ),
                          ),

                          // Optional actions.
                          const Spacer(),
                          if (actions != null) actions!,
                        ],
                      ),

                    // Space.
                    gapH6,

                    // Table.
                    Row(
                      children: [
                        Expanded(
                          child: SizedBox(
                            width: MediaQuery.of(context).size.width,
                            child: table,
                          ),
                        ),
                      ],
                    ),
                  ],
                ),
              ),
            ),
          ),
        );
      },
    );
  }
}

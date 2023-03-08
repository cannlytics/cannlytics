// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 3/7/2023
// Updated: 3/7/2023

import 'package:cannlytics_app/constants/design.dart';
import 'package:cannlytics_app/widgets/buttons/primary_button.dart';
import 'package:cannlytics_app/widgets/buttons/secondary_button.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

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
          color: Theme.of(context).scaffoldBackgroundColor,
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

                          const Spacer(),
                          if (actions != null) actions!,

                          // TODO: Allow actions to be passed.
                          // // Join an organization button.
                          // SecondaryButton(
                          //   isDark: isDark,
                          //   text: isWide ? 'Join an organization' : 'Join',
                          //   onPressed: () {
                          //     context.go('/organizations/join');
                          //   },
                          // ),

                          // // Add organization button.
                          // gapW6,
                          // PrimaryButton(
                          //   text: isWide ? 'New organization' : 'New',
                          //   onPressed: () {
                          //     context.go('/organizations/new');
                          //   },
                          // ),
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

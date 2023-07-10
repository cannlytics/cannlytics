// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 3/19/2023
// Updated: 7/1/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Flutter imports:
import 'package:flutter/material.dart';

// Package imports:
import 'package:go_router/go_router.dart';

// Project imports:
import 'package:cannlytics_data/common/buttons/primary_button.dart';
import 'package:cannlytics_data/constants/design.dart';
import 'package:cannlytics_data/ui/layout/console.dart';

// Package imports:


/// Simple not found screen used for 404 errors.
class NotFoundScreen extends StatelessWidget {
  const NotFoundScreen({super.key});

  @override
  Widget build(BuildContext context) {
    // Content.
    var content = Center(
      child: Padding(
        padding: EdgeInsets.all(24),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.center,
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            // TODO: Add a 404 image.
            SelectableText(
              'Page not found.',
              style: Theme.of(context).textTheme.titleLarge,
            ),
            gapH6,
            SelectableText(
              'Please contact dev@cannlytics.com for help sorting this issue out.',
              style: Theme.of(context).textTheme.titleMedium,
            ),
            gapH12,
            PrimaryButton(text: 'Home', onPressed: () => context.go('/')),
          ],
        ),
      ),
    );

    // Render.
    return ConsoleScreen(
      children: [
        SliverFillRemaining(
          child: content,
        ),
      ],
    );
  }
}

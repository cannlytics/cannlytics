// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 3/19/2023
// Updated: 3/19/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Flutter imports:
import 'package:flutter/material.dart';

// Package imports:
import 'package:go_router/go_router.dart';

// Project imports:
import 'package:cannlytics_data/common/buttons/custom_text_button.dart';
import 'package:cannlytics_data/common/forms/form_container.dart';
import 'package:cannlytics_data/ui/layout/footer.dart';
import 'package:cannlytics_data/constants/design.dart';

/// Simple not found screen used for 404 errors.
class NotFoundScreen extends StatelessWidget {
  const NotFoundScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: CustomScrollView(
        slivers: [
          // App header.
          // const SliverToBoxAdapter(child: AppHeader()),

          // Form.
          // TODO: Add a loading indicator.
          SliverToBoxAdapter(
              child: FormContainer(children: [
            Text(
              'Page not found.',
              style: Theme.of(context).textTheme.titleLarge,
            ),
            gapH6,
            Text(
              'You can use the following link to try to get to where you need to go.',
              style: Theme.of(context).textTheme.titleMedium,
            ),

            // Back to locations button.
            gapH24,
            Row(
              children: [
                // CustomTextButton(
                //   text: 'Back',
                //   onPressed: () {
                //     try {
                //       context.pop();
                //     } catch (error) {
                //       // Can't navigate.
                //     }
                //   },
                //   fontStyle: FontStyle.italic,
                // ),
                // gapW12,
                CustomTextButton(
                  text: 'Dashboard',
                  onPressed: () {
                    context.go('/');
                  },
                  fontStyle: FontStyle.italic,
                ),
                // gapW12,
                // CustomTextButton(
                //   text: 'Sign In',
                //   onPressed: () {
                //     context.go('/account/sign-in');
                //   },
                //   fontStyle: FontStyle.italic,
                // ),
              ],
            ),
            gapH48,
          ])),

          // Footer
          const SliverToBoxAdapter(child: Footer()),
        ],
      ),
    );
  }
}

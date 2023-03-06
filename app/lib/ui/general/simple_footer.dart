// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 3/5/2023
// Updated: 3/5/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Flutter imports:
import 'package:cannlytics_app/widgets/buttons/custom_text_button.dart';
import 'package:flutter/material.dart';

// Package imports:
import 'package:flutter_riverpod/flutter_riverpod.dart';

// Project imports:
import 'package:cannlytics_app/constants/design.dart';
import 'package:cannlytics_app/utils/web/web.dart';

/// A footer with links at the bottom of the app.
class SimpleFooter extends ConsumerWidget {
  const SimpleFooter({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    // Determine the screen size.
    final screenWidth = MediaQuery.of(context).size.width;
    final isWide = screenWidth > Breakpoints.tablet;

    // Build the footer.
    return Container(
      color: Theme.of(context).scaffoldBackgroundColor,
      margin: EdgeInsets.only(top: Insets(1).md),
      child: Center(
        child: SizedBox(
          width: 300,
          child: Padding(
            padding: EdgeInsets.symmetric(
              horizontal: horizontalPadding(screenWidth),
            ),
            child: Column(
              crossAxisAlignment:
                  isWide ? CrossAxisAlignment.start : CrossAxisAlignment.center,
              children: [
                gapH48,
                FooterLinks(),
                gapH6,
              ],
            ),
          ),
        ),
      ),
    );
  }
}

/// Row of footer links.
class FooterLinks extends StatelessWidget {
  const FooterLinks({
    Key? key,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        const FooterLink(
          text: 'Privacy',
          route: 'https://docs.cannlytics.com/about/privacy-policy',
        ),
        const SizedBox(width: 32),
        const FooterLink(
          text: 'Security',
          route: 'https://docs.cannlytics.com/about/security-policy',
        ),
        const SizedBox(width: 32),
        const FooterLink(
          text: 'Terms',
          route: 'https://docs.cannlytics.com/about/terms-of-service',
        ),
      ],
    );
  }
}

/// Link in the footer.
class FooterLink extends StatelessWidget {
  const FooterLink({
    Key? key,
    required this.text,
    required this.route,
  }) : super(key: key);
  final String text;
  final String route;

  @override
  Widget build(BuildContext context) {
    return CustomTextButton(
      text: text,
      onPressed: () {
        WebUtils.launchURL(route);
      },
    );
  }
}

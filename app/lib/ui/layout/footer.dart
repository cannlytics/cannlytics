// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 2/20/2023
// Updated: 8/19/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Flutter imports:
import 'package:flutter/material.dart';

// Package imports:
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:url_launcher/url_launcher.dart';

// Project imports:
import 'package:cannlytics_data/constants/design.dart';

/// A footer with links at the bottom of the app.
class Footer extends ConsumerWidget {
  const Footer({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    // Determine the screen size.
    final screenWidth = MediaQuery.of(context).size.width;
    final isWide = screenWidth > Breakpoints.tablet;

    // Build the footer.
    return Container(
      margin: EdgeInsets.all(0),
      padding: EdgeInsets.all(0),
      child: Center(
        child: SizedBox(
          width: Breakpoints.desktop.toDouble(),
          child: Padding(
            padding: EdgeInsets.only(
              // top: 48,
              top: 0,
              left: horizontalPadding(screenWidth),
              right: horizontalPadding(screenWidth),
            ),
            child: Column(
              crossAxisAlignment:
                  isWide ? CrossAxisAlignment.start : CrossAxisAlignment.center,
              children: [
                // Horizontal rule.
                Container(
                  margin: EdgeInsets.all(0),
                  padding: EdgeInsets.all(0),
                  color: Theme.of(context).dividerColor,
                  height: 1,
                ),
                gapH6,

                // Links.
                FooterLinks(isWide: isWide),
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
    required this.isWide,
  }) : super(key: key);
  final bool isWide;

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        // Contact link.
        if (isWide) const SizedBox(width: 8),
        // FIXME: Replace with CC logo: assets/images/logos/cc_heart.svg
        // TODO: Add a tooltip: "Except where otherwise noted, this website is licensed under a Creative Commons Attribution 4.0 International Public License."
        // TODO: Add a link to: 'https://creativecommons.org/licenses/by/4.0/'
        const FooterLink(
          text: 'CC BY 4.0',
          route: 'https://creativecommons.org/licenses/by/4.0/',
        ),

        // Spacer.
        if (isWide) const Spacer(),

        // Links.
        const FooterLink(
          text: 'Contact',
          route: 'https://cannlytics.com/contact',
        ),
        if (isWide) const SizedBox(width: 8),
        const FooterLink(
          text: 'GitHub',
          route: 'https://github.com/cannlytics/cannlytics',
        ),
        if (isWide) const SizedBox(width: 8),
        const FooterLink(
          text: 'Terms',
          route: 'https://docs.cannlytics.com/about/terms-of-service',
        ),
        if (isWide) const SizedBox(width: 8),
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
    return TextButton(
      child: Text(
        text,
        style: Theme.of(context).textTheme.bodySmall,
      ),
      onPressed: () {
        launchUrl(Uri.parse(route));
      },
    );
  }
}

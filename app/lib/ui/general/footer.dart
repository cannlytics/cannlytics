// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 2/20/2023
// Updated: 2/22/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Flutter imports:
import 'package:cannlytics_app/services/theme_service.dart';
import 'package:flutter/material.dart';

// Project imports:
import 'package:cannlytics_app/constants/colors.dart';
import 'package:cannlytics_app/constants/design.dart';
import 'package:cannlytics_app/ui/general/header.dart';
import 'package:cannlytics_app/utils/web/web.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

/// A footer with links at the bottom of the app.
class Footer extends ConsumerWidget {
  const Footer({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    // Determine the screen size.
    final screenWidth = MediaQuery.of(context).size.width;
    final isWide = screenWidth > Breakpoints.tablet;

    // Get the theme.
    final themeMode = ref.watch(themeModeProvider);
    final bool isDark = themeMode == ThemeMode.dark;

    // Build the footer.
    return Container(
      color: Theme.of(context).scaffoldBackgroundColor,
      margin: EdgeInsets.only(top: Insets(1).md),
      child: Center(
        child: SizedBox(
          width: Breakpoints.desktop.toDouble(),
          child: Padding(
            padding: EdgeInsets.symmetric(
              horizontal: horizontalPadding(screenWidth),
            ),
            child: Column(
              crossAxisAlignment:
                  isWide ? CrossAxisAlignment.start : CrossAxisAlignment.center,
              children: [
                // Logo.
                gapH6,
                AppLogo(isDark: isDark),
                gapH6,

                // Copyright and version.
                if (isWide)
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      _copyright(context),
                      _version(context),
                    ],
                  ),
                if (!isWide)
                  Column(
                    children: [
                      _copyright(context),
                      gapH6,
                      _version(context),
                    ],
                  ),
                gapH6,

                // Horizontal rule.
                Container(
                  color: AppColors.neutral2,
                  height: 1,
                ),
                const SizedBox(height: 16),

                // Links.
                FooterLinks(isWide: isWide),
                const SizedBox(height: 16),
              ],
            ),
          ),
        ),
      ),
    );
  }

  /// Copyright widget.
  Widget _copyright(BuildContext context) {
    return Text(
      'Copyright © 2023 Cannlytics',
      textAlign: TextAlign.center,
      style: Theme.of(context).textTheme.titleSmall!.copyWith(
            fontWeight: FontWeight.normal,
          ),
    );
  }

  /// Version widget.
  Widget _version(BuildContext context) {
    return Text(
      'v1.0.0',
      textAlign: TextAlign.center,
      style: Theme.of(context).textTheme.titleSmall!.copyWith(
            fontWeight: FontWeight.normal,
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
        const FooterLink(
          text: 'Contact',
          route: 'https://cannlytics.com/contact',
        ),

        // Spacer.
        if (isWide) const Spacer(),

        // Terms links.
        if (!isWide) const SizedBox(width: 32),
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
    return TextButton(
      child: Text(
        text,
        style: Theme.of(context).textTheme.titleSmall,
      ),
      onPressed: () {
        WebUtils.launchURL(route);
      },
    );
  }
}

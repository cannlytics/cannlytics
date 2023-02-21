// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 2/20/2023
// Updated: 2/20/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>
// import 'package:cannlytics_app/src/constants/app_colors.dart';
// import 'package:cannlytics_app/src/constants/breakpoints.dart';
// import 'package:cannlytics_app/src/features/app_header/app_logo.dart';
import 'package:cannlytics_app/constants/colors.dart';
import 'package:cannlytics_app/constants/design.dart';
import 'package:cannlytics_app/ui/general/header.dart';
import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

/// A footer with links at the bottom of the app.
class Footer extends StatelessWidget {
  const Footer({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final screenWidth = MediaQuery.of(context).size.width;
    final isWide = screenWidth > Breakpoints.tablet;
    return Container(
      // margin: EdgeInsets.only(top: 16),
      margin: EdgeInsets.only(top: Insets(1).md),
      // decoration: const BoxDecoration(
      //   border: Border(
      //     top: BorderSide(
      //       color: AppColors.neutral2,
      //       width: 1,
      //     ),
      //   ),
      // ),
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
                const SizedBox(height: 32),
                const AppLogo(),
                const SizedBox(height: 6),

                // Copyright.
                Text(
                  'Copyright © 2023 Cannlytics',
                  textAlign: TextAlign.center,
                  style: Theme.of(context).textTheme.titleSmall!.copyWith(
                        color: AppColors.neutral5,
                        fontWeight: FontWeight.normal,
                      ),
                ),
                const SizedBox(height: 12),

                // Horizontal rule.
                Container(
                  color: AppColors.neutral2,
                  height: 1,
                ),
                const SizedBox(height: 16),

                // Links.
                const FooterLinks(),
                const SizedBox(height: 16),
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
  const FooterLinks({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final screenWidth = MediaQuery.of(context).size.width;
    final isWide = screenWidth > Breakpoints.tablet;
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        const FooterLink(text: 'Contact', route: 'contact'),
        if (isWide) const Spacer(),
        if (!isWide) const SizedBox(width: 32),
        const FooterLink(text: 'Privacy', route: 'privacy'),
        const SizedBox(width: 32),
        const FooterLink(text: 'Security', route: 'security'),
        const SizedBox(width: 32),
        const FooterLink(text: 'Terms', route: 'terms'),
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
    return SizedBox(
      height: 48,
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 8),
        child: TextButton(
          child: Text(
            text,
            style: Theme.of(context)
                .textTheme
                .titleSmall!
                .copyWith(color: AppColors.neutral6),
          ),
          onPressed: () {
            // TODO: Open terms in dialogs!
            // context.goNamed(route);
            print('RENDER:');
            print(route);
          },
        ),
      ),
    );
  }
}

// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 3/5/2023
// Updated: 3/26/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Flutter imports:
import 'package:flutter/material.dart';

// Package imports:
import 'package:go_router/go_router.dart';

/// App logo.
class AppLogo extends StatelessWidget {
  const AppLogo({
    Key? key,
    required this.isDark,
  }) : super(key: key);

  // Properties
  final bool isDark;

  @override
  Widget build(BuildContext context) {
    return InkWell(
      // splashColor: AppColors.accent1,
      onTap: () {
        context.goNamed('dashboard');
      },
      child: Image.asset(
        isDark
            ? 'assets/images/logos/cannlytics_logo_with_text_dark.png'
            : 'assets/images/logos/cannlytics_logo_with_text_light.png',
        width: 120,
      ),
    );
  }
}

/// App icon.
class AppIcon extends StatelessWidget {
  const AppIcon({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return InkWell(
      // splashColor: AppColors.accent1,
      onTap: () {
        context.goNamed('dashboard');
      },
      child: Image.asset(
        'assets/images/logos/cannlytics_calyx_192.png',
        height: 30,
      ),
    );
  }
}

/// Responsive app logo for sign in screens.
class ResponsiveAppLogo extends StatelessWidget {
  const ResponsiveAppLogo({
    Key? key,
    required this.isDark,
  }) : super(key: key);

  // Properties
  final bool isDark;

  @override
  Widget build(BuildContext context) {
    return FractionallySizedBox(
      widthFactor: 0.6,
      child: Image.asset(
        isDark
            ? 'assets/images/logos/cannlytics_logo_with_text_dark.png'
            : 'assets/images/logos/cannlytics_logo_with_text_light.png',
        height: 45,
      ),
    );
  }
}

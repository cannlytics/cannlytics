// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 3/5/2023
// Updated: 3/5/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Flutter imports:
import 'package:cannlytics_app/constants/colors.dart';
import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

/// App logo for the menu.
class AppLogo extends StatelessWidget {
  const AppLogo({
    Key? key,
    required this.isDark,
  }) : super(key: key);
  final bool isDark;

  @override
  Widget build(BuildContext context) {
    return InkWell(
      splashColor: AppColors.accent1,
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

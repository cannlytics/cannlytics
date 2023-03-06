// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 2/18/2023
// Updated: 2/18/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Flutter imports:
import 'package:flutter/material.dart';

// Project imports:
import 'package:cannlytics_app/constants/theme.dart';
import 'package:cannlytics_app/constants/design.dart';
import 'package:cannlytics_app/widgets/layout/responsive_center.dart';

/// Scrollable widget that shows a responsive card with a given child widget.
/// Useful for displaying forms and other widgets that need to be scrollable.
class ResponsiveScrollableCard extends StatelessWidget {
  ResponsiveScrollableCard({
    super.key,
    required this.child,
    this.isDark = false,
  });
  final Widget child;
  final bool isDark;

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      child: ResponsiveCenter(
        maxContentWidth: Breakpoints.mobile,
        child: Padding(
          padding: const EdgeInsets.all(Sizes.p16),
          child: Card(
            surfaceTintColor: isDark ? null : AppColors.surface,
            child: Padding(
              padding: const EdgeInsets.all(Sizes.p16),
              child: child,
            ),
          ),
        ),
      ),
    );
  }
}

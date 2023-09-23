// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 2/18/2023
// Updated: 2/22/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Flutter imports:
import 'package:flutter/material.dart';

// Defaults.
class Defaults {
  static const primaryColor = Color(0xFF2697FF);
  static const secondaryColor = Color(0xFF2A2D3E);
  static const bgColor = Color(0xFF212332);
  static const defaultPadding = 16.0;
}

// Constant breakpoints.
class Breakpoints {
  static const desktop = 1060.0;
  static const tablet = 834.0;
  static const mobile = 375.0;
  static const twoColLayoutMinWidth = 640.0;
}

// Constant corners.
class Corners {
  static const double sm = 4;
  static const double md = 8;
  static const double lg = 32;
}

// Constant durations.
class Durations {
  static const Duration fast = Duration(milliseconds: 300);
  static const Duration med = Duration(milliseconds: 600);
  static const Duration slow = Duration(milliseconds: 900);
  static const Duration pageTransition = Duration(milliseconds: 200);
}

// Constant insets.
class Insets {
  Insets(this._scale);
  final double _scale;

  late final double xxs = 4 * _scale;
  late final double xs = 8 * _scale;
  late final double sm = 16 * _scale;
  late final double md = 24 * _scale;
  late final double lg = 32 * _scale;
  late final double xl = 48 * _scale;
  late final double xxl = 56 * _scale;
  late final double offset = 80 * _scale;
}

// Constant paddings.
class Sizes {
  static const p2 = 2.0;
  static const p4 = 4.0;
  static const p6 = 6.0;
  static const p8 = 8.0;
  static const p12 = 12.0;
  static const p16 = 16.0;
  static const p18 = 18.0;
  static const p20 = 20.0;
  static const p24 = 24.0;
  static const p32 = 32.0;
  static const p48 = 48.0;
  static const p64 = 64.0;
}

// Constant gap widths.
const gapW2 = SizedBox(width: Sizes.p2);
const gapW4 = SizedBox(width: Sizes.p4);
const gapW6 = SizedBox(width: Sizes.p6);
const gapW8 = SizedBox(width: Sizes.p8);
const gapW12 = SizedBox(width: Sizes.p12);
const gapW16 = SizedBox(width: Sizes.p16);
const gapW18 = SizedBox(width: Sizes.p18);
const gapW20 = SizedBox(width: Sizes.p20);
const gapW24 = SizedBox(width: Sizes.p24);
const gapW32 = SizedBox(width: Sizes.p32);
const gapW48 = SizedBox(width: Sizes.p48);
const gapW64 = SizedBox(width: Sizes.p64);

// Constant gap heights.
const gapH2 = SizedBox(height: Sizes.p2);
const gapH4 = SizedBox(height: Sizes.p4);
const gapH6 = SizedBox(height: Sizes.p6);
const gapH8 = SizedBox(height: Sizes.p8);
const gapH12 = SizedBox(height: Sizes.p12);
const gapH16 = SizedBox(height: Sizes.p16);
const gapH18 = SizedBox(height: Sizes.p18);
const gapH20 = SizedBox(height: Sizes.p20);
const gapH24 = SizedBox(height: Sizes.p24);
const gapH32 = SizedBox(height: Sizes.p32);
const gapH48 = SizedBox(height: Sizes.p48);
const gapH64 = SizedBox(height: Sizes.p64);

/// Standard horizontal padding.
double horizontalPadding(double screenWidth) {
  if (screenWidth > Breakpoints.desktop) {
    return 0;
  } else if (screenWidth > Breakpoints.mobile) {
    return 28;
  } else {
    return 20;
  }
}

/// Standard horizontal padding for slivers.
double sliverHorizontalPadding(double screenWidth) {
  if (screenWidth > Breakpoints.desktop) {
    return (screenWidth - Breakpoints.desktop) / 2;
  } else if (screenWidth > Breakpoints.mobile) {
    return 28;
  } else {
    return 20;
  }
}

/// Render a widget depending on the screen size.
class Responsive extends StatelessWidget {
  final Widget mobile;
  final Widget? tablet;
  final Widget desktop;

  const Responsive({
    Key? key,
    required this.mobile,
    this.tablet,
    required this.desktop,
  }) : super(key: key);

  /// Check if the screen is mobile size.
  static bool isMobile(BuildContext context) =>
      MediaQuery.of(context).size.width < Breakpoints.tablet;

  /// Check if the screen is tablet size.
  static bool isTablet(BuildContext context) =>
      MediaQuery.of(context).size.width < Breakpoints.desktop &&
      MediaQuery.of(context).size.width >= Breakpoints.tablet;

  /// Check if the screen is desktop size.
  static bool isDesktop(BuildContext context) =>
      MediaQuery.of(context).size.width >= Breakpoints.desktop;

  @override
  Widget build(BuildContext context) {
    final Size _size = MediaQuery.of(context).size;
    if (_size.width >= 1100) {
      return desktop;
    } else if (_size.width >= 850 && tablet != null) {
      return tablet!;
    } else {
      return mobile;
    }
  }
}

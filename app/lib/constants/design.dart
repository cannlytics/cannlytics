// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 2/18/2023
// Updated: 2/18/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>
import 'package:flutter/material.dart';

// Constant paddings.
class Sizes {
  static const p4 = 4.0;
  static const p8 = 8.0;
  static const p12 = 12.0;
  static const p16 = 16.0;
  static const p20 = 20.0;
  static const p24 = 24.0;
  static const p32 = 32.0;
  static const p48 = 48.0;
  static const p64 = 64.0;
}

// TODO: Constant corners.

// Constant gap widths.
const gapW4 = SizedBox(width: Sizes.p4);
const gapW8 = SizedBox(width: Sizes.p8);
const gapW12 = SizedBox(width: Sizes.p12);
const gapW16 = SizedBox(width: Sizes.p16);
const gapW20 = SizedBox(width: Sizes.p20);
const gapW24 = SizedBox(width: Sizes.p24);
const gapW32 = SizedBox(width: Sizes.p32);
const gapW48 = SizedBox(width: Sizes.p48);
const gapW64 = SizedBox(width: Sizes.p64);

// Constant gap heights.
const gapH4 = SizedBox(height: Sizes.p4);
const gapH8 = SizedBox(height: Sizes.p8);
const gapH12 = SizedBox(height: Sizes.p12);
const gapH16 = SizedBox(height: Sizes.p16);
const gapH20 = SizedBox(height: Sizes.p20);
const gapH24 = SizedBox(height: Sizes.p24);
const gapH32 = SizedBox(height: Sizes.p32);
const gapH48 = SizedBox(height: Sizes.p48);
const gapH64 = SizedBox(height: Sizes.p64);

/// Layout breakpoints used in the app.
class Breakpoints {
  static const desktop = 1060.0;
  static const tablet = 834.0;
  static const mobile = 375.0;
  static const twoColLayoutMinWidth = 640.0;
}

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

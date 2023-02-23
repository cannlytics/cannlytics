// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 2/17/2023
// Updated: 2/22/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>
import 'package:flutter/material.dart';

/// Colors used in the app for theming.
class AppColors {
  // Primary colors.
  static const primary = Color(0xFFFF9500);
  static const primary7 = Color(0xFFe53a23);
  static const primary6 = Color(0xFFFF9339);
  static const primary5 = Color(0xFFFF9500);
  static const primary4 = Color(0xFFffa600);
  static const primary3 = Color(0xFFFF8979);
  static const primary2 = Color(0xFFFFCE88);
  static const primary1 = Color(0xFFFFE4B3);

  // Shades of the primary color.
  static const MaterialColor primaryColors = MaterialColor(0xFFFF9500, {
    50: Color(0xFFFFE4B3),
    100: Color(0xFFFFD488),
    200: Color(0xFFFFC864),
    300: Color(0xFFFFCE88),
    400: Color(0xFFFF8979),
    500: Color(0xFFFFAD39),
    600: Color(0xFFffa600),
    700: Color(0xFFFF9500),
    800: Color(0xFFFF9339),
    900: Color(0xFFe53a23),
  });

  // Secondary colors.
  static const secondary = Color(0xFFE5EAFF);
  static const neutral1 = Color(0xFFF8F9F9);
  static const neutral2 = Color(0xFFD7D7DB);
  static const neutral3 = Color(0xFFB5B6BC);
  static const neutral4 = Color(0xFF7C7E84);
  static const neutral5 = Color(0xFF4A4B4F);
  static const neutral6 = Color(0xFF0F0F0F);

  // Layout colors.
  static const Color surface = Colors.white;

  // Common colors.
  static const yellow = Color(0xFFE3BE1B);
  static const blue = Color(0xFF204F96);
  static const green = Color(0xFF48731C);
  static const purple = Color(0xFF582391);
  static const brown = Color(0xFFAD5E03);
  static const red = Color(0xFFB3122F);

  // Text colors.
  static const Color accent1 = Color(0xFFFF9500);
  static const Color accent2 = Color(0xFFBEABA1);
  static const Color offWhite = Color(0xFFF8ECE5);
  static const Color caption = Color(0xFF7D7873);
  static const Color body = Color(0xFF514F4D);
  static const Color greyStrong = Color(0xFF272625);
  static const Color greyMedium = Color(0xFF9D9995);
  static const Color white = Colors.white;
  static const Color black = Color(0xFF1E1B18);

  // Whether or not the app is in dark mode.
  final bool isDark = false;

  /// Shift a color.
  Color shift(Color c, double d) =>
      ColorUtils.shiftHsl(c, d * (isDark ? -1 : 1));

  /// Convert the colors to theme data.
  ThemeData toThemeData() {
    TextTheme txtTheme =
        (isDark ? ThemeData.dark() : ThemeData.light()).textTheme;
    Color txtColor = white;
    ColorScheme colorScheme = ColorScheme(
      brightness: isDark ? Brightness.dark : Brightness.light,
      primary: accent1,
      primaryContainer: accent1,
      secondary: accent1,
      secondaryContainer: accent1,
      background: offWhite,
      surface: offWhite,
      onBackground: txtColor,
      onSurface: txtColor,
      onError: Colors.white,
      onPrimary: Colors.white,
      onSecondary: Colors.white,
      error: Colors.red.shade400,
    );

    /// Now that we have ColorScheme and TextTheme, we can create the ThemeData
    /// Also add on some extra properties that ColorScheme seems to miss
    var t = ThemeData.from(
      textTheme: txtTheme,
      colorScheme: colorScheme,
    ).copyWith(
      textSelectionTheme: const TextSelectionThemeData(
        cursorColor: accent1,
      ),
      highlightColor: accent1,
    );

    /// Return the themeData which MaterialApp can use.
    return t;
  }
}

/// Utilities to manage colors.
class ColorUtils {
  /// Shift a color.
  static Color shiftHsl(Color c, [double amt = 0]) {
    var hslc = HSLColor.fromColor(c);
    return hslc.withLightness((hslc.lightness + amt).clamp(0.0, 1.0)).toColor();
  }

  /// Parse a color hex.
  static Color parseHex(String value) =>
      Color(int.parse(value.substring(1, 7), radix: 16) + 0xFF000000);

  /// Blend two colors.
  static Color blend(Color dst, Color src, double opacity) {
    return Color.fromARGB(
      255,
      (dst.red.toDouble() * (1.0 - opacity) + src.red.toDouble() * opacity)
          .toInt(),
      (dst.green.toDouble() * (1.0 - opacity) + src.green.toDouble() * opacity)
          .toInt(),
      (dst.blue.toDouble() * (1.0 - opacity) + src.blue.toDouble() * opacity)
          .toInt(),
    );
  }
}

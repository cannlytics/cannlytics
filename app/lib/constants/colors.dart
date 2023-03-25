// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 3/25/2023
// Updated: 3/25/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

import 'package:flutter/material.dart';

/// Light theme colors.
class LightColors {
  // Primary colors.
  static const primary = Color(0xFFdc8a78);
  static const primary7 = Color(0xFFdd7878);
  static const primary6 = Color(0xFFea76cb);
  static const primary5 = Color(0xFF8839ef);
  static const primary4 = Color(0xFFd20f39);
  static const primary3 = Color(0xFFe64553);
  static const primary2 = Color(0xFFfe640b);
  static const primary1 = Color(0xFFdf8e1d);

  // Shades of the primary color.
  static const MaterialColor primaryColors = MaterialColor(0xFFdf8e1d, {
    50: Color(0xFFe6e9ef),
    100: Color(0xFFbcc0cc),
    200: Color(0xFFacb0be),
    300: Color(0xFF9ca0b0),
    400: Color(0xFF8c8fa1),
    500: Color(0xFF7c7f93),
    600: Color(0xFF6c6f85),
    700: Color(0xFF5c5f77),
    800: Color(0xFF4c4f69),
    900: Color(0xFF3c3f5b),
    1000: Color(0xFFe69e3e),
    1100: Color(0xFFc27718),
    1200: Color(0xFFc09f8b),
    1300: Color(0xFFe69b00),
    1400: Color(0xFFa6df1d),
  });

  // Secondary colors.
  static const secondary = Color(0xFF40a02b);
  static const secondary1 = Color(0xFF179299);
  static const secondary2 = Color(0xFF04a5e5);
  static const secondary3 = Color(0xFF209fb5);
  static const secondary4 = Color(0xFF1e66f5);
  static const secondary5 = Color(0xFF7287fd);
  static const secondary6 = Color(0xFF8839ef);

  // Text colors
  static const text = Color(0xFF4c4f69);
  static const subtext1 = Color(0xFF5c5f77);
  static const subtext0 = Color(0xFF6c6f85);
  static const overlay2 = Color(0xFF7c7f93);
  static const overlay1 = Color(0xFF8c8fa1);
  static const overlay0 = Color(0xFF9ca0b0);

  // Surface colors.
  static const Color surface2 = Color(0xFFacb0be);
  static const Color surface1 = Color(0xFFbcc0cc);
  static const Color surface0 = Color(0xFFccd0da);
  static const Color base = Color(0xFFeff1f5);
  static const Color mantle = Color(0xFFe6e9ef);
  static const Color crust = Color(0xFFdce0e8);

  // Additional colors.
  static const rosewater = Color(0xFFF2D5CF);
  static const flamingo = Color(0xFFEEBEBE);
  static const pink = Color(0xFFF4B8E4);
  static const mauve = Color(0xFFCA9EE6);
  static const red = Color(0xFFE78284);
  static const maroon = Color(0xFFEA999C);
  static const peach = Color(0xFFEF9F76);
  static const yellow = Color(0xFFE5C890);
  static const green = Color(0xFFA6D189);
  static const teal = Color(0xFF81C8BE);
  static const sky = Color(0xFF99D1DB);
  static const sapphire = Color(0xFF85C1DC);
  static const blue = Color(0xFF8CAaEE);
  static const lavender = Color(0xFFBABBf1);
}

/// Dark theme colors.
class DarkColors {
  // Primary colors.
  static const primary = Color(0xFFe78284);
  static const primary7 = Color(0xFFea999c);
  static const primary6 = Color(0xFFca9ee6);
  static const primary5 = Color(0xFF8839ef);
  static const primary4 = Color(0xFFd20f39);
  static const primary3 = Color(0xFFe64553);
  static const primary2 = Color(0xFFef9f76);
  static const primary1 = Color(0xFFe5c890);

  // Shades of the primary color.
  static const MaterialColor primaryColors = MaterialColor(0xFFe5c890, {
    50: Color(0xFFf2ede5),
    100: Color(0xFFdad4bd),
    200: Color(0xFFc1bb95),
    300: Color(0xFFa9a16d),
    400: Color(0xFF918847),
    500: Color(0xFF795f20),
    600: Color(0xFF635700),
    700: Color(0xFF544d00),
    800: Color(0xFF453400),
    900: Color(0xFF372b00),
    1000: Color(0xFFe6b200),
    1100: Color(0xFFb88c00),
    1200: Color(0xFFb3aa99),
    1300: Color(0xFFe6a100),
    1400: Color(0xFF7fae00),
  });

  // Secondary colors.
  static const secondary = Color(0xFFa6d189);
  static const secondary1 = Color(0xFF81c8be);
  static const secondary2 = Color(0xFF04a5e5);
  static const secondary3 = Color(0xFF209fb5);
  static const secondary4 = Color(0xFF1e66f5);
  static const secondary5 = Color(0xFF7287fd);
  static const secondary6 = Color(0xFF8839ef);

  // Text colors
  static const text = Color(0xFF795f20);
  static const subtext1 = Color(0xFF544d00);
  static const subtext0 = Color(0xFF635700);
  static const overlay2 = Color(0xFF918847);
  static const overlay1 = Color(0xFFa9a16d);
  static const overlay0 = Color(0xFFc1bb95);

  // Surface colors.
  static const Color surface2 = Color(0xFFb3bbcc);
  static const Color surface1 = Color(0xFFdadde6);
  static const Color surface0 = Color(0xFFeff1f5);
  static const Color base = Color(0xFFFFFFFF);
  static const Color mantle = Color(0xFFF2EDE5);
  static const Color crust = Color(0xFFE6E9EF);
}

/// COLOR UTILITIES

/// Utilities to manage colors.
// class ColorUtils {
//   /// Shift a color.
//   static Color shiftHsl(Color c, [double amt = 0]) {
//     var hslc = HSLColor.fromColor(c);
//     return hslc.withLightness((hslc.lightness + amt).clamp(0.0, 1.0)).toColor();
//   }

//   /// Shift a color accounting for light / dark theme.
//   Color shift(bool isDark, Color c, double d) =>
//       ColorUtils.shiftHsl(c, d * (isDark ? -1 : 1));

//   /// Parse a color hex.
//   static Color parseHex(String value) =>
//       Color(int.parse(value.substring(1, 7), radix: 16) + 0xFF000000);

//   /// Blend two colors.
//   static Color blend(Color dst, Color src, double opacity) {
//     return Color.fromARGB(
//       255,
//       (dst.red.toDouble() * (1.0 - opacity) + src.red.toDouble() * opacity)
//           .toInt(),
//       (dst.green.toDouble() * (1.0 - opacity) + src.green.toDouble() * opacity)
//           .toInt(),
//       (dst.blue.toDouble() * (1.0 - opacity) + src.blue.toDouble() * opacity)
//           .toInt(),
//     );
//   }
// }


/// ORIGINAL COLORS
  // Primary colors.
  // static const primary = Color(0xFFFF9500);
  // static const primary7 = Color(0xFFe53a23);
  // static const primary6 = Color(0xFFFF9339);
  // static const primary5 = Color(0xFFFF9500);
  // static const primary4 = Color(0xFFffa600);
  // static const primary3 = Color(0xFFFF8979);
  // static const primary2 = Color(0xFFFFCE88);
  // static const primary1 = Color(0xFFFFE4B3);


  // Shades of the primary color.
  // static const MaterialColor primaryColors = MaterialColor(0xFFFF9500, {
  //   50: Color(0xFFFFE4B3),
  //   100: Color(0xFFFFD488),
  //   200: Color(0xFFFFC864),
  //   300: Color(0xFFFFCE88),
  //   400: Color(0xFFFF8979),
  //   500: Color(0xFFFFAD39),
  //   600: Color(0xFFffa600),
  //   700: Color(0xFFFF9500),
  //   800: Color(0xFFFF9339),
  //   900: Color(0xFFe53a23),
  // });


  // Secondary colors.
  // static const secondary = Color(0xFFE5EAFF);
  // static const neutral1 = Color(0xFFF8F9F9);
  // static const neutral2 = Color(0xFFD7D7DB);
  // static const neutral3 = Color(0xFFB5B6BC);
  // static const neutral4 = Color(0xFF7C7E84);
  // static const neutral5 = Color(0xFF4A4B4F);
  // static const neutral6 = Color(0xFF0F0F0F);


  // Layout colors.
  // static const Color surface = Colors.white;

  // Common colors.
  // static const yellow = Color(0xFFE3BE1B);
  // static const blue = Color(0xFF204F96);
  // static const green = Color(0xFF48731C);
  // static const purple = Color(0xFF582391);
  // static const brown = Color(0xFFAD5E03);
  // static const red = Color(0xFFB3122F);

  // Text colors.
  // static const Color accent1 = Color(0xFFFF9500);
  // static const Color accent2 = Color(0xFFBEABA1);
  // static const Color offWhite = Color(0xFFF8ECE5);
  // static const Color caption = Color(0xFF7D7873);
  // static const Color body = Color(0xFF514F4D);
  // static const Color greyStrong = Color(0xFF272625);
  // static const Color greyMedium = Color(0xFF9D9995);
  // static const Color white = Colors.white;
  // static const Color black = Color(0xFF1E1B18);

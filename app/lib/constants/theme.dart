// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 2/17/2023
// Updated: 3/24/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Flutter imports:
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
  static const MaterialColor primaryColors = MaterialColor(0xFFdc8a78, {
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
  });

  // Secondary colors.
  static const secondary = Color(0xFF40a02b);
  static const neutral1 = Color(0xFF179299);
  static const neutral2 = Color(0xFF04a5e5);
  static const neutral3 = Color(0xFF209fb5);
  static const neutral4 = Color(0xFF1e66f5);
  static const neutral5 = Color(0xFF7287fd);
  static const neutral6 = Color(0xFF8839ef);

  // Common colors.
  static const yellow = Color(0xFFdf8e1d);
  static const blue = Color(0xFF1e66f5);
  static const green = Color(0xFF40a02b);
  static const purple = Color(0xFF8839ef);
  static const brown = Color(0xFFe64553);
  static const red = Color(0xFFd20f39);

  // Text colors.
  static const Color accent1 = Color(0xFFd20f39);
  static const Color accent2 = Color(0xFF8839ef);
  static const Color offWhite = Color(0xFFe6e9ef);
  static const Color caption = Color(0xFF4c4f69);
  static const Color body = Color(0xFF6c6f85);
  static const Color greyStrong = Color(0xFFe6e9ef);
  static const Color greyMedium = Color(0xFFbcc0cc);
  static const Color white = Colors.white;
  static const Color black = Color(0xFF4c4f69);
}

/// Dark theme colors.
class DarkColors {
  // Primary colors.
  static const primary = Color(0xFFe78284);
  static const primary7 = Color(0xFFea999c);
  static const primary6 = Color(0xFFeebebe);
  static const primary5 = Color(0xFFf2d5cf);
  static const primary4 = Color(0xFFf4b8e4);
  static const primary3 = Color(0xFFca9ee6);
  static const primary2 = Color(0xFFbabbf1);
  static const primary1 = Color(0xFF8caaee);

  // Shades of the primary color.
  static const MaterialColor primaryColors = MaterialColor(0xFFe78284, {
    50: Color(0xFFf4b8e4),
    100: Color(0xFFf2d5cf),
    200: Color(0xFFeebebe),
    300: Color(0xFFca9ee6),
    400: Color(0xFFbabbf1),
    500: Color(0xFF85c1dc),
    600: Color(0xFF8caaee),
    700: Color(0xFFe78284),
    800: Color(0xFFea999c),
    900: Color(0xFF737994),
  });

  // Secondary colors.
  static const secondary = Color(0xFF99d1db);
  static const neutral1 = Color(0xFF51576d);
  static const neutral2 = Color(0xFFa5adce);
  static const neutral3 = Color(0xFFb5bfe2);
  static const neutral4 = Color(0xFF949cbb);
  static const neutral5 = Color(0xFF838ba7);
  static const neutral6 = Color(0xFF303446);

  // Common colors.
  static const yellow = Color(0xFFe5c890);
  static const blue = Color(0xFF8caaee);
  static const green = Color(0xFFa6d189);
  static const purple = Color(0xFFca9ee6);
  static const brown = Color(0xFFea999c);
  static const red = Color(0xFFe78284);

  // Text colors.
  static const Color accent1 = Color(0xFFe78284);
  static const Color accent2 = Color(0xFFbabbf1);
  static const Color offWhite = Color(0xFFc6d0f5);
  static const Color caption = Color(0xFF737994);
  static const Color body = Color(0xFF626880);
  static const Color greyStrong = Color(0xFF292c3c);
  static const Color greyMedium = Color(0xFF51576d);
  static const Color white = Colors.white;
  static const Color black = Color(0xFF303446);
}

/// Colors used in the app for theming.
class AppTheme {
  /// Convert the colors to theme data.
  static ThemeData toThemeData(bool isDark) {
    ThemeData themeMode = isDark ? ThemeData.dark() : ThemeData.light();
    TextTheme textTheme = themeMode.textTheme;
    ColorScheme colorScheme = ColorScheme(
      brightness: isDark ? Brightness.dark : Brightness.light,
      primary: isDark ? DarkColors.accent1 : LightColors.accent1,
      primaryContainer: isDark ? DarkColors.accent1 : LightColors.accent1,
      secondary: isDark ? DarkColors.accent1 : LightColors.accent1,
      secondaryContainer: isDark ? DarkColors.accent1 : LightColors.accent1,
      background: isDark ? DarkColors.offWhite : LightColors.offWhite,
      surface: isDark ? const Color(0xFF323443) : Colors.white,
      onBackground: isDark ? const Color(0xFFf5f5f5) : const Color(0xFF24292e),
      onSurface: isDark ? const Color(0xFFf5f5f5) : const Color(0xFF24292e),
      onError: Colors.white,
      onPrimary: Colors.white,
      onSecondary: Colors.white,
      error: Colors.red.shade400,
    );

    // Create the ThemeData with the ColorScheme and TextTheme.
    // Also add on extra properties that ColorScheme seems to miss.
    // See: https://medium.com/@omlondhe/themedata-in-flutter-f6a67d9c636d
    var t = ThemeData.from(
      textTheme: textTheme,
      colorScheme: colorScheme,
    ).copyWith(
      useMaterial3: true,
      materialTapTargetSize: MaterialTapTargetSize.shrinkWrap,
      highlightColor: isDark ? DarkColors.accent1 : LightColors.accent1,
      visualDensity: VisualDensity.compact,
      scaffoldBackgroundColor: isDark ? const Color(0xFF323443) : Colors.white,
      canvasColor: isDark
          ? const Color(0xFF323443)
          : isDark
              ? DarkColors.neutral1
              : LightColors.neutral1,

      // App bar theme.
      appBarTheme: const AppBarTheme(
        elevation: 0.0,
        centerTitle: true,
      ),

      // Button theme.
      buttonTheme: ButtonThemeData(
        buttonColor: isDark ? DarkColors.primary2 : LightColors.primary2,
        textTheme: ButtonTextTheme.primary,
        colorScheme: colorScheme.copyWith(
          secondary: isDark ? Colors.white : const Color(0xFF323443),
        ),
      ),

      // Card style.
      cardColor: isDark ? const Color(0xFF323443) : Colors.white,
      cardTheme: CardTheme(
        elevation: 1,
        surfaceTintColor: isDark
            ? null
            : isDark
                ? DarkColors.surface
                : LightColors.surface,
      ),

      // Data table style.
      dataTableTheme: DataTableThemeData(
        // headingTextStyle: TextStyle(
        //   fontWeight: FontWeight.bold,
        //   fontSize: 16.0,
        // ),
        // dataTextStyle: TextStyle(
        //   fontSize: 14.0,
        // ),
        // headingRowColor: MaterialStateProperty.all(Colors.transparent),
        // dataRowColor: MaterialStateProperty.all(Colors.transparent),
        decoration: BoxDecoration(
          border: Border.all(color: Colors.grey),
          borderRadius: BorderRadius.circular(3),
        ),
      ),

      // Dialog style.
      dialogBackgroundColor:
          isDark ? const Color(0xFF323443) : AppColors.neutral1,
      dialogTheme: DialogTheme(
        elevation: 1,
        surfaceTintColor: isDark ? null : AppColors.surface,
      ),

      // Input style.
      inputDecorationTheme: InputDecorationTheme(
        labelStyle: TextStyle(
          fontFamily: 'SourceSerifPro',
        ),
        floatingLabelBehavior: FloatingLabelBehavior.never,
        floatingLabelStyle: TextStyle(
          color: isDark ? const Color(0xFFf5f5f5) : const Color(0xFF24292e),
          fontFamily: 'SourceSerifPro',
        ),
        helperStyle: TextStyle(
          // color: isDark ? const Color(0xFFf5f5f5) : const Color(0xFF24292e),
          fontFamily: 'SourceSerifPro',
        ),
        hintStyle: TextStyle(
          fontFamily: 'SourceSerifPro',
        ),
        errorStyle: TextStyle(
          color: isDark ? const Color(0xFFf5f5f5) : const Color(0xFF24292e),
          fontFamily: 'SourceSerifPro',
        ),
        isDense: true,
        contentPadding: null,
        outlineBorder: null,
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(3),
          borderSide: BorderSide(color: Color(0xFFdadce0)),
        ),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(3),
          borderSide: BorderSide(color: Color(0xFFdadce0)),
        ),
      ),

      // Text button style.
      textButtonTheme: TextButtonThemeData(
        style: TextButton.styleFrom(
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(3),
          ),
        ),
      ),

      // Text selection style.
      textSelectionTheme: TextSelectionThemeData(
        cursorColor: isDark ? const Color(0xFFf5f5f5) : const Color(0xFF24292e),
      ),

      // Text style.
      textTheme: TextTheme(
        displayLarge: TextStyle(
          color: isDark ? const Color(0xFFf5f5f5) : const Color(0xFF24292e),
          fontFamily: 'LibreBaskerville',
          fontSize: 48,
          letterSpacing: 1.5,
        ),
        displayMedium: TextStyle(
          color: isDark ? const Color(0xFFf5f5f5) : const Color(0xFF24292e),
          fontFamily: 'LibreBaskerville',
          fontSize: 36,
          letterSpacing: 1.2,
        ),
        displaySmall: TextStyle(
          color: isDark ? AppColors.neutral2 : AppColors.neutral4,
          fontFamily: 'LibreBaskerville',
          fontSize: 28,
        ),
        headlineLarge: TextStyle(
          color: isDark ? const Color(0xFFf5f5f5) : const Color(0xFF24292e),
          fontFamily: 'SourceSerifPro',
          fontSize: 24,
        ),
        headlineMedium: TextStyle(
          color: isDark ? const Color(0xFFf5f5f5) : const Color(0xFF24292e),
          fontFamily: 'SourceSerifPro',
          fontSize: 21,
        ),
        headlineSmall: TextStyle(
          color: isDark ? const Color(0xFFf5f5f5) : const Color(0xFF24292e),
          fontFamily: 'SourceSerifPro',
          fontSize: 18,
        ),
        titleLarge: TextStyle(
          color: isDark ? const Color(0xFFf5f5f5) : const Color(0xFF24292e),
          fontFamily: 'LibreBaskerville',
          fontSize: 21,
        ),
        titleMedium: TextStyle(
          color: isDark ? const Color(0xFFf5f5f5) : const Color(0xFF24292e),
          fontFamily: 'SourceSerifPro',
          fontSize: 17,
          height: 1.33,
        ),
        titleSmall: TextStyle(
          color: isDark ? AppColors.neutral2 : AppColors.neutral4,
          fontFamily: 'CormorantGaramond',
          fontSize: 16,
        ),
        bodyLarge: TextStyle(
          color: isDark ? const Color(0xFFf5f5f5) : const Color(0xFF24292e),
          fontFamily: 'CormorantGaramond',
          fontSize: 18,
          height: 1.5,
        ),
        bodyMedium: TextStyle(
          color: isDark ? AppColors.neutral2 : AppColors.neutral4,
          fontFamily: 'SourceSerifPro',
          fontSize: 16,
          height: 1.5,
        ),
        bodySmall: TextStyle(
          color: isDark ? const Color(0xFFf5f5f5) : const Color(0xFF24292e),
          fontFamily: 'SourceSerifPro',
          fontSize: 14,
          height: 1.5,
        ),
        labelLarge: TextStyle(
          fontSize: 18,
          color: isDark ? const Color(0xFFf5f5f5) : const Color(0xFF24292e),
          fontFamily: 'LibreBaskerville',
        ),
        labelMedium: TextStyle(
          fontSize: 16,
          color: isDark ? const Color(0xFFf5f5f5) : const Color(0xFF24292e),
          fontFamily: 'IBMPlexSans',
        ),
        labelSmall: TextStyle(
          fontSize: 15,
          color: isDark ? AppColors.neutral2 : AppColors.neutral4,
          fontFamily: 'IBMPlexSans',
          fontWeight: FontWeight.w700,
          letterSpacing: 0.25,
        ),
      ),
    );

    // Return theme data that MaterialApp can use.
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

  /// Shift a color accounting for light / dark theme.
  Color shift(bool isDark, Color c, double d) =>
      ColorUtils.shiftHsl(c, d * (isDark ? -1 : 1));

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

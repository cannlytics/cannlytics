// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 2/17/2023
// Updated: 3/24/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Flutter imports:
import 'package:flutter/material.dart';

import 'colors.dart';

/// Colors used in the app for theming.
class AppTheme {
  /// Convert the colors to theme data.
  static ThemeData toThemeData({bool isDark = false}) {
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

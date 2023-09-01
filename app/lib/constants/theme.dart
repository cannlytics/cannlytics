// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 2/17/2023
// Updated: 9/1/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Flutter imports:
import 'package:flutter/material.dart';

// Package imports:
import 'package:flutter_riverpod/flutter_riverpod.dart';

// Project imports:
import 'colors.dart';

/// An instance of the theme provider.
final themeModeProvider = StateProvider<ThemeMode>((ref) {
  // Set the initial theme mode based on the time of day.
  final now = TimeOfDay.now();
  final isDaytime = now.hour >= 8 && now.hour < 20;
  return isDaytime ? ThemeMode.light : ThemeMode.dark;
});

/// Colors used in the app for theming.
class AppTheme {
  /// Convert the colors to theme data.
  static ThemeData toThemeData({bool isDark = false}) {
    ThemeData themeMode = isDark ? ThemeData.dark() : ThemeData.light();
    TextTheme textTheme = themeMode.textTheme;
    ColorScheme colorScheme = ColorScheme(
      brightness: isDark ? Brightness.dark : Brightness.light,
      primary: isDark ? DarkColors.primaryColors : LightColors.primaryColors,
      primaryContainer:
          isDark ? DarkColors.primaryColors : LightColors.primaryColors,
      secondary: isDark ? DarkColors.primaryColors : LightColors.primaryColors,
      secondaryContainer:
          isDark ? DarkColors.primaryColors : LightColors.primaryColors,
      background: isDark ? DarkColors.mantle : LightColors.mantle,
      surface: isDark ? const Color(0xFF323443) : Colors.white,
      onBackground: isDark ? DarkColors.surface0 : LightColors.crust,
      onSurface: isDark ? DarkColors.surface0 : LightColors.mantle,
      onError: Colors.white,
      onPrimary: Colors.white,
      onSecondary: Colors.white,
      error: isDark ? DarkColors.darkOrange : LightColors.darkOrange,
    );

    // Create the ThemeData with the ColorScheme and TextTheme.
    // Note: Also adds extra properties that `ColorScheme` seems to miss.
    // See: https://medium.com/@omlondhe/themedata-in-flutter-f6a67d9c636d
    var t = ThemeData.from(
      textTheme: textTheme,
      colorScheme: colorScheme,
    ).copyWith(
      // General theme settings.
      materialTapTargetSize: MaterialTapTargetSize.shrinkWrap,
      useMaterial3: true,
      visualDensity: VisualDensity.compact,

      // Color scheme.
      highlightColor:
          isDark ? DarkColors.primaryColors : LightColors.primaryColors,
      scaffoldBackgroundColor: isDark ? const Color(0xFF323443) : Colors.white,
      dividerColor: isDark ? DarkColors.surface2 : LightColors.surface2,
      canvasColor: isDark
          ? const Color(0xFF323443)
          : isDark
              ? DarkColors.mantle
              : LightColors.mantle,

      // App bar theme.
      appBarTheme: const AppBarTheme(
        elevation: 0.0,
        centerTitle: true,
      ),

      // Button theme.
      buttonTheme: ButtonThemeData(
        buttonColor: isDark ? DarkColors.green : LightColors.green,
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
                ? DarkColors.surface0
                : LightColors.surface0,
      ),

      // Data table style.
      dataTableTheme: DataTableThemeData(
        dataRowColor: MaterialStateProperty.resolveWith<Color?>(
            (Set<MaterialState> states) {
          if (states.contains(MaterialState.hovered)) {
            return isDark ? DarkColors.mantle : LightColors.mantle;
          }
          return Colors.transparent;
        }),
      ),

      // Dialog style.
      dialogBackgroundColor: isDark ? DarkColors.mantle : LightColors.mantle,
      dialogTheme: DialogTheme(
        elevation: 5,
        backgroundColor: isDark ? DarkColors.base : LightColors.base,
        surfaceTintColor: isDark ? DarkColors.base : LightColors.base,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(3),
        ),
      ),

      // Input style.
      inputDecorationTheme: InputDecorationTheme(
        labelStyle: TextStyle(
          fontFamily: 'SourceSerifPro',
        ),
        floatingLabelBehavior: FloatingLabelBehavior.never,
        floatingLabelStyle: TextStyle(
          color: isDark ? DarkColors.subtext0 : LightColors.subtext0,
          fontFamily: 'SourceSerifPro',
        ),
        helperStyle: TextStyle(
          color: isDark ? DarkColors.subtext0 : LightColors.subtext0,
          fontFamily: 'SourceSerifPro',
        ),
        hintStyle: TextStyle(
          fontFamily: 'SourceSerifPro',
        ),
        errorStyle: TextStyle(
          color: isDark ? DarkColors.darkOrange : LightColors.darkOrange,
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
        cursorColor: isDark ? DarkColors.surface0 : LightColors.text,
      ),

      // Text style.
      textTheme: TextTheme(
        displayLarge: TextStyle(
          color: isDark ? DarkColors.text : LightColors.text,
          fontFamily: 'LibreBaskerville',
          fontSize: 48,
          letterSpacing: 1.5,
        ),
        displayMedium: TextStyle(
          color: isDark ? DarkColors.text : LightColors.text,
          fontFamily: 'LibreBaskerville',
          fontSize: 36,
          letterSpacing: 1.2,
        ),
        displaySmall: TextStyle(
          color: isDark ? DarkColors.text : LightColors.text,
          fontFamily: 'LibreBaskerville',
          fontSize: 28,
        ),
        headlineLarge: TextStyle(
          color: isDark ? DarkColors.text : LightColors.text,
          fontFamily: 'SourceSerifPro',
          fontSize: 24,
        ),
        headlineMedium: TextStyle(
          color: isDark ? DarkColors.text : LightColors.text,
          fontFamily: 'SourceSerifPro',
          fontSize: 21,
        ),
        headlineSmall: TextStyle(
          color: isDark ? DarkColors.text : LightColors.text,
          fontFamily: 'SourceSerifPro',
          fontSize: 18,
        ),
        titleLarge: TextStyle(
          color: isDark ? DarkColors.darkText : LightColors.darkText,
          fontFamily: 'LibreBaskerville',
          fontSize: 21,
        ),
        titleMedium: TextStyle(
          color: isDark ? DarkColors.text : LightColors.text,
          fontFamily: 'SourceSerifPro',
          fontSize: 17,
          height: 1.33,
        ),
        titleSmall: TextStyle(
          color: isDark ? DarkColors.text : LightColors.text,
          fontFamily: 'SourceSerifPro',
          fontSize: 16,
        ),
        bodyLarge: TextStyle(
          color: isDark ? DarkColors.text : LightColors.text,
          fontFamily: 'SourceSerifPro',
          fontSize: 18,
          height: 1.5,
        ),
        bodyMedium: TextStyle(
          color: isDark ? DarkColors.text : LightColors.text,
          fontFamily: 'SourceSerifPro',
          fontSize: 16,
          height: 1.5,
        ),
        bodySmall: TextStyle(
          color: isDark ? DarkColors.text : LightColors.text,
          fontFamily: 'SourceSerifPro',
          fontSize: 14,
          height: 1.5,
        ),
        labelLarge: TextStyle(
          fontSize: 18,
          color: isDark ? DarkColors.text : LightColors.text,
          fontFamily: 'LibreBaskerville',
        ),
        labelMedium: TextStyle(
          fontSize: 16,
          color: isDark ? DarkColors.text : LightColors.text,
          fontFamily: 'SourceSerifPro',
        ),
        labelSmall: TextStyle(
          fontSize: 15,
          color: isDark ? DarkColors.text : LightColors.text,
          fontFamily: 'SourceSerifPro',
          fontWeight: FontWeight.w700,
          letterSpacing: 0.25,
        ),
      ),
    );

    // Return theme data that MaterialApp can use.
    return t;
  }
}

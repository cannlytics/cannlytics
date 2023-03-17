// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 2/17/2023
// Updated: 3/16/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Flutter imports:
import 'package:flutter/material.dart';

// Package imports:
import 'package:flutter_riverpod/flutter_riverpod.dart';

/// An instance of the theme provider.
final themeModeProvider = StateProvider<ThemeMode>((ref) {
  // Get the current time of day.
  final now = TimeOfDay.now();

  // Determine whether it is daytime (between 8am and 8pm).
  final isDaytime = now.hour >= 8 && now.hour < 20;

  // Set the theme mode based on the time of day.
  return isDaytime ? ThemeMode.light : ThemeMode.dark;
});

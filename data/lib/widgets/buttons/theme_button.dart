// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 2/18/2023
// Updated: 4/9/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Flutter imports:
import 'package:flutter/material.dart';

// Package imports:
import 'package:flutter_riverpod/flutter_riverpod.dart';

// Project imports:
import 'package:cannlytics_data/constants/colors.dart';
import 'package:cannlytics_data/constants/theme.dart';

/// Light / dark theme toggle.
class ThemeToggle extends StatelessWidget {
  const ThemeToggle({
    super.key,
    this.isDark = false,
  });
  final bool isDark;

  @override
  Widget build(BuildContext context) {
    return Consumer(builder: (context, ref, child) {
      final theme = ref.watch(themeModeProvider);
      return Row(
        mainAxisAlignment: MainAxisAlignment.end,
        children: [
          Padding(
            padding: const EdgeInsets.only(top: 6, right: 24, bottom: 6),
            child: IconButton(
              splashRadius: 18,
              onPressed: () {
                // Toggle light / dark theme.
                ref.read(themeModeProvider.notifier).state =
                    theme == ThemeMode.light ? ThemeMode.dark : ThemeMode.light;
              },
              icon: Icon(
                theme == ThemeMode.dark ? Icons.dark_mode : Icons.light_mode,
                color: isDark ? DarkColors.subtext0 : LightColors.subtext0,
              ),
            ),
          ),
        ],
      );
    });
  }
}

// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 2/18/2023
// Updated: 3/6/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Flutter imports:
import 'package:flutter/material.dart';

// Project imports:
import 'package:cannlytics_app/constants/theme.dart';

/// Secondary button based on [TextButton].
/// [isDark] - Whether or not the theme is dark.
/// [text] - Text displayed  on the button.
/// [isLoading] - Whether or not to show a loading indicator.
/// [onPressed] - Callback to be called when the button is pressed.
class SecondaryButton extends StatelessWidget {
  const SecondaryButton({
    super.key,
    required this.text,
    this.isDark = false,
    this.isLoading = false,
    this.onPressed,
  });

  // Properties.
  final bool isDark;
  final String text;
  final bool isLoading;
  final VoidCallback? onPressed;

  @override
  Widget build(BuildContext context) {
    return TextButton(
      onPressed: onPressed,
      style: TextButton.styleFrom(
        backgroundColor: isDark ? AppColors.neutral4 : Colors.grey[200],
        padding: EdgeInsets.symmetric(horizontal: 16, vertical: 8),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(3),
        ),
      ),
      child: isLoading
          ? const SizedBox(
              width: 16,
              height: 16,
              child: CircularProgressIndicator(strokeWidth: 1.42),
            )
          : Text(
              text,
              style: Theme.of(context).textTheme.titleMedium!.copyWith(
                    color: isDark ? AppColors.neutral2 : AppColors.neutral5,
                  ),
            ),
    );
  }
}

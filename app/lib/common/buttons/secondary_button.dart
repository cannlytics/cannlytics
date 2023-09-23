// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 2/18/2023
// Updated: 3/26/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Flutter imports:
import 'package:flutter/material.dart';

// Project imports:
import 'package:cannlytics_data/constants/design.dart';

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
    this.leading,
    this.disabled = false,
  });

  // Properties.
  final bool isDark;
  final String text;
  final bool isLoading;
  final VoidCallback? onPressed;
  final Widget? leading;
  final bool disabled;

  @override
  Widget build(BuildContext context) {
    return TextButton(
      onPressed: disabled ? null : onPressed,
      style: TextButton.styleFrom(
        backgroundColor: Colors.transparent,
        padding: EdgeInsets.symmetric(horizontal: 16, vertical: 8),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(3),
          side: BorderSide(
            color: isDark
                ? Theme.of(context).textTheme.titleMedium!.color!
                : Color(0x1b1f2326),
            width: 1,
          ),
        ),
      ),
      child: isLoading
          ? const SizedBox(
              width: 16,
              height: 16,
              child: CircularProgressIndicator(strokeWidth: 1.42),
            )
          : (leading != null)
              ? Row(
                  crossAxisAlignment: CrossAxisAlignment.center,
                  children: [
                    leading!,
                    gapW8,
                    Text(
                      text,
                      style: Theme.of(context).textTheme.titleMedium,
                    ),
                  ],
                )
              : Text(
                  text,
                  style: Theme.of(context).textTheme.titleMedium,
                ),
    );
  }
}

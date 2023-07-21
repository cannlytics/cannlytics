// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 2/18/2023
// Updated: 3/11/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Flutter imports:
import 'package:flutter/material.dart';

/// Primary button based on [ElevatedButton].
/// [text] - Text displayed  on the button.
/// [isLoading] - Whether or not to show a loading indicator.
/// [onPressed] - Callback to be called when the button is pressed.
/// [backgroundColor] - Optional color to use for the button color.
class PrimaryButton extends StatelessWidget {
  const PrimaryButton({
    super.key,
    required this.text,
    this.isLoading = false,
    this.inline = false,
    this.onPressed,
    this.backgroundColor,
  });

  // Properties.
  final String text;
  final bool isLoading;
  final VoidCallback? onPressed;
  final Color? backgroundColor;
  final bool? inline;

  @override
  Widget build(BuildContext context) {
    return ElevatedButton(
      style: ElevatedButton.styleFrom(
        backgroundColor:
            (backgroundColor == null) ? Colors.green : backgroundColor,
        padding: EdgeInsets.symmetric(horizontal: 16, vertical: 8),
        shape: RoundedRectangleBorder(
          borderRadius: (inline ?? false)
              ? BorderRadius.only(
                  topLeft: Radius.zero,
                  bottomLeft: Radius.zero,
                  topRight: Radius.circular(3),
                  bottomRight: Radius.circular(3),
                )
              : BorderRadius.circular(3),
        ),
      ),
      onPressed: onPressed,
      child: isLoading
          ? const SizedBox(
              width: 16,
              height: 16,
              child: CircularProgressIndicator(strokeWidth: 1.42),
            )
          : Text(
              text,
              textAlign: TextAlign.center,
              style: Theme.of(context).textTheme.titleMedium!.copyWith(
                    color: Colors.white,
                  ),
            ),
    );
  }
}

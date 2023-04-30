// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 2/18/2023
// Updated: 3/9/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Flutter imports:
import 'package:flutter/material.dart';

/// Custom text button with a fixed height.
class CustomTextButton extends StatelessWidget {
  CustomTextButton({
    super.key,
    required this.text,
    this.onPressed,
    this.fontStyle,
  });
  final String text;
  final VoidCallback? onPressed;
  final FontStyle? fontStyle;

  @override
  Widget build(BuildContext context) {
    // Render the button.
    return TextButton(
      onPressed: onPressed,
      child: Text(
        text,
        textAlign: TextAlign.center,
        style: Theme.of(context).textTheme.titleMedium!.copyWith(
              color: Theme.of(context).textTheme.titleLarge!.color,
              fontStyle: fontStyle,
            ),
      ),
    );
  }
}

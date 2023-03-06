// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 2/18/2023
// Updated: 2/22/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Flutter imports:
import 'package:flutter/material.dart';

// Project imports:
import 'package:cannlytics_app/constants/design.dart';

/// Custom text button with a fixed height.
class CustomTextButton extends StatelessWidget {
  CustomTextButton({
    super.key,
    required this.text,
    this.onPressed,
  });
  final String text;
  final VoidCallback? onPressed;

  @override
  Widget build(BuildContext context) {
    // Render the button.
    return TextButton(
      onPressed: onPressed,
      child: Text(
        text,
        style: Theme.of(context).textTheme.labelSmall!.copyWith(
              color: Theme.of(context).textTheme.labelLarge!.color,
            ),
        textAlign: TextAlign.center,
      ),
    );
  }
}

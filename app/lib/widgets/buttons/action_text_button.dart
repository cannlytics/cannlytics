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
import 'package:cannlytics_app/constants/theme.dart';

/// Text button to be used as an [AppBar] action.
class ActionTextButton extends StatelessWidget {
  const ActionTextButton({
    super.key,
    required this.text,
    this.onPressed,
  });
  final String text;
  final VoidCallback? onPressed;
  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(
        horizontal: Sizes.p16,
      ),
      child: TextButton(
        onPressed: onPressed,
        child: Text(text, style: Theme.of(context).textTheme.titleMedium!),
      ),
    );
  }
}

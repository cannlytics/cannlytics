// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 3/23/2023
// Updated: 3/23/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Flutter imports:
import 'package:flutter/material.dart';

/// A full-width card.
class WideCard extends StatelessWidget {
  final Widget child;
  final Color? color;
  final Color? surfaceTintColor;

  const WideCard({
    required this.child,
    this.color,
    this.surfaceTintColor,
  });

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: double.infinity,
      child: Card(
        color: color,
        surfaceTintColor: surfaceTintColor,
        margin: EdgeInsets.symmetric(vertical: 16),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(3),
        ),
        child: Padding(
          padding: EdgeInsets.symmetric(
            vertical: 21,
            horizontal: 16,
          ),
          child: child,
        ),
      ),
    );
  }
}

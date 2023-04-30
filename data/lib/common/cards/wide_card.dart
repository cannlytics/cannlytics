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

  const WideCard({required this.child});

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: double.infinity,
      child: Card(
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

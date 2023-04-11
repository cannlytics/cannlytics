// Cannlytics Data
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 3/12/2023
// Updated: 4/9/2023

// Flutter imports:
import 'package:flutter/material.dart';

// Project imports:
import 'package:cannlytics_data/constants/design.dart';

/// A container for forms.
class FormContainer extends StatelessWidget {
  const FormContainer({required this.children});
  final List<Widget> children;

  @override
  Widget build(BuildContext context) {
    final screenWidth = MediaQuery.of(context).size.width;
    return Container(
      padding: const EdgeInsets.all(16.0),
      margin: EdgeInsets.only(top: Insets(1).md),
      child: Center(
        child: SizedBox(
          width: Breakpoints.desktop.toDouble(),
          child: Padding(
            padding: EdgeInsets.symmetric(
              horizontal: horizontalPadding(screenWidth),
            ),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: children,
            ),
          ),
        ),
      ),
    );
  }
}

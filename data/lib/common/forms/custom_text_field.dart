// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 3/6/2023
// Updated: 3/6/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Flutter imports:
import 'package:cannlytics_data/constants/colors.dart';
import 'package:cannlytics_data/constants/design.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

/// A custom text field.
class CustomTextField extends StatelessWidget {
  final TextEditingController controller;
  final String label;
  final bool isNumeric;

  CustomTextField({
    required this.controller,
    required this.label,
    this.isNumeric = false,
  });

  @override
  Widget build(BuildContext context) {
    bool isDark = Theme.of(context).brightness == Brightness.dark;
    final screenWidth = MediaQuery.of(context).size.width;
    return Row(
      children: [
        Container(
          width: (screenWidth < Breakpoints.tablet)
              ? MediaQuery.of(context).size.width * 0.25
              : MediaQuery.of(context).size.width * 0.125,
          padding: EdgeInsets.only(left: 16, bottom: 8),
          child: SelectableText(
            label,
            style: Theme.of(context).textTheme.bodySmall,
          ),
        ),
        Container(
          width: isNumeric
              ? (screenWidth < Breakpoints.tablet)
                  ? MediaQuery.of(context).size.width * 0.25
                  : MediaQuery.of(context).size.width * 0.15
              : (screenWidth < Breakpoints.tablet)
                  ? MediaQuery.of(context).size.width * 0.7
                  : MediaQuery.of(context).size.width * 0.5,
          padding: EdgeInsets.only(left: 8, right: 8, bottom: 8),
          child: TextFormField(
            controller: controller,
            style: Theme.of(context).textTheme.bodySmall,
            keyboardType: isNumeric ? TextInputType.number : TextInputType.text,
            inputFormatters: isNumeric
                ? <TextInputFormatter>[FilteringTextInputFormatter.digitsOnly]
                : <TextInputFormatter>[],
            decoration: InputDecoration(
              isDense: true,
              contentPadding: EdgeInsets.only(
                top: 12,
                left: 4,
                right: 4,
                bottom: 4,
              ),
              filled: true,
              labelStyle: TextStyle(
                color: Theme.of(context).textTheme.bodyMedium!.color,
                fontSize: 16,
                fontWeight: FontWeight.w500,
              ),
              focusedBorder: OutlineInputBorder(
                borderSide: BorderSide(
                  color:
                      isDark ? DarkColors.accentGreen : LightColors.lightGreen,
                  width: 2.0,
                ),
              ),
              enabledBorder: OutlineInputBorder(
                borderSide: BorderSide(
                  color: Theme.of(context).dividerColor,
                  width: 1.0,
                ),
              ),
            ),
          ),
        ),
      ],
    );
  }
}

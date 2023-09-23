// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 3/6/2023
// Updated: 6/29/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Dart imports:
import 'dart:math';

// Flutter imports:
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

// Project imports:
import 'package:cannlytics_data/constants/colors.dart';
import 'package:cannlytics_data/constants/design.dart';

/// A custom text field.
class CustomTextField extends StatelessWidget {
  CustomTextField({
    required this.label,
    this.controller,
    this.isNumeric = false,
    this.value,
    this.onChanged,
    this.maxWidth,
    this.maxLabelWidth,
    this.disabled = false,
    this.maxLines = 1,
  });

  // Parameters.
  final TextEditingController? controller;
  final String label;
  final bool isNumeric;
  final dynamic value;
  final void Function(String)? onChanged;
  final double? maxWidth;
  final double? maxLabelWidth;
  final bool disabled;
  final int? maxLines;

  @override
  Widget build(BuildContext context) {
    bool isDark = Theme.of(context).brightness == Brightness.dark;
    final screenWidth = MediaQuery.of(context).size.width;
    return Row(
      children: [
        Container(
          width: min(
            (screenWidth < Breakpoints.tablet)
                ? MediaQuery.of(context).size.width * 0.25
                : MediaQuery.of(context).size.width * 0.125,
            maxLabelWidth ?? double.infinity,
          ),
          padding: EdgeInsets.only(left: 16, bottom: 8),
          child: SelectableText(
            label,
            style: Theme.of(context).textTheme.bodySmall,
          ),
        ),
        Container(
          // Width. Use the minimum of the calculated width and maxWidth.
          width: min(
            isNumeric
                ? (screenWidth < Breakpoints.tablet)
                    ? MediaQuery.of(context).size.width * 0.25
                    : MediaQuery.of(context).size.width * 0.15
                : (screenWidth < Breakpoints.tablet)
                    ? MediaQuery.of(context).size.width * 0.7
                    : MediaQuery.of(context).size.width * 0.5,
            maxWidth ?? double.infinity,
          ),

          // Padding.
          padding: EdgeInsets.only(left: 8, right: 8, bottom: 8),

          // Text field.
          child: TextFormField(
            // Controller.
            controller: controller,
            initialValue: value?.toString() ?? '',
            enabled: !disabled,

            // Allow multiple lines
            maxLines: maxLines,

            // Validation.
            keyboardType: isNumeric ? TextInputType.number : TextInputType.text,
            inputFormatters: isNumeric
                ? <TextInputFormatter>[
                    FilteringTextInputFormatter.allow(RegExp(r'^\d*\.?\d*'))
                  ]
                : <TextInputFormatter>[],

            // On change.
            onChanged: onChanged,

            // Style.
            style: Theme.of(context).textTheme.bodySmall,
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

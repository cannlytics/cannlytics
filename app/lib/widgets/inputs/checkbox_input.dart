// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 3/12/2023
// Updated: 3/12/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Flutter imports:
import 'package:flutter/material.dart';

/// Checkbox field.
class CheckboxField extends StatelessWidget {
  final String? title;
  final bool? value;
  final Function(bool?)? onChanged;

  const CheckboxField({
    Key? key,
    this.title,
    this.value,
    this.onChanged,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        Checkbox(
          value: value,
          onChanged: onChanged,
        ),
        Text(
          title ?? '',
          style: Theme.of(context).textTheme.titleMedium!.copyWith(
                color: Theme.of(context).textTheme.titleLarge!.color,
              ),
        ),
      ],
    );
  }
}

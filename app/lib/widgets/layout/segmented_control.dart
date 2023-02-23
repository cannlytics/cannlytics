// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 2/18/2023
// Updated: 2/18/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>
import 'package:flutter/cupertino.dart';

class SegmentedControl<T extends Object> extends StatelessWidget {
  const SegmentedControl({
    super.key,
    required this.header,
    required this.value,
    required this.children,
    required this.onValueChanged,
  });
  final Widget header;
  final T value;
  final Map<T, Widget> children;
  final ValueChanged<T> onValueChanged;

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: <Widget>[
        Padding(
          padding: const EdgeInsets.symmetric(horizontal: 16.0, vertical: 8.0),
          child: header,
        ),
        SizedBox(
          width: double.infinity,
          child: CupertinoSegmentedControl<T>(
            children: children,
            groupValue: value,
            onValueChanged: onValueChanged,
          ),
        ),
      ],
    );
  }
}

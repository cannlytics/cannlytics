// Cannlytics Data
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 3/22/2023
// Updated: 3/22/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Flutter imports:
import 'package:flutter/material.dart';

class MainScreen extends StatelessWidget {
  final List<Widget> slivers;

  const MainScreen({Key? key, required this.slivers}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    bool isDark = Theme.of(context).brightness == Brightness.dark;
    return Scaffold(
      body: Container(
        // Background gradient.
        decoration: BoxDecoration(
          gradient: RadialGradient(
            center: Alignment(1, -1),
            radius: 4.0,
            colors: [
              isDark ? Colors.transparent : Colors.white,
              isDark ? Color(0xFF4E5165) : Color(0xFFe8e8e8),
            ],
          ),
        ),
        child: CustomScrollView(slivers: slivers),
      ),
    );
  }
}

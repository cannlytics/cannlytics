// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 6/27/2023
// Updated: 6/30/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Flutter imports:
import 'package:flutter/material.dart';

/// A pill-shaped tab button.
class PillTabButton extends StatelessWidget {
  final String text;
  final IconData icon;
  final bool isSelected;

  PillTabButton({
    required this.text,
    required this.icon,
    this.isSelected = false,
  });

  @override
  Widget build(BuildContext context) {
    // Whether or not the tab is hovered.
    ValueNotifier<bool> isHovered = ValueNotifier(false);

    // Selected colors.
    // Color lightScreenGold = Color(0xFFFFBF5F);
    Color lightScreenGold = Theme.of(context).colorScheme.secondary;
    Color darkScreenGold = Color(0xFFFFD700);
    Color goldColor = Theme.of(context).brightness == Brightness.light
        ? lightScreenGold
        : darkScreenGold;

    // Render.
    return MouseRegion(
      onEnter: (_) => isHovered.value = true,
      onExit: (_) => isHovered.value = false,
      child: ValueListenableBuilder<bool>(
        valueListenable: isHovered,
        builder: (context, value, child) {
          return InkWell(
            borderRadius: BorderRadius.circular(30),
            splashColor: Colors.blue.withOpacity(0.5),
            hoverColor: Colors.blue.withOpacity(0.2),
            child: Container(
              padding: EdgeInsets.symmetric(horizontal: 12, vertical: 6),
              decoration: BoxDecoration(
                borderRadius: BorderRadius.circular(30),
                color: isSelected
                    ? Colors.blue.withOpacity(0.1)
                    : (value
                        ? Colors.blue.withOpacity(0.05)
                        : Colors.transparent),
              ),
              child: Row(
                children: [
                  // Icon.
                  Icon(
                    icon,
                    size: 16,
                    color: isSelected
                        ? goldColor
                        : Theme.of(context).textTheme.bodyMedium?.color,
                  ),
                  SizedBox(width: 8),

                  // Text.
                  Text(text),
                ],
              ),
            ),
          );
        },
      ),
    );
  }
}

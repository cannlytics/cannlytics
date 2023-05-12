// Cannlytics Data
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 4/15/2023
// Updated: 4/16/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Flutter imports:
import 'package:flutter/material.dart';

/// Breadcrumbs.
class Breadcrumbs extends StatelessWidget {
  final List<BreadcrumbItem> items;

  const Breadcrumbs({
    Key? key,
    required this.items,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Wrap(
      spacing: 4,
      children: List.generate(
        items.length,
        (index) {
          final item = items[index];
          final isLast = index == items.length - 1;

          return Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              InkWell(
                // Breadcrumb links.
                onTap: isLast ? null : item.onTap,

                // Breadcrumb text.
                child: Text(
                  item.title,
                  style: Theme.of(context).textTheme.labelLarge!.copyWith(
                      color: Theme.of(context).textTheme.titleLarge!.color),
                ),
              ),

              // Caret icon.
              if (!isLast)
                Icon(
                  Icons.chevron_right,
                  size: 16,
                  color: Theme.of(context).textTheme.labelSmall!.color,
                ),
            ],
          );
        },
      ),
    );
  }
}

/// A breadcrumb item.
class BreadcrumbItem {
  final String title;
  final VoidCallback? onTap;

  BreadcrumbItem({
    required this.title,
    this.onTap,
  });
}

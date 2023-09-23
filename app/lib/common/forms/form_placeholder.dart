// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 3/6/2023
// Updated: 3/6/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Flutter imports:
import 'package:flutter/material.dart';

// Project imports:
import 'package:cannlytics_data/constants/design.dart';

/// A custom placeholder.
class FormPlaceholder extends StatelessWidget {
  const FormPlaceholder({
    Key? key,
    required this.image,
    required this.title,
    required this.description,
    required this.onTap,
    this.isDark = false,
  }) : super(key: key);

  final String image;
  final String title;
  final String description;
  final Function()? onTap;
  final bool isDark;

  @override
  Widget build(BuildContext context) {
    return Card(
      // surfaceTintColor: isDark ? null : AppColors.surface,
      margin: EdgeInsets.symmetric(vertical: 12),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(3),
      ),
      child: InkWell(
        onTap: onTap,
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            gapH16,
            Image.asset(
              image,
              height: 100,
              fit: BoxFit.fitHeight,
            ),
            Padding(
              padding: const EdgeInsets.all(16.0),
              child: Column(
                mainAxisSize: MainAxisSize.min,
                crossAxisAlignment: CrossAxisAlignment.center,
                children: [
                  Text(
                    title,
                    style: Theme.of(context).textTheme.titleLarge,
                  ),
                  gapH6,
                  Text(
                    description,
                    style: Theme.of(context).textTheme.titleMedium,
                  ),
                  gapH12,
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}

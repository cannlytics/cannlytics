// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 3/6/2023
// Updated: 3/6/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

import 'package:cannlytics_app/constants/design.dart';
import 'package:flutter/material.dart';

/// A custom placeholder.
class CustomPlaceholder extends StatelessWidget {
  const CustomPlaceholder({
    Key? key,
    required this.image,
    required this.title,
    required this.description,
    required this.onTap,
  }) : super(key: key);

  final String image;
  final String title;
  final String description;
  final Function()? onTap;

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: EdgeInsets.symmetric(vertical: 16),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(3),
      ),
      child: InkWell(
        onTap: onTap,
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
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
                    style: Theme.of(context).textTheme.bodyLarge,
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

// Cannlytics Data
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 4/16/2023
// Updated: 4/16/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

import 'package:cannlytics_data/constants/design.dart';
import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

class StatisticalModelCard extends StatelessWidget {
  final String modelDescription;
  final String imageUrl;
  final String route;

  StatisticalModelCard({
    required this.modelDescription,
    required this.imageUrl,
    required this.route,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(3),
      ),
      child: InkWell(
        borderRadius: BorderRadius.circular(3),
        splashColor: Theme.of(context).primaryColor.withOpacity(0.2),
        onTap: () => context.goNamed(route),
        child: Padding(
          padding: EdgeInsets.all(Defaults.defaultPadding),
          child: Column(
            children: [
              Image.network(
                imageUrl,
                height: 120,
              ),
              Text(modelDescription),
            ],
          ),
        ),
      ),
    );
  }
}

// Cannlytics Data
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 4/16/2023
// Updated: 5/8/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Flutter imports:
import 'package:flutter/material.dart';

// Package imports:
import 'package:go_router/go_router.dart';

// Project imports:
import 'package:cannlytics_data/constants/design.dart';

/// A card used to display information about a statistical model.
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

/// A card used to display information about a dataset.
class DatasetCard extends StatelessWidget {
  final String imageUrl;
  final String title;
  final String description;
  final String tier;
  final String? rows;
  final String? columns;
  final void Function()? onTap;

  DatasetCard({
    required this.imageUrl,
    required this.title,
    required this.description,
    required this.tier,
    this.rows,
    this.columns,
    this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: EdgeInsets.zero,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(3)),
      elevation: 2,
      child: InkWell(
        // Action.
        onTap: onTap,

        // Border.
        child: Padding(
          padding: EdgeInsets.all(8),
          child: Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Image.
              Padding(
                padding: EdgeInsets.only(top: 16),
                child: ClipRRect(
                  borderRadius: BorderRadius.circular(8),
                  child: Image.network(
                    imageUrl,
                    width: 64,
                    height: 64,
                  ),
                ),
              ),

              // Body.
              gapW16,
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    // Title.
                    gapH8,
                    Text(
                      title,
                      style: Theme.of(context).textTheme.titleLarge,
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                    ),

                    // Description.
                    Text(
                      description,
                      style: Theme.of(context).textTheme.bodyMedium,
                      maxLines: 2,
                      overflow: TextOverflow.ellipsis,
                    ),

                    // Row of information.
                    gapH6,
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        buildInfoItem(Icons.workspace_premium, tier),
                        if (rows != null)
                          buildInfoItem(Icons.list_sharp, rows!),
                        if (columns != null)
                          buildInfoItem(Icons.table_chart_outlined, columns!),
                        gapW4,
                      ],
                    ),
                    gapH2,
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  /// Builds a single cell in the row of information.
  Widget buildInfoItem(IconData icon, String text) {
    return Row(
      children: [
        Icon(icon, size: 20),
        SizedBox(width: 4),
        Text(
          text,
          maxLines: 1,
          overflow: TextOverflow.ellipsis,
        ),
      ],
    );
  }
}

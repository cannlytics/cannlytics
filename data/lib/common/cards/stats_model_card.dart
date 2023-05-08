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

class CustomCard extends StatelessWidget {
  final String imageUrl;
  final String title;
  final String description;
  final String category;
  final String instances;
  final String attributes;

  CustomCard({
    required this.imageUrl,
    required this.title,
    required this.description,
    required this.category,
    required this.instances,
    required this.attributes,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
      elevation: 2,
      child: InkWell(
        onTap: () {}, // Add your onTap event or navigation here
        child: Padding(
          padding: EdgeInsets.all(8),
          child: Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              ClipRRect(
                borderRadius: BorderRadius.circular(8),
                child: Image.network(
                  imageUrl,
                  width: 48,
                  height: 48,
                ),
              ),
              SizedBox(width: 8),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      title,
                      style:
                          TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                    ),
                    Text(
                      description,
                      maxLines: 2,
                      overflow: TextOverflow.ellipsis,
                    ),
                    SizedBox(height: 8),
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        buildInfoItem(Icons.search, category),
                        buildInfoItem(
                            Icons.insert_drive_file_outlined, instances),
                        buildInfoItem(Icons.apps, attributes),
                      ],
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

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

// Cannlytics Data
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 2/18/2023
// Updated: 5/24/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Flutter imports:
import 'package:cannlytics_data/common/buttons/primary_button.dart';
import 'package:cannlytics_data/constants/design.dart';
import 'package:cannlytics_data/ui/account/subscription_management.dart';
import 'package:cannlytics_data/ui/dashboard/dashboard_controller.dart';
import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

// Package imports:
import 'package:hooks_riverpod/hooks_riverpod.dart';

// Project imports:
import 'package:cannlytics_data/common/cards/sponsorship_card.dart';
import 'package:cannlytics_data/ui/layout/console.dart';
import 'package:cannlytics_data/ui/results/results_form.dart';

/// Dashboard screen.
class DashboardScreen extends ConsumerWidget {
  const DashboardScreen({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    // Dynamic width.
    final screenWidth = MediaQuery.of(context).size.width;

    // Calculate the aspect ratio of grid based on screen width
    final double crossAxisCount = screenWidth < 600
        ? 2
        : screenWidth < 1200
            ? 3
            : 4;
    final double childAspectRatio = screenWidth < 600
        ? 1
        : screenWidth < 1200
            ? 1.5
            : 2;

    // Render the widget.
    return ConsoleScreen(
      bottomSearch: true,
      children: [
        SliverFillRemaining(
          child: Padding(
            padding: const EdgeInsets.all(10),
            child: GridView.builder(
              shrinkWrap: true,
              physics: NeverScrollableScrollPhysics(),
              itemCount: aiModels.length,
              gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
                crossAxisCount: crossAxisCount.toInt(),
                childAspectRatio: childAspectRatio,
              ),
              itemBuilder: (context, index) {
                return Card(
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(3),
                  ),
                  child: InkWell(
                    borderRadius: BorderRadius.circular(3),
                    onTap: () {
                      context.go(aiModels[index]['path']);
                    },
                    child: Padding(
                      padding: const EdgeInsets.all(8.0),
                      child: Column(
                        children: [
                          Image.network(
                            aiModels[index]['image_url'],
                            height: 68.8,
                          ),
                          Text(
                            aiModels[index]['title'],
                            style: TextStyle(fontWeight: FontWeight.bold),
                          ),
                          Text(aiModels[index]['description']),
                        ],
                      ),
                    ),
                  ),
                );
              },
            ),
          ),
        ),
      ],
    );
  }
}

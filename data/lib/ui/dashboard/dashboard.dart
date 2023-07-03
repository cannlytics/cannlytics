// Cannlytics Data
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 2/18/2023
// Updated: 6/27/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Flutter imports:
import 'package:cannlytics_data/common/cards/sponsorship_card.dart';
import 'package:cannlytics_data/constants/design.dart';
import 'package:cannlytics_data/ui/dashboard/dashboard_controller.dart';
import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

// Package imports:
import 'package:hooks_riverpod/hooks_riverpod.dart';

// Project imports:
// import 'package:cannlytics_data/common/cards/sponsorship_card.dart';
import 'package:cannlytics_data/ui/layout/console.dart';

/// Dashboard screen.
class DashboardScreen extends ConsumerWidget {
  const DashboardScreen({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    // Dynamic width.
    final screenWidth = MediaQuery.of(context).size.width;

    // Calculate the aspect ratio of grid based on screen width
    final int crossAxisCount = screenWidth < 600
        ? 1
        : screenWidth < 1120
            ? 2
            : 3;
    final double childAspectRatio = screenWidth < 600
        ? 2.5
        : screenWidth < 1120
            ? 1.44
            : 1.66;

    // Listen to the data providers.
    final aiModels = ref.watch(aiModelsProvider).value ?? [];
    final mainDatasets = ref.watch(datasetsProvider).value ?? [];

    // Render the widget.
    return ConsoleScreen(
      children: [
        // AI cards.
        SliverToBoxAdapter(
          child: Padding(
            padding: EdgeInsets.only(left: 28, top: 24),
            child: Text('AI'),
          ),
        ),
        SliverToBoxAdapter(
          child: Padding(
            padding: const EdgeInsets.only(
              left: 24,
              right: 24,
              bottom: 16,
              top: 8,
            ),
            child: GridView.builder(
              shrinkWrap: true,
              physics: NeverScrollableScrollPhysics(),
              itemCount: aiModels.length,
              gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
                crossAxisCount: crossAxisCount,
                childAspectRatio: childAspectRatio,
              ),
              itemBuilder: (context, index) {
                return _card(context, aiModels[index]);
              },
            ),
          ),
        ),

        // Data cards.
        SliverToBoxAdapter(
          child: Padding(
            padding: EdgeInsets.only(left: 28, top: 24),
            child: Text('Data'),
          ),
        ),
        SliverToBoxAdapter(
          child: Padding(
            padding: const EdgeInsets.only(
              left: 24,
              right: 24,
              bottom: 16,
              top: 8,
            ),
            child: GridView.builder(
              shrinkWrap: true,
              physics: NeverScrollableScrollPhysics(),
              itemCount: mainDatasets.length,
              gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
                crossAxisCount: crossAxisCount.toInt(),
                childAspectRatio: childAspectRatio,
              ),
              itemBuilder: (context, index) {
                return _card(context, mainDatasets[index]);
              },
            ),
          ),
        ),

        // Sponsorship
        SliverToBoxAdapter(
          child: Padding(
            padding: EdgeInsets.only(left: 28, top: 24),
            child: Text('Sponsor'),
          ),
        ),
        SliverToBoxAdapter(
          child: Padding(
            padding: EdgeInsets.only(top: 12, left: 28, right: 28, bottom: 48),
            child: SponsorshipCard(),
          ),
        ),
      ],
    );
  }

  Widget _card(BuildContext context, item) {
    final screenWidth = MediaQuery.of(context).size.width;
    return Card(
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(3),
      ),
      child: InkWell(
        borderRadius: BorderRadius.circular(3),
        onTap: () {
          context.go(item['path']);
        },
        child: Padding(
          padding: const EdgeInsets.all(8.0),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Image.network(item['image_url'],
                  height: screenWidth < 600
                      ? 60
                      : screenWidth < 1120
                          ? 92
                          : 72),
              gapH8,
              Text(
                item['title'],
                style: Theme.of(context).textTheme.titleSmall!.copyWith(
                      color: Theme.of(context).textTheme.titleLarge!.color,
                    ),
              ),
              Text(
                item['description'],
                style: Theme.of(context).textTheme.bodySmall,
              ),
            ],
          ),
        ),
      ),
    );
  }
}

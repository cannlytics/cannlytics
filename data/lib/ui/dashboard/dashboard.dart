// Cannlytics Data
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 2/18/2023
// Updated: 5/9/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Flutter imports:
import 'package:flutter/material.dart';

// Package imports:
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:intl/intl.dart';

// Project imports:
import 'package:cannlytics_data/common/cards/card_grid.dart';
import 'package:cannlytics_data/common/cards/sponsorship_card.dart';
import 'package:cannlytics_data/common/cards/stats_model_card.dart';
import 'package:cannlytics_data/common/layout/console.dart';
import 'package:cannlytics_data/constants/design.dart';
import 'package:cannlytics_data/ui/dashboard/dashboard_controller.dart';

/// Dashboard screen.
class DashboardScreen extends ConsumerWidget {
  const DashboardScreen({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return ConsoleScreen(
      children: [
        // Optional: Welcome message
        // _welcomeMessage(context, screenWidth),

        // Dataset cards.
        _datasetsCards(context),

        // Future work: Statistical models cards.
        // _statsModelsCards(),

        // Call for contributions.
        SliverToBoxAdapter(
          child: Padding(
            padding: EdgeInsets.symmetric(
              vertical: 24,
              horizontal: Defaults.defaultPadding,
            ),
            child: Column(
              mainAxisAlignment: MainAxisAlignment.start,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text('Statistics',
                    style: Theme.of(context).textTheme.labelLarge!.copyWith(
                        color: Theme.of(context).textTheme.titleLarge!.color)),
                gapH8,
                SponsorshipCard(),
              ],
            ),
          ),
        ),
      ],
    );
  }

  /// Dataset cards.
  Widget _datasetsCards(BuildContext context) {
    final screenWidth = MediaQuery.of(context).size.width;
    var grid = CardGridView(
      crossAxisCount: screenWidth < Breakpoints.desktop ? 1 : 2,
      childAspectRatio: 3,
      items: mainDatasets.map((model) {
        return DatasetCard(
          imageUrl: model['image_url'],
          title: model['title'],
          description: model['description'],
          tier: model['tier'],
          rows: NumberFormat('#,###').format(model['observations']) + ' rows',
          columns: NumberFormat('#,###').format(model['fields']) + ' columns',
          onTap: () => context.push(model['path']),
        );
      }).toList(),
    );
    return SliverToBoxAdapter(
      child: Padding(
        padding: EdgeInsets.symmetric(
          vertical: 24,
          horizontal: Defaults.defaultPadding,
        ),
        child: Column(children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text('Data',
                  style: Theme.of(context).textTheme.labelLarge!.copyWith(
                      color: Theme.of(context).textTheme.titleLarge!.color)),
            ],
          ),
          gapH8,
          grid,
        ]),
      ),
    );
  }
}

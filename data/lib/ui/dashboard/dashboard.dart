// Cannlytics Data
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 2/18/2023
// Updated: 5/24/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Flutter imports:
import 'package:cannlytics_data/ui/results/results_form.dart';
import 'package:flutter/material.dart';

// Package imports:
import 'package:hooks_riverpod/hooks_riverpod.dart';

// Project imports:
import 'package:cannlytics_data/common/cards/sponsorship_card.dart';
import 'package:cannlytics_data/common/layout/console.dart';

/// Dashboard screen.
class DashboardScreen extends ConsumerWidget {
  const DashboardScreen({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return ConsoleScreen(
      bottomSearch: true,
      children: [
        // Quick search.
        SliverToBoxAdapter(child: LabResultsSearchForm()),

        // Call for contributions.
        _contributions(context),
      ],
    );
  }

  /// Call for contributions card.
  Widget _contributions(BuildContext context) {
    return SliverToBoxAdapter(
      child: Padding(
        padding: EdgeInsets.only(
          top: 64,
          left: 24,
          right: 24,
        ),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.start,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            SponsorshipCard(),
          ],
        ),
      ),
    );
  }
}

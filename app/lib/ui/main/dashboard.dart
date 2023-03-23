// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 2/18/2023
// Updated: 3/22/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Flutter imports:
import 'package:cannlytics_app/widgets/layout/main_screen.dart';
import 'package:flutter/material.dart';

// Package imports:
import 'package:flutter_layout_grid/flutter_layout_grid.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

// Project imports:
import 'package:cannlytics_app/constants/design.dart';
import 'package:cannlytics_app/routing/routes.dart';
import 'package:cannlytics_app/ui/layout/footer.dart';
import 'package:cannlytics_app/ui/layout/header.dart';
import 'package:cannlytics_app/ui/main/app_controller.dart';
import 'package:cannlytics_app/widgets/cards/border_card.dart';

/// Dashboard screen.
/// The initial screen the user sees after signing in.
class DashboardScreen extends ConsumerWidget {
  const DashboardScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    // Provider data and dynamic width.
    final userType = ref.watch(userTypeProvider);
    final screenWidth = MediaQuery.of(context).size.width;

    // Get the primary license.
    var currentFacility = ref.watch(primaryFacility);

    // Get the cards depending on the user type.
    List cards = (userType == 'consumer')
        ? ScreenData.consumerScreens
        : ScreenData.businessScreens;

    // Incorporate permissions when showing cards.
    print('CARDS: ${cards.length}');
    try {
      for (int i = cards.length - 1; i >= 0; i--) {
        ScreenData card = cards[i];
        if (card.permissions != null) {
          if (currentFacility == null) {
            cards.removeAt(i);
          } else {
            bool authorized =
                currentFacility.facilityType[card.permissions] ?? false;
            if (!authorized) {
              print('REMOVING CARD: $i');
              cards.removeAt(i);
            }
          }
        }
      }
      print('FINAL CARDS: ${cards.length}');
    } catch (e) {
      print('ERROR: $e');
    }

    // Break screen data into chunks.
    var chunks = [];
    int chunkSize = (screenWidth >= Breakpoints.twoColLayoutMinWidth) ? 3 : 2;
    for (var i = 0; i < cards.length; i += chunkSize) {
      chunks.add(cards.sublist(
          i, i + chunkSize > cards.length ? cards.length : i + chunkSize));
    }

    // Body.
    return MainScreen(
      slivers: [
        // App header.
        const SliverToBoxAdapter(child: AppHeader()),

        // Navigation cards.
        for (var chunk in chunks)
          SliverToBoxAdapter(child: DashboardCards(items: chunk)),

        // Footer
        const SliverToBoxAdapter(child: Footer()),
      ],
    );
  }
}

/// Dashboard navigation cards.
class DashboardCards extends StatelessWidget {
  const DashboardCards({
    Key? key,
    required this.items,
  }) : super(key: key);
  final List<ScreenData> items;

  @override
  Widget build(BuildContext context) {
    final screenWidth = MediaQuery.of(context).size.width;
    final crossAxisCount =
        (screenWidth >= Breakpoints.twoColLayoutMinWidth) ? 3 : 2;
    return Padding(
      padding: EdgeInsets.only(
        left: sliverHorizontalPadding(screenWidth),
        right: sliverHorizontalPadding(screenWidth),
        top: 24,
      ),
      child: ItemCardGrid(
        crossAxisCount: crossAxisCount,
        items: items,
      ),
    );
  }
}

/// Grid to layout cards.
class ItemCardGrid extends StatelessWidget {
  const ItemCardGrid({
    Key? key,
    required this.crossAxisCount,
    required this.items,
  }) : super(key: key);
  final int crossAxisCount;
  final List<ScreenData> items;

  @override
  Widget build(BuildContext context) {
    return LayoutGrid(
      columnSizes: List.filled(crossAxisCount, const FlexibleTrackSize(1.5)),
      rowSizes: List.filled(crossAxisCount, auto),
      rowGap: 6,
      columnGap: 12,
      children: [
        for (var i = 0; i < items.length; i++) ItemCard(data: items[i]),
      ],
    );
  }
}

/// Dashboard navigation card.
class ItemCard extends StatelessWidget {
  const ItemCard({
    Key? key,
    required this.data,
  }) : super(key: key);
  final ScreenData data;
  @override
  Widget build(BuildContext context) {
    // final screenWidth = MediaQuery.of(context).size.width;
    // final horizontalPadding = screenWidth >= Breakpoints.tablet ? 48.0 : 24.0;
    // final verticalPadding = screenWidth >= Breakpoints.tablet ? 24.0 : 12.0;
    final horizontalPadding = 24.0;
    final verticalPadding = 6.0;
    return BorderCard(
      backgroundColor: Theme.of(context).scaffoldBackgroundColor,
      builder: (context, value) => InkWell(
        borderRadius: BorderRadius.circular(8),
        onTap: () {
          context.goNamed(data.route);
        },
        child: Column(
          children: [
            // Spacer.
            gapH12,

            // Image.
            AspectRatio(
              aspectRatio: 36.0 / 8.0,
              // aspectRatio:
              //     (screenWidth >= Breakpoints.tablet) ? 12.0 / 8.0 : 24.0 / 8.0,
              child: DecoratedBox(
                decoration: BoxDecoration(
                  image: DecorationImage(
                    fit: BoxFit.fitHeight,
                    image: AssetImage(data.imageName),
                  ),
                ),
              ),
            ),
            Padding(
              padding: EdgeInsets.symmetric(
                horizontal: horizontalPadding,
                vertical: verticalPadding,
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Title.
                  Center(
                    child: Text(
                      data.title,
                      textAlign: TextAlign.center,
                      style: Theme.of(context).textTheme.titleLarge,
                    ),
                  ),

                  // Spacer.
                  gapH8,

                  // Description.
                  Text(
                    data.description,
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

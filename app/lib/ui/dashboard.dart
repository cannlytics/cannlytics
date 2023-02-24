// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 2/18/2023
// Updated: 2/20/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Flutter imports:
import 'package:flutter/material.dart';

// Package imports:
import 'package:flutter_layout_grid/flutter_layout_grid.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

// Project imports:
import 'package:cannlytics_app/constants/colors.dart';
import 'package:cannlytics_app/constants/design.dart';
import 'package:cannlytics_app/routing/app_router.dart';
import 'package:cannlytics_app/routing/routes.dart';
import 'package:cannlytics_app/ui/account/onboarding/onboarding_controller.dart';
import 'package:cannlytics_app/ui/general/footer.dart';
import 'package:cannlytics_app/ui/general/header.dart';
import 'package:cannlytics_app/widgets/cards/hover_border.dart';

/// The initial screen the user sees after signing in.
class DashboardScreen extends ConsumerWidget {
  const DashboardScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    // Provider data and dynamic width.
    final store = ref.watch(onboardingStoreProvider);
    final screenWidth = MediaQuery.of(context).size.width;

    // Break screen data into chunks.
    var chunks = [];
    List cards = (store.userType() == 'consumer')
        ? ScreenData.consumerScreens
        : ScreenData.businessScreens;
    int chunkSize = (screenWidth >= Breakpoints.twoColLayoutMinWidth) ? 3 : 2;
    for (var i = 0; i < cards.length; i += chunkSize) {
      chunks.add(cards.sublist(
          i, i + chunkSize > cards.length ? cards.length : i + chunkSize));
    }

    // Body.
    return Scaffold(
      // backgroundColor: AppColors.white,
      body: CustomScrollView(
        slivers: [
          // App header.
          const SliverToBoxAdapter(child: AppHeader()),

          // Navigation cards.
          for (var chunk in chunks)
            SliverToBoxAdapter(child: DashboardCards(items: chunk)),

          // Footer
          const SliverToBoxAdapter(child: Footer()),
        ],
      ),
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

/// General grid to layout cards.
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
    List<FlexibleTrackSize> columnSizes =
        List.filled(crossAxisCount, const FlexibleTrackSize(1.5));
    List<IntrinsicContentTrackSize> rowSizes =
        List.filled(crossAxisCount, auto);
    return LayoutGrid(
      columnSizes: columnSizes,
      rowSizes: rowSizes,
      rowGap: 12,
      columnGap: 12,
      children: [
        for (var i = 0; i < items.length; i++) ItemCard(data: items[i]),
      ],
    );
  }
}

/// A dashboard navigation card.
class ItemCard extends StatelessWidget {
  const ItemCard({
    Key? key,
    required this.data,
  }) : super(key: key);
  final ScreenData data;
  @override
  Widget build(BuildContext context) {
    final screenWidth = MediaQuery.of(context).size.width;
    final horizontalPadding = screenWidth >= Breakpoints.tablet ? 48.0 : 24.0;
    final verticalPadding = screenWidth >= Breakpoints.tablet ? 24.0 : 12.0;
    return BorderMouseHover(
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
              aspectRatio: 24.0 / 8.0,
              child: DecoratedBox(
                decoration: BoxDecoration(
                  image: DecorationImage(
                    fit: BoxFit.fitHeight,
                    image: AssetImage(data.imageName),
                  ),
                  borderRadius: const BorderRadius.only(
                    topLeft: Radius.circular(16),
                    topRight: Radius.circular(16),
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
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}

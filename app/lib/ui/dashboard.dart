// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 2/18/2023
// Updated: 2/20/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>
import 'package:cannlytics_app/constants/design.dart';
import 'package:cannlytics_app/widgets/style/app_colors.dart';
import 'package:cannlytics_app/widgets/style/border_mouse_hover.dart';
import 'package:flutter_layout_grid/flutter_layout_grid.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:cannlytics_app/ui/account/onboarding/onboarding_controller.dart';
import 'package:cannlytics_app/routing/app_router.dart';

/// The initial screen the user sees after signing in.
class DashboardScreen extends ConsumerWidget {
  const DashboardScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final store = ref.watch(onboardingStoreProvider);
    final screenWidth = MediaQuery.of(context).size.width;
    var chunks = [];
    List cards = (store.userType() == 'consumer')
        ? ScreenData.consumerScreens
        : ScreenData.businessScreens;
    int chunkSize = (screenWidth >= Breakpoints.twoColLayoutMinWidth) ? 3 : 2;
    for (var i = 0; i < cards.length; i += chunkSize) {
      chunks.add(cards.sublist(
          i, i + chunkSize > cards.length ? cards.length : i + chunkSize));
    }
    return Scaffold(
      backgroundColor: AppColors.neutral1,
      body: CustomScrollView(
        slivers: [
          for (var chunk in chunks)
            SliverToBoxAdapter(child: DashboardCards(items: chunk)),
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
      padding: EdgeInsets.symmetric(
        horizontal: sliverHorizontalPadding(screenWidth),
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
        List.filled(crossAxisCount, FlexibleTrackSize(1.5));
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
            AspectRatio(
              aspectRatio: 24.0 / 8.0,
              child: DecoratedBox(
                decoration: BoxDecoration(
                  image: DecorationImage(
                    fit: BoxFit.fitWidth,
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
                  Text(
                    data.title,
                  ),
                  gapH12,
                  Text(
                    data.description,
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

/// Data for each screen.
class ScreenData {
  const ScreenData({
    required this.imageName,
    required this.title,
    required this.description,
    required this.route,
  });
  final String imageName;
  final String title;
  final String description;
  final String route;

  // Business screens.
  static const businessScreens = [
    ScreenData(
      imageName: 'assets/images/icons/figures.png',
      title: 'Deliveries',
      description: 'Manage your deliveries to consumers.',
      route: 'deliveries',
    ),
    ScreenData(
      imageName: 'assets/images/icons/figures.png',
      title: 'Employees',
      description: 'Manage your employees and staff.',
      route: 'employees',
    ),
    ScreenData(
      imageName: 'assets/images/icons/figures.png',
      title: 'Facilities',
      description: 'Manage your facilities and locations.',
      route: 'facilities',
    ),
    ScreenData(
      imageName: 'assets/images/icons/figures.png',
      title: 'Packages',
      description: 'Manage your packages and their items.',
      route: 'packages',
    ),
    ScreenData(
      imageName: 'assets/images/icons/figures.png',
      title: 'Items',
      description: 'Manage your items.',
      route: 'items',
    ),
    ScreenData(
      imageName: 'assets/images/icons/figures.png',
      title: 'Locations',
      description: 'Manage your locations and addresses.',
      route: 'locations',
    ),
    ScreenData(
      imageName: 'assets/images/icons/figures.png',
      title: 'Patients',
      description: 'Manage your patients and customers.',
      route: 'patients',
    ),
    ScreenData(
      imageName: 'assets/images/icons/figures.png',
      title: 'Plants',
      description: 'Manage your plants and cultivation processes.',
      route: 'plants',
    ),
    ScreenData(
      imageName: 'assets/images/icons/figures.png',
      title: 'Results',
      description: 'Manage your test results and analyses.',
      route: 'results',
    ),
    ScreenData(
      imageName: 'assets/images/icons/figures.png',
      title: 'Sales',
      description: 'Manage your sale receipts, transactions, and revenue.',
      route: 'receipts',
    ),
    ScreenData(
      imageName: 'assets/images/icons/figures.png',
      title: 'Strains',
      description: 'Manage your strains and product catalog.',
      route: 'strains',
    ),
    ScreenData(
      imageName: 'assets/images/icons/figures.png',
      title: 'Transfers',
      description: 'Manage your transfers and shipments.',
      route: 'transfers',
    ),
  ];

  // Consumer screens.
  static const consumerScreens = [
    ScreenData(
      imageName: 'assets/images/icons/figures.png',
      title: 'Homegrow',
      description: 'Manage your home cultivation.',
      route: 'garden',
    ),
    ScreenData(
      imageName: 'assets/images/icons/figures.png',
      title: 'Products',
      description: 'Manage your cannabis products.',
      route: 'products',
    ),
    ScreenData(
      imageName: 'assets/images/icons/figures.png',
      title: 'results',
      description: 'Explore lab results.',
      route: 'results',
    ),
    ScreenData(
      imageName: 'assets/images/icons/figures.png',
      title: 'Retailers',
      description: 'Find cannabis retailers.',
      route: 'retailers',
    ),
    ScreenData(
      imageName: 'assets/images/icons/figures.png',
      title: 'Brands',
      description: 'Find cannabis brands.',
      route: 'brands',
    ),
    ScreenData(
      imageName: 'assets/images/icons/figures.png',
      title: 'Spending',
      description: 'Manage your cannabis spending.',
      route: 'spending',
    ),
  ];
}

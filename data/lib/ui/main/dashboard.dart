// Cannlytics Data
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 2/18/2023
// Updated: 4/15/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Flutter imports:
import 'package:cannlytics_data/models/dataset.dart';
import 'package:cannlytics_data/widgets/cards/datasets_cards.dart';
import 'package:cannlytics_data/widgets/cards/storage_details_card.dart';
import 'package:cannlytics_data/widgets/cards/wide_card.dart';
import 'package:cannlytics_data/widgets/layout/header.dart';
import 'package:cannlytics_data/widgets/layout/main_screen.dart';
import 'package:flutter/material.dart';

// Package imports:
import 'package:flutter_riverpod/flutter_riverpod.dart';

// Project imports:
import 'package:cannlytics_data/constants/design.dart';
import 'package:cannlytics_data/ui/main/dashboard_controller.dart';
import 'package:cannlytics_data/widgets/layout/sidebar.dart';

/// Dashboard screen.
class DashboardScreen extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      // App bar.
      appBar: DashboardHeader(),

      // Side menu.
      drawer: Responsive.isMobile(context) ? MobileDrawer() : null,

      // Body.
      body: Dashboard(),
    );
  }
}

/// Dashboard widget.
class Dashboard extends ConsumerWidget {
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    // Get the menu state.
    final _sideMenuOpen = ref.watch(sideMenuOpen);

    /// Welcome message for new users.
    /// TODO: Only show if the user hasn't already hidden.
    _welcomeMessage() {
      return SliverToBoxAdapter(
        child: Padding(
          padding: EdgeInsets.all(Defaults.defaultPadding),
          child: WideCard(
              child: Row(
            children: [
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Welcome to the Cannlytics Data and Analytics Platform!',
                    style: Theme.of(context).textTheme.titleLarge,
                    textAlign: TextAlign.left,
                  ),
                  gapH8,
                  Text(
                    'This is a new platform for managing data.',
                    style: Theme.of(context).textTheme.titleMedium,
                    textAlign: TextAlign.left,
                  ),
                ],
              ),
              Spacer(),
              IconButton(
                onPressed: () {
                  // TODO: Dismiss the welcome message.
                },
                icon: Icon(Icons.close),
              )
            ],
          )),
        ),
      );
    }

    /// Datasets cards.
    /// TODO: Get datasets from Firestore.
    _datasetsCards() {
      List cards = [
        Dataset(
          title: 'WA Lab Results',
          numOfFiles: 1328,
          svgSrc: "assets/icons/Documents.svg",
          totalStorage: "1.9GB",
          color: Defaults.primaryColor,
          percentage: 35,
        ),
      ];
      return SliverToBoxAdapter(
        child: Padding(
          padding: EdgeInsets.all(Defaults.defaultPadding),
          child: DatasetsCards(title: 'Datasets', items: cards),
        ),
      );
    }

    /// Statistical models cards.
    /// TODO: Get datasets from Firestore.
    _statsModelsCards() {
      List cards = [
        Dataset(
          title: 'CoA Doc',
          numOfFiles: 1328,
          svgSrc: "assets/icons/Documents.svg",
          totalStorage: "1.9GB",
          color: Defaults.primaryColor,
          percentage: 35,
        ),
      ];
      return SliverToBoxAdapter(
        child: Padding(
            padding: EdgeInsets.all(Defaults.defaultPadding),
            child: DatasetsCards(title: 'Analytics', items: cards)),
      );
    }

    // TODO: Design the dashboard!

    // Render the dashboard.
    return Console(
      slivers: [
        // Welcome message
        _welcomeMessage(),

        // Statistical models cards.
        _statsModelsCards(),

        // Dataset cards.
        _datasetsCards(),
      ],
    );
  }
}

/// Console widget.
class Console extends ConsumerWidget {
  const Console({
    Key? key,
    required this.slivers,
  }) : super(key: key);

  // The slivers to render in the console.
  final List<Widget> slivers;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    // Get the menu state.
    final _sideMenuOpen = ref.watch(sideMenuOpen);

    // Render the console.
    return Row(
      children: [
        // Desktop and tablet side menu.
        if (!Responsive.isMobile(context) && _sideMenuOpen)
          Expanded(
            child: Container(
              decoration: BoxDecoration(
                border: Border(
                  top: BorderSide(
                    color: Theme.of(context).dividerColor,
                    width: 1.0,
                    style: BorderStyle.solid,
                  ),
                  right: BorderSide(
                    color: Theme.of(context).dividerColor,
                    width: 1.0,
                    style: BorderStyle.solid,
                  ),
                ),
              ),
              child: SideMenu(),
            ),
          ),

        // Main content.
        Expanded(
          flex: 5,
          child: Container(
            decoration: BoxDecoration(
              border: Border(
                top: BorderSide(
                  color: Theme.of(context).dividerColor,
                  width: 1.0,
                  style: BorderStyle.solid,
                ),
              ),
            ),
            child: MainScreen(slivers: slivers),
          ),
        ),
      ],
    );
  }
}

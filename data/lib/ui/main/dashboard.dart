// Cannlytics Data
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 2/18/2023
// Updated: 4/15/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Flutter imports:
import 'package:cannlytics_data/ui/layout/footer.dart';
import 'package:cannlytics_data/widgets/layout/console.dart';
import 'package:flutter/gestures.dart';
import 'package:flutter/material.dart';

// Package imports:
import 'package:flutter_riverpod/flutter_riverpod.dart';

// Project imports:
import 'package:cannlytics_data/constants/design.dart';
import 'package:cannlytics_data/models/dataset.dart';
import 'package:cannlytics_data/ui/main/dashboard_controller.dart';
import 'package:cannlytics_data/widgets/cards/datasets_cards.dart';
import 'package:cannlytics_data/widgets/cards/wide_card.dart';
import 'package:cannlytics_data/widgets/layout/header.dart';
import 'package:cannlytics_data/widgets/layout/sidebar.dart';
import 'package:url_launcher/url_launcher.dart';

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

    // Dynamic screen width.
    final screenWidth = MediaQuery.of(context).size.width;

    /// Welcome message for new users.
    /// TODO: Only show if the user hasn't already hidden.
    _welcomeMessage() {
      return SliverToBoxAdapter(
        child: Padding(
          padding: EdgeInsets.symmetric(horizontal: Defaults.defaultPadding),
          child: WideCard(
              child: Row(
            children: [
              SizedBox(
                width: (screenWidth > Breakpoints.tablet) ? 475 : 275,
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Welcome to the Cannlytics\nData and Analytics Platform!',
                      style: Theme.of(context).textTheme.titleLarge,
                      textAlign: TextAlign.left,
                    ),
                    gapH8,
                    Text.rich(
                      TextSpan(
                        text:
                            'This is a new platform for managing your cannabis data. Stay tuned as new data and analytics are added. You can join the development on ',
                        style: Theme.of(context).textTheme.titleMedium,
                        children: [
                          TextSpan(
                            text: 'GitHub',
                            style: TextStyle(
                              decoration: TextDecoration.underline,
                              color: Colors.blue,
                            ),
                            recognizer: TapGestureRecognizer()
                              ..onTap = () {
                                launchUrl(Uri.parse(
                                    'https://github.com/cannlytics/cannlytics'));
                              },
                          ),
                          TextSpan(
                            text: '.',
                          ),
                        ],
                      ),
                      textAlign: TextAlign.left,
                    ),
                  ],
                ),
              ),
              Spacer(),
              // TODO: Make the welcome message dismissable.
              // IconButton(
              //   onPressed: () {},
              //   icon: Icon(Icons.close),
              // )
            ],
          )),
        ),
      );
    }

    /// Datasets cards.
    /// TODO: Get data from Firestore.
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
          padding: EdgeInsets.only(
            top: Defaults.defaultPadding * 2,
            left: Defaults.defaultPadding,
            right: Defaults.defaultPadding,
          ),
          child: DatasetsCards(title: 'Datasets', items: cards),
        ),
      );
    }

    /// Statistical models cards.
    /// TODO: Get data from Firestore.
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
            padding: EdgeInsets.symmetric(horizontal: Defaults.defaultPadding),
            child: DatasetsCards(title: 'Analytics', items: cards)),
      );
    }

    // Render the dashboard.
    return Console(
      slivers: [
        // Welcome message
        _welcomeMessage(),

        // Statistical models cards.
        _statsModelsCards(),

        // Dataset cards.
        _datasetsCards(),

        // Footer.
        const SliverToBoxAdapter(child: Footer()),
      ],
    );
  }
}

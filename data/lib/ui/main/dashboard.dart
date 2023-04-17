// Cannlytics Data
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 2/18/2023
// Updated: 4/16/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Flutter imports:
import 'package:cannlytics_data/widgets/cards/card_grid.dart';
import 'package:cannlytics_data/widgets/cards/stats_model_card.dart';
import 'package:cannlytics_data/widgets/layout/console.dart';
import 'package:flutter/gestures.dart';
import 'package:flutter/material.dart';

// Package imports:
import 'package:flutter_riverpod/flutter_riverpod.dart';

// Project imports:
import 'package:cannlytics_data/constants/design.dart';
import 'package:cannlytics_data/models/dataset.dart';
import 'package:cannlytics_data/widgets/cards/datasets_cards.dart';
import 'package:cannlytics_data/widgets/cards/wide_card.dart';
import 'package:url_launcher/url_launcher.dart';

/// Dashboard screen.
class DashboardScreen extends ConsumerWidget {
  const DashboardScreen({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    // Dynamic screen width.
    final screenWidth = MediaQuery.of(context).size.width;

    /// Welcome message for new users.
    /// TODO: Only show if the user hasn't already hidden.
    Widget _welcomeMessage() {
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
    Widget _datasetsCards() {
      return SliverToBoxAdapter(
        child: Padding(
          padding: EdgeInsets.symmetric(horizontal: Defaults.defaultPadding),
          child: CardGrid(
            title: 'Data',
            items: [
              StatisticalModelCard(
                imageUrl:
                    'https://firebasestorage.googleapis.com/v0/b/cannlytics.appspot.com/o/public%2Fimages%2Flogos%2Fcannlytics_coa_doc.png?alt=media&token=1871dde9-82db-4342-a29d-d373671491b3',
                modelDescription: 'AI Lab Results Parser',
                route: 'CoADoc',
              ),
              StatisticalModelCard(
                imageUrl:
                    'https://firebasestorage.googleapis.com/v0/b/cannlytics.appspot.com/o/public%2Fimages%2Flogos%2Fskunkfx_logo.png?alt=media&token=1a75b3cc-3230-446c-be7d-5c06012c8e30',
                modelDescription: 'Effects & Aromas Predictor',
                route: 'SkunkFx',
              ),
            ],
          ),
        ),
      );
    }

    /// Statistical models cards.
    /// TODO: Get data from Firestore.
    Widget _statsModelsCards() {
      return SliverToBoxAdapter(
        child: Padding(
          padding: EdgeInsets.symmetric(horizontal: Defaults.defaultPadding),
          child: CardGrid(
            title: 'AI',
            items: [
              StatisticalModelCard(
                imageUrl:
                    'https://firebasestorage.googleapis.com/v0/b/cannlytics.appspot.com/o/public%2Fimages%2Flogos%2Fcannlytics_coa_doc.png?alt=media&token=1871dde9-82db-4342-a29d-d373671491b3',
                modelDescription: 'AI Lab Results Parser',
                route: 'CoADoc',
              ),
            ],
          ),
        ),
      );
    }

    // Render the dashboard.
    return ConsoleScreen(
      children: [
        // Welcome message
        // _welcomeMessage(),

        // Statistical models cards.
        _statsModelsCards(),

        // Dataset cards.
        _datasetsCards(),
      ],
    );
  }
}

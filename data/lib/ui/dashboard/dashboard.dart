// Cannlytics Data
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 2/18/2023
// Updated: 5/7/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Flutter imports:
import 'package:cannlytics_data/common/cards/card_grid.dart';
import 'package:cannlytics_data/common/cards/stats_model_card.dart';
import 'package:cannlytics_data/common/layout/console.dart';
import 'package:cannlytics_data/ui/dashboard/dashboard_controller.dart';
import 'package:flutter/gestures.dart';
import 'package:flutter/material.dart';

// Package imports:
import 'package:flutter_riverpod/flutter_riverpod.dart';

// Project imports:
import 'package:cannlytics_data/constants/design.dart';
import 'package:cannlytics_data/common/cards/wide_card.dart';
import 'package:url_launcher/url_launcher.dart';

/// Dashboard screen.
class DashboardScreen extends ConsumerWidget {
  const DashboardScreen({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    // Dynamic screen width.
    final screenWidth = MediaQuery.of(context).size.width;

    // Render the dashboard.
    return ConsoleScreen(
      children: [
        // Welcome message
        _welcomeMessage(context, screenWidth),

        // Statistical models cards.
        // _statsModelsCards(),

        // Dataset cards.
        _datasetsCards(),
      ],
    );
  }

  /// Welcome message for new users.
  /// TODO: Only show if the user hasn't already hidden.
  Widget _welcomeMessage(BuildContext context, double screenWidth) {
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

  /// Dataset cards.
  Widget _datasetsCards() {
    return SliverToBoxAdapter(
      child: Padding(
        padding: EdgeInsets.symmetric(horizontal: Defaults.defaultPadding),
        child: CardGrid(
          title: 'Data',
          items: [
            CustomCard(
              imageUrl:
                  'https://firebasestorage.googleapis.com/v0/b/cannlytics.appspot.com/o/public%2Fimages%2Flogos%2Fcannlytics_coa_doc.png?alt=media&token=1871dde9-82db-4342-a29d-d373671491b3',
              title: 'Cannabis Licenses',
              description:
                  'A collection of 11,060 cannabis licenses from each state with permitted adult-use cannabis.',
              category: 'Classification',
              instances: '11,060 observations',
              attributes: '28 Attributes',
            ),
          ],
          // items: mainDatasets.map((model) {
          //   return StatisticalModelCard(
          //     imageUrl: model['image_url'],
          //     modelDescription: model['description'],
          //     route: model['route'],
          //   );
          // }).toList(),
        ),
      ),
    );
  }

  // /// Statistical models cards.
  // /// TODO: Get data from Firestore.
  // Widget _statsModelsCards() {
  //   return SliverToBoxAdapter(
  //     child: Padding(
  //       padding: EdgeInsets.symmetric(horizontal: Defaults.defaultPadding),
  //       child: CardGrid(
  //         title: 'AI',
  //         items: [
  //           StatisticalModelCard(
  //             imageUrl:
  //                 'https://firebasestorage.googleapis.com/v0/b/cannlytics.appspot.com/o/public%2Fimages%2Flogos%2Fcannlytics_coa_doc.png?alt=media&token=1871dde9-82db-4342-a29d-d373671491b3',
  //             modelDescription: 'AI Lab Results Parser',
  //             route: 'CoADoc',
  //           ),
  //         ],
  //       ),
  //     ),
  //   );
  // }
}

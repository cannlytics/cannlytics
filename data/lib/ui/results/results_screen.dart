// Cannlytics Data
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 4/15/2023
// Updated: 6/13/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// TODO: Links to places where users can get their COAs:
// ACS Labs: https://portal.acslabcannabis.com/clientpage
// Curaleaf: https://curaleaf.com/transparency
// Fluent: https://getfluent.com/testresults/
// Jungle Boys: https://www.jungleboys.com/verify/
// Sunnyside: https://www.verifyhemp.com/
// Trulieve: https://www.trulieve.com/discover/product-test-search
// Green Scientific Labs: https://www.greenscientificlabs.com/find-coa.php
// Sanctuary: https://sanctuary-coa-portal.anvil.app/
// VidaCann: https://www.vidacann.com/lab-results/
// HT Medical Cannabis: https://htcannabis.com/lab-results/

// TODO: Infinitely scrolling grid of recently added lab results.

// TODO: Allow user's to add lab results through URLS, images that contain
// QR codes, or by uploading a COA PDF.

// TODO: Move lab results search to : /results/search

// TODO: Allow people to make queries like the following:
// - full spectrum surterra carts?
// - Bernie Mac Hangover Haze
// - I'm looking for a high terpinolene cart

// Flutter imports:
import 'package:cannlytics_data/ui/results/coa_doc_ui.dart';
import 'package:cannlytics_data/ui/results/results_form.dart';
import 'package:cannlytics_data/ui/results/user_results.dart';
import 'package:flutter/material.dart';

// Package imports:
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

// Project imports:
import 'package:cannlytics_data/ui/layout/breadcrumbs.dart';
import 'package:cannlytics_data/ui/layout/console.dart';
import 'package:cannlytics_data/constants/design.dart';

/// Screen.
class LabResultsScreen extends StatelessWidget {
  const LabResultsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return ConsoleScreen(
      children: [
        SliverToBoxAdapter(child: MainContent()),
      ],
    );
  }
}

/// Main content.
class MainContent extends ConsumerWidget {
  const MainContent({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    // Dynamic screen width.
    final screenWidth = MediaQuery.of(context).size.width;

    // Render the widget.
    return Padding(
      padding: EdgeInsets.only(
        left: sliverHorizontalPadding(screenWidth),
        right: sliverHorizontalPadding(screenWidth),
        top: 24,
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        mainAxisAlignment: MainAxisAlignment.start,
        children: [
          // Breadcrumbs.
          Row(
            children: [
              Breadcrumbs(
                items: [
                  BreadcrumbItem(
                      title: 'Data',
                      onTap: () {
                        context.go('/');
                      }),
                  BreadcrumbItem(
                    title: 'Lab Results',
                  )
                ],
              ),
            ],
          ),

          // Main interface.
          gapH12,
          ResultsTabs(),
          gapH48,
        ],
      ),
    );
  }

  /// Dataset cards.
  // Widget _datasetsCards(BuildContext context, WidgetRef ref) {
  //   var datasets =
  //       mainDatasets.where((element) => element['type'] == 'results').toList();
  //   final screenWidth = MediaQuery.of(context).size.width;
  //   final user = ref.watch(authProvider).currentUser;
  //   return Column(children: [
  //     Row(
  //       mainAxisAlignment: MainAxisAlignment.start,
  //       children: [
  //         Text('Lab Results Datasets',
  //             style: Theme.of(context).textTheme.labelLarge!.copyWith(
  //                 color: Theme.of(context).textTheme.titleLarge!.color)),
  //       ],
  //     ),
  //     gapH12,
  //     CardGridView(
  //       crossAxisCount: screenWidth < Breakpoints.desktop ? 1 : 2,
  //       childAspectRatio: 3,
  //       items: datasets.map((model) {
  //         return DatasetCard(
  //           imageUrl: model['image_url'],
  //           title: model['title'],
  //           description: model['description'],
  //           tier: model['tier'],
  //           rows: NumberFormat('#,###').format(model['observations']) + ' rows',
  //           columns: NumberFormat('#,###').format(model['fields']) + ' columns',
  //           onTap: () async {
  //             // Note: Requires the user to be signed in.
  //             if (user == null) {
  //               showDialog(
  //                 context: context,
  //                 builder: (BuildContext context) {
  //                   return SignInDialog(isSignUp: false);
  //                 },
  //               );
  //               return;
  //             }
  //             // Get URL for file in Firebase Storage.
  //             String? url =
  //                 await StorageService.getDownloadUrl(model['file_ref']);
  //             DataService.openInANewTab(url);
  //           },
  //         );
  //       }).toList(),
  //     ),
  //   ]);
  // }
}

/// Tabs of results.
class ResultsTabs extends StatelessWidget {
  const ResultsTabs({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return DefaultTabController(
      length: 3,
      child: Column(
        children: <Widget>[
          Container(
            decoration: BoxDecoration(
              // color: Theme.of(context).scaffoldBackgroundColor,
              color: Colors.transparent,
              borderRadius: BorderRadius.circular(3),
              border: Border.all(
                color: Theme.of(context).dividerColor,
                width: 1,
              ),
            ),
            child: TabBar(
              isScrollable: true,
              unselectedLabelColor:
                  Theme.of(context).textTheme.titleSmall!.color,
              labelColor: Theme.of(context).textTheme.titleLarge!.color,
              indicatorSize: TabBarIndicatorSize.label,
              // indicator: BoxDecoration(
              //   borderRadius: BorderRadius.circular(3),
              //   color: Colors.greenAccent,
              // ),
              tabs: [
                Tab(text: 'Parse'),
                Tab(text: 'Explore'),
                Tab(text: 'Your Results'),
              ],
            ),
          ),
          Container(
            height: MediaQuery.of(context).size.height * 0.75,
            child: TabBarView(
              children: [
                CoADocInterface(),
                LabResultsSearchForm(),
                UserResultsInterface(),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

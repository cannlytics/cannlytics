// Cannlytics Data
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 4/15/2023
// Updated: 8/18/2023
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

// Flutter imports:
import 'package:flutter/material.dart';

// Package imports:
import 'package:flutter_riverpod/flutter_riverpod.dart';

// Project imports:
import 'package:cannlytics_data/common/layout/breadcrumbs.dart';
import 'package:cannlytics_data/common/layout/pill_tab.dart';
import 'package:cannlytics_data/constants/design.dart';
import 'package:cannlytics_data/ui/layout/console.dart';
import 'package:cannlytics_data/ui/results/results_parser.dart';
import 'package:cannlytics_data/ui/results/user_results.dart';

// import 'package:cannlytics_data/ui/results/results_search.dart';

/// Results screen.
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
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      mainAxisAlignment: MainAxisAlignment.start,
      children: [
        // Breadcrumbs.
        BreadcrumbsRow(
          items: [
            {'label': 'Data', 'path': '/'},
            {'label': 'Lab Results', 'path': null},
          ],
        ),

        // Main interface.
        gapH12,
        ResultsTabs(),
      ],
    );
  }
}

/// Tabs of results.
class ResultsTabs extends StatefulWidget {
  const ResultsTabs({Key? key}) : super(key: key);

  @override
  _ResultsTabsState createState() => _ResultsTabsState();
}

/// Tabs state.
class _ResultsTabsState extends State<ResultsTabs>
    with SingleTickerProviderStateMixin {
  // State.
  late final TabController _tabController;
  final int _tabCount = 2;

  /// Initialize the tab controller.
  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: _tabCount, vsync: this);
    _tabController.addListener(() => setState(() {}));
  }

  // Dispose the controllers.
  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      children: <Widget>[
        Align(
          alignment: Alignment.centerLeft,
          child: TabBar(
            controller: _tabController,
            padding: EdgeInsets.symmetric(horizontal: 4, vertical: 0),
            labelPadding: EdgeInsets.symmetric(horizontal: 2, vertical: 0),
            isScrollable: true,
            unselectedLabelColor: Theme.of(context).textTheme.bodyMedium!.color,
            labelColor: Theme.of(context).textTheme.titleLarge!.color,
            splashBorderRadius: BorderRadius.circular(30),
            splashFactory: NoSplash.splashFactory,
            overlayColor: MaterialStateProperty.all<Color>(Colors.transparent),
            indicator: BoxDecoration(),
            dividerColor: Colors.transparent,
            tabs: [
              PillTabButton(
                text: 'Your Results',
                icon: Icons.science,
                isSelected: _tabController.index == 0,
              ),
              PillTabButton(
                text: 'Parse',
                icon: Icons.auto_awesome,
                isSelected: _tabController.index == 1,
              ),
              // PillTabButton(
              //   text: 'Explore',
              //   icon: Icons.explore,
              //   isSelected: _tabController.index == 2,
              // ),
            ],
          ),
        ),
        Container(
          height: MediaQuery.of(context).size.height * 2,
          child: TabBarView(
            controller: _tabController,
            children: [
              UserResultsInterface(tabController: _tabController),
              ResultsParserInterface(tabController: _tabController),
              // LabResultsSearchForm(),
            ],
          ),
        ),
      ],
    );
  }
}


  // UNUSED: Dataset cards.
  /// Dataset cards.
  // Widget _datasetsCards(BuildContext context, WidgetRef ref) {
  //   var datasets =
  //       mainDatasets.where((element) => element['type'] == 'results').toList();
  //   final screenWidth = MediaQuery.of(context).size.width;
  //   final user = ref.watch(userProvider).value;;
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

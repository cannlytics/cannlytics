// Cannlytics Data
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 4/15/2023
// Updated: 6/29/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>
// Flutter imports:
import 'package:cannlytics_data/common/layout/breadcrumbs.dart';
import 'package:cannlytics_data/common/layout/pill_tab.dart';
import 'package:cannlytics_data/ui/sales/receipts_parser.dart';
import 'package:cannlytics_data/ui/sales/user_receipts.dart';
import 'package:flutter/material.dart';

// Package imports:
import 'package:flutter_riverpod/flutter_riverpod.dart';

// Project imports:
import 'package:cannlytics_data/ui/layout/console.dart';
import 'package:cannlytics_data/constants/design.dart';

/// Sales screen.
class SalesScreen extends StatelessWidget {
  const SalesScreen({super.key});

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
            {'label': 'Purchases', 'path': '/sales'},
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

  /// Initialize the tab controller.
  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 2, vsync: this);
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
                text: 'Your Receipts',
                icon: Icons.science,
                isSelected: _tabController.index == 0,
              ),
              PillTabButton(
                text: 'Parse',
                icon: Icons.auto_awesome,
                isSelected: _tabController.index == 1,
              ),
            ],
          ),
        ),
        Container(
          height: MediaQuery.of(context).size.height,
          child: TabBarView(
            controller: _tabController,
            children: [
              UserReceiptsInterface(tabController: _tabController),
              ReceiptsParserInterface(),
            ],
          ),
        ),
      ],
    );
  }
}

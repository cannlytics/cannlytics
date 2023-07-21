// Cannlytics Data
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 4/15/2023
// Updated: 7/10/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Flutter imports:
import 'package:flutter/material.dart';

// Project imports:
import 'package:cannlytics_data/common/layout/breadcrumbs.dart';
import 'package:cannlytics_data/common/layout/pill_tab.dart';
import 'package:cannlytics_data/ui/layout/console.dart';
import 'package:cannlytics_data/ui/strains/strains_search.dart';

// TODO: Allow user's to report new strains.

/// Strains screen.
class StrainsScreen extends StatelessWidget {
  const StrainsScreen({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return ConsoleScreen(
      children: [
        // Breadcrumbs.
        SliverToBoxAdapter(
          child: BreadcrumbsRow(
            items: [
              {'label': 'Data', 'path': '/'},
              {'label': 'Strains', 'path': null},
            ],
          ),
        ),

        // Main content.
        SliverToBoxAdapter(
          child: StrainsTabs(),
        ),
      ],
    );
  }
}

/// Tabs of strains.
class StrainsTabs extends StatefulWidget {
  const StrainsTabs({Key? key}) : super(key: key);

  @override
  _StrainsTabsState createState() => _StrainsTabsState();
}

/// Tabs state.
class _StrainsTabsState extends State<StrainsTabs>
    with SingleTickerProviderStateMixin {
  // State.
  late final TabController _tabController;
  int _selectedIndex = 0;

  /// Initialize the tab controller.
  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 3, vsync: this);
    _tabController.addListener(() => setState(() {
          _selectedIndex = _tabController.index;
        }));
  }

  // Dispose of the controllers.
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
            padding: EdgeInsets.only(left: 4, right: 4, top: 12),
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
                text: 'All',
                icon: Icons.apps,
                isSelected: _selectedIndex == 0,
              ),
              PillTabButton(
                text: 'Hot',
                icon: Icons.local_fire_department,
                isSelected: _selectedIndex == 1,
              ),
              PillTabButton(
                text: 'Favorites',
                icon: Icons.favorite,
                isSelected: _selectedIndex == 2,
              ),
            ],
          ),
        ),
        Container(
          height: MediaQuery.of(context).size.height,
          child: TabBarView(
            controller: _tabController,
            children: [
              StrainsSearch(orderBy: 'strain_name'),
              StrainsSearch(orderBy: 'total_favorites'),
              StrainsSearch(orderBy: 'favorites'),
            ],
          ),
        ),
      ],
    );
  }
}

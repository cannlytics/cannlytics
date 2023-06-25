// Cannlytics Data
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 4/15/2023
// Updated: 6/24/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>
// Flutter imports:
import 'package:cannlytics_data/ui/sales/receipts_parser.dart';
import 'package:cannlytics_data/ui/sales/user_receipts.dart';
import 'package:flutter/material.dart';

// Package imports:
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

// Project imports:
import 'package:cannlytics_data/ui/layout/breadcrumbs.dart';
import 'package:cannlytics_data/ui/layout/console.dart';
import 'package:cannlytics_data/constants/design.dart';

/// Screen.
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
        Padding(
          padding: EdgeInsets.only(left: 16, top: 12),
          child: Row(
            children: [
              Breadcrumbs(
                items: [
                  BreadcrumbItem(
                      title: 'Data',
                      onTap: () {
                        context.go('/');
                      }),
                  BreadcrumbItem(
                    title: 'Sales',
                  )
                ],
              ),
            ],
          ),
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

class _ResultsTabsState extends State<ResultsTabs>
    with SingleTickerProviderStateMixin {
  late final TabController _tabController;
  int _selectedIndex = 0;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 3, vsync: this);
    _tabController.addListener(() {
      setState(() {
        _selectedIndex = _tabController.index;
      });
    });
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      children: <Widget>[
        Align(
          alignment: Alignment.centerLeft,
          child: TabBar(
            controller: _tabController,
            padding: EdgeInsets.all(0),
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
              _buildTab('Parse', 0, Icons.auto_awesome),
              _buildTab('Analytics', 1, Icons.explore),
              _buildTab('Your Receipts', 2, Icons.science),
            ],
          ),
        ),
        Container(
          height: MediaQuery.of(context).size.height,
          child: TabBarView(
            controller: _tabController,
            children: [
              ReceiptsParserInterface(),
              UserReceiptsInterface(),
              UserReceiptsInterface(),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildTab(String text, int index, IconData icon) {
    bool isSelected = _selectedIndex == index;
    Color lightScreenGold = Color(0xFFD4AF37);
    Color darkScreenGold = Color(0xFFFFD700);
    Color goldColor = Theme.of(context).brightness == Brightness.light
        ? lightScreenGold
        : darkScreenGold;
    ValueNotifier<bool> isHovered = ValueNotifier(false);
    return MouseRegion(
      onEnter: (_) => isHovered.value = true,
      onExit: (_) => isHovered.value = false,
      child: ValueListenableBuilder<bool>(
        valueListenable: isHovered,
        builder: (context, value, child) {
          return GestureDetector(
            onTap: () {
              _tabController.animateTo(index);
            },
            child: InkWell(
              borderRadius: BorderRadius.circular(30),
              splashColor: Colors.blue.withOpacity(0.5),
              hoverColor: Colors.blue.withOpacity(0.2),
              child: Container(
                padding: EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                decoration: BoxDecoration(
                  borderRadius: BorderRadius.circular(30),
                  color: isSelected
                      ? Colors.blue.withOpacity(0.1)
                      : (value
                          ? Colors.blue.withOpacity(0.05)
                          : Colors.transparent),
                ),
                child: Row(
                  children: [
                    Icon(icon,
                        size: 16,
                        color: isSelected
                            ? goldColor
                            : Theme.of(context).colorScheme.secondary),
                    SizedBox(width: 8),
                    Text(text),
                  ],
                ),
              ),
            ),
          );
        },
      ),
    );
  }
}

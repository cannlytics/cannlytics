// Cannlytics Data
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 4/15/2023
// Updated: 4/15/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Flutter imports:
import 'package:flutter/material.dart';

// Package imports:
import 'package:flutter_riverpod/flutter_riverpod.dart';

// Project imports:
import 'package:cannlytics_data/ui/layout/footer.dart';
import 'package:cannlytics_data/ui/layout/header.dart';
import 'package:cannlytics_data/ui/layout/main_screen.dart';
import 'package:cannlytics_data/ui/layout/sidebar.dart';
import 'package:cannlytics_data/constants/design.dart';
import 'package:cannlytics_data/ui/dashboard/dashboard_controller.dart';

/// General console screen that renders given widgets.
class ConsoleScreen extends StatelessWidget {
  const ConsoleScreen({
    super.key,
    required this.children,
    this.bottomSearch = false,
  });

  final List<Widget> children;
  final bool bottomSearch;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      // App bar.
      appBar: DashboardHeader(),

      // Side menu.
      drawer: Responsive.isMobile(context) ? MobileDrawer() : null,

      // Body.
      body: Console(slivers: [
        // Main content.
        ...children,

        // Footer.
        const SliverToBoxAdapter(child: Footer()),
      ]),

      // Navigation.
      // bottomNavigationBar: bottomSearch ? HoverSearchBar() : null,
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
              // constraints: BoxConstraints(
              //   minWidth: 275, // Set the desired minimum width
              // ),
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
          flex: 4,
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

/// Bottom search button.
class HoverSearchBar extends StatefulWidget {
  @override
  _HoverSearchBarState createState() => _HoverSearchBarState();
}

class _HoverSearchBarState extends State<HoverSearchBar> {
  bool _isHovered = false;

  @override
  Widget build(BuildContext context) {
    return BottomAppBar(
      child: Container(
        height: 250,
        width: double.maxFinite,
        decoration: BoxDecoration(
            color: Colors.orange,
            borderRadius: BorderRadius.vertical(top: Radius.circular(20.0))),
        child: Row(
          mainAxisSize: MainAxisSize.max,
          mainAxisAlignment: MainAxisAlignment.spaceEvenly,
          children: <Widget>[
            IconButton(
              icon: Icon(Icons.arrow_forward),
              onPressed: () {
//on Presses functionaluty goes here
              },
            ),
            //add as many tabs as you want here
          ],
        ),
      ),
    );
  }
}
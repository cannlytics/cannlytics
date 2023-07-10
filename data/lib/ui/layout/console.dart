// Cannlytics Data
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 4/15/2023
// Updated: 6/19/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Flutter imports:
import 'package:flutter/material.dart';

// Package imports:
import 'package:flutter_riverpod/flutter_riverpod.dart';

// Project imports:
import 'package:cannlytics_data/constants/design.dart';
import 'package:cannlytics_data/ui/dashboard/dashboard_controller.dart';
import 'package:cannlytics_data/ui/layout/footer.dart';
import 'package:cannlytics_data/ui/layout/header.dart';
import 'package:cannlytics_data/ui/layout/sidebar.dart';

/// General console screen that renders given widgets.
class ConsoleScreen extends StatelessWidget {
  const ConsoleScreen({Key? key, required this.children}) : super(key: key);

  // Parameters.
  final List<Widget> children;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      // App bar.
      appBar: DashboardHeader(key: Key('app_header')),

      // Side menu.
      drawer: Responsive.isMobile(context) ? MobileDrawer() : null,

      // Body.
      body: Console(slivers: [
        // Main content.
        ...children,

        // Footer.
        const SliverToBoxAdapter(child: Footer()),
      ]),
    );
  }
}

/// Console widget.
class Console extends ConsumerWidget {
  const Console({
    Key? key,
    required this.slivers,
  }) : super(key: key);

  // Parameters.
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

        // Main screen area.
        Expanded(
          flex: 4,
          child: Container(
            // height: MediaQuery.sizeOf(context).height,
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

/// The main screen of the app.
class MainScreen extends StatelessWidget {
  const MainScreen({Key? key, required this.slivers}) : super(key: key);

  // Parameters.
  final List<Widget> slivers;

  @override
  Widget build(BuildContext context) {
    bool isDark = Theme.of(context).brightness == Brightness.dark;
    return Container(
      // Background gradient.
      decoration: BoxDecoration(
        gradient: RadialGradient(
          center: Alignment(1, -1),
          radius: 4.0,
          colors: [
            isDark ? Colors.transparent : Colors.white,
            isDark ? Color(0xFF4E5165) : Color(0xFFe8e8e8),
          ],
        ),
      ),
      child: CustomScrollView(
        slivers: [
          ...slivers,
        ],
      ),
    );
  }
}

/// A console screen with one child of main content.
class MainContent extends ConsumerWidget {
  const MainContent({
    Key? key,
    required this.child,
    this.fillRemaining = false,
  }) : super(key: key);

  // Parameters.
  final Widget child;
  final bool? fillRemaining;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return ConsoleScreen(
      children: [
        if (fillRemaining!)
          SliverFillRemaining(child: child)
        else
          SliverToBoxAdapter(child: child),
      ],
    );
  }
}

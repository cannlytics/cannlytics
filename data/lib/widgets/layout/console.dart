// Cannlytics Data
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 4/15/2023
// Updated: 4/15/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Flutter imports:
import 'package:cannlytics_data/ui/main/dashboard_controller.dart';
import 'package:cannlytics_data/widgets/layout/main_screen.dart';
import 'package:cannlytics_data/widgets/layout/sidebar.dart';
import 'package:flutter/material.dart';

// Package imports:
import 'package:flutter_riverpod/flutter_riverpod.dart';

// Project imports:
import 'package:cannlytics_data/constants/design.dart';

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
          flex: 5,
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

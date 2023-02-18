// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 2/17/2023
// Updated: 2/18/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>
import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:cannlytics_app/utils/strings/string_hardcoded.dart';
import 'package:cannlytics_app/routing/app_router.dart';

// This is a temporary implementation
// TODO: Implement a better solution once this PR is merged:
// https://github.com/flutter/packages/pull/2650
class ScaffoldWithBottomNavBar extends StatefulWidget {
  const ScaffoldWithBottomNavBar({Key? key, required this.child})
      : super(key: key);
  final Widget child;

  @override
  State<ScaffoldWithBottomNavBar> createState() =>
      _ScaffoldWithBottomNavBarState();
}

class _ScaffoldWithBottomNavBarState extends State<ScaffoldWithBottomNavBar> {
  // used for the currentIndex argument of BottomNavigationBar
  int _selectedIndex = 0;

  void _tap(BuildContext context, int index) {
    if (index == _selectedIndex) {
      // If the tab hasn't changed, do nothing
      return;
    }
    setState(() => _selectedIndex = index);
    if (index == 0) {
      // Note: this won't remember the previous state of the route
      // More info here:
      // https://github.com/flutter/flutter/issues/99124
      context.goNamed(AppRoute.jobs.name);
    } else if (index == 1) {
      context.goNamed(AppRoute.entries.name);
    } else if (index == 2) {
      context.goNamed(AppRoute.account.name);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: widget.child,
      bottomNavigationBar: BottomNavigationBar(
        type: BottomNavigationBarType.fixed,
        currentIndex: _selectedIndex,
        items: [
          // products
          BottomNavigationBarItem(
            icon: const Icon(Icons.work),
            label: 'Jobs'.hardcoded,
          ),
          BottomNavigationBarItem(
            icon: const Icon(Icons.view_headline),
            label: 'Entries'.hardcoded,
          ),
          BottomNavigationBarItem(
            icon: const Icon(Icons.person),
            label: 'Account'.hardcoded,
          ),
        ],
        onTap: (index) => _tap(context, index),
      ),
    );
  }
}

// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 2/17/2023
// Updated: 2/20/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>
import 'package:cannlytics_app/constants/design.dart';
import 'package:cannlytics_app/routing/routes.dart';
import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:cannlytics_app/utils/strings/string_hardcoded.dart';

/// Bottom navigation bar for mobile.
class MainScreen extends StatefulWidget {
  const MainScreen({
    Key? key,
    required this.child,
  }) : super(key: key);
  final Widget child;

  @override
  State<MainScreen> createState() => _MainScreenState();
}

class _MainScreenState extends State<MainScreen> {
  // The current index of the bottom navigation bar.
  int _selectedIndex = 0;

  /// Change route from bottom navigation.
  void _tap(BuildContext context, int index) {
    if (index == _selectedIndex) {
      return;
    }
    setState(() => _selectedIndex = index);
    if (index == 0) {
      context.goNamed(AppRoutes.dashboard.name);
    } else if (index == 1) {
      context.goNamed(AppRoutes.search.name);
    } else if (index == 2) {
      context.goNamed(AppRoutes.account.name);
    }
  }

  @override
  Widget build(BuildContext context) {
    // Determine if it is mobile.
    final screenWidth = MediaQuery.of(context).size.width;
    bool isWide = screenWidth > Breakpoints.tablet;

    // Render the screen with navigation items on mobile.
    return Scaffold(
      body: widget.child,
      bottomNavigationBar: isWide
          ? null
          : BottomNavigationBar(
              currentIndex: _selectedIndex,
              type: BottomNavigationBarType.fixed,
              // showSelectedLabels: false,
              // showUnselectedLabels: false,
              items: const [
                BottomNavigationBarItem(
                  icon: Icon(Icons.home_outlined),
                  label: 'Home',
                ),
                BottomNavigationBarItem(
                  icon: Icon(Icons.search_outlined),
                  label: 'Search',
                ),
                BottomNavigationBarItem(
                  icon: Icon(Icons.account_box_outlined),
                  label: 'Account',
                ),
              ],
              onTap: (index) => _tap(context, index),
            ),
    );
  }
}

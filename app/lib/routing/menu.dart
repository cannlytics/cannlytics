// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 2/20/2023
// Updated: 2/20/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>
import 'package:cannlytics_app/constants/colors.dart';
import 'package:cannlytics_app/constants/design.dart';
import 'package:cannlytics_app/routing/mobile_menu.dart';
import 'package:cannlytics_app/routing/routes.dart';
import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

/// The main navigation header.
class AppHeader extends StatelessWidget {
  const AppHeader({
    Key? key,
    // required this.child,
  }) : super(key: key);
  // final Widget child;

  @override
  Widget build(BuildContext context) {
    final screenWidth = MediaQuery.of(context).size.width;
    bool isWide = screenWidth > Breakpoints.tablet;
    return Container(
      color: AppColors.white,
      child: isWide
          ? const DesktopNavigationLayout()
          : const MobileNavigationLayout(),
    );
  }
}

/// Navigation layout for desktop.
class DesktopNavigationLayout extends StatelessWidget {
  const DesktopNavigationLayout({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final screenWidth = MediaQuery.of(context).size.width;
    bool isVeryWide = screenWidth > Breakpoints.desktop;
    return SizedBox(
      height: 64,
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.center,
        children: [
          SizedBox(width: isVeryWide ? 80 : 28),
          const AppLogo(),
          const Spacer(),
          NavigationLink(
            text: 'Home',
            path: AppRoutes.dashboard.name,
          ),
          NavigationLink(
            text: 'Search',
            path: AppRoutes.search.name,
          ),
          NavigationLink(
            text: 'Account',
            path: AppRoutes.account.name,
          ),
          // const NavigationIconButton(assetName: Constants.search),
          // const NavigationIconButton(assetName: Constants.toggleDay),
          SizedBox(width: isVeryWide ? 80 : 28),
        ],
      ),
    );
  }
}

/// Navigation layout for mobile.
class MobileNavigationLayout extends StatefulWidget {
  const MobileNavigationLayout({Key? key}) : super(key: key);

  @override
  State<MobileNavigationLayout> createState() => _MobileNavigationLayoutState();
}

class _MobileNavigationLayoutState extends State<MobileNavigationLayout>
    with SingleTickerProviderStateMixin {
  late final _menuController = AnimationController(
    vsync: this,
    duration: const Duration(milliseconds: 150),
  );

  /// Open / close the menu.
  void _toggleMenu() {
    if (_menuController.isCompleted) {
      _menuController.reverse();
    } else {
      _menuController.forward();
    }
  }

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: _menuController,
      builder: (context, _) {
        final height =
            64 + _menuController.value * MobileNavigationMenu.menuHeight;
        return SizedBox(
          height: height,
          child: Column(
            children: [
              SizedBox(
                height: 64,
                child: Row(
                  crossAxisAlignment: CrossAxisAlignment.center,
                  children: [
                    // App logo.
                    const SizedBox(width: 28),
                    const AppLogo(),
                    const Spacer(),

                    // Search button.
                    // IconButton(
                    //   icon: const Icon(
                    //     Icons.search,
                    //     color: Colors.white,
                    //     size: 30,
                    //   ),
                    //   onPressed: () {},
                    // ),
                    // const NavigationIconButton(assetName: Constants.search),

                    // Open / close menu button.
                    GestureDetector(
                      onTap: _toggleMenu,
                      child: AnimatedIcon(
                        icon: AnimatedIcons.menu_close,
                        progress: _menuController,
                        color: AppColors.neutral2,
                      ),
                    ),
                    const SizedBox(width: 28),
                  ],
                ),
              ),
              const Expanded(child: MobileNavigationMenu()),
            ],
          ),
        );
      },
    );
  }
}

/// App logo for the menu.
class AppLogo extends StatelessWidget {
  const AppLogo({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Image.asset(
      'assets/images/logos/cannlytics_logo_with_text_light.png',
      width: 120,
    );
  }
}

/// Link used for navigation.
class NavigationLink extends StatelessWidget {
  const NavigationLink({
    Key? key,
    required this.text,
    required this.path,
  }) : super(key: key);
  final String text;
  final String path;
  @override
  Widget build(BuildContext context) {
    return SizedBox(
      height: 48,
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 8),
        child: TextButton(
          child: Text(
            text,
            style: Theme.of(context)
                .textTheme
                .titleSmall!
                .copyWith(color: AppColors.neutral6),
          ),
          onPressed: () {
            context.goNamed(path);
          },
        ),
      ),
    );
  }
}

/// Icon in navigation.
class NavigationIconButton extends StatelessWidget {
  const NavigationIconButton({
    Key? key,
    required this.assetName,
  }) : super(key: key);
  final String assetName;
  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 16.0),
      child: GestureDetector(
        child: Image.asset(assetName),
        onTap: () {},
      ),
    );
  }
}

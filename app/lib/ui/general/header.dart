// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 2/20/2023
// Updated: 2/20/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Flutter imports:
import 'package:flutter/material.dart';

// Package imports:
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

// Project imports:
import 'package:cannlytics_app/constants/colors.dart';
import 'package:cannlytics_app/constants/design.dart';
import 'package:cannlytics_app/routing/routes.dart';
import 'package:cannlytics_app/ui/account/onboarding/onboarding_controller.dart';

/// The main navigation header.
class AppHeader extends StatelessWidget {
  const AppHeader({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final screenWidth = MediaQuery.of(context).size.width;
    bool isWide = screenWidth > Breakpoints.tablet;
    return Container(
      color: AppColors.white,
      // decoration: const BoxDecoration(
      //   border: Border(
      //     bottom: BorderSide(
      //       color: AppColors.neutral2,
      //       width: 1,
      //     ),
      //   ),
      // ),
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
    return Container(
      decoration: const BoxDecoration(
        border: Border(
          bottom: BorderSide(
            color: AppColors.neutral2,
            width: 1,
          ),
        ),
      ),
      child: SizedBox(
        height: 64,
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.center,
          children: [
            // Logo.
            SizedBox(width: isVeryWide ? 80 : 28),
            const AppLogo(),

            // TODO: Select license if business!

            // Links.
            const Spacer(),
            // NavigationLink(
            //   text: 'Home',
            //   path: AppRoutes.dashboard.name,
            // ),
            // NavigationLink(
            //   text: 'Search',
            //   path: AppRoutes.search.name,
            // ),
            NavigationLink(
              text: 'Account',
              path: AppRoutes.account.name,
            ),
            // const NavigationIconButton(assetName: Constants.toggleDay),
            SizedBox(width: isVeryWide ? 80 : 28),

            // FIXME: A sidebar menu is needed for desktop!
          ],
        ),
      ),
    );
  }
}

/// Navigation layout for mobile.
class MobileNavigationLayout extends ConsumerStatefulWidget {
  const MobileNavigationLayout({Key? key}) : super(key: key);

  @override
  MobileNavigationLayoutState createState() => MobileNavigationLayoutState();
}

class MobileNavigationLayoutState extends ConsumerState<MobileNavigationLayout>
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
    final store = ref.watch(onboardingStoreProvider);
    return AnimatedBuilder(
      animation: _menuController,
      builder: (context, _) {
        final List<ScreenData> screens = (store.userType() == 'consumer')
            ? ScreenData.consumerScreens
            : ScreenData.businessScreens;
        final int screenCount = screens.length;
        final menuHeight = 56 * screenCount + 64;
        final height = 64 + _menuController.value * menuHeight;
        return Container(
          decoration: const BoxDecoration(
            border: Border(
              bottom: BorderSide(
                color: AppColors.neutral2,
                width: 1,
              ),
            ),
          ),
          child: SizedBox(
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

                // List of routes.
                Expanded(child: MobileNavigationMenu(screens: screens)),
              ],
            ),
          ),
        );
      },
    );
  }
}

/// The main navigation for user's on mobile.
class MobileNavigationMenu extends ConsumerWidget {
  const MobileNavigationMenu({
    Key? key,
    required this.screens,
  }) : super(key: key);
  final List<ScreenData> screens;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return Material(
      // color: AppColors.offWhite,
      child: ListView(
        shrinkWrap: true,
        children: [
          for (ScreenData screen in screens)
            MobileMenuListTile(
              title: screen.title,
              route: screen.route,
              description: screen.description,
              imageName: screen.imageName,
            ),
          // TODO: Add light/dark theme toggle.
          // Container(
          //   height: 64.0,
          //   alignment: Alignment.center,
          //   child: MobileToggleButton(onPressed: () {}),
          // )
        ],
      ),
    );
  }
}

/// Mobile menu list item.
class MobileMenuListTile extends StatelessWidget {
  const MobileMenuListTile({
    Key? key,
    required this.title,
    required this.description,
    required this.route,
    required this.imageName,
  }) : super(key: key);
  final String title;
  final String description;
  final String route;
  final String imageName;

  @override
  Widget build(BuildContext context) {
    return Material(
      color: AppColors.surface,
      child: InkWell(
        splashColor: AppColors.accent1,
        onTap: () {
          context.goNamed(route);
        },
        child: ListTile(
          leading: Image.asset(
            imageName,
            height: 45,
          ),
          title: Text(title),
          subtitle: Text(description),
        ),
      ),
    );
  }
}

/// App logo for the menu.
class AppLogo extends StatelessWidget {
  const AppLogo({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return InkWell(
      splashColor: AppColors.accent1,
      onTap: () {
        context.goNamed('dashboard');
      },
      child: Image.asset(
        'assets/images/logos/cannlytics_logo_with_text_light.png',
        width: 120,
      ),
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

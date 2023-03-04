// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 2/20/2023
// Updated: 2/20/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Flutter imports:
import 'package:cannlytics_app/services/auth_service.dart';
import 'package:cannlytics_app/ui/account/user/account_controller.dart';
import 'package:cannlytics_app/ui/general/dashboard_controller.dart';
import 'package:cannlytics_app/utils/dialogs/alert_dialogs.dart';
import 'package:cannlytics_app/widgets/buttons/action_text_button.dart';
import 'package:cannlytics_app/widgets/images/avatar.dart';
import 'package:flutter/material.dart';

// Package imports:
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

// Project imports:
import 'package:cannlytics_app/constants/colors.dart';
import 'package:cannlytics_app/constants/design.dart';
import 'package:cannlytics_app/routing/routes.dart';
import 'package:cannlytics_app/services/theme_service.dart';
import 'package:cannlytics_app/ui/account/onboarding/onboarding_controller.dart';

/// The main navigation header.
class AppHeader extends StatelessWidget {
  const AppHeader({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final screenWidth = MediaQuery.of(context).size.width;
    bool isWide = screenWidth > Breakpoints.tablet;
    return Container(
      color: Theme.of(context).scaffoldBackgroundColor,
      child: isWide
          ? const DesktopNavigationLayout()
          : const MobileNavigationLayout(),
    );
  }
}

/// Navigation layout for desktop.
class DesktopNavigationLayout extends ConsumerWidget {
  const DesktopNavigationLayout({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    // Get the screen width.
    final screenWidth = MediaQuery.of(context).size.width;
    bool isVeryWide = screenWidth > Breakpoints.desktop;

    // Get the theme.
    final themeMode = ref.watch(themeModeProvider);
    final bool isDark = themeMode == ThemeMode.dark;

    // Watch the user's licenses.
    // final dashboardStore = ref.watch(dashboardStoreProvider);
    // print('LICENSES:');
    // print(dashboardStore.getLicenses());
    // print('PRIMARY LICENSE:');
    // print(dashboardStore.getPrimaryLicense());

    // Build the layout.
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
            // TODO: Turn into organization selection.
            SizedBox(width: isVeryWide ? 80 : 28),
            // AppLogo(isDark: isDark),
            OrganizationSelection(),

            // License selection.
            gapW6,
            LicenseDropDown(),

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
            SizedBox(width: isVeryWide ? 28 : 12),

            // FIXME: A sidebar menu is needed for desktop!

            // Theme toggle.
            const ThemeToggle(),
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
    // Get the provider.
    final store = ref.watch(onboardingStoreProvider);

    // Get the theme.
    final themeMode = ref.watch(themeModeProvider);
    final bool isDark = themeMode == ThemeMode.dark;

    // Build the layout.
    return AnimatedBuilder(
      animation: _menuController,
      builder: (context, _) {
        // Get the user type.
        final List<ScreenData> screens = (store.userType() == 'consumer')
            ? ScreenData.consumerScreens
            : ScreenData.businessScreens;

        // Format the height.
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
                      gapW12,
                      // AppLogo(isDark: isDark),
                      OrganizationSelection(),

                      // License selection.
                      gapW6,
                      LicenseDropDown(),

                      // Spacer.
                      const Spacer(),

                      // Open / close menu button.
                      GestureDetector(
                        onTap: _toggleMenu,
                        child: AnimatedIcon(
                          icon: AnimatedIcons.menu_close,
                          progress: _menuController,
                          // color: AppColors.neutral2,
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
    // Listen to the current user.
    final state = ref.watch(accountProvider);
    final user = ref.watch(authProvider).currentUser;

    return Material(
      elevation: 8,
      child: ListView(
        shrinkWrap: true,
        children: [
          // Account.
          Container(
            // padding: EdgeInsets.all(16.0),
            child: Column(
              children: [
                // User photo, name, and email.
                gapH6,
                Row(
                  children: [
                    // User photo.
                    gapW12,
                    Avatar(
                      photoUrl: user!.photoURL,
                      radius: 24,
                      borderColor: Theme.of(context).secondaryHeaderColor,
                      borderWidth: 1.0,
                    ),
                    gapW12,

                    Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        // User name.
                        Text(
                          user.displayName!,
                          textAlign: TextAlign.start,
                          style: Theme.of(context)
                              .textTheme
                              .labelMedium!
                              .copyWith(
                                  fontWeight: FontWeight.bold,
                                  color: Theme.of(context)
                                      .textTheme
                                      .titleLarge!
                                      .color),
                        ),

                        // User email.
                        Text(
                          user.email!,
                          textAlign: TextAlign.start,
                          style: Theme.of(context).textTheme.labelMedium,
                        ),
                      ],
                    ),

                    // Theme toggle.
                    const Spacer(),
                    const ThemeToggle(),
                  ],
                ),

                // Divider.
                Divider(
                  color: AppColors.neutral2,
                  thickness: 0.25,
                  // height: 20,
                ),

                // Manage account.
                InkWell(
                  splashColor: AppColors.accent1,
                  onTap: () {
                    context.goNamed(AppRoutes.account.name);
                  },
                  child: ListTile(
                    dense: true,
                    title: Text(
                      'Manage account',
                      style: Theme.of(context).textTheme.titleMedium!.copyWith(
                          color: Theme.of(context).textTheme.titleLarge!.color),
                    ),
                  ),
                ),

                // Sign out.
                InkWell(
                  splashColor: AppColors.accent1,
                  onTap: state.isLoading
                      ? null
                      : () async {
                          final logout = await showAlertDialog(
                            context: context,
                            title: 'Are you sure?',
                            cancelActionText: 'Cancel',
                            defaultActionText: 'Sign out',
                          );
                          if (logout == true) {
                            ref.read(accountProvider.notifier).signOut();
                          }
                        },
                  child: ListTile(
                    dense: true,
                    title: Text(
                      'Sign out',
                      style: Theme.of(context).textTheme.titleMedium!.copyWith(
                          color: Theme.of(context).textTheme.titleLarge!.color),
                    ),
                  ),
                ),
              ],
            ),
          ),

          // Divider.
          Divider(
            color: AppColors.neutral2,
            thickness: 0.25,
            // height: 20,
          ),

          // Links.
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
      // color: AppColors.surface,
      child: InkWell(
        splashColor: AppColors.accent1,
        onTap: () {
          context.goNamed(route);
        },
        child: ListTile(
          dense: true,
          leading: Image.asset(
            imageName,
            height: 45,
          ),
          title: Text(
            title,
            style: Theme.of(context).textTheme.titleMedium!.copyWith(
                  color: Theme.of(context).textTheme.titleLarge!.color,
                ),
          ),
          subtitle: Text(
            description,
            style: Theme.of(context).textTheme.titleSmall,
          ),
        ),
      ),
    );
  }
}

/// App logo for the menu.
class AppLogo extends StatelessWidget {
  const AppLogo({
    Key? key,
    required this.isDark,
  }) : super(key: key);
  final bool isDark;

  @override
  Widget build(BuildContext context) {
    return InkWell(
      splashColor: AppColors.accent1,
      onTap: () {
        context.goNamed('dashboard');
      },
      child: Image.asset(
        isDark
            ? 'assets/images/logos/cannlytics_logo_with_text_dark.png'
            : 'assets/images/logos/cannlytics_logo_with_text_light.png',
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
    return TextButton(
      onPressed: () {
        context.goNamed(path);
      },
      child: Text(
        text,
        style: Theme.of(context).textTheme.titleMedium!.copyWith(
              color: Theme.of(context).textTheme.titleLarge!.color,
            ),
      ),
    );
  }
}

/// Organization selection.
class OrganizationSelection extends ConsumerWidget {
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final value = ref.watch(licenseProvider).primaryLicense;
    final items = ref.watch(licenseProvider).licenses;
    // If no organization, return a create/join organization button.
    if (items.length == 1) {
      return NavigationLink(
        text: '+ Add a license',
        path: AppRoutes.addLicense.name,
      );
    }

    // Dropdown.
    return DropdownButton(
      isDense: true,
      value: value,
      items: items
          .map((e) => DropdownMenuItem<String>(
                onTap: () => e,
                value: e,
                child: Text(e),
              ))
          .toList(),
      onChanged: (value) {
        if (value == '+ Add a license') {
          GoRouter.of(context).go('/licenses/add');
          return;
        }
        ref.read(licenseProvider.notifier).changeLicense(value as String);
      },
    );
  }
}

/// A dropdown selection for the user to choose their primary license.
class LicenseDropDown extends ConsumerWidget {
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final value = ref.watch(licenseProvider).primaryLicense;
    final items = ref.watch(licenseProvider).licenses;
    // If no license, return an add license button.
    if (items.length == 1) {
      return NavigationLink(
        text: '+ Add a license',
        path: AppRoutes.addLicense.name,
      );
    }

    // Dropdown.
    return DropdownButton(
      isDense: true,
      value: value,
      items: items
          .map((e) => DropdownMenuItem<String>(
                onTap: () => e,
                value: e,
                child: Text(e),
              ))
          .toList(),
      onChanged: (value) {
        if (value == '+ Add a license') {
          GoRouter.of(context).go('/licenses/add');
          return;
        }
        ref.read(licenseProvider.notifier).changeLicense(value as String);
      },
    );
  }
}

/// Light / dark theme toggle.
class ThemeToggle extends StatelessWidget {
  const ThemeToggle({super.key});

  @override
  Widget build(BuildContext context) {
    return Consumer(builder: (context, ref, child) {
      final theme = ref.watch(themeModeProvider);
      return Row(
        mainAxisAlignment: MainAxisAlignment.end,
        children: [
          Padding(
            padding: const EdgeInsets.only(top: 6, right: 24, bottom: 6),
            child: IconButton(
              splashRadius: 18,
              onPressed: () {
                // Toggle light / dark theme.
                ref.read(themeModeProvider.notifier).state =
                    theme == ThemeMode.light ? ThemeMode.dark : ThemeMode.light;
              },
              icon: Icon(
                theme == ThemeMode.dark ? Icons.dark_mode : Icons.light_mode,
                color: AppColors.neutral4,
              ),
            ),
          ),
        ],
      );
    });
  }
}

// /// Icon in navigation.
// class NavigationIconButton extends StatelessWidget {
//   const NavigationIconButton({
//     Key? key,
//     required this.assetName,
//   }) : super(key: key);
//   final String assetName;
//   @override
//   Widget build(BuildContext context) {
//     return Padding(
//       padding: const EdgeInsets.symmetric(horizontal: 16.0),
//       child: GestureDetector(
//         child: Image.asset(assetName),
//         onTap: () {},
//       ),
//     );
//   }
// }

// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 2/20/2023
// Updated: 3/8/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Flutter imports:
import 'package:cannlytics_app/services/auth_service.dart';
import 'package:cannlytics_app/ui/account/user/account_controller.dart';
import 'package:cannlytics_app/ui/business/facilities/facilities_controller.dart';
import 'package:cannlytics_app/ui/general/app_controller.dart';
import 'package:cannlytics_app/utils/dialogs/alert_dialogs.dart';
import 'package:cannlytics_app/widgets/buttons/theme_toggle.dart';
import 'package:cannlytics_app/widgets/images/app_logo.dart';
import 'package:cannlytics_app/widgets/images/avatar.dart';
import 'package:flutter/material.dart';

// Package imports:
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

// Project imports:
import 'package:cannlytics_app/constants/theme.dart';
import 'package:cannlytics_app/constants/design.dart';
import 'package:cannlytics_app/routing/routes.dart';
import 'package:cannlytics_app/services/theme_service.dart';

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
            gapW24,
            AppIcon(),

            // Organization selection.
            SizedBox(width: isVeryWide ? 24 : 12),
            OrganizationSelection(),

            // License / facility selection.
            gapW6,
            FacilitySelection(),

            // Links.
            const Spacer(),
            NavigationLink(
              text: 'Account',
              path: AppRoutes.account.name,
            ),
            SizedBox(width: isVeryWide ? 24 : 12),

            // TODO: A sidebar menu is needed for desktop!

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
    // Get the user type.
    final userType = ref.watch(userTypeProvider);

    // Get the theme.
    // final themeMode = ref.watch(themeModeProvider);
    // final bool isDark = themeMode == ThemeMode.dark;

    // Build the layout.
    return AnimatedBuilder(
      animation: _menuController,
      builder: (context, _) {
        // Get the user type.
        final List<ScreenData> screens = (userType == 'consumer')
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
                      // Icon.
                      gapW6,
                      AppIcon(),

                      // Organization selection.
                      gapW12,
                      OrganizationSelection(),

                      // License / facility selection.
                      gapW6,
                      FacilitySelection(),

                      // Spacer.
                      const Spacer(),

                      // Open / close menu button.
                      GestureDetector(
                        onTap: _toggleMenu,
                        child: AnimatedIcon(
                          icon: AnimatedIcons.menu_close,
                          progress: _menuController,
                        ),
                      ),
                      gapW24,
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
    if (user == null) return Container();

    return Material(
      elevation: 8,
      child: ListView(
        shrinkWrap: true,
        children: [
          // Account.
          Container(
            child: Column(
              children: [
                // User photo, name, and email.
                gapH6,
                Row(
                  children: [
                    // User photo.
                    gapW12,
                    Avatar(
                      photoUrl: user.photoURL,
                      radius: 24,
                      borderColor: Theme.of(context).secondaryHeaderColor,
                      borderWidth: 1.0,
                    ),
                    gapW12,

                    // User name and email.
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
          ),

          // Links.
          for (ScreenData screen in screens)
            MobileMenuListTile(
              title: screen.title,
              route: screen.route,
              description: screen.description,
              imageName: screen.imageName,
            ),
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

/// Primary organization selection.
class OrganizationSelection extends ConsumerWidget {
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    // Get the user's organizations.
    final orgs = ref.watch(organizationsProvider).value ?? [];

    // Return organizations link button.
    if (orgs.length == 0) {
      return NavigationLink(
        text: 'Organizations',
        path: AppRoutes.organizations.name,
      );
    }

    // Get the user's current organization.
    var value = ref.watch(primaryOrganizationProvider) ?? orgs[0].id;

    // Build the selection.
    var dropdown = DropdownButton(
      underline: Container(),
      isDense: true,
      isExpanded: true,
      // icon: Icon(Icons.business_center_outlined),
      // iconSize: 18,
      value: value,
      items: orgs
              .map(
                (item) => DropdownMenuItem<String>(
                  onTap: () => item.id,
                  value: item.id,
                  child: ListTile(
                    dense: true,
                    title: Text(item.id),
                  ),
                ),
              )
              .toList() +
          [
            DropdownMenuItem<String>(
              onTap: () => 'organizations',
              value: 'organizations',
              child: ListTile(
                dense: true,
                title: Text('Manage organizations'),
              ),
            ),
          ],
      onChanged: (String? value) {
        if (value == 'organizations') {
          GoRouter.of(context).go('/organizations');
          return;
        }
        ref.read(primaryOrganizationProvider.notifier).state = value!;
      },
    );

    // Render the dropdown.
    return Container(
      height: 45.0,
      width: 150.0,
      child: dropdown,
    );
  }
}

/// Primary license selection.
class FacilitySelection extends ConsumerWidget {
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    // Get the user's organizations.
    final orgs = ref.watch(organizationsProvider).value ?? [];
    if (orgs.length == 0) return Container();

    // Get the active organization.
    final primaryOrg = ref.watch(primaryOrganizationProvider);

    // Get all organization's licenses.
    List<String> licenseIds = [];
    for (var org in orgs) {
      if (org.id == primaryOrg) {
        var licenses = org.licenses ?? [];
        if (licenses.isEmpty) continue;
        for (var license in licenses) {
          licenseIds.add(license!['license_number']);
        }
      }
    }

    // Return prompt to add a license if no licenses.
    if (licenseIds.isEmpty) {
      return NavigationLink(
        text: '+ Add a license',
        path: AppRoutes.addLicense.name,
      );
    }

    /// Get the user's facilities.
    final facilities = ref.watch(facilitiesProvider).value ?? [];

    // Return prompt to add a license if no facilities.
    if (facilities.isEmpty) {
      return NavigationLink(
        text: '+ Add a license',
        path: AppRoutes.addLicense.name,
      );
    }

    // Get the current facility.
    var primaryFacility =
        ref.watch(primaryFacilityProvider) ?? facilities[0].id;

    // TODO: Add licenses and facilities to dropdown.

    // Build the dropdown.
    var dropdown = DropdownButton(
      underline: Container(),
      isDense: true,
      isExpanded: true,
      value: primaryFacility,
      items: facilities
              .map(
                (item) => DropdownMenuItem<String>(
                  onTap: () => item.id,
                  value: item.id,
                  child: ListTile(
                    dense: true,
                    title: Text(item.id),
                  ),
                ),
              )
              .toList() +
          [
            DropdownMenuItem<String>(
              onTap: () => 'add',
              value: 'add',
              child: ListTile(
                dense: true,
                title: Text('+ Add a license'),
              ),
            ),
          ],
      onChanged: (String? value) {
        if (value == 'add') {
          GoRouter.of(context).go('/licenses/add');
          return;
        }
        ref.read(primaryFacilityProvider.notifier).state = value!;
      },
    );

    // Render the dropdown.
    return Container(
      height: 45.0,
      width: 150.0,
      child: dropdown,
    );
  }
}

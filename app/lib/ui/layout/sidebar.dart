// Cannlytics Data
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 3/22/2023
// Updated: 8/6/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Flutter imports:
import 'package:flutter/material.dart';

// Package imports:
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_svg/flutter_svg.dart';
import 'package:go_router/go_router.dart';

// Project imports:
import 'package:cannlytics_data/common/dialogs/help_dialog.dart';
import 'package:cannlytics_data/services/auth_service.dart';
import 'package:cannlytics_data/ui/account/account_controller.dart';
import 'package:cannlytics_data/utils/utils.dart';

/// Mobile side menu.
class MobileDrawer extends StatelessWidget {
  const MobileDrawer({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Drawer(
      // Elevation.
      elevation: 0,

      // Corners.
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.only(
          topRight: Radius.circular(3),
          bottomRight: Radius.circular(3),
        ),
      ),

      // Widget.
      child: SideMenu(),
    );
  }
}

/// Side menu.
class SideMenu extends ConsumerWidget {
  const SideMenu({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    // Listen to the current user.
    final user = ref.watch(userProvider).value;

    // Get the current route.
    final currentRoute = GoRouterState.of(context).uri.toString();

    // Render the side menu.
    return ListView(
      children: [
        // Dashboard link.
        DrawerListTile(
          title: 'Dashboard',
          leading: SvgPicture.asset(
            'assets/icons/emoji/house_with_garden.svg',
            width: 28,
          ),
          onTap: () => context.go('/'),
        ),

        // Lab results link.
        DrawerListTile(
          title: 'Lab Results',
          leading: SvgPicture.asset(
            'assets/icons/emoji/microscope.svg',
            width: 28,
          ),
          onTap: () => context.go('/results'),
          isSelected: currentRoute.contains('/results'),
        ),

        // Licensees link.
        DrawerListTile(
          title: 'Licenses',
          leading: SvgPicture.asset(
            'assets/icons/emoji/dispensary-plain.svg',
            width: 28,
          ),
          onTap: () => context.go('/licenses'),
          isSelected: currentRoute.contains('/licenses'),
        ),

        // Sales link.
        DrawerListTile(
          title: 'Purchases',
          leading: SvgPicture.asset(
            'assets/icons/emoji/money_bag.svg',
            width: 28,
          ),
          onTap: () => context.go('/sales'),
          isSelected: currentRoute.contains('/sales'),
        ),

        // Strains link.
        DrawerListTile(
          title: 'Strains',
          leading: SvgPicture.asset(
            'assets/images/ai-icons/cannabis-leaf.svg',
            width: 28,
          ),
          onTap: () => context.go('/strains'),
          isSelected: currentRoute.contains('/strains'),
        ),

        // Divider
        Divider(),

        // Upgrade link.
        if (user == null)
          DrawerListTile(
            title: 'Upgrade',
            leading: SvgPicture.asset(
              'assets/icons/emoji/glowing_star.svg',
              width: 28,
            ),
            onTap: () => context.go('/account?upgrade=true'),
          ),

        // Settings link.
        if (user != null)
          DrawerListTile(
            title: 'Settings',
            leading: SvgPicture.asset(
              'assets/icons/emoji/gear.svg',
              width: 28,
            ),
            onTap: () => context.go('/account'),
            isSelected: currentRoute.contains('/account'),
          ),

        // Help link.
        DrawerListTile(
          title: 'Get help',
          leading: SvgPicture.asset(
            'assets/icons/emoji/ring_buoy.svg',
            width: 28,
          ),
          onTap: () {
            showDialog(
              context: context,
              builder: (BuildContext context) {
                return HelpDialog();
              },
            );
          },
        ),

        // Sign out link.
        if (user != null)
          DrawerListTile(
            title: 'Sign Out',
            leading: SvgPicture.asset(
              'assets/icons/emoji/sign_out.svg',
              width: 28,
            ),
            onTap: () async {
              final logout = await InterfaceUtils.showAlertDialog(
                context: context,
                title: 'Are you sure?',
                cancelActionText: 'Cancel',
                defaultActionText: 'Sign out',
              );
              if (logout == true) {
                await ref.read(authProvider).signOut();
              }
            },
          ),
      ],
    );
  }
}

/// A drawer list tile.
class DrawerListTile extends StatelessWidget {
  const DrawerListTile({
    Key? key,
    required this.title,
    required this.leading,
    required this.onTap,
    this.isSelected = false,
  }) : super(key: key);

  final String title;
  final Widget leading;
  final VoidCallback onTap;
  final bool isSelected;

  @override
  Widget build(BuildContext context) {
    return ListTile(
      // Style.
      horizontalTitleGap: 12.0,

      // Leading icon.
      leading: leading,

      // Title.
      title: Row(
        children: [
          Text(
            title,
            style: Theme.of(context).textTheme.labelMedium,
          ),
        ],
      ),

      // Background color.
      tileColor: isSelected
          ? Theme.of(context).dialogBackgroundColor.withOpacity(0.66)
          : null,

      // Action.
      onTap: onTap,
    );
  }
}

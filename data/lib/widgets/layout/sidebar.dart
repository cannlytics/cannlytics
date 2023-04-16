// Cannlytics Data
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 3/22/2023
// Updated: 4/15/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// TODO:
// - Highlight active route accordingly.

// Flutter imports:
import 'package:cannlytics_data/widgets/dialogs/help_dialog.dart';
import 'package:flutter/material.dart';

// Package imports:
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_svg/flutter_svg.dart';
import 'package:go_router/go_router.dart';

// Project imports:
import 'package:cannlytics_data/services/auth_service.dart';
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
    final user = ref.watch(authProvider).currentUser;

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

        // Licensees link.
        DrawerListTile(
          title: 'Licensees',
          leading: SvgPicture.asset(
            'assets/icons/emoji/scroll.svg',
            width: 28,
          ),
          onTap: () => context.go('/licensees'),
        ),

        // Strains link.
        DrawerListTile(
          title: 'Strains',
          leading: SvgPicture.asset(
            'assets/icons/emoji/tanabata_tree.svg',
            width: 28,
          ),
          onTap: () => context.go('/strains'),
        ),

        // // Products link.
        // DrawerListTile(
        //   title: 'Products',
        //   leading: SvgPicture.asset(
        //     'assets/icons/emoji/package.svg',
        //     width: 28,
        //   ),
        //   onTap: () => context.go('/products'),
        // ),

        // Lab results link.
        DrawerListTile(
          title: 'Lab Results',
          leading: SvgPicture.asset(
            'assets/icons/emoji/microscope.svg',
            width: 28,
          ),
          onTap: () => context.go('/results'),
        ),

        // Sales link.
        DrawerListTile(
          title: 'Sales',
          leading: SvgPicture.asset(
            'assets/icons/emoji/money_bag.svg',
            width: 28,
          ),
          onTap: () => context.go('/sales'),
        ),

        // // Industry link.
        // DrawerListTile(
        //   title: 'Industry',
        //   leading: SvgPicture.asset(
        //     'assets/icons/emoji/tractor.svg',
        //     width: 28,
        //   ),
        //   onTap: () => context.go('/production'),
        // ),

        // // Research link.
        // DrawerListTile(
        //   title: 'Research',
        //   leading: SvgPicture.asset(
        //     'assets/icons/emoji/dna.svg',
        //     width: 28,
        //   ),
        //   onTap: () => context.go('/research'),
        // ),

        // Divider
        Divider(),

        // Upgrade link.
        DrawerListTile(
          title: 'Upgrade',
          leading: SvgPicture.asset(
            'assets/icons/emoji/glowing_star.svg',
            width: 28,
          ),
          onTap: () => context.go('/account?upgrade=true'),
        ),

        // Settings link.
        DrawerListTile(
          title: 'Settings',
          leading: SvgPicture.asset(
            'assets/icons/emoji/gear.svg',
            width: 28,
          ),
          onTap: () => context.go('/account'),
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
                context.go('/dashboard');
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
  }) : super(key: key);

  final String title;
  final Widget leading;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return ListTile(
      // Style.
      horizontalTitleGap: 0.0,

      // Leading icon.
      leading: leading,

      // Title.
      title: Text(
        title,
        style: Theme.of(context).textTheme.labelMedium,
      ),

      // Action.
      onTap: onTap,
    );
  }
}

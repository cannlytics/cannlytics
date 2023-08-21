// Cannlytics Data
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 4/14/2023
// Updated: 6/23/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Flutter imports:
import 'package:flutter/material.dart';

// Package imports:
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:url_launcher/url_launcher.dart';

// Project imports:
import 'package:cannlytics_data/common/buttons/custom_text_button.dart';
import 'package:cannlytics_data/common/buttons/primary_button.dart';
import 'package:cannlytics_data/common/dialogs/auth_dialog.dart';
import 'package:cannlytics_data/common/images/avatar.dart';
import 'package:cannlytics_data/constants/colors.dart';
import 'package:cannlytics_data/constants/design.dart';
import 'package:cannlytics_data/constants/theme.dart';
import 'package:cannlytics_data/services/auth_service.dart';
import 'package:cannlytics_data/ui/account/account_controller.dart';
import 'package:cannlytics_data/ui/dashboard/dashboard_controller.dart';
import 'package:cannlytics_data/utils/utils.dart';

/// Dashboard header.
class DashboardHeader extends ConsumerWidget implements PreferredSizeWidget {
  DashboardHeader({Key? key}) : super(key: key);

  @override
  Size get preferredSize => AppBar().preferredSize;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    // Listen to the current user.
    final user = ref.watch(userProvider).value;

    // Listen to the user's current amount of tokens.
    final asyncSnapshot = ref.watch(userSubscriptionProvider);
    final int currentTokens = asyncSnapshot.when(
      data: (data) => data?['tokens'] ?? 0,
      loading: () => 0,
      error: (error, stack) => 0,
    );

    // Get the theme.
    final themeMode = ref.watch(themeModeProvider);
    final bool isDark = themeMode == ThemeMode.dark;

    // Dynamic width.
    final screenWidth = MediaQuery.of(context).size.width;

    // Render the widget.
    return AppBar(
      // Menu button.
      leading: Responsive.isMobile(context)
          ? null
          : IconButton(
              onPressed: () {
                ref.read(sideMenuOpen.notifier).state = !ref.read(sideMenuOpen);
              },
              icon: Icon(
                Icons.menu,
                color: Theme.of(context).colorScheme.onSurface,
              ),
            ),

      // Title.
      centerTitle: false,
      titleSpacing: 0,
      title: Row(
        children: [
          if (screenWidth > Breakpoints.tablet - 200)
            GestureDetector(
              onTap: () => context.go('/'),
              child: Image.asset(
                isDark
                    ? 'assets/images/logos/cannlytics_logo_with_text_dark.png'
                    : 'assets/images/logos/cannlytics_logo_with_text_light.png',
                height: 28,
              ),
            ),
        ],
      ),

      // Actions.
      actions: [
        if (user == null)
          Row(
            children: [
              // Sign in button.
              CustomTextButton(
                text: 'Sign In',
                onPressed: () {
                  showDialog(
                    context: context,
                    builder: (BuildContext context) {
                      return SignInDialog(isSignUp: false);
                    },
                  );
                },
              ),

              // Space.
              gapW8,

              // Sign up button.
              PrimaryButton(
                text: 'Sign Up',
                onPressed: () {
                  showDialog(
                    context: context,
                    builder: (BuildContext context) {
                      return SignInDialog(isSignUp: true);
                    },
                  );
                },
              ),

              // Space.
              gapW16,
            ],
          ),
        if (user != null)
          Row(children: [
            // Token count and coin image.
            Padding(
              padding: EdgeInsets.only(right: 4),
              child: MouseRegion(
                cursor: SystemMouseCursors.click,
                child: Tooltip(
                  message:
                      "Each AI job requires 1 token.\nYou can get tokens with a\nsubscription or piecemeal.",
                  child: InkWell(
                    onTap: () {
                      const url =
                          'https://cannlytics.com/account/subscriptions';
                      launchUrl(Uri.parse(url));
                    },
                    child: Row(
                      children: [
                        Image.network(
                          'https://firebasestorage.googleapis.com/v0/b/cannlytics.appspot.com/o/assets%2Fimages%2Femojies%2Fopenmoji%2Fai-coin.png?alt=media&token=465724f9-8e53-44f7-bd47-698cc90bc2c6',
                          height: 24,
                          width: 24,
                        ),
                        gapW2,
                        Text(
                          '$currentTokens tokens',
                          style: Theme.of(context)
                              .textTheme
                              .bodyLarge!
                              .copyWith(
                                  color: Theme.of(context)
                                      .textTheme
                                      .titleLarge!
                                      .color),
                        ),
                      ],
                    ),
                  ),
                ),
              ),
            ),

            // User profile image.
            UserMenu(
              displayName: user.displayName ?? '',
              email: user.email ?? '',
              photoUrl: user.photoURL ??
                  'https://firebasestorage.googleapis.com/v0/b/cannlytics.appspot.com/o/assets%2Fimages%2Fplaceholders%2Fhomegrower-placeholder.png?alt=media&token=29331691-c2ef-4bc5-89e8-cec58a7913e4',
            ),
          ]),
      ],
    );
  }
}

/// User menu.
class UserMenu extends ConsumerWidget {
  UserMenu({
    Key? key,
    required this.photoUrl,
    required this.displayName,
    required this.email,
  }) : super(key: key);

  // Parameters.
  final String photoUrl;
  final String displayName;
  final String email;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    // Get the theme.
    final themeMode = ref.watch(themeModeProvider);
    final bool isDark = themeMode == ThemeMode.dark;

    // Render.
    return Padding(
      padding: EdgeInsets.only(top: 8, bottom: 8, right: 8),
      child: PopupMenuButton<String>(
        tooltip: 'User menu',
        offset: Offset(0, 40),
        padding: EdgeInsets.all(0),
        surfaceTintColor: Colors.transparent,
        itemBuilder: (context) => [
          PopupMenuItem(
            enabled: false,
            padding: EdgeInsets.symmetric(vertical: 0, horizontal: 0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Padding(
                  padding: EdgeInsets.symmetric(vertical: 0, horizontal: 8),
                  child: Text(
                    displayName,
                    style: Theme.of(context).textTheme.bodyLarge,
                  ),
                ),
                Padding(
                  padding: EdgeInsets.symmetric(vertical: 0, horizontal: 8),
                  child: Text(
                    email,
                    style: Theme.of(context).textTheme.bodySmall,
                  ),
                ),
                Divider(),
              ],
            ),
          ),
          PopupMenuItem(
            padding: EdgeInsets.symmetric(vertical: 0, horizontal: 8),
            value: 'account',
            child: Text(
              'Your account',
              style: Theme.of(context).textTheme.bodyMedium!.copyWith(
                  color: Theme.of(context).textTheme.bodyLarge!.color),
            ),
          ),
          PopupMenuItem(
            padding: EdgeInsets.symmetric(vertical: 0, horizontal: 8),
            value: 'subscription',
            child: Text(
              'Manage your subscription',
              style: Theme.of(context).textTheme.bodyMedium!.copyWith(
                  color: Theme.of(context).textTheme.bodyLarge!.color),
            ),
          ),
          PopupMenuItem(
            padding: EdgeInsets.symmetric(vertical: 0, horizontal: 8),
            value: 'api-keys',
            child: Text(
              'Manage your API keys',
              style: Theme.of(context).textTheme.bodyMedium!.copyWith(
                  color: Theme.of(context).textTheme.bodyLarge!.color),
            ),
          ),
          PopupMenuItem(
            padding: EdgeInsets.symmetric(vertical: 0, horizontal: 8),
            value: 'sign-out',
            child: Text(
              'Sign out',
              style: Theme.of(context).textTheme.bodyMedium!.copyWith(
                  color: Theme.of(context).textTheme.bodyLarge!.color),
            ),
          ),
        ],
        icon: Avatar(
          key: Key('user_avatar'),
          photoUrl: photoUrl,
          radius: 33,
          borderColor: Theme.of(context).secondaryHeaderColor,
          borderWidth: 2.0,
        ),
        onSelected: (value) async {
          // Handle menu selection
          switch (value) {
            case 'account':
              // Navigate to the account page.
              context.go('/account');
              break;
            case 'subscription':
              // Navigate to the subscriptions page.
              launchUrl(
                  Uri.parse('https://cannlytics.com/account/subscriptions'));
              break;
            case 'api-keys':
              // Navigate to the API keys page.
              launchUrl(Uri.parse('https://cannlytics.com/account/api-keys'));
              break;
            case 'sign-out':
              // Sign out.
              final logout = await InterfaceUtils.showAlertDialog(
                context: context,
                title: 'Are you sure that you want to sign out?',
                cancelActionText: 'Cancel',
                defaultActionText: 'Sign out',
                primaryActionColor:
                    isDark ? DarkColors.orange : LightColors.orange,
              );
              if (logout == true) {
                await ref.read(authProvider).signOut();
              }
              break;
          }
        },
      ),
    );
  }
}

// Cannlytics Data
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 4/14/2023
// Updated: 4/16/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Flutter imports:
import 'package:flutter/material.dart';

// Package imports:
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

// Project imports:
import 'package:cannlytics_data/constants/design.dart';
import 'package:cannlytics_data/constants/theme.dart';
import 'package:cannlytics_data/services/auth_service.dart';
import 'package:cannlytics_data/ui/main/dashboard_controller.dart';
import 'package:cannlytics_data/widgets/buttons/custom_text_button.dart';
import 'package:cannlytics_data/widgets/buttons/primary_button.dart';
import 'package:cannlytics_data/widgets/dialogs/auth_dialogs.dart';
import 'package:cannlytics_data/widgets/images/avatar.dart';

/// Dashboard header.
class DashboardHeader extends ConsumerWidget with PreferredSizeWidget {
  DashboardHeader({Key? key}) : super(key: key);

  @override
  Size get preferredSize => AppBar().preferredSize;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    // Listen to the current user.
    final user = ref.watch(authProvider).currentUser;

    // Get the theme.
    final themeMode = ref.watch(themeModeProvider);
    final bool isDark = themeMode == ThemeMode.dark;

    // Render the widget.
    return AppBar(
      // Menu button.
      leading: Responsive.isMobile(context)
          ? null
          : IconButton(
              onPressed: () {
                ref.read(sideMenuOpen.notifier).state = !ref.read(sideMenuOpen);
              },
              icon: Icon(Icons.menu),
            ),

      // Title.
      centerTitle: false,
      titleSpacing: 0,
      title: Row(
        children: [
          GestureDetector(
            onTap: () => context.go('/'),
            child: Image.asset(
              isDark
                  ? 'assets/images/logos/cannlytics_logo_with_text_dark.png'
                  : 'assets/images/logos/cannlytics_logo_with_text_light.png',
              height: 33,
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

        // User profile image.
        if (user != null)
          Padding(
            padding: EdgeInsets.only(top: 8, bottom: 8, right: 8),
            child: InkWell(
              onTap: () => context.go('/account'),
              customBorder: CircleBorder(),
              child: Avatar(
                photoUrl: user!.photoURL ?? 'https://robohash.org/${user.uid}',
                radius: 33,
                borderColor: Theme.of(context).secondaryHeaderColor,
                borderWidth: 1.0,
              ),
            ),
          ),
      ],
    );
  }
}

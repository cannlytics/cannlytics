// Cannlytics Data
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 4/14/2023
// Updated: 5/24/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Flutter imports:
import 'package:cannlytics_data/constants/colors.dart';
import 'package:flutter/material.dart';

// Package imports:
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:package_info_plus/package_info_plus.dart';

// Project imports:
import 'package:cannlytics_data/common/buttons/custom_text_button.dart';
import 'package:cannlytics_data/common/buttons/primary_button.dart';
import 'package:cannlytics_data/common/dialogs/auth_dialogs.dart';
import 'package:cannlytics_data/common/images/avatar.dart';
import 'package:cannlytics_data/constants/design.dart';
import 'package:cannlytics_data/constants/theme.dart';
import 'package:cannlytics_data/services/auth_service.dart';
import 'package:cannlytics_data/ui/dashboard/dashboard_controller.dart';

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
              // FIXME: Prefer to use SVG.
              child: Image.asset(
                isDark
                    ? 'assets/images/logos/cannlytics_logo_with_text_dark.png'
                    : 'assets/images/logos/cannlytics_logo_with_text_light.png',
                height: 33,
              ),
            ),
          gapW4,
          Tooltip(
            message:
                'This is a test release. Please bear in mind\nthat the data is incomplete and not up-to-date.\nPlease contact dev@cannlytics.com \nwith all of your concerns. Please use at your\nown discretion.',
            preferBelow: false,
            child: TestBadge(isDark: isDark),
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
                photoUrl: user.photoURL ?? 'https://robohash.org/${user.uid}',
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

/// Indicator for beta features.
class TestBadge extends StatelessWidget {
  final bool isDark;

  const TestBadge({Key? key, required this.isDark}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: EdgeInsets.symmetric(horizontal: 12, vertical: 6),
      decoration: BoxDecoration(
        color: isDark ? Color(0xFFFFCC80) : Color(0xFFFFB300),
        borderRadius: BorderRadius.circular(16),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(
            Icons.warning_amber_outlined,
            color: LightColors.text,
            size: 16,
          ),
          SizedBox(width: 4),
          Text(
            'Test Version ',
            style: Theme.of(context)
                .textTheme
                .bodySmall!
                .copyWith(color: LightColors.text),
          ),
          FutureBuilder<String>(
            future: getVersionNumber(),
            builder: (BuildContext context, AsyncSnapshot<String> snapshot) {
              if (snapshot.hasData && snapshot.data != null) {
                return Text(
                  snapshot.data ?? '',
                  style: Theme.of(context)
                      .textTheme
                      .bodySmall!
                      .copyWith(color: LightColors.text),
                );
              } else if (snapshot.hasError) {
                return gapW2;
              } else {
                return gapW2;
              }
            },
          )
        ],
      ),
    );
  }

  /// Get app version number.
  Future<String> getVersionNumber() async {
    PackageInfo packageInfo = await PackageInfo.fromPlatform();
    List<String> parts = packageInfo.version.split('.');
    String truncatedVersion = parts[0] + '.' + parts[1];
    return truncatedVersion;
  }
}

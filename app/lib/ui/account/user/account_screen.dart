// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 2/17/2023
// Updated: 3/9/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Flutter imports:
import 'package:cannlytics_app/services/theme_service.dart';
import 'package:cannlytics_app/widgets/buttons/primary_button.dart';
import 'package:cannlytics_app/widgets/buttons/secondary_button.dart';
import 'package:cannlytics_app/widgets/cards/responsive_card.dart';
import 'package:flutter/material.dart';

// Package imports:
import 'package:firebase_auth/firebase_auth.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

// Project imports:
import 'package:cannlytics_app/constants/design.dart';
import 'package:cannlytics_app/constants/theme.dart';
import 'package:cannlytics_app/models/common/user.dart';
import 'package:cannlytics_app/services/auth_service.dart';
import 'package:cannlytics_app/ui/account/user/account_controller.dart';
import 'package:cannlytics_app/ui/layout/header.dart';
import 'package:cannlytics_app/widgets/buttons/custom_text_button.dart';
import 'package:cannlytics_app/widgets/dialogs/alert_dialog_ui.dart';
import 'package:cannlytics_app/widgets/dialogs/alert_dialogs.dart';
import 'package:cannlytics_app/widgets/images/avatar.dart';
import 'package:cannlytics_app/widgets/layout/shimmer.dart';

/// Screen for the user to manage their account.
class AccountScreen extends StatelessWidget {
  const AccountScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: CustomScrollView(
        slivers: [
          // App header.
          const SliverToBoxAdapter(child: AppHeader()),

          // Account management.
          SliverToBoxAdapter(child: AccountManagement()),
        ],
      ),
    );
  }
}

/// Dashboard navigation cards.
class AccountManagement extends ConsumerWidget {
  const AccountManagement({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    // Listen to the account state,
    final state = ref.watch(accountProvider);

    // Dynamic screen width.
    final screenWidth = MediaQuery.of(context).size.width;

    // // Get the theme.
    // final themeMode = ref.watch(themeModeProvider);
    // final bool isDark = themeMode == ThemeMode.dark;

    // Listen to the current user.
    ref.listen<AsyncValue>(
      accountProvider,
      (_, state) => state.showAlertDialogOnError(context),
    );
    final user = ref.watch(authProvider).currentUser;

    // User photo choice.
    Widget _userPhoto = InkWell(
      customBorder: const CircleBorder(),
      splashColor: AppColors.accent1,
      onTap: state.isLoading
          ? null
          : () async {
              await ref.read(accountProvider.notifier).changePhoto();
            },
      child: ShimmerLoading(
        isLoading: state.isLoading,
        child: Avatar(
          photoUrl:
              user!.photoURL ?? 'https://cannlytics.com/robohash/${user.uid}',
          radius: 60,
          borderColor: Theme.of(context).secondaryHeaderColor,
          borderWidth: 1.0,
        ),
      ),
    );

    // Render the widget.
    return Padding(
      padding: EdgeInsets.only(
        left: sliverHorizontalPadding(screenWidth),
        right: sliverHorizontalPadding(screenWidth),
        top: 24,
      ),
      child: PreferredSize(
        preferredSize: const Size.fromHeight(130.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          mainAxisAlignment: MainAxisAlignment.start,
          children: [
            ...[
              // User photo.
              _userPhoto,
              gapH8,

              Row(
                children: [
                  // Reset password.
                  SecondaryButton(
                    // isDark: isDark,
                    text: 'Reset password',
                    onPressed: state.isLoading
                        ? null
                        : () {
                            context.go('/account/reset-password');
                          },
                  ),
                  gapW8,

                  // Sign out.
                  SecondaryButton(
                    // isDark: isDark,
                    text: 'Sign out',
                    onPressed: state.isLoading
                        ? null
                        : () async {
                            final logout = await showAlertDialog(
                              context: context,
                              title: 'Are you sure?',
                              cancelActionText: 'Cancel',
                              defaultActionText: 'Sign out',
                            );
                            if (logout == true) {
                              await ref
                                  .read(accountProvider.notifier)
                                  .signOut();
                              context.go('/sign-in');
                            }
                          },
                  ),
                ],
              ),

              // Account information
              SizedBox(
                // width: double.infinity,
                child: Card(
                  // color: isDark ? AppColors.neutral5 : AppColors.neutral2,
                  margin: EdgeInsets.symmetric(vertical: 16),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(3),
                  ),
                  child: Padding(
                    padding: EdgeInsets.symmetric(vertical: 21, horizontal: 16),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        // Title
                        Text(
                          'Account Information',
                          style:
                              Theme.of(context).textTheme.titleMedium!.copyWith(
                                    color: Theme.of(context)
                                        .textTheme
                                        .titleLarge!
                                        .color,
                                  ),
                        ),
                        gapH12,

                        // User name.
                        // TODO: Change user name.
                        if (user.displayName != null)
                          Text(
                            'Username: ${user.displayName!}',
                            style: Theme.of(context).textTheme.bodyMedium,
                          ),
                        gapH8,

                        // User email.
                        // TODO: Change email.
                        if (user.email != null)
                          Text(
                            'Email: ${user.email!}',
                            style: Theme.of(context).textTheme.bodyMedium,
                          ),
                        gapH8,

                        // User phone.
                        // TODO: Change user phone.
                        if (user.phoneNumber != null)
                          Text(
                            'Phone: ${user.phoneNumber!}',
                            style: Theme.of(context).textTheme.bodyMedium,
                          ),

                        // TODO: Add phone number.
                        if (user.phoneNumber == null)
                          CustomTextButton(
                            text: 'Add phone number',
                            fontStyle: FontStyle.italic,
                            onPressed: () {
                              // TODO: Add phone number.
                            },
                          ),

                        gapH8,
                      ],
                    ),
                  ),

                  // TODO: Toggle light / dark theme.
                  // ThemeInput(),

                  // TODO: Implement a body for the user to manage their account!
                  // - Reset password.

                  // - View user data:
                  //  * Account created date.
                  //  * Last sign in date.
                  // - View logs.
                  // - View / manage organizations and teams.
                  // - Delete account.

                  // Business:
                  // - state (restrict to Cannlytics-verified states)
                  // - licenses (/admin/create-license and /admin/delete-license)
                  // - license type
                ),
              ),

              // Delete account option.
              // _deleteAccount(context, screenWidth),
              gapH48,
            ],
          ],
        ),
      ),
    );
  }

  Widget _deleteAccount(BuildContext context, double screenWidth) {
    return SizedBox(
      // width: double.infinity,
      child: Card(
        margin: EdgeInsets.symmetric(vertical: 16),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(3),
        ),
        child: Padding(
          padding: EdgeInsets.symmetric(vertical: 21, horizontal: 16),
          child: Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Icon(
                Icons.error_outline,
                color: Colors.red,
              ),
              gapW16,
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Deleting this account will also remove your account data.',
                    style: Theme.of(context).textTheme.titleMedium!.copyWith(
                          color: Theme.of(context).textTheme.titleLarge!.color,
                        ),
                  ),
                  Text(
                      'Make sure that you have exported your data if you want to keep your data.'),
                  gapH12,
                  PrimaryButton(
                    backgroundColor: Colors.red,
                    text: 'Delete account',
                    onPressed: () {
                      print('TODO: DELETE ACCOUNT!');
                    },
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }
}

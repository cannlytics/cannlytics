// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 2/17/2023
// Updated: 2/22/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Flutter imports:
import 'package:flutter/material.dart';

// Package imports:
import 'package:firebase_auth/firebase_auth.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

// Project imports:
import 'package:cannlytics_app/constants/colors.dart';
import 'package:cannlytics_app/constants/design.dart';
import 'package:cannlytics_app/models/user.dart';
import 'package:cannlytics_app/services/auth_service.dart';
import 'package:cannlytics_app/ui/account/account_controller.dart';
import 'package:cannlytics_app/ui/general/header.dart';
import 'package:cannlytics_app/utils/dialogs/alert_dialog_ui.dart';
import 'package:cannlytics_app/utils/dialogs/alert_dialogs.dart';
import 'package:cannlytics_app/utils/strings/string_hardcoded.dart';
import 'package:cannlytics_app/widgets/buttons/action_text_button.dart';
import 'package:cannlytics_app/widgets/images/avatar.dart';

/// Screen for the user to manage their account.
class AccountScreen extends ConsumerWidget {
  const AccountScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    ref.listen<AsyncValue>(
      accountProvider,
      (_, state) => state.showAlertDialogOnError(context),
    );
    final user = ref.watch(authServiceProvider).currentUser;
    return Scaffold(
      body: CustomScrollView(
        slivers: [
          // App header.
          const SliverToBoxAdapter(child: AppHeader()),

          // Account management.
          SliverToBoxAdapter(child: AccountManagement(user: user)),
        ],
      ),
      // TODO: Implement a body for the user to manage their account!
      // - Reset password.
      // - Change user email.
      // - Change user phone.
      // - Change user name.
      // - Change user photo.
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
    );
  }
}

/// Dashboard navigation cards.
class AccountManagement extends ConsumerWidget {
  const AccountManagement({
    Key? key,
    required this.user,
  }) : super(key: key);
  final User? user;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final state = ref.watch(accountProvider);
    final screenWidth = MediaQuery.of(context).size.width;
    // final crossAxisCount =
    //     (screenWidth >= Breakpoints.twoColLayoutMinWidth) ? 3 : 2;
    return Padding(
      padding: EdgeInsets.only(
        left: sliverHorizontalPadding(screenWidth),
        right: sliverHorizontalPadding(screenWidth),
        top: 24,
      ),
      child: PreferredSize(
        preferredSize: const Size.fromHeight(130.0),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.start,
          children: [
            if (user != null) ...[
              // User photo.
              InkWell(
                customBorder: const CircleBorder(),
                splashColor: AppColors.accent1,
                onTap: state.isLoading
                    ? null
                    : () async {
                        ref.read(accountProvider.notifier).changePhoto();
                      },
                child: Avatar(
                  photoUrl: user!.photoURL,
                  radius: 60,
                  borderColor: Colors.black54,
                  borderWidth: 1.0,
                ),
              ),
              gapH8,

              // User name.
              // TODO: Change user name.
              if (user!.displayName != null)
                Text(
                  'Username: ${user!.displayName!}',
                  style: const TextStyle(color: AppColors.neutral6),
                ),
              gapH8,

              // User email.
              // TODO: Change email.
              if (user!.email != null)
                Text(
                  'Email: ${user!.email!}',
                  style: const TextStyle(color: AppColors.neutral6),
                ),
              gapH8,

              // User phone.
              // TODO: Change user phone.
              if (user!.phoneNumber != null)
                Text(
                  'Phone: ${user!.phoneNumber!}',
                  style: const TextStyle(color: AppColors.neutral6),
                ),
              gapH8,

              // Sign out.
              ActionTextButton(
                text: 'Logout'.hardcoded,
                onPressed: state.isLoading
                    ? null
                    : () async {
                        final logout = await showAlertDialog(
                          context: context,
                          title: 'Are you sure?'.hardcoded,
                          cancelActionText: 'Cancel'.hardcoded,
                          defaultActionText: 'Logout'.hardcoded,
                        );
                        if (logout == true) {
                          ref.read(accountProvider.notifier).signOut();
                        }
                      },
              ),
            ],
          ],
        ),
      ),
    );
  }
}

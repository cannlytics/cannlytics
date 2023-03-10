// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 2/17/2023
// Updated: 3/9/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Flutter imports:
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
import 'package:cannlytics_app/ui/general/header.dart';
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
  const AccountManagement({
    Key? key,
    // required this.user,
  }) : super(key: key);
  // final User? user;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    // Listen to the account state,
    final state = ref.watch(accountProvider);

    // Dynamic screen width.
    final screenWidth = MediaQuery.of(context).size.width;

    // Listen to the current user.
    ref.listen<AsyncValue>(
      accountProvider,
      (_, state) => state.showAlertDialogOnError(context),
    );
    final user = ref.watch(authProvider).currentUser;

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
                        await ref.read(accountProvider.notifier).changePhoto();
                      },
                child: ShimmerLoading(
                  isLoading: state.isLoading,
                  child: Avatar(
                    photoUrl: user.photoURL,
                    radius: 60,
                    borderColor: Theme.of(context).secondaryHeaderColor,
                    borderWidth: 1.0,
                  ),
                ),
              ),
              gapH8,

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
                  onPressed: () {
                    // TODO: Add phone number.
                  },
                ),
              gapH8,

              // TODO: Toggle light / dark theme.
              // ThemeInput(),

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

              // Sign out.
              CustomTextButton(
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

/// TODO: Light / dark theme input.
// class ThemeInput extends StatelessWidget {
//   const ThemeInput({super.key});

//   @override
//   Widget build(BuildContext context) {
//     return Consumer(builder: (context, ref, child) {
//       final theme = ref.watch(themeModeProvider);
//       return Row(
//         mainAxisAlignment: MainAxisAlignment.end,
//         children: [
//           Padding(
//             padding: const EdgeInsets.only(top: 6, right: 24, bottom: 6),
//             child: IconButton(
//               splashRadius: 18,
//               onPressed: () {
//                 // Toggle light / dark theme.
//                 ref.read(themeModeProvider.notifier).state =
//                     theme == ThemeMode.light ? ThemeMode.dark : ThemeMode.light;
//               },
//               icon: Icon(
//                 theme == ThemeMode.dark ? Icons.dark_mode : Icons.light_mode,
//                 color: AppColors.neutral4,
//               ),
//             ),
//           ),
//         ],
//       );
//     });
//   }
// }

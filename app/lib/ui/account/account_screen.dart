// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 2/17/2023
// Updated: 2/18/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>
import 'package:cannlytics_app/routing/menu.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:cannlytics_app/widgets/action_text_button.dart';
import 'package:cannlytics_app/widgets/avatar.dart';
import 'package:cannlytics_app/services/auth_service.dart';
import 'package:cannlytics_app/ui/account/account_controller.dart';
import 'package:cannlytics_app/utils/strings/string_hardcoded.dart';
import 'package:cannlytics_app/utils/dialogs/alert_dialogs.dart';
import 'package:cannlytics_app/utils/dialogs/alert_dialog_ui.dart';

class AccountScreen extends ConsumerWidget {
  const AccountScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    ref.listen<AsyncValue>(
      accountProvider,
      (_, state) => state.showAlertDialogOnError(context),
    );
    final state = ref.watch(accountProvider);
    final user = ref.watch(authServiceProvider).currentUser;
    return const Scaffold(
      // appBar: AppBar(
      //   title: state.isLoading
      //       ? const CircularProgressIndicator()
      //       : Text('Account'.hardcoded),
      //   actions: [
      //     ActionTextButton(
      //       text: 'Logout'.hardcoded,
      //       onPressed: state.isLoading
      //           ? null
      //           : () async {
      //               final logout = await showAlertDialog(
      //                 context: context,
      //                 title: 'Are you sure?'.hardcoded,
      //                 cancelActionText: 'Cancel'.hardcoded,
      //                 defaultActionText: 'Logout'.hardcoded,
      //               );
      //               if (logout == true) {
      //                 ref.read(accountProvider.notifier).signOut();
      //               }
      //             },
      //     ),
      //   ],
      //   bottom: PreferredSize(
      //     preferredSize: const Size.fromHeight(130.0),
      //     child: Column(
      //       children: [
      //         if (user != null) ...[
      //           Avatar(
      //             photoUrl: user.photoURL,
      //             radius: 50,
      //             borderColor: Colors.black54,
      //             borderWidth: 2.0,
      //           ),
      //           const SizedBox(height: 8),
      //           if (user.displayName != null)
      //             Text(
      //               user.displayName!,
      //               style: const TextStyle(color: Colors.white),
      //             ),
      //           const SizedBox(height: 8),
      //         ],
      //       ],
      //     ),
      //   ),
      // ),
      body: CustomScrollView(
        slivers: [
          // App header.
          SliverToBoxAdapter(child: AppHeader()),

          // FIXME: Add account management here!
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

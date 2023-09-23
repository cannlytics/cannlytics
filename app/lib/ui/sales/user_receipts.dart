// Cannlytics Data
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 6/15/2023
// Updated: 9/3/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Flutter imports:
import 'package:flutter/material.dart';

// Package imports:
import 'package:flutter_riverpod/flutter_riverpod.dart';

// Project imports:
import 'package:cannlytics_data/common/dialogs/auth_dialog.dart';
import 'package:cannlytics_data/common/layout/sign_in_placeholder.dart';
import 'package:cannlytics_data/ui/account/account_controller.dart';
import 'package:cannlytics_data/ui/sales/user_receipts_table.dart';

/// User receipts user interface.
class UserReceiptsInterface extends ConsumerWidget {
  const UserReceiptsInterface({super.key, this.tabController});

  // Parameters.
  final TabController? tabController;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    // Render placeholder if user is not signed in.
    final user = ref.watch(userProvider).value;
    if (user == null) return _noUser(context);

    // Render table of user receipts.
    return Scrollbar(
      child: SingleChildScrollView(
        child: Padding(
          padding: EdgeInsets.only(left: 16, right: 16, top: 24),
          child: Column(children: [UserReceiptsTable()]),
        ),
      ),
    );
  }

  /// No user interface.
  Widget _noUser(BuildContext context) {
    return Column(
      mainAxisAlignment: MainAxisAlignment.start,
      crossAxisAlignment: CrossAxisAlignment.start,
      mainAxisSize: MainAxisSize.min,
      children: [
        SignInPlaceholder(
          titleText: 'Your receipts',
          imageUrl:
              'https://firebasestorage.googleapis.com/v0/b/cannlytics.appspot.com/o/public%2Fimages%2Flogos%2Fbud_spender.png?alt=media&token=e0de707b-9c18-44b9-9944-b36fcffd9fd3',
          mainText: 'Sign in to manage your receipts',
          subTitle:
              'If you are signed in, then you can manage your receipts here.',
          onButtonPressed: () {
            showDialog(
              context: context,
              builder: (BuildContext context) => SignInDialog(isSignUp: false),
            );
          },
          buttonText: 'Sign in',
        ),
      ],
    );
  }
}

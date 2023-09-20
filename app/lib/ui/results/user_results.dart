// Cannlytics Data
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 6/13/2023
// Updated: 9/1/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Flutter imports:
import 'package:flutter/material.dart';

// Package imports:
import 'package:flutter_riverpod/flutter_riverpod.dart';

// Project imports:
import 'package:cannlytics_data/common/dialogs/auth_dialog.dart';
import 'package:cannlytics_data/common/layout/sign_in_placeholder.dart';
import 'package:cannlytics_data/ui/account/account_controller.dart';
import 'package:cannlytics_data/ui/results/user_results_table.dart';

/// User lab results user interface.
class UserResultsInterface extends ConsumerWidget {
  const UserResultsInterface({super.key, this.tabController});

  // Parameters.
  final TabController? tabController;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    // Render placeholder if user is not signed in.
    final user = ref.watch(userProvider).value;
    if (user == null)
      return SingleChildScrollView(
        child: Padding(
          padding: EdgeInsets.only(left: 16, right: 16, top: 24),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.start,
            children: [
              SignInPlaceholder(
                titleText: 'Your results',
                imageUrl:
                    'https://firebasestorage.googleapis.com/v0/b/cannlytics.appspot.com/o/public%2Fimages%2Flogos%2Fcannlytics_coa_doc.png?alt=media&token=1871dde9-82db-4342-a29d-d373671491b3',
                mainText: 'Sign in to manage your results',
                subTitle:
                    'If you are signed in, then you can manage your results here.',
                onButtonPressed: () {
                  showDialog(
                    context: context,
                    builder: (BuildContext context) =>
                        SignInDialog(isSignUp: false),
                  );
                },
                buttonText: 'Sign in',
              ),
            ],
          ),
        ),
      );

    // Render table of user results.
    return Scrollbar(
      child: SingleChildScrollView(
        primary: true,
        child: Padding(
          padding: EdgeInsets.only(left: 16, right: 16, top: 24),
          child: Column(children: [UserResultsTable()]),
        ),
      ),
    );
  }
}

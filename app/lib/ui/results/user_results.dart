// Cannlytics Data
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 6/13/2023
// Updated: 8/6/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Flutter imports:
// import 'package:cannlytics_data/services/api_service.dart';
// import 'package:cannlytics_data/services/storage_service.dart';
import 'package:cannlytics_data/common/dialogs/auth_dialog.dart';
import 'package:cannlytics_data/ui/results/user_results_table.dart';
import 'package:flutter/material.dart';
// import 'package:flutter/services.dart';

// Package imports:
import 'package:flutter_riverpod/flutter_riverpod.dart';

// Project imports:
import 'package:cannlytics_data/common/buttons/download_button.dart';
import 'package:cannlytics_data/common/buttons/primary_button.dart';
import 'package:cannlytics_data/constants/colors.dart';
import 'package:cannlytics_data/constants/design.dart';
import 'package:cannlytics_data/models/lab_result.dart';
import 'package:cannlytics_data/services/download_service.dart';
import 'package:cannlytics_data/ui/account/account_controller.dart';
import 'package:cannlytics_data/ui/results/result_card.dart';
import 'package:cannlytics_data/ui/results/results_service.dart';
import 'package:cannlytics_data/utils/utils.dart';

/// User lab results user interface.
class UserResultsInterface extends ConsumerWidget {
  const UserResultsInterface({super.key, this.tabController});

  // Parameters.
  final TabController? tabController;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    // Listen to the user's results.
    final asyncData = ref.watch(userResults);

    // Render the data.
    return asyncData.when(
      // Loading state.
      loading: () => _body(
        context,
        children: [_placeholder(context, ref)],
      ),

      // Error state.
      error: (err, stack) => _errorMessage(context, ref, err.toString()),

      // Data loaded state.
      data: (items) => (items.length == 0)
          ? _body(
              context,
              children: [_placeholder(context, ref)],
            )
          // FIXME: Replace with a table!
          // : UserResultsGrid(items: items),
          : SingleChildScrollView(
              child: Padding(
                padding: EdgeInsets.only(
                  left: 16,
                  right: 16,
                  top: 24,
                ),
                child: Column(
                  children: [
                    UserResultsTable(),
                  ],
                ),
              ),
            ),
    );
  }

  /// The main dynamic body of the screen.
  Widget _body(BuildContext context, {required List<Widget> children}) {
    return SingleChildScrollView(
      child: Column(
        children: [
          Container(
            height: MediaQuery.of(context).size.height,
            child: Column(
              mainAxisAlignment: MainAxisAlignment.start,
              crossAxisAlignment: CrossAxisAlignment.start,
              mainAxisSize: MainAxisSize.min,
              children: children,
            ),
          ),
        ],
      ),
    );
  }

  /// Message displayed when there are no user results.
  Widget _placeholder(BuildContext context, WidgetRef ref) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            // Title.
            Row(
              children: [
                SelectableText(
                  'Your results',
                  style: Theme.of(context).textTheme.titleLarge,
                ),
              ],
            ),
            gapH16,

            // Image.
            Padding(
              padding: EdgeInsets.only(top: 16),
              child: Image.network(
                'https://firebasestorage.googleapis.com/v0/b/cannlytics.appspot.com/o/public%2Fimages%2Flogos%2Fcannlytics_coa_doc.png?alt=media&token=1871dde9-82db-4342-a29d-d373671491b3',
                // width: 128,
                height: 128,
                fit: BoxFit.cover,
              ),
            ),

            // Text.
            Container(
              width: 540,
              child: Column(
                children: <Widget>[
                  SelectableText(
                    'Sign in to track your results',
                    textAlign: TextAlign.center,
                    style: TextStyle(
                        fontSize: 20,
                        color: Theme.of(context).textTheme.titleLarge!.color),
                  ),
                  SelectableText(
                    'If you are signed in, then we will save your parsed results.\n You will be able to access them here.',
                    textAlign: TextAlign.center,
                    style: Theme.of(context).textTheme.bodyMedium,
                  ),
                  gapH12,
                  PrimaryButton(
                    text: 'Sign in',
                    onPressed: () {
                      showDialog(
                        context: context,
                        builder: (BuildContext context) {
                          return SignInDialog(isSignUp: false);
                        },
                      );
                    },
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  /// Message displayed when an error occurs.
  Widget _errorMessage(
    BuildContext context,
    WidgetRef ref,
    String? message,
  ) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            // Reset button.
            Row(
              mainAxisAlignment: MainAxisAlignment.end,
              children: [
                IconButton(
                  icon: Icon(
                    Icons.refresh,
                    color: Theme.of(context).textTheme.bodyMedium!.color,
                  ),
                  onPressed: () {
                    ref.read(coaParser.notifier).clear();
                  },
                ),
              ],
            ),

            // Image.
            Padding(
              padding: EdgeInsets.only(top: 16),
              child: ClipOval(
                child: Image.network(
                  'https://firebasestorage.googleapis.com/v0/b/cannlytics.appspot.com/o/public%2Fimages%2Flogos%2Fbud_spender.png?alt=media&token=e0de707b-9c18-44b9-9944-b36fcffd9fd3',
                  width: 128,
                  height: 128,
                  fit: BoxFit.cover,
                ),
              ),
            ),

            // Text.
            Container(
              width: 540,
              child: Column(
                children: <Widget>[
                  SelectableText(
                    'An error occurred while retrieving your receipts',
                    textAlign: TextAlign.center,
                    style: TextStyle(
                        fontSize: 20,
                        color: Theme.of(context).textTheme.titleLarge!.color),
                  ),
                  // DEV:
                  SelectableText(
                    message ?? '',
                    textAlign: TextAlign.center,
                    style: Theme.of(context).textTheme.bodyMedium,
                  ),
                  // PRODUCTION:
                  // SelectableText(
                  //   'An unknown error occurred while retrieving your receipts. Please report this issue on GitHub or to dev@cannlytics.com to get a human to help ASAP.',
                  //   textAlign: TextAlign.center,
                  //   style: Theme.of(context).textTheme.bodyMedium,
                  // ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}

/// A grid of the user's results.
class UserResultsGrid extends ConsumerWidget {
  const UserResultsGrid({super.key, required this.items});

  // Parameters.
  final List<Map?> items;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    // Listen to the user.
    final user = ref.watch(userProvider).value;

    // Get the theme.
    bool isDark = Theme.of(context).brightness == Brightness.dark;

    /// Download function.
    var _onDownload = (dynamic item) {
      // Show a downloading notification.
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(
            'Preparing your download...',
            style: Theme.of(context).textTheme.bodyMedium,
          ),
          duration: Duration(seconds: 2),
          backgroundColor: isDark ? DarkColors.green : LightColors.lightGreen,
          showCloseIcon: true,
        ),
      );

      // Download the data.
      DownloadService.downloadData(
        [item!],
        '/api/data/coas/download',
      );
    };

    /// Share function.
    // Future<void> _onShare(dynamic item) async {
    //   // Show a 'preparing' snackbar notification.
    //   ScaffoldMessenger.of(context).showSnackBar(
    //     SnackBar(
    //       content: Text(
    //         'Preparing your shareable link...',
    //         style: Theme.of(context).textTheme.bodyMedium,
    //       ),
    //       duration: Duration(seconds: 2),
    //       backgroundColor: isDark ? DarkColors.green : LightColors.lightGreen,
    //       showCloseIcon: true,
    //     ),
    //   );

    //   // Get the data for sharing (similar to download).
    //   Map response = await APIService.apiRequest(
    //     '/api/data/coas/download',
    //     data: {
    //       'data': [item!]
    //     },
    //   );

    //   // Get the download URL from the response.
    //   String? shareableUrl =
    //       await StorageService.getDownloadUrl(response['file_ref']);

    //   if (shareableUrl != null) {
    //     // Copy the URL to the clipboard.
    //     await Clipboard.setData(ClipboardData(text: shareableUrl));

    //     // Show a 'copied to clipboard' snackbar notification.
    //     ScaffoldMessenger.of(context).showSnackBar(
    //       SnackBar(
    //         content: Text(
    //           'Link copied to clipboard!',
    //           style: Theme.of(context).textTheme.bodyMedium,
    //         ),
    //         duration: Duration(seconds: 2),
    //         backgroundColor: isDark ? DarkColors.green : LightColors.lightGreen,
    //         showCloseIcon: true,
    //       ),
    //     );
    //   } else {
    //     // Handle errors or null URLs here.
    //     ScaffoldMessenger.of(context).showSnackBar(
    //       SnackBar(
    //         content: Text(
    //           'Failed to generate shareable link.',
    //           style: Theme.of(context).textTheme.bodyMedium,
    //         ),
    //         duration: Duration(seconds: 2),
    //         backgroundColor:
    //             isDark ? DarkColors.darkOrange : LightColors.darkOrange,
    //         showCloseIcon: true,
    //       ),
    //     );
    //   }
    // }

    /// Delete function.
    var _onDelete = (dynamic item) async {
      final delete = await InterfaceUtils.showAlertDialog(
        context: context,
        title: 'Are you sure that you want to delete this result?',
        cancelActionText: 'Cancel',
        defaultActionText: 'Delete',
        primaryActionColor: Colors.redAccent,
      );
      if (delete == true) {
        ref.read(resultService).deleteResult(item!['id']);
      }
    };

    /// Listen to the selected items for downloading.
    final downloadItems = ref.watch(resultsFilterProvider).value;

    // Render the card.
    return Column(
      mainAxisAlignment: MainAxisAlignment.start,
      crossAxisAlignment: CrossAxisAlignment.start,
      mainAxisSize: MainAxisSize.min,
      children: <Widget>[
        // Title.
        Padding(
          padding:
              const EdgeInsets.only(left: 16.0, right: 16, top: 16, bottom: 8),
          child: Row(
            children: [
              SelectableText(
                'Your results',
                style: Theme.of(context).textTheme.titleLarge,
              ),
              Spacer(),

              // Download all button.
              if (user != null)
                DownloadButton(
                  items: downloadItems ?? items,
                  url: '/api/data/coas/download',
                ),
            ],
          ),
        ),
        gapH12,

        // Grid of results.
        Expanded(
          child: GridView.builder(
            shrinkWrap: true,
            gridDelegate: const SliverGridDelegateWithMaxCrossAxisExtent(
              maxCrossAxisExtent: 540.0,
              mainAxisSpacing: 10.0,
              crossAxisSpacing: 10.0,
            ),
            itemCount: items.length,
            itemBuilder: (context, index) {
              final item = items[index];
              return ResultCard(
                item: LabResult.fromMap(item ?? {}),
                onDownload: () => _onDownload(item),
                onDelete: () => _onDelete(item),
                // onShare: () => _onShare(item),
              );
            },
          ),
        ),
        gapH48,
      ],
    );
  }
}

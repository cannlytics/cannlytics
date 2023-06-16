// Cannlytics Data
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 6/15/2023
// Updated: 6/15/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>
import 'package:cannlytics_data/common/cards/scrollable_card.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

/// User receipts user interface.
class UserReceiptsInterface extends ConsumerWidget {
  const UserReceiptsInterface({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return ScrollableCard(
      children: <Widget>[
        // FIXME: Render sign in placeholder if no user.

        // Title.
        Row(
          children: [
            Text(
              'Your receipts',
              style: Theme.of(context).textTheme.titleLarge,
            ),

            // Receipts tabs.
            Spacer(),
            // TabToggleButtons(),
          ],
        ),

        // Placeholder for when there are no receipts.
        _userReceiptsPlaceholder(context),

        // TODO: Grid of user receipts.

        // TODO: Table of user receipts.
        // UserReceiptsList(),
      ],
    );
  }

  /// Message displayed when there are no user receipts.
  Widget _userReceiptsPlaceholder(BuildContext context) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            // Image.
            Padding(
              padding: EdgeInsets.only(top: 16),
              child: ClipOval(
                child: Image.network(
                  'https://firebasestorage.googleapis.com/v0/b/cannlytics.appspot.com/o/assets%2Fimages%2Fai%2FCannlytics_a_scroll_with_robot_arms_and_a_disguise_for_a_face_a_57549317-7365-4350-9b7b-84fd7421b103.png?alt=media&token=72631010-56c8-4981-a936-58b89294f336',
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
                    'This feature is coming soon!',
                    textAlign: TextAlign.center,
                    style: TextStyle(
                        fontSize: 20,
                        color: Theme.of(context).textTheme.titleLarge!.color),
                  ),
                  SelectableText(
                    'If you are signed in, then we will save your parsed receipts and you will be able to access them here in the near future. If you need your data pronto, then please email dev@cannlytics.com to get any data associated with your account. Thank you for your patience as we implement this feature.',
                    textAlign: TextAlign.center,
                    style: Theme.of(context).textTheme.bodySmall,
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}

/// List of user's results.
class UserReceiptsList extends StatelessWidget {
  final bool isLoading =
      false; // This would typically come from your state management system

  // FIXME: Use LabResultItem instead.

  // TODO: Download all results.

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      child: Column(
        children: <Widget>[
          Visibility(
            visible: isLoading,
            child: CircularProgressIndicator(),
          ),
          Visibility(
            visible: !isLoading,
            child: DataTable(
              columns: const <DataColumn>[
                DataColumn(
                  label: Text(
                    'Column A',
                    style: TextStyle(fontStyle: FontStyle.italic),
                  ),
                ),
                DataColumn(
                  label: Text(
                    'Column B',
                    style: TextStyle(fontStyle: FontStyle.italic),
                  ),
                ),
                // Add more DataColumn widgets here for each column in your data
              ],
              rows: const <DataRow>[
                DataRow(
                  cells: <DataCell>[
                    DataCell(Text('Cell A1')),
                    DataCell(Text('Cell B1')),
                  ],
                ),
                // Add more DataRow widgets here for each row in your data
              ],
            ),
          ),
        ],
      ),
    );
  }
}

// Cannlytics Data
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 6/13/2023
// Updated: 6/14/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

/// User lab results user interface.
class UserResultsInterface extends ConsumerWidget {
  const UserResultsInterface({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return SingleChildScrollView(
      child: Column(
        children: [
          // Results list, centered when there are no results, top-aligned otherwise.
          Container(
            height: MediaQuery.of(context).size.height * 0.75,
            child: SingleChildScrollView(
              child: Card(
                margin: EdgeInsets.only(top: 12),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(3),
                ),
                child: Padding(
                  padding: const EdgeInsets.all(16.0),
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.start,
                    crossAxisAlignment: CrossAxisAlignment.start,
                    mainAxisSize: MainAxisSize.min,
                    children: <Widget>[
                      // FIXME: Render sign in placeholder if no user.

                      // Title.
                      Row(
                        children: [
                          Text(
                            'Your lab results',
                            style: Theme.of(context).textTheme.titleLarge,
                          ),

                          // Results tabs.
                          Spacer(),
                          // TabToggleButtons(),
                        ],
                      ),

                      // Placeholder for when there are no results.
                      _userResultsPlaceholder(context),

                      // TODO: Grid of user results.

                      // // Sample results options.
                      // SampleResultsOptions(),

                      // // Sample card template.
                      // SampleCardTemplate(),

                      // // Sample results.
                      // SampleCard(),

                      // TODO: Table of user results.
                      // UserResultsList(),
                    ],
                  ),
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }

  /// Message displayed when there are no user results.
  Widget _userResultsPlaceholder(BuildContext context) {
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
                    'If you are signed in, then we will save your parsed lab results and you will be able to access them here in the near future. If you need your lab results pronto, then please email dev@cannlytics.com to get any data associated with your account. Thank you for your patience as we implement this feature.',
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
class UserResultsList extends StatelessWidget {
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

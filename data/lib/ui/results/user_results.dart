// Cannlytics Data
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 6/13/2023
// Updated: 6/13/2023
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

                      // FIXME: Grid of user results.

                      // // Sample results options.
                      // SampleResultsOptions(),

                      // // Sample card template.
                      // SampleCardTemplate(),

                      // // Sample results.
                      // SampleCard(),

                      // FIXME: Table of user results.
                      UserResultsList(),
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

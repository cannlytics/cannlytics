// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 3/8/2023
// Updated: 3/23/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Flutter imports:
import 'package:cannlytics_app/widgets/layout/main_screen.dart';
import 'package:flutter/material.dart';

// Package imports:
import 'package:dartx/dartx.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_typeahead/flutter_typeahead.dart';
import 'package:go_router/go_router.dart';

// Project imports:
import 'package:cannlytics_app/constants/design.dart';
import 'package:cannlytics_app/models/metrc/strain.dart';
import 'package:cannlytics_app/ui/business/strains/strains_controller.dart';
import 'package:cannlytics_app/ui/layout/footer.dart';
import 'package:cannlytics_app/ui/layout/header.dart';
import 'package:cannlytics_app/widgets/buttons/primary_button.dart';
import 'package:cannlytics_app/widgets/layout/custom_placeholder.dart';
import 'package:cannlytics_app/widgets/tables/table_data.dart';
import 'package:cannlytics_app/widgets/tables/table_form.dart';

/// Strains screen.
class StrainsScreen extends StatelessWidget {
  const StrainsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return MainScreen(
      slivers: [
        // App header.
        const SliverToBoxAdapter(child: AppHeader()),

        // Strains form.
        SliverToBoxAdapter(
          child: TableForm(
            title: 'Strains',
            table: StrainsTable(),
          ),
        ),

        // Footer
        const SliverToBoxAdapter(child: Footer()),
      ],
    );
  }
}

/// Strains table.
/// // TODO: Additional Firestore data:
// - avg. days in veg.
// - stretch
// - notes
// - genetics
// * pest, disease, drought resistance
// - weeks of flower
class StrainsTable extends ConsumerWidget {
  const StrainsTable({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    // Determine the screen size.
    final screenWidth = MediaQuery.of(context).size.width;
    final isWide = screenWidth > Breakpoints.tablet;

    // Get the filtered data.
    final data = ref.watch(filteredStrainsProvider);

    // Define the table headers.
    List<Map> headers = [
      {'name': 'ID', 'key': 'id', 'sort': true},
      {'name': 'Name', 'key': 'name', 'sort': true},
      {'name': 'Testing Status', 'key': 'testing_status', 'sort': true},
      {'name': 'THC Level', 'key': 'thc_level', 'sort': true},
      {'name': 'CBD Level', 'key': 'cbd_level', 'sort': true},
      {'name': 'Indica Percentage', 'key': 'indica_percentage', 'sort': false},
      {'name': 'Sativa Percentage', 'key': 'sativa_percentage', 'sort': false},
    ];

    // Define the cell builder function.
    _buildCells(Strain item) {
      List<dynamic> values = [
        item.id,
        item.name,
        item.testingStatus ?? '',
        item.thcLevel.toString(),
        item.cbdLevel.toString(),
        item.indicaPercentage.toString(),
        item.sativaPercentage.toString(),
      ];
      return values.map((value) {
        return DataCell(
          Text(value),
          onTap: () => context.go('/strains/${item.id}'),
        );
      }).toList();
    }

    // Format the table headers.
    List<DataColumn> tableHeader = <DataColumn>[
      for (Map header in headers)
        DataColumn(
          label: Expanded(
            child: Text(
              header['name'],
              style: TextStyle(fontStyle: FontStyle.italic),
            ),
          ),
          onSort: (columnIndex, sortAscending) {
            var field = headers[columnIndex]['key'];
            var sort = headers[columnIndex]['sort'];
            if (!sort) return;
            var sorted = data;
            if (sortAscending) {
              sorted = data.sortedBy((x) => x.toMap()[field]);
            } else {
              sorted = data.sortedByDescending((x) => x.toMap()[field]);
            }
            ref.read(strainsSortColumnIndex.notifier).state = columnIndex;
            ref.read(strainsSortAscending.notifier).state = sortAscending;
            ref.read(strainsProvider.notifier).setStrains(sorted);
          },
        ),
    ];

    // Get the rows per page.
    final rowsPerPage = ref.watch(strainsRowsPerPageProvider);

    // Get the selected rows.
    List<Strain> selectedRows = ref.watch(selectedStrainsProvider);
    List<String> selectedIds = selectedRows.map((x) => x.id).toList();

    // Get the sorting state.
    final sortColumnIndex = ref.read(strainsSortColumnIndex);
    final sortAscending = ref.read(strainsSortAscending);

    // Build the data table.
    Widget table = PaginatedDataTable(
      // Options.
      showCheckboxColumn: true,
      showFirstLastButtons: true,
      sortColumnIndex: sortColumnIndex,
      sortAscending: sortAscending,
      // Columns
      columns: tableHeader,
      // Style.
      dataRowHeight: 48,
      columnSpacing: 48,
      headingRowHeight: 48,
      horizontalMargin: 12,
      // Pagination.
      availableRowsPerPage: [5, 10, 25, 50, 100],
      rowsPerPage: rowsPerPage,
      onRowsPerPageChanged: (index) {
        ref.read(strainsRowsPerPageProvider.notifier).state = index!;
      },
      // Table.
      source: TableData<Strain>(
        // Table data.
        data: data,

        // Table cells.
        cellsBuilder: _buildCells,

        // Tap on a location.
        onTap: (Strain item) async {
          // await ref.read(locationProvider.notifier).set(item);
          // FIXME: Pass location data to avoid extra API request.
          context.go('/strains/${item.id}');
        },

        // Select a location.
        onSelect: (bool selected, Strain item) {
          if (selected) {
            ref.read(selectedStrainsProvider.notifier).selectStrain(item);
          } else {
            ref.read(selectedStrainsProvider.notifier).unselectStrain(item);
          }
        },

        // Specify selected strains.
        isSelected: (item) => selectedIds.contains(item.id),
      ),
    );

    // Read the controller.
    final _controller = ref.watch(searchController);

    // Define the table actions.
    var actions = Row(
      children: [
        // Search box.
        SizedBox(
          width: 175,
          child: TypeAheadField(
            textFieldConfiguration: TextFieldConfiguration(
              // Controller.
              controller: _controller,

              // Decoration.
              decoration: InputDecoration(
                hintText: 'Search...',
                contentPadding:
                    EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.all(Radius.circular(3)),
                ),
                suffixIcon: _controller.text.isNotEmpty
                    ? GestureDetector(
                        onTap: () {
                          ref.read(searchTermProvider.notifier).state = '';
                          _controller.clear();
                        },
                        child: Icon(Icons.clear),
                      )
                    : null,
              ),
              style: DefaultTextStyle.of(context).style.copyWith(
                    fontStyle: FontStyle.italic,
                  ),
            ),
            // Search engine function.
            suggestionsCallback: (pattern) async {
              ref.read(searchTermProvider.notifier).state = pattern;
              final suggestions = ref.read(filteredStrainsProvider);
              return suggestions;
            },

            // Autocomplete menu.
            itemBuilder: (BuildContext context, Strain suggestion) {
              return ListTile(
                title: Text(suggestion.name),
              );
            },

            // Menu selection function.
            onSuggestionSelected: (Strain suggestion) {
              context.go('/strains/${suggestion.id}');
            },
          ),
        ),

        // Spacer
        const Spacer(),

        // Delete button if any rows selected.
        if (selectedIds.length > 0)
          PrimaryButton(
            backgroundColor: Colors.red,
            text: isWide ? 'Delete strains' : 'Delete',
            onPressed: () {
              print('DELETE LOCATIONS!');
            },
          ),

        // Add button.
        if (selectedIds.length > 0) gapW6,
        PrimaryButton(
          text: isWide ? 'New location' : 'New',
          onPressed: () {
            context.go('/strains/new');
          },
        ),
      ],
    );

    // Return the table and actions.
    if (data.isEmpty)
      table = FormPlaceholder(
        image: 'assets/images/icons/plant-data.png',
        title: 'Add a strain',
        description: 'Strains are used to track packages, items, and plants.',
        onTap: () {
          context.go('/strains/new');
        },
      );
    return Column(children: [actions, gapH12, table]);
  }
}

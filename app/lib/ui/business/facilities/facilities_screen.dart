// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 2/18/2023
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
import 'package:cannlytics_app/models/metrc/facility.dart';
import 'package:cannlytics_app/ui/business/facilities/facilities_controller.dart';
import 'package:cannlytics_app/ui/layout/footer.dart';
import 'package:cannlytics_app/ui/layout/header.dart';
import 'package:cannlytics_app/widgets/layout/custom_placeholder.dart';
import 'package:cannlytics_app/widgets/tables/table_data.dart';
import 'package:cannlytics_app/widgets/tables/table_form.dart';

/// Facilities screen.
class FacilitiesScreen extends ConsumerWidget {
  const FacilitiesScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return MainScreen(
      slivers: [
        // App header.
        const SliverToBoxAdapter(child: AppHeader()),

        // Form.
        SliverToBoxAdapter(
          child: TableForm(
            title: 'Facilities',
            table: FacilitiesTable(),
          ),
        ),

        // Footer
        const SliverToBoxAdapter(child: Footer()),
      ],
    );
  }
}

/// Facilities table.
class FacilitiesTable extends ConsumerWidget {
  const FacilitiesTable({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    // Determine the screen size.
    final screenWidth = MediaQuery.of(context).size.width;
    final isWide = screenWidth > Breakpoints.tablet;

    // Get the filtered data.
    final data = ref.watch(filteredFacilitiesProvider);

    // Define the table headers.
    List<Map> headers = [
      {'name': 'ID', 'key': 'id', 'sort': true},
      {'name': 'Name', 'key': 'name', 'sort': true},
      {'name': 'Display Name', 'key': 'display_name', 'sort': true},
      {'name': 'License Type', 'key': 'license.type', 'sort': false},
    ];

    // Define the cell builder function.
    _buildCells(Facility item) {
      var values = [
        item.id,
        item.name,
        item.displayName,
        item.licenseType,
      ];
      return values.map((value) {
        return DataCell(
          Text(value),
          onTap: () => context.go('/facilities/${item.id}'),
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
            ref.read(facilitiesSortColumnIndex.notifier).state = columnIndex;
            ref.read(facilitiesSortAscending.notifier).state = sortAscending;
            ref.read(facilitiesProvider.notifier).setFacilities(sorted);
          },
        ),
    ];

    // Get the rows per page.
    final rowsPerPage = ref.watch(facilitiesRowsPerPageProvider);

    // Get the selected rows.
    // List<Facility> selectedRows = ref.watch(selectedFacilitiesProvider);
    // List<String> selectedIds = selectedRows.map((x) => x.id).toList();

    // Get the sorting state.
    final sortColumnIndex = ref.read(facilitiesSortColumnIndex);
    final sortAscending = ref.read(facilitiesSortAscending);

    // Build the data table.
    Widget table = PaginatedDataTable(
      // Options.
      showCheckboxColumn: false,
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
        ref.read(facilitiesRowsPerPageProvider.notifier).state = index!;
      },

      // Table.
      source: TableData<Facility>(
        // Table data.
        data: data,

        // Table cells.
        cellsBuilder: _buildCells,

        // Select a facility.
        onSelect: (bool selected, Facility item) {
          if (selected) {
            ref.read(selectedFacilitiesProvider.notifier).selectFacility(item);
          } else {
            ref
                .read(selectedFacilitiesProvider.notifier)
                .unselectFacility(item);
          }
        },

        // Specify selected facilities.
        // isSelected: (item) => selectedIds.contains(item.id),
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
                suffixIcon: (_controller.text.isEmpty)
                    ? null
                    : GestureDetector(
                        onTap: () => _controller.clear(),
                        child: Icon(Icons.clear),
                      ),
              ),
              style: DefaultTextStyle.of(context)
                  .style
                  .copyWith(fontStyle: FontStyle.italic),
            ),
            // Search engine function.
            suggestionsCallback: (pattern) async {
              ref.read(searchTermProvider.notifier).state = pattern;
              final suggestions = ref.read(filteredFacilitiesProvider);
              return suggestions;
            },

            // Autocomplete menu.
            itemBuilder: (BuildContext context, Facility suggestion) {
              return ListTile(title: Text(suggestion.name));
            },

            // Menu selection function.
            onSuggestionSelected: (Facility suggestion) {
              context.go('/facilities/${suggestion.id}');
            },
          ),
        ),

        // Spacer
        const Spacer(),
      ],
    );

    // Return the table and actions.
    if (data.isEmpty)
      table = CustomPlaceholder(
        image: 'assets/images/icons/facilities.png',
        title: 'Add a facility',
        description:
            'Facilities are used to track packages, items, and plants.',
        onTap: () {
          context.go('/facilities/new');
        },
      );
    return Column(children: [actions, gapH12, table]);
  }
}

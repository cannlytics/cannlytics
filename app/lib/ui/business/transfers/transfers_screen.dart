// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 3/8/2023
// Updated: 3/18/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Flutter imports:
import 'package:flutter/material.dart';

// Package imports:
import 'package:dartx/dartx.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_typeahead/flutter_typeahead.dart';
import 'package:go_router/go_router.dart';

// Project imports:
import 'package:cannlytics_app/constants/design.dart';
import 'package:cannlytics_app/models/metrc/transfer.dart';
import 'package:cannlytics_app/ui/business/transfers/transfers_controller.dart';
import 'package:cannlytics_app/ui/layout/footer.dart';
import 'package:cannlytics_app/ui/layout/header.dart';
import 'package:cannlytics_app/widgets/buttons/primary_button.dart';
import 'package:cannlytics_app/widgets/layout/custom_placeholder.dart';
import 'package:cannlytics_app/widgets/tables/table_data.dart';
import 'package:cannlytics_app/widgets/tables/table_form.dart';

/// Transfers screen.
class TransfersScreen extends ConsumerWidget {
  const TransfersScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return Scaffold(
      body: CustomScrollView(
        slivers: [
          // App header.
          const SliverToBoxAdapter(child: AppHeader()),

          // Form.
          SliverToBoxAdapter(
            child: TableForm(
              title: 'Transfers',
              table: TransfersTable(),
            ),
          ),

          // Footer
          const SliverToBoxAdapter(child: Footer()),
        ],
      ),
    );
  }
}

/// Transfers table.
class TransfersTable extends ConsumerWidget {
  const TransfersTable({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    // Determine the screen size.
    final screenWidth = MediaQuery.of(context).size.width;
    final isWide = screenWidth > Breakpoints.tablet;

    // Get the filtered data.
    final data = ref.watch(filteredTransfersProvider);

    // Define the cell builder function.
    _buildCells(Transfer item) {
      return <DataCell>[
        DataCell(Text(item.id ?? '')),
      ];
    }

    // Define the table headers.
    List<Map> headers = [
      {'name': 'ID', 'key': 'id', 'sort': true},
    ];

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
            ref.read(transfersSortColumnIndex.notifier).state = columnIndex;
            ref.read(transfersSortAscending.notifier).state = sortAscending;
            ref.read(transfersProvider.notifier).setTransfers(sorted);
          },
        ),
    ];

    // Get the rows per page.
    final rowsPerPage = ref.watch(transfersRowsPerPageProvider);

    // Get the selected rows.
    // List<Transfer> selectedRows = ref.watch(selectedTransfersProvider);
    // FIXME:
    // List<String> selectedIds = selectedRows.map((x) => x.id).toList();
    List<String> selectedIds = [];

    // Get the sorting state.
    final sortColumnIndex = ref.read(transfersSortColumnIndex);
    final sortAscending = ref.read(transfersSortAscending);

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
        ref.read(transfersRowsPerPageProvider.notifier).state = index!;
      },
      // Table.
      source: TableData<Transfer>(
        // Table data.
        data: data,

        // Table cells.
        cellsBuilder: _buildCells,

        // Tap on a transfer.
        onTap: (Transfer item) async {
          // await ref.read(transferProvider.notifier).set(item);
          // FIXME: Pass transfer data to avoid extra API request.
          context.go('/transfers/${item.id}');
        },

        // Select a transfer.
        onSelect: (bool selected, Transfer item) {
          if (selected) {
            ref.read(selectedTransfersProvider.notifier).selectTransfer(item);
          } else {
            ref.read(selectedTransfersProvider.notifier).unselectTransfer(item);
          }
        },

        // Specify selected transfers.
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
          // height: 34,
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
              style: DefaultTextStyle.of(context).style.copyWith(
                    fontStyle: FontStyle.italic,
                    // fontSize: 16.0,
                    // height: 1.25,
                  ),
            ),
            // Search engine function.
            suggestionsCallback: (pattern) async {
              ref.read(searchTermProvider.notifier).state = pattern;
              final suggestions = ref.read(filteredTransfersProvider);
              return suggestions;
            },

            // Autocomplete menu.
            itemBuilder: (BuildContext context, Transfer suggestion) {
              return ListTile(
                title: Text(suggestion.name ?? ''),
              );
            },

            // Menu selection function.
            onSuggestionSelected: (Transfer suggestion) {
              context.go('/transfers/${suggestion.id}');
            },
          ),
        ),

        // Spacer
        const Spacer(),

        // Delete button if any rows selected.
        if (selectedIds.length > 0)
          PrimaryButton(
            backgroundColor: Colors.red,
            text: isWide ? 'Delete transfers' : 'Delete',
            onPressed: () {
              print('TODO: DELETE!');
            },
          ),

        // Add button.
        if (selectedIds.length > 0) gapW6,
        PrimaryButton(
          text: isWide ? 'New transfer' : 'New',
          onPressed: () {
            context.go('/transfers/new');
          },
        ),
      ],
    );

    // Return the table and actions.
    if (data.isEmpty)
      table = FormPlaceholder(
        image: 'assets/images/icons/facilities.png',
        title: 'Add a transfer',
        description: 'Transfers are used to track packages, items, and plants.',
        onTap: () {
          context.go('/transfers/new');
        },
      );
    return Column(children: [actions, gapH12, table]);
  }
}

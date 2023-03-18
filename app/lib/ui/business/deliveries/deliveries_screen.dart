// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 3/7/2023
// Updated: 3/17/2023
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
import 'package:cannlytics_app/models/metrc/delivery.dart';
import 'package:cannlytics_app/ui/business/deliveries/deliveries_controller.dart';
import 'package:cannlytics_app/ui/layout/footer.dart';
import 'package:cannlytics_app/ui/layout/header.dart';
import 'package:cannlytics_app/widgets/buttons/primary_button.dart';
import 'package:cannlytics_app/widgets/layout/custom_placeholder.dart';
import 'package:cannlytics_app/widgets/tables/table_data.dart';
import 'package:cannlytics_app/widgets/tables/table_form.dart';

/// Deliveries screen.
class DeliveriesScreen extends ConsumerWidget {
  const DeliveriesScreen({super.key});

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
              title: 'Deliveries',
              table: DeliveriesTable(),
            ),
          ),

          // Footer
          const SliverToBoxAdapter(child: Footer()),
        ],
      ),
    );
  }
}

/// Deliveries table.
class DeliveriesTable extends ConsumerWidget {
  const DeliveriesTable({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    // Determine the screen size.
    final screenWidth = MediaQuery.of(context).size.width;
    final isWide = screenWidth > Breakpoints.tablet;

    // Get the filtered data.
    final data = ref.watch(filteredDeliveriesProvider);

    // Define the cell builder function.
    _buildCells(Delivery item) {
      return <DataCell>[
        DataCell(Text(item.consumerId ?? '')),
        DataCell(Text(item.driverEmployeeId ?? '')),
        DataCell(Text(item.driverName ?? '')),
      ];
    }

    // Define the table headers.
    List<Map> headers = [
      {'name': 'Consumer ID', 'key': 'consumer_id', 'sort': true},
      {'name': 'Driver Employee ID', 'key': 'driver_employee_id', 'sort': true},
      {'name': 'Driver Name', 'key': 'driver_name', 'sort': true},
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
            ref.read(deliveriesSortColumnIndex.notifier).state = columnIndex;
            ref.read(deliveriesSortAscending.notifier).state = sortAscending;
            ref.read(deliveriesProvider.notifier).setDeliveries(sorted);
          },
        ),
    ];

    // Get the rows per page.
    final rowsPerPage = ref.watch(deliveriesRowsPerPageProvider);

    // Get the selected rows.
    List<Delivery> selectedRows = ref.watch(selectedDeliveriesProvider);
    List<dynamic> selectedIds = selectedRows.map((x) => x.consumerId).toList();

    // Get the sorting state.
    final sortColumnIndex = ref.read(deliveriesSortColumnIndex);
    final sortAscending = ref.read(deliveriesSortAscending);

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
        ref.read(deliveriesRowsPerPageProvider.notifier).state = index!;
      },
      // Table.
      source: TableData<Delivery>(
        // Table data.
        data: data,

        // Table cells.
        cellsBuilder: _buildCells,

        // Tap on a delivery.
        onTap: (Delivery item) async {
          // await ref.read(deliveryProvider.notifier).set(item);
          // FIXME: Pass delivery data to avoid extra API request.
          context.go('/deliveries/${item.consumerId}');
        },

        // Select a delivery.
        onSelect: (bool selected, Delivery item) {
          if (selected) {
            ref.read(selectedDeliveriesProvider.notifier).selectDelivery(item);
          } else {
            ref
                .read(selectedDeliveriesProvider.notifier)
                .unselectDelivery(item);
          }
        },

        // Specify selected deliveries.
        isSelected: (item) => selectedIds.contains(item.consumerId),
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
              final suggestions = ref.read(filteredDeliveriesProvider);
              return suggestions;
            },

            // Autocomplete menu.
            itemBuilder: (BuildContext context, Delivery suggestion) {
              return ListTile(
                title: Text(suggestion.driverName ?? ''),
              );
            },

            // Menu selection function.
            onSuggestionSelected: (Delivery suggestion) {
              context.go('/deliveries/${suggestion.consumerId}');
            },
          ),
        ),

        // Spacer
        const Spacer(),

        // Delete button if any rows selected.
        if (selectedIds.length > 0)
          PrimaryButton(
            backgroundColor: Colors.red,
            text: isWide ? 'Delete deliveries' : 'Delete',
            onPressed: () {
              print('DELETE LOCATIONS!');
            },
          ),

        // Add button.
        if (selectedIds.length > 0) gapW6,
        PrimaryButton(
          text: isWide ? 'New delivery' : 'New',
          onPressed: () {
            context.go('/deliveries/new');
          },
        ),
      ],
    );

    // Return the table and actions.
    if (data.isEmpty)
      table = CustomPlaceholder(
        image: 'assets/images/icons/driver.png',
        title: 'Add a delivery',
        description: 'You do not have any active deliveries at this facility.',
        onTap: () {
          context.go('/deliveries/new');
        },
      );
    return Column(children: [actions, gapH12, table]);
  }
}

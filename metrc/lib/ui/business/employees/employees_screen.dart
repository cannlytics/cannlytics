// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 3/8/2023
// Updated: 3/16/2023
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
import 'package:cannlytics_app/models/metrc/employee.dart';
import 'package:cannlytics_app/ui/business/employees/employees_controller.dart';
import 'package:cannlytics_app/ui/layout/footer.dart';
import 'package:cannlytics_app/ui/layout/header.dart';
import 'package:cannlytics_app/widgets/layout/custom_placeholder.dart';
import 'package:cannlytics_app/widgets/tables/table_data.dart';
import 'package:cannlytics_app/widgets/tables/table_form.dart';

/// Employees screen.
class EmployeesScreen extends ConsumerWidget {
  const EmployeesScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return MainScreen(
      slivers: [
        // App header.
        const SliverToBoxAdapter(child: AppHeader()),

        // Form.
        SliverToBoxAdapter(
          child: TableForm(
            title: 'Employees',
            table: EmployeesTable(),
          ),
        ),

        // Footer
        const SliverToBoxAdapter(child: Footer()),
      ],
    );
  }
}

/// Employees table.
class EmployeesTable extends ConsumerWidget {
  const EmployeesTable({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    // Determine the screen size.
    // final screenWidth = MediaQuery.of(context).size.width;
    // final isWide = screenWidth > Breakpoints.tablet;

    // Get the filtered data.
    final data = ref.watch(filteredEmployeesProvider);

    // Define the cell builder function.
    _buildCells(Employee item) {
      var values = [
        item.fullName ?? '',
        item.licenseNumber ?? '',
        item.licenseStartDate ?? '',
        item.licenseEndDate ?? '',
        item.licenseType ?? '',
      ];
      return values.map((value) {
        return DataCell(
          Text(value),
          onTap: () => context.go('/employees/${item.licenseNumber}'),
        );
      }).toList();
    }

    // Define the table headers.
    List<Map> headers = [
      {'name': 'Full Name', 'key': 'full_name', 'sort': true},
      {'name': 'License Number', 'key': 'license_number', 'sort': true},
      {'name': 'Start', 'key': 'license_start_date', 'sort': true},
      {'name': 'End', 'key': 'license_end_date', 'sort': true},
      {'name': 'Type', 'key': 'license_type', 'sort': true},
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
            ref.read(employeesSortColumnIndex.notifier).state = columnIndex;
            ref.read(employeesSortAscending.notifier).state = sortAscending;
            ref.read(employeesProvider.notifier).setEmployees(sorted);
          },
        ),
    ];

    // Get the rows per page.
    final rowsPerPage = ref.watch(employeesRowsPerPageProvider);

    // Get the sorting state.
    final sortColumnIndex = ref.read(employeesSortColumnIndex);
    final sortAscending = ref.read(employeesSortAscending);

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
        ref.read(employeesRowsPerPageProvider.notifier).state = index!;
      },

      // Table.
      source: TableData<Employee>(
        data: data,
        cellsBuilder: _buildCells,
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
              final suggestions = ref.read(filteredEmployeesProvider);
              return suggestions;
            },

            // Autocomplete menu.
            itemBuilder: (BuildContext context, Employee suggestion) {
              return ListTile(
                title: Text(suggestion.fullName ?? suggestion.licenseNumber!),
              );
            },

            // Menu selection function.
            onSuggestionSelected: (Employee suggestion) {
              context.go('/employees/${suggestion.licenseNumber}');
            },
          ),
        ),
      ],
    );

    // Return the table and actions.
    if (data.isEmpty)
      table = FormPlaceholder(
        image: 'assets/images/icons/figures.png',
        title: 'Add a employee',
        description: 'Employees are used to track packages, items, and plants.',
        onTap: () {
          context.go('/employees/new');
        },
      );
    return Column(children: [actions, gapH12, table]);
  }
}

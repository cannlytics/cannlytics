// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 3/8/2023
// Updated: 3/16/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Flutter imports:
import 'package:flutter/material.dart';

// Package imports:
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

// Project imports:
import 'package:cannlytics_app/models/metrc/employee.dart';
import 'package:cannlytics_app/ui/business/employees/employees_controller.dart';
import 'package:cannlytics_app/ui/layout/footer.dart';
import 'package:cannlytics_app/ui/layout/header.dart';
import 'package:cannlytics_app/widgets/layout/custom_placeholder.dart';
import 'package:cannlytics_app/widgets/tables/table_form.dart';

// Flutter imports:
import 'package:cannlytics_app/constants/design.dart';
import 'package:cannlytics_app/widgets/buttons/primary_button.dart';
import 'package:cannlytics_app/widgets/tables/table_data.dart';
import 'package:flutter/material.dart';
import 'package:dartx/dartx.dart';

// Package imports:
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_typeahead/flutter_typeahead.dart';
import 'package:go_router/go_router.dart';

// Project imports:
import 'package:cannlytics_app/models/metrc/employee.dart';
import 'package:cannlytics_app/ui/business/employees/employees_controller.dart';
import 'package:cannlytics_app/ui/layout/footer.dart';
import 'package:cannlytics_app/ui/layout/header.dart';
import 'package:cannlytics_app/widgets/layout/custom_placeholder.dart';
import 'package:cannlytics_app/widgets/tables/table_form.dart';

/// Employees screen.
class EmployeesScreen extends ConsumerWidget {
  const EmployeesScreen({super.key});

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
              title: 'Employees',
              table: EmployeesTable(),
            ),
          ),

          // Footer
          const SliverToBoxAdapter(child: Footer()),
        ],
      ),
    );
  }
}

/// Employees table.
class EmployeesTable extends ConsumerWidget {
  const EmployeesTable({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    // Determine the screen size.
    final screenWidth = MediaQuery.of(context).size.width;
    final isWide = screenWidth > Breakpoints.tablet;

    // Get the filtered data.
    final data = ref.watch(filteredEmployeesProvider);

    // Define the cell builder function.
    _buildCells(Employee item) {
      return <DataCell>[
        DataCell(Text(item.fullName ?? '')),
        DataCell(Text(item.licenseNumber ?? '')),
      ];
    }

    // Define the table headers.
    List<Map> headers = [
      {'name': 'Full Name', 'key': 'full_name', 'sort': true},
      {'name': 'License Number', 'key': 'license_number', 'sort': true},
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

    // Get the selected rows.
    List<Employee> selectedRows = ref.watch(selectedEmployeesProvider);
    List<String> selectedIds =
        selectedRows.map((x) => x.licenseNumber!).toList();

    // Get the sorting state.
    final sortColumnIndex = ref.read(employeesSortColumnIndex);
    final sortAscending = ref.read(employeesSortAscending);

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
        ref.read(employeesRowsPerPageProvider.notifier).state = index!;
      },
      // Table.
      source: TableData<Employee>(
        // Table data.
        data: data,

        // Table cells.
        cellsBuilder: _buildCells,

        // Tap on a employee.
        onTap: (Employee item) async {
          // await ref.read(employeeProvider.notifier).set(item);
          // FIXME: Pass employee data to avoid extra API request.
          context.go('/employees/${item.licenseNumber}');
        },

        // Select a employee.
        onSelect: (bool selected, Employee item) {
          if (selected) {
            ref.read(selectedEmployeesProvider.notifier).selectEmployee(item);
          } else {
            ref.read(selectedEmployeesProvider.notifier).unselectEmployee(item);
          }
        },

        // Specify selected employees.
        isSelected: (item) => selectedIds.contains(item.licenseNumber),
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

        // Spacer
        const Spacer(),

        // // Delete button if any rows selected.
        // if (selectedIds.length > 0)
        //   PrimaryButton(
        //     backgroundColor: Colors.red,
        //     text: isWide ? 'Delete employees' : 'Delete',
        //     onPressed: () {
        //       print('DELETE LOCATIONS!');
        //     },
        //   ),

        // Add button.
        // if (selectedIds.length > 0) gapW6,
        // PrimaryButton(
        //   text: isWide ? 'New employee' : 'New',
        //   onPressed: () {
        //     context.go('/employees/new');
        //   },
        // ),
      ],
    );

    // Return the table and actions.
    if (data.isEmpty)
      table = CustomPlaceholder(
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

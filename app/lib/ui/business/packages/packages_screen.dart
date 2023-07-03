// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 2/18/2023
// Updated: 2/20/2023
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
import 'package:cannlytics_app/models/metrc/package.dart';
import 'package:cannlytics_app/ui/business/packages/packages_controller.dart';
import 'package:cannlytics_app/ui/layout/footer.dart';
import 'package:cannlytics_app/ui/layout/header.dart';
import 'package:cannlytics_app/widgets/buttons/primary_button.dart';
import 'package:cannlytics_app/widgets/layout/custom_placeholder.dart';
import 'package:cannlytics_app/widgets/tables/table_data.dart';
import 'package:cannlytics_app/widgets/tables/table_form.dart';

/// Packages screen.
class PackagesScreen extends ConsumerWidget {
  const PackagesScreen({super.key});

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
              title: 'Packages',
              table: PackagesTable(),
            ),
          ),

          // Footer
          const SliverToBoxAdapter(child: Footer()),
        ],
      ),
    );
  }
}

/// Packages table.
class PackagesTable extends ConsumerWidget {
  const PackagesTable({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    // Determine the screen size.
    final screenWidth = MediaQuery.of(context).size.width;
    final isWide = screenWidth > Breakpoints.tablet;

    // Get the filtered data.
    final data = ref.watch(filteredPackagesProvider);

    // Define the cell builder function.
    _buildCells(Package item) {
      return <DataCell>[
        DataCell(Text(item.id ?? '')),
        // DataCell(Text(item.name)),
        // DataCell(Text(item.packageTypeName ?? '')),
        // DataCell(Text(item.forPackages! ? '✓' : 'x')),
        // DataCell(Text(item.forPlantBatches! ? '✓' : 'x')),
        // DataCell(Text(item.forPlants! ? '✓' : 'x')),
        // DataCell(Text(item.forHarvests! ? '✓' : 'x')),
      ];
    }

    // Define the table headers.
    List<Map> headers = [
      {'name': 'ID', 'key': 'id', 'sort': true},
      // {'name': 'Name', 'key': 'name', 'sort': true},
      // {'name': 'Type', 'key': 'package_type_name', 'sort': true},
      // {'name': 'Packages', 'key': 'for_plant_batches', 'sort': false},
      // {'name': 'Batches', 'key': 'for_plants', 'sort': false},
      // {'name': 'Plants', 'key': 'for_harvests', 'sort': false},
      // {'name': 'Harvests', 'key': 'for_packages', 'sort': false},
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
            ref.read(packagesSortColumnIndex.notifier).state = columnIndex;
            ref.read(packagesSortAscending.notifier).state = sortAscending;
            ref.read(packagesProvider.notifier).setPackages(sorted);
          },
        ),
    ];

    // Get the rows per page.
    final rowsPerPage = ref.watch(packagesRowsPerPageProvider);

    // Get the selected rows.
    // List<Package> selectedRows = ref.watch(selectedPackagesProvider);
    // FIXME:
    // List<String> selectedIds = selectedRows.map((x) => x.id).toList();
    List<String> selectedIds = [];

    // Get the sorting state.
    final sortColumnIndex = ref.read(packagesSortColumnIndex);
    final sortAscending = ref.read(packagesSortAscending);

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
        ref.read(packagesRowsPerPageProvider.notifier).state = index!;
      },
      // Table.
      source: TableData<Package>(
        // Table data.
        data: data,

        // Table cells.
        cellsBuilder: _buildCells,

        // Tap on a package.
        onTap: (Package item) async {
          // await ref.read(packageProvider.notifier).set(item);
          // FIXME: Pass package data to avoid extra API request.
          context.go('/packages/${item.id}');
        },

        // Select a package.
        onSelect: (bool selected, Package item) {
          if (selected) {
            ref.read(selectedPackagesProvider.notifier).selectPackage(item);
          } else {
            ref.read(selectedPackagesProvider.notifier).unselectPackage(item);
          }
        },

        // Specify selected packages.
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
              final suggestions = ref.read(filteredPackagesProvider);
              return suggestions;
            },

            // Autocomplete menu.
            itemBuilder: (BuildContext context, Package suggestion) {
              return ListTile(
                title: Text(suggestion.id ?? ''),
              );
            },

            // Menu selection function.
            onSuggestionSelected: (Package suggestion) {
              context.go('/packages/${suggestion.id}');
            },
          ),
        ),

        // Spacer
        const Spacer(),

        // Delete button if any rows selected.
        if (selectedIds.length > 0)
          PrimaryButton(
            backgroundColor: Colors.red,
            text: isWide ? 'Delete packages' : 'Delete',
            onPressed: () {
              print('DELETE LOCATIONS!');
            },
          ),

        // Add button.
        if (selectedIds.length > 0) gapW6,
        PrimaryButton(
          text: isWide ? 'New package' : 'New',
          onPressed: () {
            context.go('/packages/new');
          },
        ),
      ],
    );

    // Return the table and actions.
    if (data.isEmpty)
      table = FormPlaceholder(
        image: 'assets/images/icons/facilities.png',
        title: 'Add a package',
        description: 'Packages are used to track packages, items, and plants.',
        onTap: () {
          context.go('/packages/new');
        },
      );
    return Column(children: [actions, gapH12, table]);
  }
}

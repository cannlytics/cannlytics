// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 3/9/2023
// Updated: 3/18/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

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
import 'package:cannlytics_app/models/metrc/plant_harvest.dart';
import 'package:cannlytics_app/ui/business/plant_harvests/plant_harvests_controller.dart';
import 'package:cannlytics_app/ui/layout/footer.dart';
import 'package:cannlytics_app/ui/layout/header.dart';
import 'package:cannlytics_app/widgets/layout/custom_placeholder.dart';
import 'package:cannlytics_app/widgets/tables/table_form.dart';

/// PlantHarvests screen.
class PlantHarvestsScreen extends ConsumerWidget {
  const PlantHarvestsScreen({super.key});

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
              title: 'PlantHarvests',
              table: PlantHarvestsTable(),
            ),
          ),

          // Footer
          const SliverToBoxAdapter(child: Footer()),
        ],
      ),
    );
  }
}

/// PlantHarvests table.
class PlantHarvestsTable extends ConsumerWidget {
  const PlantHarvestsTable({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    // Determine the screen size.
    final screenWidth = MediaQuery.of(context).size.width;
    final isWide = screenWidth > Breakpoints.tablet;

    // Get the filtered data.
    final data = ref.watch(filteredPlantHarvestsProvider);

    // Define the cell builder function.
    _buildCells(PlantHarvest item) {
      return <DataCell>[
        DataCell(Text(item.id ?? '')),
        DataCell(Text(item.name ?? '')),
      ];
    }

    // Define the table headers.
    List<Map> headers = [
      {'name': 'ID', 'key': 'id', 'sort': true},
      {'name': 'Name', 'key': 'name', 'sort': true},
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
            ref.read(plantHarvestsSortColumnIndex.notifier).state = columnIndex;
            ref.read(plantHarvestsSortAscending.notifier).state = sortAscending;
            ref.read(plantHarvestsProvider.notifier).setPlantHarvests(sorted);
          },
        ),
    ];

    // Get the rows per page.
    final rowsPerPage = ref.watch(plantHarvestsRowsPerPageProvider);

    // Get the selected rows.
    List<PlantHarvest> selectedRows = ref.watch(selectedPlantHarvestsProvider);
    List<String> selectedIds = selectedRows.map((x) => x.id!).toList();

    // Get the sorting state.
    final sortColumnIndex = ref.read(plantHarvestsSortColumnIndex);
    final sortAscending = ref.read(plantHarvestsSortAscending);

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
        ref.read(plantHarvestsRowsPerPageProvider.notifier).state = index!;
      },
      // Table.
      source: TableData<PlantHarvest>(
        // Table data.
        data: data,

        // Table cells.
        cellsBuilder: _buildCells,

        // Tap on a plantHarvest.
        onTap: (PlantHarvest item) async {
          // await ref.read(plantHarvestProvider.notifier).set(item);
          // FIXME: Pass plantHarvest data to avoid extra API request.
          context.go('/plantHarvests/${item.id}');
        },

        // Select a plantHarvest.
        onSelect: (bool selected, PlantHarvest item) {
          if (selected) {
            ref
                .read(selectedPlantHarvestsProvider.notifier)
                .selectPlantHarvest(item);
          } else {
            ref
                .read(selectedPlantHarvestsProvider.notifier)
                .unselectPlantHarvest(item);
          }
        },

        // Specify selected plantHarvests.
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
              final suggestions = ref.read(filteredPlantHarvestsProvider);
              return suggestions;
            },

            // Autocomplete menu.
            itemBuilder: (BuildContext context, PlantHarvest suggestion) {
              return ListTile(
                title: Text(suggestion.name ?? ''),
              );
            },

            // Menu selection function.
            onSuggestionSelected: (PlantHarvest suggestion) {
              context.go('/plantHarvests/${suggestion.id}');
            },
          ),
        ),

        // Spacer
        const Spacer(),

        // Delete button if any rows selected.
        if (selectedIds.length > 0)
          PrimaryButton(
            backgroundColor: Colors.red,
            text: isWide ? 'Delete plantHarvests' : 'Delete',
            onPressed: () {
              print('DELETE LOCATIONS!');
            },
          ),

        // Add button.
        if (selectedIds.length > 0) gapW6,
        PrimaryButton(
          text: isWide ? 'New plantHarvest' : 'New',
          onPressed: () {
            context.go('/plantHarvests/new');
          },
        ),
      ],
    );

    // Return the table and actions.
    if (data.isEmpty)
      table = CustomPlaceholder(
        image: 'assets/images/icons/facilities.png',
        title: 'Add a plantHarvest',
        description:
            'PlantHarvests are used to track packages, items, and plants.',
        onTap: () {
          context.go('/plantHarvests/new');
        },
      );
    return Column(children: [actions, gapH12, table]);
  }
}

// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 3/9/2023
// Updated: 3/15/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// TODO: Move plants.
// TODO: Destroy plants.
// TODO: Manicure plants.
// TODO: Harvest plants.

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
import 'package:cannlytics_app/models/metrc/plant.dart';
import 'package:cannlytics_app/ui/business/plants/plants_controller.dart';
import 'package:cannlytics_app/ui/layout/footer.dart';
import 'package:cannlytics_app/ui/layout/header.dart';
import 'package:cannlytics_app/widgets/layout/custom_placeholder.dart';
import 'package:cannlytics_app/widgets/tables/table_form.dart';

/// Plants screen.
class PlantsScreen extends ConsumerWidget {
  const PlantsScreen({super.key});

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
              title: 'Plants',
              table: PlantsTable(),
            ),
          ),

          // Footer
          const SliverToBoxAdapter(child: Footer()),
        ],
      ),
    );
  }
}

/// Plants table.
class PlantsTable extends ConsumerWidget {
  const PlantsTable({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    // Determine the screen size.
    final screenWidth = MediaQuery.of(context).size.width;
    final isWide = screenWidth > Breakpoints.tablet;

    // Get the filtered data.
    final data = ref.watch(filteredPlantsProvider);

    // Define the cell builder function.
    _buildCells(Plant item) {
      return <DataCell>[
        DataCell(Text(item.id)),
        DataCell(Text(item.strainName ?? '')),
        DataCell(Text(item.growthPhase ?? '')),
      ];
    }

    // Define the table headers.
    List<Map> headers = [
      {'name': 'ID', 'key': 'id', 'sort': true},
      {'name': 'Strain Name', 'key': 'strain_name', 'sort': true},
      {'name': 'Growth Phase', 'key': 'growth_phase', 'sort': true},
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
            ref.read(plantsSortColumnIndex.notifier).state = columnIndex;
            ref.read(plantsSortAscending.notifier).state = sortAscending;
            ref.read(plantsProvider.notifier).setPlants(sorted);
          },
        ),
    ];

    // Get the rows per page.
    final rowsPerPage = ref.watch(plantsRowsPerPageProvider);

    // Get the selected rows.
    List<Plant> selectedRows = ref.watch(selectedPlantsProvider);
    List<String> selectedIds = selectedRows.map((x) => x.id).toList();

    // Get the sorting state.
    final sortColumnIndex = ref.read(plantsSortColumnIndex);
    final sortAscending = ref.read(plantsSortAscending);

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
        ref.read(plantsRowsPerPageProvider.notifier).state = index!;
      },
      // Table.
      source: TableData<Plant>(
        // Table data.
        data: data,

        // Table cells.
        cellsBuilder: _buildCells,

        // Tap on a plant.
        onTap: (Plant item) async {
          // await ref.read(plantProvider.notifier).set(item);
          // FIXME: Pass plant data to avoid extra API request.
          context.go('/plants/${item.id}');
        },

        // Select a plant.
        onSelect: (bool selected, Plant item) {
          if (selected) {
            ref.read(selectedPlantsProvider.notifier).selectPlant(item);
          } else {
            ref.read(selectedPlantsProvider.notifier).unselectPlant(item);
          }
        },

        // Specify selected plants.
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
              final suggestions = ref.read(filteredPlantsProvider);
              return suggestions;
            },

            // Autocomplete menu.
            itemBuilder: (BuildContext context, Plant suggestion) {
              return ListTile(
                title: Text('#${suggestion.id} ${suggestion.strainName ?? ''}'),
              );
            },

            // Menu selection function.
            onSuggestionSelected: (Plant suggestion) {
              context.go('/plants/${suggestion.id}');
            },
          ),
        ),

        // Spacer
        const Spacer(),

        // Delete button if any rows selected.
        if (selectedIds.length > 0)
          PrimaryButton(
            backgroundColor: Colors.red,
            text: isWide ? 'Delete plants' : 'Delete',
            onPressed: () {
              print('DELETE LOCATIONS!');
            },
          ),

        // Add button.
        if (selectedIds.length > 0) gapW6,
        PrimaryButton(
          text: isWide ? 'New plant' : 'New',
          onPressed: () {
            context.go('/plants/new');
          },
        ),
      ],
    );

    // Return the table and actions.
    if (data.isEmpty)
      table = CustomPlaceholder(
        image: 'assets/images/icons/plant.png',
        title: 'Add a plant',
        description: 'Plants are used to track packages, items, and plants.',
        onTap: () {
          context.go('/plants/new');
        },
      );
    return Column(children: [actions, gapH12, table]);
  }
}

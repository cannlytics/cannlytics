// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 3/7/2023
// Updated: 3/22/2023
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
import 'package:cannlytics_app/models/metrc/location.dart';
import 'package:cannlytics_app/ui/business/locations/locations_controller.dart';
import 'package:cannlytics_app/ui/layout/footer.dart';
import 'package:cannlytics_app/ui/layout/header.dart';
import 'package:cannlytics_app/widgets/buttons/primary_button.dart';
import 'package:cannlytics_app/widgets/layout/custom_placeholder.dart';
import 'package:cannlytics_app/widgets/tables/table_data.dart';
import 'package:cannlytics_app/widgets/tables/table_form.dart';

/// Locations screen.
class LocationsScreen extends ConsumerWidget {
  const LocationsScreen({super.key});
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return MainScreen(
      slivers: [
        // App header.
        const SliverToBoxAdapter(child: AppHeader()),

        // Form.
        SliverToBoxAdapter(
          child: TableForm(
            title: 'Locations',
            table: LocationsTable(),
          ),
        ),

        // Footer
        const SliverToBoxAdapter(child: Footer()),
      ],
    );
  }
}

/// Locations table.
class LocationsTable extends ConsumerWidget {
  const LocationsTable({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    // Determine the screen size.
    final screenWidth = MediaQuery.of(context).size.width;
    final isWide = screenWidth > Breakpoints.tablet;

    // Get the filtered data.
    final data = ref.watch(filteredLocationsProvider);

    // Cell builder function.
    _buildCells(Location item) {
      var values = [
        item.id,
        item.name,
        item.locationTypeName ?? '',
        item.forPackages! ? '✓' : 'x',
        item.forPlantBatches! ? '✓' : 'x',
        item.forPlants! ? '✓' : 'x',
        item.forHarvests! ? '✓' : 'x',
      ];
      return values.map((value) {
        return DataCell(
          Text(value),
          onTap: () => context.go('/locations/${item.id}'),
        );
      }).toList();
    }

    // Table headers.
    List<Map> headers = [
      {'name': 'ID', 'key': 'id', 'sort': true},
      {'name': 'Name', 'key': 'name', 'sort': true},
      {'name': 'Type', 'key': 'location_type_name', 'sort': true},
      {'name': 'Packages', 'key': 'for_plant_batches', 'sort': false},
      {'name': 'Batches', 'key': 'for_plants', 'sort': false},
      {'name': 'Plants', 'key': 'for_harvests', 'sort': false},
      {'name': 'Harvests', 'key': 'for_packages', 'sort': false},
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
            ref.read(locationsSortColumnIndex.notifier).state = columnIndex;
            ref.read(locationsSortAscending.notifier).state = sortAscending;
            ref.read(locationsProvider.notifier).setLocations(sorted);
          },
        ),
    ];

    // Get the rows per page.
    final rowsPerPage = ref.watch(locationsRowsPerPageProvider);

    // Get the selected rows.
    List<Location> selectedRows = ref.watch(selectedLocationsProvider);
    List<String> selectedIds = selectedRows.map((x) => x.id).toList();

    // Get the sorting state.
    final sortColumnIndex = ref.read(locationsSortColumnIndex);
    final sortAscending = ref.read(locationsSortAscending);

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
        ref.read(locationsRowsPerPageProvider.notifier).state = index!;
      },

      // Table.
      source: TableData<Location>(
        // Table data.
        data: data,

        // Table cells.
        cellsBuilder: _buildCells,

        // Select a location.
        onSelect: (bool selected, Location item) {
          if (selected) {
            ref.read(selectedLocationsProvider.notifier).selectLocation(item);
          } else {
            ref.read(selectedLocationsProvider.notifier).unselectLocation(item);
          }
        },

        // Specify selected locations.
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
              style: DefaultTextStyle.of(context)
                  .style
                  .copyWith(fontStyle: FontStyle.italic),
            ),
            // Search engine function.
            suggestionsCallback: (pattern) async {
              ref.read(searchTermProvider.notifier).state = pattern;
              final suggestions = ref.read(filteredLocationsProvider);
              return suggestions;
            },

            // Autocomplete menu.
            itemBuilder: (BuildContext context, Location suggestion) {
              return ListTile(title: Text(suggestion.name));
            },

            // Menu selection function.
            onSuggestionSelected: (Location suggestion) {
              context.go('/locations/${suggestion.id}');
            },
          ),
        ),

        // Spacer
        const Spacer(),

        // Delete button if any rows selected.
        if (selectedIds.length > 0)
          PrimaryButton(
            backgroundColor: Colors.red,
            text: isWide ? 'Delete locations' : 'Delete',
            onPressed: () {
              print('DELETE LOCATIONS!');
            },
          ),

        // Add button.
        if (selectedIds.length > 0) gapW6,
        PrimaryButton(
          text: isWide ? 'New location' : 'New',
          onPressed: () {
            context.go('/locations/new');
          },
        ),
      ],
    );

    // Return the table and actions.
    if (data.isEmpty)
      table = FormPlaceholder(
        image: 'assets/images/icons/facilities.png',
        title: 'Add a location',
        description: 'Locations are used to track packages, items, and plants.',
        onTap: () {
          context.go('/locations/new');
        },
      );
    return Column(children: [actions, gapH12, table]);
  }
}

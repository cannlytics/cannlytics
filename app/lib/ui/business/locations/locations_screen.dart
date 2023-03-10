// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 3/7/2023
// Updated: 3/9/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Flutter imports:
import 'package:cannlytics_app/ui/business/facilities/facilities_controller.dart';
import 'package:cannlytics_app/ui/general/app_controller.dart';
import 'package:flutter/material.dart';
import 'package:dartx/dartx.dart';

// Package imports:
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

// Project imports:
import 'package:cannlytics_app/models/metrc/location.dart';
import 'package:cannlytics_app/ui/business/locations/locations_controller.dart';
import 'package:cannlytics_app/ui/general/footer.dart';
import 'package:cannlytics_app/ui/general/header.dart';
import 'package:cannlytics_app/widgets/layout/custom_placeholder.dart';
import 'package:cannlytics_app/widgets/layout/table_form.dart';

/// The locations screen.
class LocationsScreen extends StatelessWidget {
  const LocationsScreen({super.key});

  // TODO: Add Create / delete (if selected) actions.

  @override
  Widget build(BuildContext context) {
    // Render the widget.
    return Scaffold(
      body: CustomScrollView(
        slivers: [
          // App header.
          const SliverToBoxAdapter(child: AppHeader()),

          // Form.
          SliverToBoxAdapter(
            child: TableForm(
              title: 'Locations',
              table: LocationsTable(),
              // actions: actions,
            ),
          ),

          // Footer
          const SliverToBoxAdapter(child: Footer()),
        ],
      ),
    );
  }
}

/// Locations table.
class LocationsTable extends ConsumerWidget {
  const LocationsTable({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    // Get the data for the primary license / facility.
    final data = ref.watch(locationsProvider).value ?? [];

    // Return a placeholder if no data.
    if (data.isEmpty)
      return CustomPlaceholder(
        image: 'assets/images/icons/facilities.png',
        title: 'Add a location',
        description: 'You do not have any active locations for this facility.',
        onTap: () {
          context.go('/locations/new');
        },
      );

    // Format the table headers.
    List<String> headers = [
      'ID',
      'Name',
      'Type',
      'Packages',
      'Batches',
      'Plants',
      'Harvests',
    ];
    List<String> fields = [
      'id',
      'name',
      'location_type_name',
      'for_plant_batches',
      'for_plants',
      'for_harvests',
      'for_packages',
    ];
    List<DataColumn> tableHeader = <DataColumn>[
      for (String header in headers)
        DataColumn(
          label: Expanded(
            child: Text(
              header,
              style: TextStyle(fontStyle: FontStyle.italic),
            ),
          ),
          onSort: (columnIndex, sortAscending) {
            // FIXME: Actually sort the data!
            var field = fields[columnIndex];
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

    // Get the sorting state.
    final sortColumnIndex = ref.read(locationsSortColumnIndex);
    final sortAscending = ref.read(locationsSortAscending);

    // Build the data table.
    // TODO: Make sortable.
    return PaginatedDataTable(
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
      availableRowsPerPage: [5, 10, 25, 50],
      rowsPerPage: rowsPerPage,
      onRowsPerPageChanged: (index) {
        ref.read(locationsRowsPerPageProvider.notifier).state = index!;
      },
      // Table data.
      source: LocationsTableSource(
        data: data,

        // Tap on a location.
        onTap: (Location item) async {
          await ref.read(locationProvider.notifier).setLocation(item);
          context.go('/locations/${item.id}');
        },

        // Select a location.
        onSelect: (bool selected, Location item) {
          if (selected) {
            ref.read(selectedLocationsProvider.notifier).selectLocation(item);
          } else {
            ref.read(selectedLocationsProvider.notifier).unselectLocation(item);
          }
        },

        // Specify selected locations.
        selected: selectedRows.map((x) => x.id).toList(),
      ),
    );
  }
}

/// Facilities table data.
class LocationsTableSource extends DataTableSource {
  LocationsTableSource({
    required this.data,
    this.onTap,
    this.onSelect,
    this.selected,
  });

  // Properties.
  final List<Location> data;
  final void Function(Location item)? onTap;
  final void Function(bool selected, Location item)? onSelect;
  final List? selected;

  @override
  DataRow getRow(int index) {
    final item = data[index];
    return DataRow.byIndex(
      index: index,
      selected: selected!.contains(item.id),
      onSelectChanged: (bool? selected) {
        onSelect!(selected ?? false, item);
      },
      onLongPress: () {
        onTap!(item);
      },
      cells: <DataCell>[
        DataCell(Text(item.id)),
        DataCell(Text(item.name ?? '')),
        DataCell(Text(item.locationTypeName ?? '')),
        DataCell(Text(item.forPackages! ? '✓' : 'x')),
        DataCell(Text(item.forPlantBatches! ? '✓' : 'x')),
        DataCell(Text(item.forPlants! ? '✓' : 'x')),
        DataCell(Text(item.forHarvests! ? '✓' : 'x')),
      ],
    );
  }

  @override
  int get rowCount => data.length;

  @override
  bool get isRowCountApproximate => false;

  @override
  int get selectedRowCount => 0;
}

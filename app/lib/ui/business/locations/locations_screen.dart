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

  @override
  Widget build(BuildContext context) {
    // TODO: Add Create / delete (if selected) actions.
    var actions = Padding(
        padding: EdgeInsets.all(8.0),
        child: SearchBox(
            key: Key('LocationsSearch'),
            onSearch: (searchTerm) {
              // context.read(searchTermProvider).state = searchTerm),
              return null;
            }));

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
              actions: actions,
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
    List<Map> headers = [
      {'name': 'ID', 'key': 'id', 'sort': true},
      {'name': 'Name', 'key': 'name', 'sort': true},
      {'name': 'Type', 'key': 'location_type_name', 'sort': true},
      {'name': 'Packages', 'key': 'for_plant_batches', 'sort': false},
      {'name': 'Batches', 'key': 'for_plants', 'sort': false},
      {'name': 'Plants', 'key': 'for_harvests', 'sort': false},
      {'name': 'Harvests', 'key': 'for_packages', 'sort': false},
    ];
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

    // Get the sorting state.
    final sortColumnIndex = ref.read(locationsSortColumnIndex);
    final sortAscending = ref.read(locationsSortAscending);

    // Build the data table.
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
      availableRowsPerPage: [5, 10, 25, 50, 100],
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

/// Table search.
/// TODO: Add clear.
class SearchBox extends StatelessWidget {
  final ValueChanged<String> onSearch;

  const SearchBox({
    required Key key,
    required this.onSearch,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: 150,
      child: TextFormField(
        initialValue: '',
        style: TextStyle(color: Colors.white),
        cursorColor: Colors.white,
        decoration: InputDecoration(
          hintText: 'Search',
          hintStyle: TextStyle(fontSize: 16, color: Colors.white),
          isDense: true,
          suffixIcon: Icon(Icons.search, color: Colors.white),
          focusedBorder: OutlineInputBorder(
            borderRadius: BorderRadius.circular(16),
            borderSide: BorderSide(
              color: Colors.white,
              width: 2.0,
            ),
          ),
          enabledBorder: OutlineInputBorder(
            borderRadius: BorderRadius.circular(16),
            borderSide: BorderSide(style: BorderStyle.none),
          ),
          filled: true,
          fillColor: Colors.lightBlue.shade200,
        ),
        onChanged: onSearch,
      ),
    );
  }
}

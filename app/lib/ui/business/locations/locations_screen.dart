// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 3/7/2023
// Updated: 3/9/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Flutter imports:
import 'package:flutter/material.dart';

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
    if (data.length == 0)
      return CustomPlaceholder(
        image: 'assets/images/icons/facilities.png',
        title: 'Add a location',
        description: 'You do not have any active locations for this facility.',
        onTap: () {
          context.go('/locations/new');
        },
      );

    print('OBSERVATION:');
    print(data[0]);

    // Get the rows per page.
    final rowsPerPage = ref.watch(locationsRowsPerPageProvider);

    // Get the selected rows.
    List<Location> selectedRows = ref.watch(selectedLocationsProvider);

    // Format the table headers.
    List<String> headers = ['ID', 'Name', 'Type'];
    List<DataColumn> tableHeader = <DataColumn>[
      for (String header in headers)
        DataColumn(
          label: Expanded(
            child: Text(
              header,
              style: TextStyle(fontStyle: FontStyle.italic),
            ),
          ),
        ),
    ];

    // Build the data table.
    // TODO: Make sortable.
    return PaginatedDataTable(
      showCheckboxColumn: true,
      columns: tableHeader,
      dataRowHeight: 48,
      columnSpacing: 48,
      headingRowHeight: 48,
      horizontalMargin: 12,
      availableRowsPerPage: [5, 10, 25, 50],
      rowsPerPage: rowsPerPage,
      onRowsPerPageChanged: (index) {
        ref.read(locationsRowsPerPageProvider.notifier).state = index!;
      },
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
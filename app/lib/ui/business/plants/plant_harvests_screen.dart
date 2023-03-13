// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 3/9/2023
// Updated: 3/9/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Flutter imports:
import 'package:flutter/material.dart';

// Package imports:
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

// Project imports:
import 'package:cannlytics_app/models/metrc/plant_harvest.dart';
import 'package:cannlytics_app/ui/business/plants/plant_harvests_controller.dart';
import 'package:cannlytics_app/ui/layout/footer.dart';
import 'package:cannlytics_app/ui/layout/header.dart';
import 'package:cannlytics_app/widgets/layout/custom_placeholder.dart';
import 'package:cannlytics_app/widgets/tables/table_form.dart';

/// The plant harvests screen.
class PlantHarvestsScreen extends StatelessWidget {
  const PlantHarvestsScreen({super.key});

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
              title: 'Plant Harvests',
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

/// Plant harvests table.
class PlantHarvestsTable extends ConsumerWidget {
  const PlantHarvestsTable({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    // Get the data for the primary license / facility.
    final data = ref.watch(plantHarvestsProvider).value ?? [];

    // Return a placeholder if no data.
    if (data.length == 0)
      return CustomPlaceholder(
        image: 'assets/images/icons/products.png',
        title: 'No plants',
        description: 'You do not have any active plants for this facility.',
        onTap: () {
          context.go('/plants/new');
        },
      );

    print('OBSERVATION:');
    print(data[0]);

    // Get the rows per page.
    final rowsPerPage = ref.watch(plantHarvestsRowsPerPageProvider);

    // Format the table headers.
    List<String> headers = ['ID', 'Name', 'Location'];
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
      columns: tableHeader,
      dataRowHeight: 48,
      columnSpacing: 48,
      headingRowHeight: 48,
      horizontalMargin: 12,
      availableRowsPerPage: [5, 10, 25, 50],
      rowsPerPage: rowsPerPage,
      onRowsPerPageChanged: (index) {
        ref.read(plantHarvestsRowsPerPageProvider.notifier).state = index!;
      },
      showCheckboxColumn: false,
      source: PlantHarvestsTableSource(
        data: data,
        onTap: (Harvest item) {
          // String slug = Format.slugify(item.name);
          context.go('/plants/${item.id}');
        },
      ),
    );
  }
}

/// PlantHarvests table data.
class PlantHarvestsTableSource extends DataTableSource {
  PlantHarvestsTableSource({
    required this.data,
    this.onTap,
  });

  // Properties.
  final List<Harvest> data;
  final void Function(Harvest item)? onTap;

  @override
  DataRow getRow(int index) {
    final item = data[index];
    return DataRow.byIndex(
      index: index,
      onSelectChanged: (bool? selected) {
        if (selected!) {
          onTap!(item);
        }
      },
      cells: <DataCell>[
        DataCell(Text(item.id)),
        DataCell(Text(item.name)),
        DataCell(Text(item.dryingLocationName)),
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

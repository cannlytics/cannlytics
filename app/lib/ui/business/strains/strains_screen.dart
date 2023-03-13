// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 3/8/2023
// Updated: 3/8/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Flutter imports:
import 'package:flutter/material.dart';

// Package imports:
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

// Project imports:
import 'package:cannlytics_app/models/metrc/strain.dart';
import 'package:cannlytics_app/ui/business/strains/strains_controller.dart';
import 'package:cannlytics_app/ui/layout/footer.dart';
import 'package:cannlytics_app/ui/layout/header.dart';
import 'package:cannlytics_app/widgets/layout/custom_placeholder.dart';
import 'package:cannlytics_app/widgets/tables/table_form.dart';

/// The strains screen.
class StrainsScreen extends StatelessWidget {
  const StrainsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    // Render the widget.
    return Scaffold(
      body: CustomScrollView(
        slivers: [
          // App header.
          const SliverToBoxAdapter(child: AppHeader()),

          // Strains form.
          SliverToBoxAdapter(
            child: TableForm(
              title: 'Strains',
              table: StrainsTable(),
            ),
          ),

          // Footer
          const SliverToBoxAdapter(child: Footer()),
        ],
      ),
    );
  }
}

/// Strains table.
class StrainsTable extends ConsumerWidget {
  const StrainsTable({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    // Get the data for the primary license / facility.
    final data = ref.watch(strainsProvider).value ?? [];

    // Return a placeholder if no data.
    if (data.length == 0)
      return CustomPlaceholder(
        image: 'assets/images/icons/plant-data.png',
        title: 'No strains',
        description: 'You do not have any active strains for this facility.',
        onTap: () {
          context.go('/strains/new');
        },
      );

    print('OBSERVATION:');
    print(data[0]);

    // Get the rows per page.
    final rowsPerPage = ref.watch(strainsRowsPerPageProvider);

    // Format the table headers.
    List<String> headers = ['ID', 'Name', 'Testing Status'];
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
        ref.read(strainsRowsPerPageProvider.notifier).state = index!;
      },
      showCheckboxColumn: false,
      source: StrainsTableSource(
        data: data,
        onTap: (Strain item) {
          // String slug = Format.slugify(item.name);
          context.go('/strains/${item.id}');
        },
      ),
    );
  }
}

/// Strains table data.
class StrainsTableSource extends DataTableSource {
  StrainsTableSource({
    required this.data,
    this.onTap,
  });

  // Properties.
  final List<Strain> data;
  final void Function(Strain item)? onTap;

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
        DataCell(Text(item.testingStatus)),
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

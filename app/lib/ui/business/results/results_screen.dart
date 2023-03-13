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
import 'package:cannlytics_app/models/metrc/lab_result.dart';
import 'package:cannlytics_app/ui/business/results/results_controller.dart';
import 'package:cannlytics_app/ui/layout/footer.dart';
import 'package:cannlytics_app/ui/layout/header.dart';
import 'package:cannlytics_app/widgets/layout/custom_placeholder.dart';
import 'package:cannlytics_app/widgets/tables/table_form.dart';

/// The results screen.
class ResultsScreen extends StatelessWidget {
  const ResultsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    // Render the widget.
    return Scaffold(
      body: CustomScrollView(
        slivers: [
          // App header.
          const SliverToBoxAdapter(child: AppHeader()),

          // Results form.
          SliverToBoxAdapter(
            child: TableForm(
              title: 'Results',
              table: ResultsTable(),
            ),
          ),

          // Footer
          const SliverToBoxAdapter(child: Footer()),
        ],
      ),
    );
  }
}

/// Results table.
class ResultsTable extends ConsumerWidget {
  const ResultsTable({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    // Get the data for the primary license / facility.
    final data = ref.watch(resultsProvider).value ?? [];

    // Return a placeholder if no data.
    if (data.length == 0)
      return CustomPlaceholder(
        image: 'assets/images/icons/certificate.png',
        title: 'No results',
        description: 'You do not have any active results for this facility.',
        onTap: () {
          context.go('/results/new');
        },
      );

    print('OBSERVATION:');
    print(data[0]);

    // Get the rows per page.
    final rowsPerPage = ref.watch(resultsRowsPerPageProvider);

    // Format the table headers.
    List<String> headers = ['ID', 'Test', 'Notes'];
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
        ref.read(resultsRowsPerPageProvider.notifier).state = index!;
      },
      showCheckboxColumn: false,
      source: ResultsTableSource(
        data: data,
        onTap: (LabResult item) {
          // String slug = Format.slugify(item.name);
          context.go('/results/${item.id}');
        },
      ),
    );
  }
}

/// Results table data.
class ResultsTableSource extends DataTableSource {
  ResultsTableSource({
    required this.data,
    this.onTap,
  });

  // Properties.
  final List<LabResult> data;
  final void Function(LabResult item)? onTap;

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
        DataCell(Text(item.labTestTypeName)),
        DataCell(Text(item.notes)),
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

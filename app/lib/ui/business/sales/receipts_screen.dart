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
import 'package:cannlytics_app/models/metrc/sales_receipt.dart';
import 'package:cannlytics_app/ui/business/sales/receipts_controller.dart';
import 'package:cannlytics_app/ui/general/footer.dart';
import 'package:cannlytics_app/ui/general/header.dart';
import 'package:cannlytics_app/utils/string_utils.dart';
import 'package:cannlytics_app/widgets/layout/custom_placeholder.dart';
import 'package:cannlytics_app/widgets/layout/table_form.dart';

/// The receipts screen.
class ReceiptsScreen extends StatelessWidget {
  const ReceiptsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    // Render the widget.
    return Scaffold(
      body: CustomScrollView(
        slivers: [
          // App header.
          const SliverToBoxAdapter(child: AppHeader()),

          // Receipts form.
          SliverToBoxAdapter(
            child: TableForm(
              title: 'Receipts',
              table: ReceiptsTable(),
            ),
          ),

          // Footer
          const SliverToBoxAdapter(child: Footer()),
        ],
      ),
    );
  }
}

/// Receipts table.
class ReceiptsTable extends ConsumerWidget {
  const ReceiptsTable({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    // Get the data for the primary license / facility.
    final data = ref.watch(receiptsProvider).value ?? [];

    // Return a placeholder if no data.
    if (data.length == 0)
      return CustomPlaceholder(
        image: 'assets/images/icons/spend.png',
        title: 'No receipts',
        description: 'You do not have any active receipts for this facility.',
        onTap: () {
          context.go('/receipts/new');
        },
      );

    print('OBSERVATION:');
    print(data[0]);

    // Get the rows per page.
    final rowsPerPage = ref.watch(receiptsRowsPerPageProvider);

    // Format the table headers.
    List<String> headers = ['ID', 'Manifest Number', 'Name'];
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
        ref.read(receiptsRowsPerPageProvider.notifier).state = index!;
      },
      showCheckboxColumn: false,
      source: ReceiptsTableSource(
        data: data,
        onTap: (SalesReceipt item) {
          var _id = item.salesDateTime.toIso8601String();
          _id = Format.slugify(_id);
          context.go('/receipts/$_id');
        },
      ),
    );
  }
}

/// Receipts table data.
class ReceiptsTableSource extends DataTableSource {
  ReceiptsTableSource({
    required this.data,
    this.onTap,
  });

  // Properties.
  final List<SalesReceipt> data;
  final void Function(SalesReceipt item)? onTap;

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
        DataCell(Text(item.caregiverLicenseNumber)),
        DataCell(Text(item.identificationMethod)),
        DataCell(Text(item.patientLicenseNumber)),
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

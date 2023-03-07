// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 2/18/2023
// Updated: 3/7/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Flutter imports:
import 'package:cannlytics_app/constants/design.dart';
import 'package:cannlytics_app/models/metrc/facility.dart';
import 'package:cannlytics_app/utils/strings/string_format.dart';
import 'package:cannlytics_app/widgets/layout/custom_placeholder.dart';
import 'package:flutter/material.dart';

// Package imports:
import 'package:flutter_riverpod/flutter_riverpod.dart';

// Project imports:
import 'package:cannlytics_app/ui/business/facilities/facilities_controller.dart';
import 'package:cannlytics_app/ui/general/footer.dart';
import 'package:cannlytics_app/ui/general/header.dart';
import 'package:go_router/go_router.dart';

/// The facilities screen.
class FacilitiesScreen extends StatelessWidget {
  const FacilitiesScreen({super.key});

  @override
  Widget build(BuildContext context) {
    // Render the widget.
    return Scaffold(
      body: CustomScrollView(
        slivers: [
          // App header.
          const SliverToBoxAdapter(child: AppHeader()),

          // Facilities form.
          SliverToBoxAdapter(child: FacilitiesForm()),

          // Footer
          const SliverToBoxAdapter(child: Footer()),
        ],
      ),
    );
  }
}

/// Facilities form.
class FacilitiesForm extends ConsumerWidget {
  const FacilitiesForm({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    // Determine the screen size.
    final screenWidth = MediaQuery.of(context).size.width;

    // Build the form.
    return Consumer(
      builder: (context, ref, child) {
        return Container(
          color: Theme.of(context).scaffoldBackgroundColor,
          margin: EdgeInsets.only(top: Insets(1).md),
          constraints: BoxConstraints(
            minHeight: 320,
          ),
          child: Center(
            child: SizedBox(
              width: Breakpoints.desktop.toDouble(),
              child: Padding(
                padding: EdgeInsets.symmetric(
                  horizontal: horizontalPadding(screenWidth),
                ),
                child: Column(
                  children: [
                    // Table header.
                    Row(
                      children: [
                        // Title
                        Text(
                          'Facilities',
                          style:
                              Theme.of(context).textTheme.titleLarge!.copyWith(
                                    color: Theme.of(context)
                                        .textTheme
                                        .titleLarge!
                                        .color,
                                  ),
                        ),
                      ],
                    ),

                    // Space.
                    gapH6,

                    // Table.
                    Row(
                      children: [
                        Expanded(
                          child: SizedBox(
                            width: MediaQuery.of(context).size.width,
                            child: FacilitiesTable(),
                          ),
                        ),
                      ],
                    ),
                  ],
                ),
              ),
            ),
          ),
        );
      },
    );
  }
}

/// Facilities table.
class FacilitiesTable extends ConsumerWidget {
  const FacilitiesTable({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    // Get the facilities for the primary license.
    final data = ref.watch(facilitiesProvider).value ?? [];

    // Return a placeholder if no organizations.
    if (data.length == 0)
      return CustomPlaceholder(
        image: 'assets/images/icons/facilities.png',
        title: 'No facilities',
        description: 'There are no facilities associated with your license.',
        onTap: () {
          context.go('/facilities/new');
        },
      );

    // Get the rows per page.
    final rowsPerPage = ref.watch(facilitiesRowsPerPageProvider);

    // Format the table headers.
    List<String> headers = ['Name', 'DBA', 'License Type'];
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
      availableRowsPerPage: [5, 25, 50],
      rowsPerPage: rowsPerPage,
      onRowsPerPageChanged: (index) {
        ref.read(facilitiesRowsPerPageProvider.notifier).state = index!;
      },
      showCheckboxColumn: false,
      source: FacilitiesTableSource(
        data: data,
        onTap: (Facility item) {
          String slug = Format.slugify(item.displayName);
          context.go('/facilities/$slug');
        },
      ),
    );
  }
}

/// Facilities table data.
class FacilitiesTableSource extends DataTableSource {
  FacilitiesTableSource({
    required this.data,
    this.onTap,
  });

  // Properties.
  final List<Facility> data;
  final void Function(Facility item)? onTap;

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
        DataCell(Text(item.name)),
        DataCell(Text(item.displayName)),
        DataCell(Text(item.licenseType)),
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

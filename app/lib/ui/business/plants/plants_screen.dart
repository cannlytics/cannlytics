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
import 'package:cannlytics_app/constants/design.dart';
import 'package:cannlytics_app/models/metrc/plant.dart';
import 'package:cannlytics_app/services/theme_service.dart';
import 'package:cannlytics_app/ui/business/plants/plants_controller.dart';
import 'package:cannlytics_app/ui/layout/footer.dart';
import 'package:cannlytics_app/ui/layout/header.dart';
import 'package:cannlytics_app/widgets/buttons/primary_button.dart';
import 'package:cannlytics_app/widgets/layout/custom_placeholder.dart';
import 'package:cannlytics_app/widgets/tables/table_form.dart';

/// The plants screen.
class PlantsScreen extends ConsumerWidget {
  const PlantsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    // Determine the screen size.
    final screenWidth = MediaQuery.of(context).size.width;
    final isWide = screenWidth > Breakpoints.tablet;

    // Table actions.
    var actions = Row(children: [
      // TODO: Allow the user to select rows and perform the following actions.

      // TODO: Move plants.

      // TODO: Destroy plants.

      // TODO: Manicure plants.

      // TODO: Harvest plants.

      // Add plant button.
      PrimaryButton(
        text: isWide ? 'Add a plant' : 'Add',
        onPressed: () {
          context.go('/plants/new');
        },
      ),
    ]);

    // Render the widget.
    return Scaffold(
      body: CustomScrollView(
        slivers: [
          // App header.
          const SliverToBoxAdapter(child: AppHeader()),

          // Plants form.
          SliverToBoxAdapter(
            child: TableForm(
              title: 'Plants',
              table: PlantsTable(),
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

/// Plants table.
class PlantsTable extends ConsumerWidget {
  const PlantsTable({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    // Get the data for the primary license / facility.
    final data = ref.watch(plantsProvider).value ?? [];

    // Get the theme.
    final themeMode = ref.watch(themeModeProvider);
    final bool isDark = themeMode == ThemeMode.dark;

    // Return a placeholder if no data.
    if (data.length == 0)
      return CustomPlaceholder(
        isDark: isDark,
        image: 'assets/images/icons/clones.png',
        title: 'Create plants',
        description: 'You do not have any active plants for this facility.',
        onTap: () {
          context.go('/plants/new');
        },
      );

    print('OBSERVATION:');
    print(data[0]);

    // Get the rows per page.
    final rowsPerPage = ref.watch(plantsRowsPerPageProvider);

    // Format the table headers.
    List<String> headers = ['ID', 'Strain Name', 'Batch Name'];
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
        ref.read(plantsRowsPerPageProvider.notifier).state = index!;
      },
      showCheckboxColumn: false,
      source: PlantsTableSource(
        data: data,
        onTap: (Plant item) {
          // String slug = Format.slugify(item.name);
          context.go('/plants/${item.id}');
        },
      ),
    );
  }
}

/// Plants table data.
class PlantsTableSource extends DataTableSource {
  PlantsTableSource({
    required this.data,
    this.onTap,
  });

  // Properties.
  final List<Plant> data;
  final void Function(Plant item)? onTap;

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
        DataCell(Text(item.strainName)),
        DataCell(Text(item.plantBatchName)),
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

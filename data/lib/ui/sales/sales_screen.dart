// Cannlytics Data
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 4/15/2023
// Updated: 4/15/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Flutter imports:
import 'package:cannlytics_data/services/auth_service.dart';
import 'package:cannlytics_data/common/layout/breadcrumbs.dart';
import 'package:cannlytics_data/common/layout/console.dart';
import 'package:cannlytics_data/common/forms/form_placeholder.dart';
import 'package:flutter/material.dart';

// Project imports:
import 'package:cannlytics_data/constants/design.dart';
import 'package:cannlytics_data/common/layout/header.dart';
import 'package:cannlytics_data/common/layout/sidebar.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

/// Screen.
class SalesScreen extends StatelessWidget {
  const SalesScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      // App bar.
      appBar: DashboardHeader(),

      // Side menu.
      drawer: Responsive.isMobile(context) ? MobileDrawer() : null,

      // Body.
      body: Console(slivers: [
        SliverToBoxAdapter(child: MainContent()),
      ]),
    );
  }
}

/// Main content.
class MainContent extends ConsumerWidget {
  const MainContent({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    // Dynamic screen width.
    final screenWidth = MediaQuery.of(context).size.width;

    // Listen to the current user.
    final user = ref.watch(authProvider).currentUser;

    // Render the widget.
    return Padding(
      padding: EdgeInsets.only(
        left: sliverHorizontalPadding(screenWidth),
        right: sliverHorizontalPadding(screenWidth),
        top: 24,
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        mainAxisAlignment: MainAxisAlignment.start,
        children: [
          SalesTable(),
          gapH48,
        ],
      ),
    );
  }
}

/// Table.
class SalesTable extends ConsumerWidget {
  const SalesTable({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    // Get the filtered data.
    // final data = ref.watch(filteredFacilitiesProvider);
    final data = [];

    // TODO: Actions and breadcrumbs.
    Widget actions = Row(
      children: [
        Breadcrumbs(
          items: [
            BreadcrumbItem(
                title: 'Data',
                onTap: () {
                  context.go('/');
                }),
            BreadcrumbItem(
                title: 'Licensees',
                onTap: () {
                  // Add navigation to Category screen.
                })
          ],
        ),
      ],
    );

    // FIXME: Create a licensees table.
    var table;

    // // Define the cell builder function.
    // _buildCells(Facility item) {
    //   var values = [
    //     item.id,
    //     item.name,
    //     item.displayName,
    //     item.licenseType,
    //   ];
    //   return values.map((value) {
    //     return DataCell(
    //       Text(value),
    //       onTap: () => context.go('/facilities/${item.id}'),
    //     );
    //   }).toList();
    // }

    // // Define the table headers.
    // List<Map> headers = [
    //   {'name': 'ID', 'key': 'id', 'sort': true},
    //   {'name': 'Name', 'key': 'name', 'sort': true},
    //   {'name': 'Display Name', 'key': 'display_name', 'sort': true},
    //   {'name': 'License Type', 'key': 'license_type', 'sort': false},
    // ];

    // // Format the table headers.
    // List<DataColumn> tableHeader = <DataColumn>[
    //   for (Map header in headers)
    //     DataColumn(
    //       label: Expanded(
    //         child: Text(
    //           header['name'],
    //           style: TextStyle(fontStyle: FontStyle.italic),
    //         ),
    //       ),
    //       onSort: (columnIndex, sortAscending) {
    //         var field = headers[columnIndex]['key'];
    //         var sort = headers[columnIndex]['sort'];
    //         if (!sort) return;
    //         var sorted = data;
    //         if (sortAscending) {
    //           sorted = data.sortedBy((x) => x.toMap()[field]);
    //         } else {
    //           sorted = data.sortedByDescending((x) => x.toMap()[field]);
    //         }
    //         ref.read(facilitiesSortColumnIndex.notifier).state = columnIndex;
    //         ref.read(facilitiesSortAscending.notifier).state = sortAscending;
    //         ref.read(facilitiesProvider.notifier).setFacilities(sorted);
    //       },
    //     ),
    // ];

    // // Get the rows per page.
    // final rowsPerPage = ref.watch(facilitiesRowsPerPageProvider);

    // // Get the sorting state.
    // final sortColumnIndex = ref.read(facilitiesSortColumnIndex);
    // final sortAscending = ref.read(facilitiesSortAscending);

    // // Build the data table.
    // Widget table = PaginatedDataTable(
    //   // Options.
    //   showCheckboxColumn: false,
    //   showFirstLastButtons: true,
    //   sortColumnIndex: sortColumnIndex,
    //   sortAscending: sortAscending,

    //   // Columns
    //   columns: tableHeader,

    //   // Style.
    //   dataRowHeight: 48,
    //   columnSpacing: 48,
    //   headingRowHeight: 48,
    //   horizontalMargin: 12,

    //   // Pagination.
    //   availableRowsPerPage: [5, 10, 25, 50, 100],
    //   rowsPerPage: rowsPerPage,
    //   onRowsPerPageChanged: (index) {
    //     ref.read(facilitiesRowsPerPageProvider.notifier).state = index!;
    //   },

    //   // Table.
    //   source: TableData<Facility>(
    //     data: data,
    //     cellsBuilder: _buildCells,
    //   ),
    // );

    // // Read the search controller.
    // final _controller = ref.watch(facilitiesSearchController);

    // // Define the table actions.
    // var actions = Row(
    //   children: [
    //     // Search box.
    //     SizedBox(
    //       width: 175,
    //       child: TypeAheadField(
    //         textFieldConfiguration: TextFieldConfiguration(
    //           // Controller.
    //           controller: _controller,

    //           // Decoration.
    //           decoration: InputDecoration(
    //             hintText: 'Search...',
    //             contentPadding:
    //                 EdgeInsets.symmetric(horizontal: 12, vertical: 8),
    //             border: OutlineInputBorder(
    //               borderRadius: BorderRadius.all(Radius.circular(3)),
    //             ),
    //             suffixIcon: _controller.text.isNotEmpty
    //                 ? GestureDetector(
    //                     onTap: () {
    //                       ref.read(searchTermProvider.notifier).state = '';
    //                       _controller.clear();
    //                     },
    //                     child: Icon(Icons.clear),
    //                   )
    //                 : null,
    //           ),
    //           style: DefaultTextStyle.of(context)
    //               .style
    //               .copyWith(fontStyle: FontStyle.italic),
    //         ),
    //         // Search engine function.
    //         suggestionsCallback: (pattern) async {
    //           ref.read(searchTermProvider.notifier).state = pattern;
    //           final suggestions = ref.read(filteredFacilitiesProvider);
    //           return suggestions;
    //         },

    //         // Autocomplete menu.
    //         itemBuilder: (BuildContext context, Facility suggestion) {
    //           return ListTile(title: Text(suggestion.name));
    //         },

    //         // Menu selection function.
    //         onSuggestionSelected: (Facility suggestion) {
    //           context.go('/facilities/${suggestion.id}');
    //         },
    //       ),
    //     ),
    //   ],
    // );

    // TODO: Loading placeholder.
    if (data.isEmpty)
      table = FormPlaceholder(
        image: 'assets/images/icons/facilities.png',
        title: 'Add a facility',
        description:
            'Facilities are used to track packages, items, and plants.',
        onTap: () {
          context.go('/facilities/new');
        },
      );
    return Column(children: [actions, gapH12, table]);
  }
}

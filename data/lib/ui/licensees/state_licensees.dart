// Cannlytics Data
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 5/7/2023
// Updated: 5/8/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Flutter imports:
import 'package:cannlytics_data/common/buttons/secondary_button.dart';
import 'package:cannlytics_data/common/forms/form_placeholder.dart';
import 'package:cannlytics_data/common/layout/breadcrumbs.dart';
import 'package:cannlytics_data/common/layout/console.dart';
import 'package:cannlytics_data/common/layout/footer.dart';
import 'package:cannlytics_data/common/layout/header.dart';
import 'package:cannlytics_data/common/layout/sidebar.dart';
import 'package:cannlytics_data/common/tables/table_data.dart';
import 'package:cannlytics_data/models/licensee.dart';
import 'package:cannlytics_data/services/data_service.dart';
import 'package:cannlytics_data/ui/licensees/licensees_controller.dart';
import 'package:dartx/dartx.dart';
import 'package:flutter/material.dart';

// Project imports:
import 'package:cannlytics_data/constants/design.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_typeahead/flutter_typeahead.dart';
import 'package:go_router/go_router.dart';

/// Screen.
class StateLicensesScreen extends StatelessWidget {
  const StateLicensesScreen({super.key, required this.id});

  // Properties.
  final String id;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      // App bar.
      appBar: DashboardHeader(),

      // Side menu.
      drawer: Responsive.isMobile(context) ? MobileDrawer() : null,

      // Body.
      body: Console(slivers: [
        // Table.
        SliverToBoxAdapter(
          child: Container(
            height: 750,
            child: MainContent(id: id),
          ),
        ),

        // Footer.
        const SliverToBoxAdapter(child: Footer()),
      ]),
    );
  }
}

/// Main content.
class MainContent extends ConsumerWidget {
  const MainContent({Key? key, required this.id}) : super(key: key);
  final String id;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final screenWidth = MediaQuery.of(context).size.width;
    // FIXME: Set the active state.
    // ref.read(activeStateProvider.notifier).state = id;
    return Padding(
      padding: EdgeInsets.only(
        left: sliverHorizontalPadding(screenWidth) / 2,
        right: sliverHorizontalPadding(screenWidth) / 2,
        top: 24,
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        mainAxisAlignment: MainAxisAlignment.start,
        children: [
          _breadcrumbs(context),
          gapH8,
          LicenseesTable(id: id),
          gapH48,
        ],
      ),
    );
  }

  /// Page breadcrumbs.
  Widget _breadcrumbs(BuildContext context) {
    return Row(
      children: [
        Breadcrumbs(
          items: [
            BreadcrumbItem(
                title: 'Data',
                onTap: () {
                  context.push('/');
                }),
            BreadcrumbItem(
                title: 'Licenses',
                onTap: () {
                  context.push('/licenses');
                }),
            BreadcrumbItem(
              title: id.toUpperCase(),
            ),
          ],
        ),
      ],
    );
  }
}

/// Table.
class LicenseesTable extends ConsumerWidget {
  const LicenseesTable({super.key, required this.id});
  final String id;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    // FIXME: Get the filtered data.
    final data = ref.watch(filteredLicenseesProvider);
    print('NO DATA YET...');
    // if (ref.read(activeStateProvider) == null) {
    //   ref.read(activeStateProvider.notifier).state = id;
    //   // return Center(child: CircularProgressIndicator(strokeWidth: 1.42));
    // }
    print('DATA: ${data.length}');
    if (data.isEmpty) {
      return FormPlaceholder(
        image: 'assets/images/icons/document.png',
        title: 'No licenses',
        description: 'There are no active licenses in this state.',
        onTap: () {
          context.push('/licenses');
        },
      );
    }

    // Define the cell builder function.
    _buildCells(Map item) {
      var values = [
        item['license_number'],
        item['business_legal_name'],
        item['license_type'],
        item['premise_city'],
      ];
      return values.map((value) {
        return DataCell(
          Text(value),
          onTap: () => context.push('/licenses/$id/${item["license_number"]}'),
        );
      }).toList();
    }

    // Define the table headers.
    List<Map> headers = [
      {'name': 'License number', 'key': 'license_number', 'sort': true},
      {
        'name': 'Business legal name',
        'key': 'business_legal_name',
        'sort': true
      },
      {'name': 'License type', 'key': 'license_type', 'sort': true},
      {'name': 'Premise city', 'key': 'premise_city', 'sort': false},
    ];

    // Format the table headers.
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
            ref.read(licenseesSortColumnIndex.notifier).state = columnIndex;
            ref.read(licenseesSortAscending.notifier).state = sortAscending;
            // FIXME:
            ref.read(licenseesProvider.notifier).setLicensees(sorted);
          },
        ),
    ];

    // Get the rows per page.
    final rowsPerPage = ref.watch(licenseesRowsPerPageProvider);

    // Get the sorting state.
    final sortColumnIndex = ref.read(licenseesSortColumnIndex);
    final sortAscending = ref.read(licenseesSortAscending);

    // Build the data table.
    Widget table = PaginatedDataTable(
      // Options.
      showCheckboxColumn: false,
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
        ref.read(licenseesRowsPerPageProvider.notifier).state = index!;
      },

      // Table.
      source: TableData<Map<String, dynamic>>(
        data: data,
        cellsBuilder: _buildCells,
      ),
    );

    // Read the search controller.
    final _controller = ref.watch(licenseesSearchController);

    // Define the table actions.
    var actions = Row(
      children: [
        // Search box.
        SizedBox(
          width: 175,
          child: TypeAheadField(
            textFieldConfiguration: TextFieldConfiguration(
              // Controller.
              controller: _controller,

              // Decoration.
              decoration: InputDecoration(
                hintText: 'Search...',
                contentPadding:
                    EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.all(Radius.circular(3)),
                ),
                suffixIcon: _controller.text.isNotEmpty
                    ? GestureDetector(
                        onTap: () {
                          ref.read(searchTermProvider.notifier).state = '';
                          _controller.clear();
                        },
                        child: Icon(Icons.clear),
                      )
                    : null,
              ),
              style: DefaultTextStyle.of(context)
                  .style
                  .copyWith(fontStyle: FontStyle.italic),
            ),
            // Search engine function.
            suggestionsCallback: (pattern) async {
              ref.read(searchTermProvider.notifier).state = pattern;
              final suggestions = ref.read(filteredLicenseesProvider);
              return suggestions;
            },

            // Autocomplete menu.
            itemBuilder:
                (BuildContext context, Map<String, dynamic>? suggestion) {
              return ListTile(title: Text(suggestion!['business_legal_name']));
            },

            // Menu selection function.
            onSuggestionSelected: (Map<String, dynamic>? suggestion) {
              context.push('/licenses/$id/${suggestion!['id']}');
            },
          ),
        ),

        // Download button.
        SecondaryButton(
          text: 'Download',
          onPressed: () {
            // FIXME: Require the user to be signed in.

            // FIXME: Get the correct datafile (Get download URL from Firebase Storage).
            String url =
                'https://firebasestorage.googleapis.com/v0/b/cannlytics.appspot.com/o/public%2Fdata%2Flicenses%2Fwa%2Flicenses-wa-2023-04-24T21-21-31.csv?alt=media&token=33ab0328-9fa5-4658-b927-5511268fef1a';

            // Download the datafile.
            DataService.openInANewTab(url);
          },
        ),
      ],
    );

    // TODO: Loading placeholder.

    // No data placeholder.
    if (data.isEmpty)
      table = FormPlaceholder(
        image: 'assets/images/icons/document.png',
        title: 'No licenses',
        description: 'There are no active licenses in this state.',
        onTap: () {
          context.push('/licenses');
        },
      );

    // Return the widget.
    table = Material(
      // color: Theme.of(context).secondaryHeaderColor,
      color: Colors.transparent,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(3.0),
      ),
      child: table,
    );
    return Column(children: [actions, gapH12, table]);
  }
}

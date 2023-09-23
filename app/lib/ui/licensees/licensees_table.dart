// Cannlytics Data
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 5/7/2023
// Updated: 8/6/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Flutter imports:
import 'package:flutter/material.dart';

// Package imports:
import 'package:dartx/dartx.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_typeahead/flutter_typeahead.dart';
import 'package:go_router/go_router.dart';

// Project imports:
import 'package:cannlytics_data/common/buttons/secondary_button.dart';
import 'package:cannlytics_data/common/dialogs/auth_dialog.dart';
import 'package:cannlytics_data/common/forms/form_placeholder.dart';
import 'package:cannlytics_data/common/layout/breadcrumbs.dart';
import 'package:cannlytics_data/common/tables/table_data.dart';
import 'package:cannlytics_data/constants/design.dart';
import 'package:cannlytics_data/models/licensee.dart';
import 'package:cannlytics_data/services/data_service.dart';
import 'package:cannlytics_data/services/storage_service.dart';
import 'package:cannlytics_data/ui/account/account_controller.dart';
import 'package:cannlytics_data/ui/layout/console.dart';
import 'package:cannlytics_data/ui/licensees/licensees_service.dart';
import 'package:cannlytics_data/utils/utils.dart';

/// Screen.
class StateLicensesScreen extends StatelessWidget {
  const StateLicensesScreen({
    super.key,
    required this.stateId,
  });

  // Parameters.
  final String stateId;

  @override
  Widget build(BuildContext context) {
    return ConsoleScreen(
      children: [
        // Breadcrumbs.
        SliverToBoxAdapter(
          child: BreadcrumbsRow(
            items: [
              {'label': 'Data', 'path': '/'},
              {'label': 'Licenses', 'path': '/licenses'},
              {'label': stateId.toUpperCase(), 'path': '/licenses/$stateId'},
            ],
          ),
        ),

        // Table.
        SliverToBoxAdapter(
          child: SingleChildScrollView(
            child: Padding(
              padding: EdgeInsets.only(
                left: 16,
                right: 16,
                top: 24,
              ),
              child: Column(
                children: [
                  LicenseesTable(stateId: stateId),
                ],
              ),
            ),
          ),
        ),
      ],
    );
  }
}

/// Table.
class LicenseesTable extends ConsumerWidget {
  const LicenseesTable({
    super.key,
    required this.stateId,
  });

  // Parameters.
  final String stateId;

  /// Error placeholder.
  Widget _errorMessage(BuildContext context) {
    return FormPlaceholder(
      image: 'assets/images/icons/document.png',
      title: 'No licenses found',
      description:
          'Either there are no active licenses in this state or the data has not yet been populated.\nPlease contact dev@cannlytics.com to get a person on this ASAP.',
      onTap: () {
        context.go('/licenses');
      },
    );
  }

  /// No data placeholder.
  Widget _noData(BuildContext context) {
    return FormPlaceholder(
      image: 'assets/images/icons/document.png',
      title: 'No licenses found',
      description:
          'Either there are no active licenses in this state or the data has not yet been populated.\nPlease contact dev@cannlytics.com to get a person on this ASAP.',
      onTap: () {
        context.go('/licenses');
      },
    );
  }

  /// Loading results placeholder.
  Widget _loadingPlaceholder() {
    return Padding(
      padding: EdgeInsets.all(16),
      child: Center(
        child: CircularProgressIndicator(strokeWidth: 1.42),
      ),
    );
  }

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    // Listen to the state's licensees data.
    final asyncData = ref.watch(filteredLicenseesProvider);
    return asyncData.when(
        loading: () => _loadingPlaceholder(),
        error: (error, stack) => _errorMessage(context),
        data: (data) {
          // Listen to the current user.
          final user = ref.watch(userProvider).value;

          // Table style.
          bool isMobile = MediaQuery.of(context).size.width < 600;
          var fieldStyle = Theme.of(context).textTheme.bodySmall;
          var columnStyle = Theme.of(context).textTheme.bodySmall?.copyWith(
                fontStyle: FontStyle.italic,
              );

          // Define the table headers.
          List<Map> headers = [
            {
              'name': 'License number',
              'key': 'license_number',
              'sort': true,
            },
            {
              'name': 'Legal name',
              'key': 'business_legal_name',
              'sort': true,
            },
            {
              'name': 'DBA',
              'key': 'business_dba_name',
              'sort': true,
            },
            if (!isMobile)
              {
                'name': 'License type',
                'key': 'license_type',
                'sort': true,
              },
            if (!isMobile)
              {
                'name': 'Premise city',
                'key': 'premise_city',
                'sort': true,
              },
          ];

          // Define the cell builder function.
          _buildCells(Map item) {
            var values = [
              item['license_number'],
              item['business_legal_name'],
              item['business_dba_name'],
              if (!isMobile) item['license_type'],
              if (!isMobile) item['premise_city'],
            ];
            return values.map((value) {
              return DataCell(
                (value is double && value.isNaN) || value == null
                    ? Container()
                    : Text('$value', style: fieldStyle),
                onTap: () {
                  String slug = StringUtils.slugify(item['license_number']);
                  context.go('/licenses/$stateId/$slug');
                },
              );
            }).toList();
          }

          // Format the table headers.
          List<DataColumn> tableHeader = <DataColumn>[
            for (Map header in headers)
              DataColumn(
                label: Expanded(
                  child: Text(
                    header['name'],
                    style: columnStyle,
                  ),
                ),
                onSort: (columnIndex, sortAscending) {
                  var field = headers[columnIndex]['key'];
                  var sort = headers[columnIndex]['sort'];
                  if (!sort) return;
                  // ignore: unused_local_variable
                  var sorted = data;
                  if (sortAscending) {
                    sorted = data.sortedBy((x) => x?.toMap()[field] as String);
                  } else {
                    sorted = data
                        .sortedByDescending((x) => x?.toMap()[field] as String);
                  }
                  ref.read(licenseesSortColumnIndex.notifier).state =
                      columnIndex;
                  ref.read(licenseesSortAscending.notifier).state =
                      sortAscending;
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
            dataRowMinHeight: 24,
            columnSpacing: 18,
            // headingRowHeight: 28,
            horizontalMargin: 8,

            // Pagination.
            availableRowsPerPage: [5, 10, 25, 50, 100],
            rowsPerPage: rowsPerPage,
            onRowsPerPageChanged: (index) {
              ref.read(licenseesRowsPerPageProvider.notifier).state = index!;
            },

            // Table.
            source: TableData<Map<String, dynamic>>(
              data: data.map((e) => e?.toMap() ?? {}).toList(),
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
                width: isMobile ? 200 : 420,
                child: TypeAheadField(
                  suggestionsBoxDecoration: SuggestionsBoxDecoration(
                    borderRadius: BorderRadius.only(
                      topLeft: Radius.zero,
                      bottomLeft: Radius.zero,
                      topRight: Radius.circular(3),
                      bottomRight: Radius.circular(3),
                    ),
                    color: Theme.of(context).scaffoldBackgroundColor,
                  ),
                  textFieldConfiguration: TextFieldConfiguration(
                    // Controller.
                    controller: _controller,

                    // Decoration.
                    decoration: InputDecoration(
                      hintText: 'Search...',
                      labelText: 'Search...',
                      labelStyle: Theme.of(context).textTheme.bodyMedium,
                      contentPadding: EdgeInsets.only(
                        top: 18,
                        left: 8,
                        right: 8,
                        bottom: 8,
                      ),
                      border: OutlineInputBorder(
                        borderRadius: BorderRadius.only(
                          topLeft: Radius.circular(3),
                          bottomLeft: Radius.circular(3),
                          topRight: Radius.zero,
                          bottomRight: Radius.zero,
                        ),
                      ),
                      suffixIcon: _controller.text.isNotEmpty
                          ? GestureDetector(
                              onTap: () {
                                ref.read(licenseeSearchTerm.notifier).state =
                                    '';
                                _controller.clear();
                              },
                              child: Icon(
                                Icons.clear,
                                color: Theme.of(context)
                                    .textTheme
                                    .labelMedium!
                                    .color,
                              ),
                            )
                          : null,
                    ),
                    style: DefaultTextStyle.of(context)
                        .style
                        .copyWith(fontStyle: FontStyle.italic),
                  ),

                  // Autocomplete menu.
                  itemBuilder: (BuildContext context, Licensee? item) {
                    var title = (item?.businessLegalName is double &&
                                item?.businessLegalName.isNaN) ||
                            item?.businessLegalName == null
                        ? item?.businessDbaName
                        : item?.businessLegalName;
                    if ((item?.licenseNumber is double &&
                            !item?.licenseNumber.isNaN) ||
                        item?.licenseNumber is String) {
                      title = '$title (${item?.licenseNumber})';
                    }
                    return ListTile(
                      title: Text(
                        title,
                        style: Theme.of(context).textTheme.bodySmall,
                      ),
                    );
                  },

                  // Search engine function.
                  suggestionsCallback: (pattern) async {
                    ref
                        .read(licenseeSearchTerm.notifier)
                        .update((state) => pattern);
                    final suggestions = ref.read(filteredLicenseesProvider);
                    return suggestions.value!;
                  },

                  // Menu selection function.
                  onSuggestionSelected: (Licensee? suggestion) {
                    // Navigate to the licenses page on selection.
                    context
                        .go('/licenses/$stateId/${suggestion!.licenseNumber}');
                  },

                  // Loading indicator.
                  loadingBuilder: (BuildContext context) {
                    return ListTile(
                      title: CircularProgressIndicator(strokeWidth: 1.42),
                    );
                  },

                  // No items found.
                  noItemsFoundBuilder: (BuildContext context) {
                    return ListTile(
                      title: Text(
                        'No matches found',
                        style: Theme.of(context).textTheme.bodySmall,
                      ),
                    );
                  },
                ),
              ),

              // Download button.
              Spacer(),
              SecondaryButton(
                text: 'Download',
                onPressed: () async {
                  // Note: Requires the user to be signed in.
                  if (user == null) {
                    showDialog(
                      context: context,
                      builder: (BuildContext context) {
                        return SignInDialog(isSignUp: false);
                      },
                    );
                    return;
                  }

                  // Get download URL from Firebase Storage.
                  String storageRef =
                      'data/licenses/$stateId/licenses-$stateId-latest.csv';
                  String? url = await StorageService.getDownloadUrl(storageRef);
                  if (url == null) return;

                  // Download the datafile.
                  DataService.openInANewTab(url);
                },
              ),
            ],
          );

          // Use the no data placeholder if there is no data.
          if (data.isEmpty) table = _noData(context);

          // Return the widget.
          table = Theme(
            data: Theme.of(context).copyWith(
              cardTheme: CardTheme(
                margin: EdgeInsets.all(0),
                surfaceTintColor: Colors.transparent,
                color: Theme.of(context).scaffoldBackgroundColor,
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(3),
                ),
              ),
            ),
            child: table,
          );
          return Column(children: [actions, gapH12, table, gapH48]);
        });
  }
}

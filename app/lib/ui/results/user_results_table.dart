// Cannlytics Data
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 8/31/2023
// Updated: 9/20/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Flutter imports:
import 'dart:convert';

import 'package:flutter/material.dart';

// Package imports:
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_typeahead/flutter_typeahead.dart';
import 'package:go_router/go_router.dart';

// Project imports:
import 'package:cannlytics_data/common/dialogs/auth_dialog.dart';
import 'package:cannlytics_data/common/forms/form_placeholder.dart';
import 'package:cannlytics_data/common/inputs/date_range_buttons.dart';
import 'package:cannlytics_data/common/inputs/string_controller.dart';
import 'package:cannlytics_data/common/tables/table_data_source.dart';
import 'package:cannlytics_data/constants/colors.dart';
import 'package:cannlytics_data/constants/design.dart';
import 'package:cannlytics_data/constants/theme.dart';
import 'package:cannlytics_data/routing/app_router.dart';
import 'package:cannlytics_data/services/download_service.dart';
import 'package:cannlytics_data/ui/account/account_controller.dart';
import 'package:cannlytics_data/ui/results/results_service.dart';
import 'package:cannlytics_data/utils/utils.dart';

/* === Logic === */

// Rows per page.
final resultsRowsPerPageProvider = StateProvider<int>((ref) => 10);

// Sorting.
final resultsSortColumnIndex = StateProvider<int>((ref) => 0);
final resultsSortAscending = StateProvider<bool>((ref) => true);

// Search term.
final resultsSearchTerm = StateProvider<String>((ref) => '');

// Search input.
final resultsSearchController =
    StateNotifierProvider<StringController, TextEditingController>(
        (ref) => StringController());

// Selection.
final resultsSelectedProvider = StateProvider.autoDispose<int>((ref) => 0);

// Selected data.
final resultsDataSourceProvider = StateNotifierProvider.family<CustomDataSource,
    List<CustomRowData>, List<dynamic>>((ref, data) {
  return CustomDataSource(
    ref: ref,
    data: data as List<Map<dynamic, dynamic>?>,
    onRowLongPressed: (id) {
      ref.read(goRouterProvider).go('/results/$id');
    },
    config: TableConfig(
      fields: [
        'coa_parsed_at',
        'product_name',
        'strain_name',
        'producer',
        'lab',
        'date_tested',
        'total_thc',
        'total_cbd',
        'total_terpenes',
      ],
      idKey: 'sample_id',
      selectedCountProvider: resultsSelectedProvider,
      columnWidths: [
        42,
        100.0,
        160.0,
        160.0,
        160.0,
        160.0,
        160.0,
        100.0,
        100.0,
        100.0
      ],
      onView: (id) {
        ref.read(goRouterProvider).go('/results/$id');
      },
      onDelete: (id) async {
        await ref.read(resultService).deleteResult(id);
        // TODO: Add delete confirmation dialog.
        // final delete = await InterfaceUtils.showAlertDialog(
        //   context: context, // You might need to pass context through, or find another way
        //   title: 'Are you sure that you want to delete this result?',
        //   cancelActionText: 'Cancel',
        //   defaultActionText: 'Delete',
        //   primaryActionColor: Colors.redAccent,
        // );
        // if (delete)
      },
    ),
  );
});

/// Filter.
final resultsFilterProvider = StateNotifierProvider.autoDispose<
    ResultsFilterNotifier, AsyncValue<List<Map?>>>(
  (ref) {
    final searchTerm = ref.watch(resultsSearchTerm);
    final data = ref.watch(userResults).value;
    return ResultsFilterNotifier(ref, data ?? [], searchTerm);
  },
);

/// Filtered results.
class ResultsFilterNotifier extends StateNotifier<AsyncValue<List<Map?>>> {
  // Properties.
  final StateNotifierProviderRef<dynamic, dynamic> ref;
  final List<Map?> items;
  final String searchTerm;

  // Search function.
  // FUTURE WORK: Have search query the database.
  ResultsFilterNotifier(
    this.ref,
    this.items,
    this.searchTerm,
  ) : super(const AsyncLoading()) {
    state =
        searchTerm.isEmpty ? AsyncValue.data(items) : _filterByTerm(searchTerm);
  }

  /// Filter function.
  AsyncValue<List<Map?>> _filterByTerm(String term) {
    String keyword = term.toLowerCase();
    List<Map?> matched =
        items.where((x) => _itemContainsKeyword(x, keyword)).toList();
    return AsyncValue.data(matched);
  }

  /// Filter logic.
  bool _itemContainsKeyword(Map? item, String keyword) {
    Map<String, dynamic> itemMap = {
      'coa_parsed_at': item?['coa_parsed_at'],
      'product_name': item?['product_name'],
      'strain_name': item?['strain_name'],
      'producer': item?['producer'],
      'lab': item?['lab'],
      'date_tested': item?['date_tested'],
      'total_thc': item?['total_thc'],
      'total_cbd': item?['total_cbd'],
      'total_terpenes': item?['total_terpenes'],
    };
    return itemMap.values.any((value) =>
        value != null && value.toString().toLowerCase().contains(keyword));
  }

  /// Sort function.
  void sortResults(
    List<Map<dynamic, dynamic>> headers,
    int columnIndex,
  ) {
    var field = headers[columnIndex]['key'];
    bool currentAscending = ref.read(resultsSortAscending.notifier).state;
    if (currentAscending) {
      items.sort((a, b) => compareValues(a?[field], b?[field]));
    } else {
      items.sort((a, b) => compareValues(b?[field], a?[field]));
    }
    ref.read(resultsSortColumnIndex.notifier).state = columnIndex;
    ref.read(resultsSortAscending.notifier).state = !currentAscending;
    state = AsyncValue.data([...items]);
  }

  /// Sort logic.
  int compareValues(dynamic a, dynamic b) {
    if (a == null && b == null) return 0;
    if (a == null) return -1;
    if (b == null) return 1;
    if (a is String && b is String) return a.compareTo(b);
    if (a is num && b is num) return a.compareTo(b);
    return a.toString().compareTo(b.toString());
  }
}

/* === UI === */

/// Table.
class UserResultsTable extends ConsumerWidget {
  const UserResultsTable({
    super.key,
  });

  /// Error placeholder.
  Widget _errorMessage(BuildContext context) {
    return FormPlaceholder(
      image: 'assets/images/icons/document.png',
      title: 'No results found',
      description:
          "You don't have any results. You can begin parsing your COAs and your aggregated data will appear here.",
      onTap: () {
        // context.go('/licenses');
        // TODO: Open the parse tab.
      },
    );
  }

  /// Loading results placeholder.
  Widget _loadingPlaceholder() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Padding(
          padding: EdgeInsets.all(16),
          child: CircularProgressIndicator(strokeWidth: 1.42),
        ),
      ],
    );
  }

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    // Listen to the filtered data.
    final asyncData = ref.watch(resultsFilterProvider);
    final themeMode = ref.watch(themeModeProvider);
    final bool isDark = themeMode == ThemeMode.dark;
    var mainTable = asyncData.when(
      loading: () => _loadingPlaceholder(),
      error: (error, stack) => _errorMessage(context),
      data: (data) {
        // Listen to the current user.
        final user = ref.watch(userProvider).value;

        // Table style.
        bool isMobile = MediaQuery.of(context).size.width < 600;
        var headerStyle = Theme.of(context).textTheme.titleSmall?.copyWith(
              color: Theme.of(context).textTheme.titleLarge?.color,
              fontWeight: FontWeight.w600,
            );

        // Define the table headers.
        List<Map> headers = [
          {'name': 'Parsed', 'key': 'coa_parsed_at', 'sort': true},
          {'name': 'Product Name', 'key': 'product_name', 'sort': true},
          {'name': 'Strain Name', 'key': 'strain_name', 'sort': true},
          {'name': 'Producer', 'key': 'producer', 'sort': true},
          {'name': 'Lab', 'key': 'lab', 'sort': true},
          {'name': 'Date Tested', 'key': 'date_tested', 'sort': true},
          {'name': 'THC', 'key': 'total_thc', 'sort': true},
          {'name': 'CBD', 'key': 'total_cbd', 'sort': true},
          {'name': 'Terpenes', 'key': 'total_terpenes', 'sort': true},
        ];

        // Format the table headers, with menu at the beginning.
        List<DataColumn> tableHeader = <DataColumn>[
          // Menu column.
          DataColumn(
            label: SizedBox(
              width: 42.0,
              child: Text(''),
            ),
          ),

          // Main columns.
          for (Map header in headers)
            DataColumn(
              label: Expanded(
                child: Text(
                  header['name'],
                  style: headerStyle,
                ),
              ),

              // Sorting logic.
              onSort: (columnIndex, ascending) {
                ref
                    .read(resultsFilterProvider.notifier)
                    .sortResults(headers, columnIndex);
              },
            ),
        ];

        // Get the rows per page.
        var rowsPerPage = ref.watch(resultsRowsPerPageProvider);
        if (rowsPerPage > data.length) rowsPerPage = data.length;
        if (rowsPerPage == 0) rowsPerPage = 1;

        // Set the available rows per page.
        var availableRowsPerPage = <int>[10, 50, 100, data.length];
        if (data.length < 20) {
          availableRowsPerPage = [10];
        } else if (data.length < 100) {
          availableRowsPerPage = [10, 25, 50];
        } else {
          availableRowsPerPage = [10, 50, 100];
        }
        if (!availableRowsPerPage.contains(rowsPerPage)) {
          availableRowsPerPage.add(rowsPerPage);
          availableRowsPerPage.sort();
        }
        if (!availableRowsPerPage.contains(data.length)) {
          availableRowsPerPage.add(data.length);
          availableRowsPerPage.sort();
        }

        // Get the sorting state.
        final sortColumnIndex = ref.watch(resultsSortColumnIndex);
        final sortAscending = ref.watch(resultsSortAscending);

        // Read the search controller.
        final _searchController = ref.watch(resultsSearchController);

        // Search box.
        var searchBox = SizedBox(
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
              controller: _searchController,

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
                prefixIcon: Icon(
                  Icons.search,
                  color: Theme.of(context).textTheme.labelMedium!.color,
                ),
                suffixIcon: _searchController.text.isNotEmpty
                    ? IconButton(
                        icon: Icon(
                          Icons.clear,
                          color: Theme.of(context).textTheme.labelMedium!.color,
                        ),
                        onPressed: () {
                          ref.read(resultsSearchTerm.notifier).state = '';
                          _searchController.clear();
                        },
                      )
                    : null,
              ),
              style: DefaultTextStyle.of(context)
                  .style
                  .copyWith(fontStyle: FontStyle.italic),
            ),

            // Autocomplete menu.
            itemBuilder: (BuildContext context, Map? item) {
              String title = item?['product_name'] ?? 'Unknown';
              return ListTile(
                title: Text(
                  title,
                  style: Theme.of(context).textTheme.bodySmall,
                ),
              );
            },

            // Search engine function.
            suggestionsCallback: (pattern) async {
              ref.read(resultsSearchTerm.notifier).update((state) => pattern);
              final suggestions = ref.read(resultsFilterProvider);
              return suggestions.value!;
            },

            // Menu selection function.
            onSuggestionSelected: (Map? suggestion) {
              String slug = suggestion?['sample_id'];
              context.go('/results/$slug');
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
        );

        // Define the table actions.
        final selectedRowCount = ref.watch(resultsSelectedProvider);
        var actions = Row(
          children: [
            // Download button.
            IconButton(
              icon: Icon(
                Icons.cloud_download,
                color: isDark ? DarkColors.darkText : LightColors.darkText,
              ),
              onPressed: () async {
                if (user == null) {
                  showDialog(
                    context: context,
                    builder: (BuildContext context) {
                      return SignInDialog(isSignUp: false);
                    },
                  );
                  return;
                }
                final dataSource =
                    ref.read(resultsDataSourceProvider(data).notifier);
                var selectedRows = dataSource.dataTableSource.data
                    .where((row) => row.selected)
                    .map((row) => row.data)
                    .toList();
                if (selectedRows.length == 0) {
                  selectedRows = data;
                }
                List<Map<String, dynamic>> encodedSelectedRows =
                    selectedRows.map((row) {
                  var encodedRow = <String, dynamic>{};
                  for (var key in row!.keys) {
                    var value = row[key];
                    if (value is List || value is Map) {
                      encodedRow[key] = jsonEncode(value);
                    } else if (value == null) {
                      encodedRow[key] =
                          ""; // Convert null values to empty string
                    } else {
                      encodedRow[key] = value
                          .toString(); // Convert other data types to string
                    }
                  }
                  return encodedRow;
                }).toList();
                DownloadService.downloadData(
                  encodedSelectedRows,
                  '/api/data/coas/download',
                );
              },
              tooltip: 'Download',
            ),

            // Delete button.
            if (selectedRowCount > 0) ...[
              IconButton(
                icon: Icon(
                  Icons.delete,
                  color: isDark ? DarkColors.darkText : LightColors.darkText,
                ),
                onPressed: () async {
                  final delete = await InterfaceUtils.showAlertDialog(
                    context: context,
                    title:
                        'Are you sure that you want to delete these results?',
                    cancelActionText: 'Cancel',
                    defaultActionText: 'Delete',
                    primaryActionColor: Colors.redAccent,
                  );
                  if (delete == true) {
                    // Only delete selected.
                    final dataSource =
                        ref.read(resultsDataSourceProvider(data).notifier);
                    var selectedRows = dataSource.dataTableSource.data
                        .where((row) => row.selected)
                        .map((row) => row.data)
                        .toList();
                    for (var item in selectedRows) {
                      ref
                          .read(resultService)
                          .deleteResult(item?['sample_id'] ?? item?['id']);
                    }
                  }
                },
                tooltip: 'Delete',
              ),
            ],
          ],
        );

        // Build the data table.
        Widget table = PaginatedDataTable(
          // Options.
          showCheckboxColumn: true,
          showFirstLastButtons: true,
          sortColumnIndex: sortColumnIndex,
          sortAscending: sortAscending,

          // Columns
          columns: tableHeader,

          // Style.
          arrowHeadColor: Theme.of(context).textTheme.titleLarge?.color,
          dataRowMinHeight: 24,
          columnSpacing: 18,
          // headingRowHeight: 28,
          horizontalMargin: 8,

          // Pagination.
          availableRowsPerPage: availableRowsPerPage,
          rowsPerPage: rowsPerPage,
          onRowsPerPageChanged: (index) {
            ref.read(resultsRowsPerPageProvider.notifier).state = index!;
          },

          // Selection.
          onSelectAll: (bool? selected) {
            if (selected != null) {
              final dataSource =
                  ref.read(resultsDataSourceProvider(data).notifier);
              dataSource.dataTableSource.selectAll(selected);
            }
          },

          // Table.
          header: Container(),
          actions: [
            actions,
            DateRangeButtons(
              isDark: true,
              startDateProvider: startDateProvider,
              endDateProvider: endDateProvider,
            ),
          ],
          source: ref
              .read(resultsDataSourceProvider(data).notifier)
              .dataTableSource,
        );

        // Return the widget.
        table = Theme(
          data: Theme.of(context).copyWith(
            // TODO: Figure out how to change the onRowLongPressed color.
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
        return Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [searchBox, gapH12, table, gapH48],
        );
      },
    );

    // Render the table once results are loaded.
    final asyncResults = ref.watch(userResults);
    return asyncResults.when(
      loading: () => _loadingPlaceholder(),
      error: (error, stack) => _errorMessage(context),
      data: (resultsData) => mainTable,
    );
  }
}

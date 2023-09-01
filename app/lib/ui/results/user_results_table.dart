// Cannlytics Data
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 8/31/2023
// Updated: 8/31/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Flutter imports:
import 'package:cannlytics_data/common/inputs/string_controller.dart';
import 'package:cannlytics_data/routing/app_router.dart';
import 'package:cannlytics_data/services/download_service.dart';
import 'package:cannlytics_data/ui/results/results_service.dart';
import 'package:cannlytics_data/utils/utils.dart';
import 'package:flutter/material.dart';

// Package imports:
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_typeahead/flutter_typeahead.dart';
import 'package:go_router/go_router.dart';

// Project imports:
import 'package:cannlytics_data/common/buttons/secondary_button.dart';
import 'package:cannlytics_data/common/dialogs/auth_dialog.dart';
import 'package:cannlytics_data/common/forms/form_placeholder.dart';
import 'package:cannlytics_data/constants/design.dart';
import 'package:cannlytics_data/ui/account/account_controller.dart';

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
      'product_name': item?['product_name'],
      'product_type': item?['product_type'],
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

// Selection.
final selectedRowsProvider = StateProvider.autoDispose<List<String>>((_) => []);

// Selected data.
final customDataSourceProvider = StateNotifierProvider.family<CustomDataSource,
    List<CustomRowData>, List<dynamic>>((ref, data) {
  return CustomDataSource(
    data: data as List<Map<dynamic, dynamic>?>,
    onRowLongPressed: (slug) {
      final router = ref.read(goRouterProvider);
      router.go('/results/$slug');
    },
  );
});

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

  /// No data placeholder.
  Widget _noData(BuildContext context) {
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
    return Padding(
      padding: EdgeInsets.all(16),
      child: Center(
        child: CircularProgressIndicator(strokeWidth: 1.42),
      ),
    );
  }

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    // Listen to the filtered data.
    final asyncData = ref.watch(resultsFilterProvider);
    return asyncData.when(
        loading: () => _loadingPlaceholder(),
        error: (error, stack) => _errorMessage(context),
        data: (data) {
          // Listen to the current user.
          final user = ref.watch(userProvider).value;

          // Table style.
          bool isMobile = MediaQuery.of(context).size.width < 600;
          // var fieldStyle = Theme.of(context).textTheme.bodySmall;
          var columnStyle = Theme.of(context).textTheme.bodySmall?.copyWith(
                fontStyle: FontStyle.italic,
              );

          // Define the table headers.
          List<Map> headers = [
            {'name': 'Product Name', 'key': 'product_name', 'sort': true},
            {'name': 'Type', 'key': 'product_type', 'sort': true},
            {'name': 'Producer', 'key': 'producer', 'sort': true},
            {'name': 'Lab', 'key': 'lab', 'sort': true},
            {'name': 'Date Tested', 'key': 'date_tested', 'sort': true},
            {'name': 'THC', 'key': 'total_thc', 'sort': true},
            {'name': 'CBD', 'key': 'total_cbd', 'sort': true},
            {'name': 'Terpenes', 'key': 'total_terpenes', 'sort': true},
          ];

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

                // Sorting logic.
                onSort: (columnIndex, ascending) {
                  ref
                      .read(resultsFilterProvider.notifier)
                      .sortResults(headers, columnIndex);
                },
              ),
          ];

          // Get the rows per page.
          final rowsPerPage = ref.watch(resultsRowsPerPageProvider);

          // Get the sorting state.
          final sortColumnIndex = ref.watch(resultsSortColumnIndex);
          final sortAscending = ref.watch(resultsSortAscending);

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
            dataRowMinHeight: 24,
            columnSpacing: 18,
            // headingRowHeight: 28,
            horizontalMargin: 8,

            // FIXME: Pagination.
            availableRowsPerPage: [5, 10, 25, 50, 100],
            rowsPerPage: rowsPerPage,
            onRowsPerPageChanged: (index) {
              ref.read(resultsRowsPerPageProvider.notifier).state = index!;
            },

            // Selection.
            onSelectAll: (bool? selected) {
              if (selected != null) {
                final dataSource =
                    ref.read(customDataSourceProvider(data).notifier);
                dataSource.dataTableSource.selectAll(selected);
              }
            },

            // Table.
            source: ref
                .read(customDataSourceProvider(data).notifier)
                .dataTableSource,
          );

          // Read the search controller.
          final _controller = ref.watch(resultsSearchController);

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
                                ref.read(resultsSearchTerm.notifier).state = '';
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
                    ref
                        .read(resultsSearchTerm.notifier)
                        .update((state) => pattern);
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

                  // Download all of the data.
                  DownloadService.downloadData(
                    data,
                    '/api/data/coas/download',
                  );
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

/// Row data.
class CustomRowData {
  final Map? data;
  bool selected;

  CustomRowData({
    this.data,
    required this.selected,
  });
}

class CustomDataTableSource extends DataTableSource {
  final List<CustomRowData> data;
  // ignore: unused_field
  int _selectedCount = 0;
  final Function(String) onRowLongPressed;

  CustomDataTableSource({
    required this.data,
    required this.onRowLongPressed,
  });

  @override
  DataRow getRow(int index) {
    final item = data[index];
    var values = [
      item.data?['product_name'],
      item.data?['product_type'],
      item.data?['producer'],
      item.data?['lab'],
      TimeUtils.formatDate(TimeUtils.parseDate(item.data?['date_tested'])),
      item.data?['total_thc'],
      item.data?['total_cbd'],
      item.data?['total_terpenes'],
    ];
    return DataRow.byIndex(
      index: index,
      selected: item.selected,
      onSelectChanged: (bool? value) {
        if (item.selected != value) {
          _selectedCount += value! ? 1 : -1;
          item.selected = value;
          notifyListeners();
        }
      },
      onLongPress: () => onRowLongPressed(item.data?['sample_id'] ?? ''),
      cells: values.asMap().entries.map((entry) {
        int idx = entry.key;
        var value = entry.value;
        double width = idx >= 4 ? 120.0 : 160.0;
        return DataCell(
          (value is double && value.isNaN) || value == null
              ? Container()
              : Container(
                  width: width,
                  child: Text('$value'),
                ),
        );
      }).toList(),
    );
  }

  @override
  bool get isRowCountApproximate => false;

  @override
  int get rowCount => data.length;

  @override
  int get selectedRowCount => data.where((item) => item.selected).length;

  /// Select all rows.
  void selectAll(bool selected) {
    for (var item in data) {
      item.selected = selected;
    }
    _selectedCount = selected ? data.length : 0;
    notifyListeners();
  }
}

/// Table data provider.
class CustomDataSource extends StateNotifier<List<CustomRowData>> {
  CustomDataTableSource dataTableSource;
  final Function(String) onRowLongPressed;

  CustomDataSource({
    required List<Map?> data,
    required this.onRowLongPressed,
  })  : dataTableSource = CustomDataTableSource(
          onRowLongPressed: onRowLongPressed,
          data: data
              .map((item) => CustomRowData(data: item, selected: false))
              .toList(),
        ),
        super(data
            .map((item) => CustomRowData(data: item, selected: false))
            .toList());
}

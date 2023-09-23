// Cannlytics Data
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 9/2/2023
// Updated: 9/20/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Flutter imports:
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
import 'package:cannlytics_data/ui/sales/receipts_service.dart';
import 'package:cannlytics_data/utils/utils.dart';

/* === Logic === */

// Rows per page.
final receiptsRowsPerPageProvider = StateProvider<int>((ref) => 10);

// Sorting.
final receiptsSortColumnIndex = StateProvider<int>((ref) => 0);
final receiptsSortAscending = StateProvider<bool>((ref) => true);

// Search term.
final receiptsSearchTerm = StateProvider<String>((ref) => '');

// Search input.
final receiptsSearchController =
    StateNotifierProvider<StringController, TextEditingController>(
        (ref) => StringController());

// Selection.
final receiptsSelectedProvider = StateProvider.autoDispose<int>((ref) => 0);

// Selected data.
final receiptsDataSourceProvider = StateNotifierProvider.family<
    CustomDataSource, List<CustomRowData>, List<dynamic>>((ref, data) {
  return CustomDataSource(
    ref: ref,
    data: data as List<Map<dynamic, dynamic>?>,
    onRowLongPressed: (id) {
      ref.read(goRouterProvider).go('/sales/$id');
    },
    config: TableConfig(
      fields: [
        'product_names',
        'retailer',
        'date_sold',
        'total_transactions',
        'total_price',
      ],
      idKey: 'hash',
      selectedCountProvider: receiptsSelectedProvider,
      columnWidths: [240.0, 160.0, 160.0, 160.0, 120.0, 120.0],
      onView: (id) {
        ref.read(goRouterProvider).go('/sales/$id');
      },
      onDelete: (id) async {
        await ref.read(receiptService).deleteReceipt(id);
        // TODO: Add delete confirmation dialog.
        // final delete = await InterfaceUtils.showAlertDialog(
        //   context: context, // You might need to pass context through, or find another way
        //   title: 'Are you sure that you want to delete this receipt?',
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
final receiptsFilterProvider = StateNotifierProvider.autoDispose<
    ReceiptsFilterNotifier, AsyncValue<List<Map?>>>(
  (ref) {
    final searchTerm = ref.watch(receiptsSearchTerm);
    final data = ref.watch(userReceipts).value;
    return ReceiptsFilterNotifier(ref, data ?? [], searchTerm);
  },
);

/// Filtered receipts.
class ReceiptsFilterNotifier extends StateNotifier<AsyncValue<List<Map?>>> {
  // Properties.
  final StateNotifierProviderRef<dynamic, dynamic> ref;
  final List<Map?> items;
  final String searchTerm;

  // Search function.
  // FUTURE WORK: Have search query the database.
  ReceiptsFilterNotifier(
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
      'product_names': item?['product_names'],
      'retailer': item?['retailer'],
      'date_sold': item?['date_sold'],
      'total_transactions': item?['total_transactions'],
      'total_price': item?['total_price'],
    };
    return itemMap.values.any((value) =>
        value != null && value.toString().toLowerCase().contains(keyword));
  }

  /// Sort function.
  void sortReceipts(
    List<Map<dynamic, dynamic>> headers,
    int columnIndex,
  ) {
    var field = headers[columnIndex]['key'];
    bool currentAscending = ref.read(receiptsSortAscending.notifier).state;
    if (currentAscending) {
      items.sort((a, b) => compareValues(a?[field], b?[field]));
    } else {
      items.sort((a, b) => compareValues(b?[field], a?[field]));
    }
    ref.read(receiptsSortColumnIndex.notifier).state = columnIndex;
    ref.read(receiptsSortAscending.notifier).state = !currentAscending;
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
class UserReceiptsTable extends ConsumerWidget {
  const UserReceiptsTable({
    super.key,
  });

  /// Error placeholder.
  Widget _errorMessage(BuildContext context) {
    return FormPlaceholder(
      image: 'assets/images/icons/document.png',
      title: 'No receipts found',
      description:
          "You don't have any receipts. You can begin parsing your receipts and your aggregated data will appear here.",
      onTap: () {
        // context.go('/licenses');
        // TODO: Open the parse tab.
      },
    );
  }

  /// Loading receipts placeholder.
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
    final asyncData = ref.watch(receiptsFilterProvider);
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
          {'name': 'Products', 'key': 'product_names', 'sort': true},
          {'name': 'Retailer', 'key': 'retailer', 'sort': true},
          {'name': 'Date', 'key': 'date_sold', 'sort': true},
          {'name': 'Items', 'key': 'total_transactions', 'sort': true},
          {'name': 'Total Price', 'key': 'total_price', 'sort': true},
        ];

        // Format the table headers.
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
                    .read(receiptsFilterProvider.notifier)
                    .sortReceipts(headers, columnIndex);
              },
            ),
        ];

        // Get the rows per page.
        var rowsPerPage = ref.watch(receiptsRowsPerPageProvider);
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
        final sortColumnIndex = ref.watch(receiptsSortColumnIndex);
        final sortAscending = ref.watch(receiptsSortAscending);

        // Read the search controller.
        final _searchController = ref.watch(receiptsSearchController);

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
                          ref.read(receiptsSearchTerm.notifier).state = '';
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
              ref.read(receiptsSearchTerm.notifier).update((state) => pattern);
              final suggestions = ref.read(receiptsFilterProvider);
              return suggestions.value!;
            },

            // Menu selection function.
            onSuggestionSelected: (Map? suggestion) {
              String slug = suggestion?['hash'];
              context.go('/sales/$slug');
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
        final selectedRowCount = ref.watch(receiptsSelectedProvider);
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
                    ref.read(receiptsDataSourceProvider(data).notifier);
                var selectedRows = dataSource.dataTableSource.data
                    .where((row) => row.selected)
                    .map((row) => row.data)
                    .toList();
                if (selectedRows.length == 0) {
                  selectedRows = data;
                }
                DownloadService.downloadData(
                  selectedRows,
                  '/api/data/receipts/download',
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
                        'Are you sure that you want to delete these receipts?',
                    cancelActionText: 'Cancel',
                    defaultActionText: 'Delete',
                    primaryActionColor: Colors.redAccent,
                  );
                  if (delete == true) {
                    // Only delete selected.
                    final dataSource =
                        ref.read(receiptsDataSourceProvider(data).notifier);
                    var selectedRows = dataSource.dataTableSource.data
                        .where((row) => row.selected)
                        .map((row) => row.data)
                        .toList();
                    for (var item in selectedRows) {
                      ref.read(receiptService).deleteReceipt(item?['hash']);
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
          horizontalMargin: 8,

          // Pagination.
          availableRowsPerPage: availableRowsPerPage,
          rowsPerPage: rowsPerPage,
          onRowsPerPageChanged: (index) {
            ref.read(receiptsRowsPerPageProvider.notifier).state = index!;
          },

          // Selection.
          onSelectAll: (bool? selected) {
            if (selected != null) {
              final dataSource =
                  ref.read(receiptsDataSourceProvider(data).notifier);
              dataSource.dataTableSource.selectAll(selected);
            }
          },

          // Table.
          header: Container(),
          actions: [
            actions,
            DateRangeButtons(
              isDark: true,
              startDateProvider: receiptsStartDateProvider,
              endDateProvider: receiptsEndDateProvider,
            ),
          ],
          source: ref
              .read(receiptsDataSourceProvider(data).notifier)
              .dataTableSource,
        );

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
        return Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [searchBox, gapH12, table, gapH48],
        );
      },
    );

    // Render the table once results are loaded.
    final asyncReceipts = ref.watch(userReceipts);
    return asyncReceipts.when(
      loading: () => _loadingPlaceholder(),
      error: (error, stack) => _errorMessage(context),
      data: (receiptsData) => mainTable,
    );
  }
}

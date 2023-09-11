// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 9/3/2023
// Updated: 9/10/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Flutter imports:
import 'package:flutter/material.dart';

// Package imports:
import 'package:flutter_riverpod/flutter_riverpod.dart';

// Project imports:
import 'package:cannlytics_data/utils/utils.dart';

/// Table configuration.
class TableConfig {
  final List<String> fields;
  final String idKey;
  final dynamic selectedCountProvider;
  final List<double>? columnWidths;
  final Function(String)? onView; // Function to handle view logic
  final Function(String)? onDelete; // Function to handle

  TableConfig({
    required this.fields,
    required this.idKey,
    required this.selectedCountProvider,
    this.columnWidths,
    this.onView,
    this.onDelete,
  });
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

/// Table data source.
class CustomDataTableSource extends DataTableSource {
  final List<CustomRowData> data;
  int _selectedCount = 0;
  final Function(String) onRowLongPressed;
  final dynamic ref;
  final TableConfig config;

  CustomDataTableSource({
    required this.data,
    required this.onRowLongPressed,
    required this.ref,
    required this.config,
  });

  @override
  DataRow getRow(int index) {
    final item = data[index];
    // var values = config.fields.map((field) {
    //   var value = item.data?[field];
    //   return formatCellValue(value);
    // }).toList();
    var values = [
      // Add a dummy value for the new column at the beginning.
      '',
      ...config.fields.map((field) {
        var value = item.data?[field];
        return formatCellValue(value);
      }).toList()
    ];
    return DataRow.byIndex(
      index: index,
      selected: item.selected,
      onLongPress: () => onRowLongPressed(item.data?[config.idKey] ?? ''),
      onSelectChanged: (bool? value) {
        if (item.selected != value) {
          _selectedCount += value! ? 1 : -1;
          item.selected = value;
          ref.read(config.selectedCountProvider.notifier).state =
              _selectedCount;
          notifyListeners();
        }
      },
      cells: values.asMap().entries.map((entry) {
        int idx = entry.key;
        // Menu column.
        if (idx == 0) {
          return DataCell(
            PopupMenuButton<String>(
              icon: Icon(Icons.more_vert),
              padding: EdgeInsets.all(2),
              surfaceTintColor: Colors.transparent,
              onSelected: (value) async {
                if (value == 'View') {
                  config.onView!(item.data?[config.idKey] ?? '');
                } else if (value == 'Delete') {
                  await config.onDelete!(item.data?[config.idKey] ?? '');
                }
              },
              itemBuilder: (BuildContext context) => <PopupMenuEntry<String>>[
                PopupMenuItem<String>(
                  value: 'View',
                  child: Text('View',
                      style: Theme.of(context).textTheme.bodySmall!.copyWith(
                          color: Theme.of(context).textTheme.bodyLarge!.color)),
                ),

                // TODO: Download.

                // TODO: Open file.

                // Optional: Delete.
                // PopupMenuItem<String>(
                //   value: 'Delete',
                //   child: Text('Delete',
                //       style: Theme.of(context)
                //           .textTheme
                //           .bodySmall!
                //           .copyWith(color: Colors.redAccent)),
                // ),
              ],
            ),
          );
        }
        var value = entry.value;
        // double width = idx >= 4 ? 120.0 : 160.0;
        double width =
            config.columnWidths != null && idx < config.columnWidths!.length
                ? config.columnWidths![idx]
                : 160.0; // Default width if not provided
        return DataCell(
          (value is double && value.isNaN) || value == null
              ? Container()
              : Container(
                  width: width,
                  child: Text('$value'),
                ),
        );
      }).toList(),
      // cells: values.asMap().entries.map((entry) {
      //   int idx = entry.key;
      //   var value = entry.value;
      //   // double width = idx >= 4 ? 120.0 : 160.0;
      //   double width =
      //       config.columnWidths != null && idx < config.columnWidths!.length
      //           ? config.columnWidths![idx]
      //           : 160.0; // Default width if not provided
      //   return DataCell(
      //     (value is double && value.isNaN) || value == null
      //         ? Container()
      //         : Container(
      //             width: width,
      //             child: Text('$value'),
      //           ),
      //   );
      // }).toList(),
    );
  }

  /// Select all rows.
  void selectAll(bool selected) {
    for (var item in data) {
      item.selected = selected;
    }
    _selectedCount = selected ? data.length : 0;
    ref.read(config.selectedCountProvider.notifier).state = _selectedCount;
    notifyListeners();
  }

  /// Format a value as a human-readable date if it is a date.
  dynamic formatCellValue(dynamic value) {
    if (value is String) {
      DateTime? parsedDate = TimeUtils.parseDate(value);
      if (parsedDate != null) {
        return TimeUtils.formatDate(parsedDate);
      }
    } else if (value is List) {
      return value.join(', ');
    }
    return value;
  }

  @override
  bool get isRowCountApproximate => false;

  @override
  int get rowCount => data.length;

  @override
  int get selectedRowCount => _selectedCount;
}

/// Table data.
class CustomDataSource extends StateNotifier<List<CustomRowData>> {
  CustomDataTableSource dataTableSource;
  final Function(String) onRowLongPressed;
  final dynamic ref;
  final TableConfig config;

  CustomDataSource({
    required List<Map?> data,
    required this.onRowLongPressed,
    required this.ref,
    required this.config,
  })  : dataTableSource = CustomDataTableSource(
          ref: ref,
          onRowLongPressed: onRowLongPressed,
          data: data
              .map((item) => CustomRowData(data: item, selected: false))
              .toList(),
          config: config,
        ),
        super(data
            .map((item) => CustomRowData(data: item, selected: false))
            .toList());
}

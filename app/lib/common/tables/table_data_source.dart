// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 9/3/2023
// Updated: 9/3/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

import 'package:cannlytics_data/utils/utils.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

/// Table configuration.
class TableConfig {
  final List<String> fields;
  final String idKey;
  final dynamic selectedCountProvider;
  final List<double>? columnWidths;

  TableConfig({
    required this.fields,
    required this.idKey,
    required this.selectedCountProvider,
    this.columnWidths,
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
    var values = config.fields.map((field) {
      var value = item.data?[field];
      return formatCellValue(value);
    }).toList();
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

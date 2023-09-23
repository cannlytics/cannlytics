// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 3/11/2023
// Updated: 5/16/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Flutter imports:
import 'package:flutter/material.dart';

/// Table data.
class TableData<T> extends DataTableSource {
  TableData({
    required this.data,
    required this.cellsBuilder,
    this.onTap,
    this.onSelect,
    this.isSelected,
  });

  // Properties.
  final List<T> data;
  final List<DataCell> Function(T item) cellsBuilder;
  final void Function(T item)? onTap;
  final void Function(bool selected, T item)? onSelect;
  final bool Function(T item)? isSelected;

  @override
  DataRow getRow(int index) {
    final item = data[index];
    return DataRow.byIndex(
      index: index,
      cells: cellsBuilder(item),
      // color: MaterialStateColor.resolveWith(_getDataRowColor),
      selected: isSelected == null ? false : isSelected!(item),
      onSelectChanged: isSelected == null
          ? null
          : (bool? selected) => onSelect!(selected ?? false, item),
      onLongPress: () => onTap!(item),
    );
  }

  @override
  int get rowCount => data.length;

  @override
  bool get isRowCountApproximate => false;

  @override
  int get selectedRowCount => 0;

  // Define the color of the row.
  // Color _getDataRowColor(Set<MaterialState> states) {
  //   if (states.contains(MaterialState.hovered)) {
  //     return Colors.blue;
  //   }
  //   return Colors.transparent;
  // }
}

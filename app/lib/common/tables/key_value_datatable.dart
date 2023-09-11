// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 7/1/2023
// Updated: 7/1/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Flutter imports:
import 'package:flutter/material.dart';

/// A simple data table used to display key, value pairs.
class KeyValueDataTable extends StatelessWidget {
  final String tableName;
  final List<String> labels;
  final List<Widget> values;
  final TextStyle? columnStyle;
  final TextStyle? fieldStyle;
  final double headingRowHeight;
  final double dataRowMinHeight;
  final double horizontalMargin;
  final double columnSpacing;
  final double dividerThickness;

  KeyValueDataTable({
    required this.tableName,
    required this.labels,
    required this.values,
    this.columnStyle,
    this.fieldStyle,
    this.headingRowHeight = 28.0,
    this.dataRowMinHeight = 24.0,
    this.horizontalMargin = 8.0,
    this.columnSpacing = 16.0,
    this.dividerThickness = 0.0,
  });

  @override
  Widget build(BuildContext context) {
    var defaultFieldStyle = Theme.of(context).textTheme.bodySmall;
    var defaultColumnStyle = Theme.of(context).textTheme.titleSmall?.copyWith(
          color: Theme.of(context).textTheme.titleLarge?.color,
          fontWeight: FontWeight.w600,
        );
    return DataTable(
      headingRowHeight: headingRowHeight,
      dataRowMinHeight: dataRowMinHeight,
      horizontalMargin: horizontalMargin,
      columnSpacing: columnSpacing,
      dividerThickness: dividerThickness,
      columns: [
        DataColumn(
            label: Text(tableName, style: columnStyle ?? defaultColumnStyle)),
        DataColumn(label: Text('', style: columnStyle ?? defaultColumnStyle)),
      ],
      rows: List<DataRow>.generate(
        labels.length,
        (index) => DataRow(
          cells: <DataCell>[
            DataCell(
                Text(labels[index], style: fieldStyle ?? defaultFieldStyle)),
            DataCell(values[index]),
          ],
        ),
      ),
    );
  }
}

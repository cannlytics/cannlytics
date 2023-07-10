// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 7/2/2023
// Updated: 7/2/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Flutter imports:
import 'package:flutter/material.dart';

// Package imports:
import 'package:intl/intl.dart';

/// A datatable for displaying logs.
class LogsDataTable extends StatelessWidget {
  final List<Map> logs;
  final TextStyle? columnStyle;
  final TextStyle? fieldStyle;
  final double headingRowHeight;
  final double dataRowMinHeight;
  final double horizontalMargin;
  final double columnSpacing;
  final double dividerThickness;

  LogsDataTable({
    required this.logs,
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
    var defaultColumnStyle = Theme.of(context).textTheme.bodySmall?.copyWith(
          fontWeight: FontWeight.bold,
        );
    return DataTable(
      headingRowHeight: headingRowHeight,
      dataRowMinHeight: dataRowMinHeight,
      horizontalMargin: horizontalMargin,
      columnSpacing: columnSpacing,
      dividerThickness: dividerThickness,
      columns: [
        DataColumn(
            label: Text(
          '',
          style: columnStyle ?? defaultColumnStyle,
        )),
        DataColumn(
            label: Text(
          'Time',
          style: columnStyle ?? defaultColumnStyle,
        )),
        DataColumn(
            label: Text(
          'Edited By',
          style: columnStyle ?? defaultColumnStyle,
        )),
        DataColumn(
            label: Text(
          'Changes',
          style: columnStyle ?? defaultColumnStyle,
        )),
      ],
      rows: logs.map((log) {
        return DataRow(
          cells: [
            DataCell(
              CircleAvatar(
                radius: 25,
                backgroundImage: NetworkImage(log['user_photo_url']),
              ),
            ),
            DataCell(
              Text(
                DateFormat.yMd()
                    .add_jm()
                    .format(DateTime.parse(log['timestamp'])),
                style: fieldStyle ?? defaultFieldStyle,
              ),
            ),
            DataCell(
              Text(
                log['user_name'],
                style: fieldStyle ?? defaultFieldStyle,
              ),
            ),
            DataCell(
              Text(
                log['changes'].toString(),
                style: fieldStyle ?? defaultFieldStyle,
              ),
            ),
          ],
        );
      }).toList(),
    );
  }
}

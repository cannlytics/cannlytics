// Cannlytics Data
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 6/26/2023
// Updated: 6/26/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

import 'package:cannlytics_data/constants/colors.dart';
import 'package:cannlytics_data/constants/design.dart';
import 'package:cannlytics_data/models/lab_result.dart';
import 'package:cannlytics_data/ui/results/results_service.dart';
import 'package:dotted_border/dotted_border.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

// TODO:
// - Finish styling the data table.
// - Ability to add results.
// - Ability to delete results.

/// Analysis results table of compounds.
class AnalysisResultsTable extends ConsumerStatefulWidget {
  final List<Result?>? results;
  final bool isEditing;

  AnalysisResultsTable({this.results, this.isEditing = false});

  @override
  _AnalysisResultsTableState createState() => _AnalysisResultsTableState();
}

/// Analysis results table state.
class _AnalysisResultsTableState extends ConsumerState<AnalysisResultsTable> {
  // State.
  int? sortColumnIndex;
  bool sortAscending = true;

  /// Sort the table.
  void onSort<T>(int columnIndex, bool ascending,
      Comparable<T> Function(Result) getField) {
    setState(() {
      sortColumnIndex = columnIndex;
      sortAscending = ascending;
      widget.results!.sort((a, b) {
        final aValue = getField(a!);
        final bValue = getField(b!);
        return ascending
            ? Comparable.compare(aValue, bValue)
            : Comparable.compare(bValue, aValue);
      });
    });
  }

  @override
  Widget build(BuildContext context) {
    // Theme.
    bool isDark = Theme.of(context).brightness == Brightness.dark;

    // FIXME: Prefer horizontal scrolling.
    // For now, certain fields are hidden on mobile.
    bool isMobile = MediaQuery.of(context).size.width < 600;

    // Table
    var table = DataTable(
      sortColumnIndex: sortColumnIndex,
      sortAscending: sortAscending,
      columnSpacing: isMobile ? 12 : 32,
      horizontalMargin: isMobile ? 2 : 8,
      headingTextStyle: Theme.of(context).textTheme.bodySmall,
      // dividerThickness: 0.1,
      // border: TableBorder(
      //   horizontalInside: BorderSide(
      //     color: Theme.of(context).dividerColor,
      //     width: 1,
      //   ),
      //   verticalInside: BorderSide(
      //     color: Theme.of(context).dividerColor,
      //     width: 1,
      //   ),
      // ),
      columns: <DataColumn>[
        DataColumn(
          label: Text('Analysis'),
          onSort: (columnIndex, ascending) {
            onSort<String>(
                columnIndex, ascending, (result) => result.analysis ?? '');
          },
        ),
        DataColumn(
          label: Text('Name'),
          onSort: (columnIndex, ascending) {
            onSort<String>(
                columnIndex, ascending, (result) => result.name ?? '');
          },
        ),
        DataColumn(
          label: Text('Value'),
          onSort: (columnIndex, ascending) {
            onSort<num>(columnIndex, ascending, (result) => result.value ?? 0);
          },
        ),
        if (!isMobile)
          DataColumn(
            label: Text('Units'),
          ),
        if (!isMobile)
          DataColumn(
            label: Text('Limit'),
          ),
        if (!isMobile)
          DataColumn(
            label: Text('Status'),
          ),
        DataColumn(
          label: Text('Actions'),
        ),
      ],
      rows: widget.results!.map((result) {
        String key = result?.key ?? '';
        return DataRow(
          cells: <DataCell>[
            DataCell(widget.isEditing
                ? _buildEditCell(
                    key,
                    'analysis',
                    result!.analysis ?? '',
                    isDark: isDark,
                  )
                : _buildTextCell(result?.analysis ?? '')),
            DataCell(widget.isEditing
                ? _buildEditCell(
                    key,
                    'name',
                    result?.name ?? '',
                    isDark: isDark,
                  )
                : _buildTextCell(result?.name ?? '')),
            DataCell(widget.isEditing
                ? _buildEditCell(
                    key,
                    'value',
                    result?.value?.toString() ?? '',
                    isNumeric: true,
                    isDark: isDark,
                  )
                : _buildTextCell(result?.value?.toString() ?? '')),
            if (!isMobile)
              DataCell(widget.isEditing
                  ? _buildEditCell(
                      key,
                      'units',
                      result?.units ?? '',
                      isDark: isDark,
                    )
                  : _buildTextCell(result?.units ?? '')),
            if (!isMobile)
              DataCell(widget.isEditing
                  ? _buildEditCell(
                      key,
                      'limit',
                      result?.limit?.toString() ?? '',
                      isNumeric: true,
                      isDark: isDark,
                    )
                  : _buildTextCell(result?.limit?.toString() ?? '')),
            if (!isMobile)
              DataCell(widget.isEditing
                  ? _buildEditCell(
                      key,
                      'status',
                      result?.status ?? '',
                      isDark: isDark,
                    )
                  : _buildTextCell(result?.status ?? '')),
            DataCell(
              widget.isEditing
                  ? IconButton(
                      icon: Icon(Icons.delete),
                      onPressed: () {
                        // FIXME: Delete the result.
                        // ref.read(analysisResults.notifier).remove(result);
                      },
                    )
                  : Container(),
            ),
          ],
        );
      }).toList(),
    );

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      mainAxisAlignment: MainAxisAlignment.start,
      children: [
        // Table.
        Padding(
          padding: EdgeInsets.symmetric(horizontal: 16, vertical: 8),
          child: table,
        ),

        // Add button.
        Padding(
          padding: EdgeInsets.symmetric(horizontal: 16, vertical: 8),
          child: DottedBorder(
            borderType: BorderType.RRect,
            radius: Radius.circular(3),
            padding: EdgeInsets.all(0),
            color: Theme.of(context).colorScheme.secondary,
            dashPattern: [8, 4],
            child: Container(
              width: 200,
              child: OutlinedButton.icon(
                onPressed: () {
                  // FIXME: Add a result.
                  // ref.read(analysisResults.notifier).add(Result());
                },
                icon: Icon(Icons.add),
                label: Text(
                  'Add Result',
                  style: Theme.of(context).textTheme.bodySmall,
                ),
                style: OutlinedButton.styleFrom(
                  side: BorderSide(color: Colors.transparent),
                ),
              ),
            ),
          ),
        ),

        // Bottom gap.
        gapH48,
      ],
    );
  }

  /// Render a text cell.
  Widget _buildTextCell(value) {
    return Text(
      '$value',
      style: Theme.of(context).textTheme.bodySmall,
    );
  }

  /// Render a text field cell.
  Widget _buildEditCell(
    key,
    field,
    value, {
    bool isNumeric = false,
    bool isDark = false,
  }) {
    return TextField(
      controller: TextEditingController()..text = value?.toString() ?? '',
      style: Theme.of(context).textTheme.bodySmall,
      keyboardType: isNumeric ? TextInputType.number : TextInputType.text,
      inputFormatters: isNumeric
          ? <TextInputFormatter>[FilteringTextInputFormatter.digitsOnly]
          : <TextInputFormatter>[],
      decoration: InputDecoration(
        isDense: true,
        contentPadding: EdgeInsets.only(
          top: 12,
          left: 4,
          right: 4,
          bottom: 4,
        ),
        filled: true,
        labelStyle: TextStyle(
          color: Theme.of(context).textTheme.bodyMedium!.color,
          fontSize: 16,
          fontWeight: FontWeight.w500,
        ),
        focusedBorder: OutlineInputBorder(
          borderSide: BorderSide(
            color: isDark ? DarkColors.accentGreen : LightColors.lightGreen,
            width: 2.0,
          ),
        ),
        enabledBorder: OutlineInputBorder(
          borderSide: BorderSide(
            color: Theme.of(context).dividerColor,
            width: 1.0,
          ),
        ),
      ),
      onChanged: (value) {
        var currentResults = ref.read(analysisResults);
        for (var result in currentResults) {
          if (result!['key'] == key) {
            result[field] = value;
          }
        }
        ref.read(analysisResults.notifier).update((state) => currentResults);
      },
    );
  }
}

// Cannlytics Data
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 6/26/2023
// Updated: 6/26/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

import 'package:cannlytics_data/models/lab_result.dart';
import 'package:cannlytics_data/ui/results/results_service.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

// TODO:
// - Style the data table.
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
    var table = DataTable(
      sortColumnIndex: sortColumnIndex,
      sortAscending: sortAscending,
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
        DataColumn(
          label: Text('Units'),
        ),
        DataColumn(
          label: Text('Limit'),
        ),
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
                ? _buildEditCell(key, 'analysis', result!.analysis ?? '')
                : _buildTextCell(result?.analysis ?? '')),
            DataCell(widget.isEditing
                ? _buildEditCell(key, 'name', result?.name ?? '')
                : _buildTextCell(result?.name ?? '')),
            DataCell(widget.isEditing
                ? _buildEditCell(key, 'value', result?.value?.toString() ?? '',
                    numeric: true)
                : _buildTextCell(result?.value?.toString() ?? '')),
            DataCell(widget.isEditing
                ? _buildEditCell(key, 'units', result?.units ?? '')
                : _buildTextCell(result?.units ?? '')),
            DataCell(widget.isEditing
                ? _buildEditCell(key, 'limit', result?.limit?.toString() ?? '',
                    numeric: true)
                : _buildTextCell(result?.limit?.toString() ?? '')),
            DataCell(widget.isEditing
                ? _buildEditCell(key, 'status', result?.status ?? '')
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
      children: [
        table,
        if (widget.isEditing)
          ElevatedButton(
            onPressed: () {
              // FIXME: Add a result.
              // ref.read(analysisResults.notifier).add(Result());
            },
            child: Text('Add Result'),
          ),
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
  Widget _buildEditCell(key, field, value, {bool numeric = false}) {
    return TextField(
      controller: TextEditingController()..text = value?.toString() ?? '',
      keyboardType: numeric ? TextInputType.number : TextInputType.text,
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

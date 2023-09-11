// Cannlytics Data
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 6/26/2023
// Updated: 6/29/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Flutter imports:
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

// Package imports:
import 'package:dotted_border/dotted_border.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

// Project imports:
import 'package:cannlytics_data/common/buttons/primary_button.dart';
import 'package:cannlytics_data/common/buttons/secondary_button.dart';
import 'package:cannlytics_data/common/forms/custom_text_field.dart';
import 'package:cannlytics_data/constants/colors.dart';
import 'package:cannlytics_data/constants/design.dart';
import 'package:cannlytics_data/models/lab_result.dart';
import 'package:cannlytics_data/ui/results/results_service.dart';

// TODO:
// - Finish styling the data table.
// - Ability to add results.

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
  void onSort<T>(
    int columnIndex,
    bool ascending,
    Comparable<T> Function(Result) getField,
  ) {
    ref.read(analysisResults.notifier).sortResults(getField, ascending);
    setState(() {
      sortColumnIndex = columnIndex;
      sortAscending = ascending;
    });
  }

  /// Change an analysis result value.
  void changeValue(key, field, value) {
    var currentResults = ref.read(analysisResults);
    for (var result in currentResults) {
      if (result?.toMap()['key'] == key) {
        var parsedValue = double.tryParse(value);
        result?.toMap()[field] = parsedValue ?? value;
      }
    }
    ref.read(analysisResults.notifier).update(currentResults);
  }

  /// Change a value of a new result.
  void changeNewValue(key, value) {
    var currentAnalysisResult = ref.read(newAnalysisResult);
    var parsedValue = double.tryParse(value);
    currentAnalysisResult[key] = parsedValue ?? value;
    ref
        .read(newAnalysisResult.notifier)
        .update((state) => currentAnalysisResult);
  }

  /// Delete an analysis result.
  /// FIXME: This is removing the last analyte in the list!
  void deleteAnalysisResult(key) {
    var currentResults = ref.read(analysisResults);
    var updatedResults = List<Map>.from(currentResults);
    updatedResults.removeWhere((result) => result['key'] == key);
    List<Result> convertedResults =
        updatedResults.map((item) => Result.fromMap(item)).toList();
    ref.read(analysisResults.notifier).update(convertedResults);
  }

  /// Add an analysis result.
  void addAnalysisResult() {
    showDialog(
      context: context,
      builder: (BuildContext context) {
        return AlertDialog(
          title: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              gapH8,
              Padding(
                padding: EdgeInsets.symmetric(horizontal: 16),
                child: Text('Add a result'),
              ),
              Divider(),
            ],
          ),
          titlePadding: EdgeInsets.all(0),
          contentPadding: EdgeInsets.symmetric(horizontal: 8),
          actionsPadding: EdgeInsets.all(0),
          backgroundColor: Theme.of(context).cardColor,
          surfaceTintColor: Theme.of(context).cardColor,
          content: SingleChildScrollView(
            child: Column(
                mainAxisAlignment: MainAxisAlignment.start,
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Column(
                    mainAxisAlignment: MainAxisAlignment.start,
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      CustomTextField(
                        label: 'Analysis',
                        isNumeric: false,
                        onChanged: (value) => changeNewValue('analysis', value),
                        maxWidth: 200,
                        maxLabelWidth: 90,
                      ),
                      CustomTextField(
                        label: 'Key',
                        isNumeric: false,
                        onChanged: (value) => changeNewValue('key', value),
                        maxWidth: 200,
                        maxLabelWidth: 90,
                      ),
                      CustomTextField(
                        label: 'Name',
                        isNumeric: false,
                        onChanged: (value) => changeNewValue('name', value),
                        maxWidth: 200,
                        maxLabelWidth: 90,
                      ),
                      CustomTextField(
                        label: 'Status',
                        isNumeric: false,
                        onChanged: (value) => changeNewValue('status', value),
                        maxWidth: 200,
                        maxLabelWidth: 90,
                      ),
                      CustomTextField(
                        label: 'Units',
                        isNumeric: false,
                        onChanged: (value) => changeNewValue('units', value),
                        maxWidth: 200,
                        maxLabelWidth: 90,
                      ),
                      CustomTextField(
                        label: 'Value',
                        isNumeric: true,
                        onChanged: (value) => changeNewValue('value', value),
                        maxLabelWidth: 90,
                      ),
                      CustomTextField(
                        label: 'Limit',
                        isNumeric: true,
                        onChanged: (value) => changeNewValue('limit', value),
                        maxLabelWidth: 90,
                      ),
                      CustomTextField(
                        label: 'LOD',
                        isNumeric: true,
                        onChanged: (value) => changeNewValue('lod', value),
                        maxLabelWidth: 90,
                      ),
                      CustomTextField(
                        label: 'LOQ',
                        isNumeric: true,
                        onChanged: (value) => changeNewValue('loq', value),
                        maxLabelWidth: 90,
                      ),
                    ],
                  ),
                ]),
          ),
          actions: [
            Column(
              children: [
                Divider(),
                gapH4,
                Row(
                  mainAxisAlignment: MainAxisAlignment.end,
                  children: [
                    // Cancel button.
                    gapW8,
                    SecondaryButton(
                      text: 'Cancel',
                      onPressed: () {
                        Navigator.of(context).pop();
                      },
                    ),
                    gapW8,

                    // Add result button.
                    PrimaryButton(
                      text: 'Add result',
                      onPressed: () {
                        // Add the result.
                        var currentResults = ref.read(analysisResults);
                        var updatedResults = List<Map>.from(currentResults);
                        updatedResults.add(ref.read(newAnalysisResult));
                        List<Result> convertedResults = updatedResults
                            .map((item) => Result.fromMap(item))
                            .toList();
                        ref
                            .read(analysisResults.notifier)
                            .update(convertedResults);
                        Navigator.of(context).pop();

                        // Reset the update.
                        ref
                            .read(newAnalysisResult.notifier)
                            .update((state) => {});

                        // TODO: Update Firestore if not editing.
                        if (widget.isEditing) {
                          print(
                              'FIXME: it makes sense to update Firestore here');
                        }
                      },
                    ),
                    gapW16,
                  ],
                ),
                gapH8,
              ],
            ),
          ],
        );
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    // Theme.
    bool isDark = Theme.of(context).brightness == Brightness.dark;

    // FIXME: Prefer horizontal scrolling.
    // For now, certain fields are hidden on mobile.
    bool isMobile = MediaQuery.of(context).size.width < 600;

    // Listen to the analysis results.
    var results = ref.watch(analysisResults);

    // Headers.
    var headerStyle = Theme.of(context).textTheme.titleSmall?.copyWith(
          color: Theme.of(context).textTheme.titleLarge?.color,
          fontWeight: FontWeight.w600,
        );
    List<Map> analysisHeaders = [
      {'name': 'Analysis', 'key': 'analysis', 'sort': true},
      {'name': 'Name', 'key': 'name', 'sort': true},
      {'name': 'Value', 'key': 'value', 'sort': true},
      if (!isMobile) {'name': 'Units', 'key': 'units', 'sort': false},
      if (!isMobile) {'name': 'Limit', 'key': 'limit', 'sort': false},
      if (!isMobile) {'name': 'Status', 'key': 'status', 'sort': false},
      {'name': '', 'key': 'empty', 'sort': false},
    ];
    List<DataColumn> columns = <DataColumn>[
      for (Map header in analysisHeaders)
        DataColumn(
          label: Expanded(
            child: Text(
              header['name'],
              style: headerStyle,
            ),
          ),
          onSort: header['sort']
              ? (columnIndex, ascending) {
                  onSort(columnIndex, ascending, (x) {
                    var value = x.toMap()[header['key']];
                    if (value is double) {
                      value = value.toString();
                    }
                    return value ?? '';
                  });
                }
              : null,
        ),
    ];

    // Rows.
    var rows = results.map((result) {
      String key = result?.key ?? '';
      return DataRow(
        cells: <DataCell>[
          DataCell(
            widget.isEditing
                ? _buildEditCell(
                    key,
                    'analysis',
                    result?.analysis ?? '',
                    isDark: isDark,
                  )
                : _buildTextCell(result?.analysis ?? ''),
          ),
          DataCell(
            widget.isEditing
                ? _buildEditCell(
                    key,
                    'name',
                    result?.name ?? '',
                    isDark: isDark,
                  )
                : _buildTextCell(result?.name ?? ''),
          ),
          DataCell(
            widget.isEditing
                ? _buildEditCell(
                    key,
                    'value',
                    result?.value?.toString() ?? '',
                    isNumeric: true,
                    isDark: isDark,
                  )
                : _buildTextCell(result?.value?.toString() ?? ''),
          ),
          if (!isMobile)
            DataCell(
              widget.isEditing
                  ? _buildEditCell(
                      key,
                      'units',
                      result?.units ?? '',
                      isDark: isDark,
                    )
                  : _buildTextCell(result?.units ?? ''),
            ),
          if (!isMobile)
            DataCell(
              widget.isEditing
                  ? _buildEditCell(
                      key,
                      'limit',
                      result?.limit?.toString() ?? '',
                      isNumeric: true,
                      isDark: isDark,
                    )
                  : _buildTextCell(result?.limit?.toString() ?? ''),
            ),
          if (!isMobile)
            DataCell(
              widget.isEditing
                  ? _buildEditCell(
                      key,
                      'status',
                      result?.status ?? '',
                      isDark: isDark,
                    )
                  : _buildTextCell(result?.status ?? ''),
            ),

          // Delete result button.
          DataCell(
            widget.isEditing
                ? IconButton(
                    icon: Icon(Icons.delete),
                    onPressed: () => deleteAnalysisResult(key),
                  )
                : Container(),
          ),
        ],
      );
    }).toList();

    // Table
    var table = DataTable(
      sortColumnIndex: sortColumnIndex,
      sortAscending: sortAscending,
      columnSpacing: isMobile ? 12 : 32,
      horizontalMargin: isMobile ? 2 : 8,
      headingTextStyle: Theme.of(context).textTheme.bodySmall,
      dividerThickness: 0.33,
      border: TableBorder(
        horizontalInside: BorderSide(
          width: 1,
          color: Theme.of(context).dividerColor,
          style: BorderStyle.solid,
        ),
        verticalInside: BorderSide.none,
        right: BorderSide.none,
        left: BorderSide.none,
        bottom: BorderSide.none,
      ),
      columns: columns,
      rows: rows,
    );

    // Render the table.
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      mainAxisAlignment: MainAxisAlignment.start,
      children: [
        // Table.
        Padding(
          padding: EdgeInsets.symmetric(horizontal: 16, vertical: 8),
          child: SelectionArea(child: table),
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
                onPressed: addAnalysisResult,
                icon: Icon(Icons.add),
                label: Text(
                  'Add a result',
                  style: Theme.of(context).textTheme.bodySmall,
                ),
                style: OutlinedButton.styleFrom(
                  side: BorderSide(color: Colors.transparent),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(3),
                  ),
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
    bool isNew = false,
  }) {
    return TextFormField(
      // FIXME: Controller.
      // controller: TextEditingController()..text = value?.toString() ?? '',
      initialValue: value?.toString() ?? '',

      // Validation.
      keyboardType: isNumeric ? TextInputType.number : TextInputType.text,
      inputFormatters: isNumeric
          ? <TextInputFormatter>[
              FilteringTextInputFormatter.allow(RegExp(r'^\d*\.?\d*'))
            ]
          : <TextInputFormatter>[],

      // Change an analysis result value.
      onChanged: (value) =>
          isNew ? changeNewValue(key, value) : changeValue(key, field, value),

      // Style.
      style: Theme.of(context).textTheme.bodySmall,
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
    );
  }
}

// Cannlytics Data
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 5/7/2023
// Updated: 5/8/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Flutter imports:
import 'package:cannlytics_data/common/inputs/string_controller.dart';
import 'package:cannlytics_data/models/licensee.dart';
import 'package:cannlytics_data/services/firestore_service.dart';
import 'package:flutter/material.dart';

// Package imports:
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:excel/excel.dart';

/* Data */

// Licenses state.
final activeStateProvider = StateProvider<String?>((ref) => null);

/// Stream state licenses.
final stateLicensesProvider =
    StreamProvider.family<List<Map<String, dynamic>>, String>(
        (ref, stateId) async* {
  final FirestoreService _dataSource = ref.watch(firestoreProvider);
  yield* _dataSource.watchCollection(
    path: 'public/data/licenses',
    builder: (data, documentId) => data!,
    queryBuilder: (query) => query
        .where('premise_state', isEqualTo: stateId.toUpperCase())
        .limit(10),
  );
});

/* Table */

// Rows per page.
final licenseesRowsPerPageProvider = StateProvider<int>((ref) => 10);

// Sorting.
final licenseesSortColumnIndex = StateProvider<int>((ref) => 0);
final licenseesSortAscending = StateProvider<bool>((ref) => true);

/* Search */

// Search term.
final searchTermProvider = StateProvider<String>((ref) => '');

/// Filtered licensees provider.
final filteredLicenseesProvider =
    StreamProvider.family<List<Map<String, dynamic>>, String>(
        (ref, stateId) async* {
  final searchTerm = ref.watch(searchTermProvider);
  final data = ref.watch(stateLicensesProvider(stateId)).value ?? [];
  if (searchTerm.isEmpty) {
    yield data;
  }
  String keyword = searchTerm.toLowerCase();
  List<Map<String, dynamic>> matched = [];
  data.forEach((x) {
    // Matching logic.
    if (x['business_legal_name'].toLowerCase().contains(keyword) ||
        x['license_number'].toLowerCase().contains(keyword)) {
      matched.add(x);
    }
  });
  yield matched;
});

// Search input.
final licenseesSearchController =
    StateNotifierProvider<StringController, TextEditingController>(
        (ref) => StringController());

/* Licensee Details */

// Licensee ID.
final licenseeId = StateProvider<String?>((ref) => 'new');

// Licensee provider.
final licenseeProvider =
    StreamProvider.family<List<Map<String, dynamic>>, String>((ref, id) async* {
  final FirestoreService _dataSource = ref.watch(firestoreProvider);
  yield* await _dataSource.watchCollection(
    path: 'public/data/licenses',
    builder: (data, documentId) => data!,
    queryBuilder: (query) => query.where('id', isEqualTo: id).limit(1),
  );
});

/* Service */

/// Licensees service.
class LicenseesService {
  const LicenseesService._();

  // Download licensees data.
  static Future<void> downloadLicensees(List<Map> data) async {
    print('Download licensees....');
    // Create a workbook.
    var excel = Excel.createExcel();
    excel.rename('Sheet1', 'Data');
    // CellStyle cellStyle = CellStyle(
    //   leftBorder: Border(borderStyle: BorderStyle.Thin),
    //   rightBorder: Border(borderStyle: BorderStyle.Thin),
    //   topBorder: Border(borderStyle: BorderStyle.Thin, borderColorHex: 'FFFF0000'),
    //   bottomBorder: Border(borderStyle: BorderStyle.Medium, borderColorHex: 'FF0000FF'),
    // );
    var rows = [
      ['business_legal_name', 'license_number', 'premise_state'],
      ...data.map((x) => [
            x['business_legal_name'],
            x['license_number'],
            x['premise_state'],
          ])
    ];
    Sheet sheetObject = excel['Data'];
    rows.forEach((row) => sheetObject.appendRow(row));

    // TODO: Add Copyright / License / Sources sheets.

    // TODO: Create filename.

    // Download the workbook.
    var fileBytes = excel.save(fileName: 'data.xlsx');

    // FIXME: Handle downloading on mobile.
    // try {
    //   // Download mobile.
    //   var fileBytes = excel.save();
    //   var directory = await getApplicationDocumentsDirectory();
    //   File(join('$directory/output_file_name.xlsx'))
    //     ..createSync(recursive: true)
    //     ..writeAsBytesSync(fileBytes);
    // } catch(error) {
    //   // Download on the web.
    //   var fileBytes = excel.save(fileName: 'My_Excel_File_Name.xlsx');
    // }
  }
}

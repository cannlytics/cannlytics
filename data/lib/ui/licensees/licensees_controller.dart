// Cannlytics Data
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 5/7/2023
// Updated: 5/9/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Flutter imports:
// import 'dart:io';
// import 'package:path/path.dart';

import 'package:cannlytics_data/common/inputs/string_controller.dart';
import 'package:cannlytics_data/models/licensee.dart';
import 'package:cannlytics_data/services/data_service.dart';
import 'package:cannlytics_data/services/firestore_service.dart';
import 'package:flutter/material.dart';

// Package imports:
import 'package:flutter_riverpod/flutter_riverpod.dart';
// import 'package:excel/excel.dart';
// import 'package:intl/intl.dart';

/* Data */

// Licenses state.
final activeStateProvider = StateProvider<String?>((ref) => null);

// Licensees provider.
final licenseesProvider =
    AsyncNotifierProvider<LicenseesController, List<Map<String, dynamic>>>(
        () => LicenseesController());

/// Licensees controller.
class LicenseesController extends AsyncNotifier<List<Map<String, dynamic>>> {
  // Load initial licensees list from Metrc.
  @override
  Future<List<Map<String, dynamic>>> build() async => _getLicensees();

  /// Get licensees.
  Future<List<Map<String, dynamic>>> _getLicensees() async {
    // FIXME: Get the correct datafile for the state.
    final stateId = ref.read(activeStateProvider) ?? 'all';
    print('STATE WHEN GETTING LICENSEES: $stateId');
    var url =
        'https://firebasestorage.googleapis.com/v0/b/cannlytics.appspot.com/o/public%2Fdata%2Flicenses%2Fwa%2Flicenses-wa-2023-04-24T21-21-31.csv?alt=media&token=33ab0328-9fa5-4658-b927-5511268fef1a';
    return await DataService.fetchCSVFromURL(url);
  }

  /// Set the licensees.
  Future<void> setLicensees(List<Map<String, dynamic>> items) async {
    state = const AsyncValue.loading();
    state = await AsyncValue.guard(() async => items);
  }
}

/// Get state licenses.
// final stateLicensesProvider = FutureProvider.autoDispose
//     .family<List<Map<String, dynamic>>, String>((ref, stateId) async {
//   // FIXME: Get the correct datafile..
//   var url =
//       'https://firebasestorage.googleapis.com/v0/b/cannlytics.appspot.com/o/public%2Fdata%2Flicenses%2Fwa%2Flicenses-wa-2023-04-24T21-21-31.csv?alt=media&token=33ab0328-9fa5-4658-b927-5511268fef1a';
//   var data = await DataService.fetchCSVFromURL(url);
//   return data;
// });

// Example Stream:
// final stateLicensesProvider =
//     StreamProvider.family<List<Map<String, dynamic>>, String>(
//         (ref, stateId) async* {
//   final FirestoreService _dataSource = ref.watch(firestoreProvider);
//   yield* _dataSource.watchCollection(
//     path: 'public/data/licenses',
//     builder: (data, documentId) => data!,
//     queryBuilder: (query) => query
//         .where('premise_state', isEqualTo: stateId.toUpperCase())
//         .limit(10),
//   );
// });

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
// final filteredLicenseesProvider =
//     StreamProvider.family<List<Map<String, dynamic>>, String>(
//         (ref, stateId) async* {
//   final searchTerm = ref.watch(searchTermProvider);
//   final data = ref.watch(stateLicensesProvider(stateId)).value ?? [];
//   if (searchTerm.isEmpty) {
//     yield data;
//   }
//   String keyword = searchTerm.toLowerCase();
//   List<Map<String, dynamic>> matched = [];
//   data.forEach((x) {
//     // Matching logic.
//     if (x['business_legal_name'].toLowerCase().contains(keyword) ||
//         x['license_number'].toLowerCase().contains(keyword)) {
//       matched.add(x);
//     }
//   });
//   yield matched;
// });

/// Filtered licensees provider.
final filteredLicenseesProvider = StateNotifierProvider<
    FilteredLicenseesNotifier, List<Map<String, dynamic>>>(
  (ref) {
    // Listen to search term and read the data.
    final stateId = ref.read(activeStateProvider) ?? 'all';
    print('STATE WHEN FILTERED: $stateId');
    final searchTerm = ref.watch(searchTermProvider);
    final data = ref.read(licenseesProvider).value;
    return FilteredLicenseesNotifier(ref, data ?? [], searchTerm);
  },
);

/// Filtered licensees.
class FilteredLicenseesNotifier
    extends StateNotifier<List<Map<String, dynamic>>> {
  // Properties.
  final StateNotifierProviderRef<dynamic, dynamic> ref;
  final List<Map<String, dynamic>> items;
  final String searchTerm;

  // Initialization.
  FilteredLicenseesNotifier(
    this.ref,
    this.items,
    this.searchTerm,
  ) : super([]) {
    // Search function.
    if (searchTerm.isEmpty) {
      state = items;
      return;
    }
    String keyword = searchTerm.toLowerCase();
    List<Map<String, dynamic>> matched = [];
    items.forEach((x) {
      // Matching logic.
      if (x['business_legal_name'].toLowerCase().contains(keyword) ||
          x['license_number'].toLowerCase().contains(keyword)) {
        matched.add(x);
      }
    });
    state = matched;
  }
}

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
// class LicenseesService {
//   const LicenseesService._();

//   // /// Create a data download filename.
//   // static String createFileName() {
//   //   DateTime now = DateTime.now();
//   //   String formattedDateTime = DateFormat('yyyy-MM-dd-HH-mm-ss').format(now);
//   //   String fileName = 'cannlytics-data-$formattedDateTime.xlsx';
//   //   return fileName;
//   // }

//   // Download licensees data.
//   static Future<void> downloadLicensees(List<Map> data) async {
//     print('Download licensees....');
//     // Create a workbook.
//     var excel = Excel.createExcel();
//     var rows = [
//       ['business_legal_name', 'license_number', 'premise_state'],
//       ...data.map((x) => [
//             x['business_legal_name'],
//             x['license_number'],
//             x['premise_state'],
//           ])
//     ];
//     excel.rename('Sheet1', 'Data');
//     Sheet sheetObject = excel['Data'];
//     rows.forEach((row) => sheetObject.appendRow(row));

//     // TODO: Add Copyright / License / Sources sheets.

//     // TODO: Create filename.
//     String fileName = DataService.createDataFileName();

//     // Download the workbook.
//     var fileBytes = excel.save(fileName: 'data.xlsx');

//     // FIXME: Handle downloading on mobile.
//     // try {
//     //   // Download mobile.
//     //   var fileBytes = excel.save();
//     //   var directory = await getApplicationDocumentsDirectory();
//     //   File(join('$directory/output_file_name.xlsx'))
//     //     ..createSync(recursive: true)
//     //     ..writeAsBytesSync(fileBytes);
//     // } catch(error) {
//     //   // Download on the web.
//     //   var fileBytes = excel.save(fileName: 'My_Excel_File_Name.xlsx');
//     // }
//   }
// }

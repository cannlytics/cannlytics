// Cannlytics Data
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 5/7/2023
// Updated: 8/6/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Package imports:
import 'package:csv/csv.dart';
import 'package:http/http.dart' as http;
import 'package:intl/intl.dart';
import 'package:url_launcher/url_launcher.dart';

/// Data service.
class DataService {
  const DataService._();

  /// Create a data download filename.
  static String createDataFileName() {
    DateTime now = DateTime.now();
    String formattedDateTime = DateFormat('yyyy-MM-dd-HH-mm-ss').format(now);
    String fileName = 'cannlytics-data-$formattedDateTime.xlsx';
    return fileName;
  }

  /// Open a datafile in a new tab.
  static openInANewTab(url) {
    // DateTime now = DateTime.now();
    // String formattedDateTime = DateFormat('yyyy-MM-dd-HH-mm-ss').format(now);
    // String fileName = 'cannlytics-data-$formattedDateTime';
    // html.window.open(url, fileName);
    launchUrl(Uri.parse(url));
  }

  /// Load data from a CSV file.
  static Future<List<Map<String, String>>> fetchCSVFromURL(String url) async {
    // Fetch CSV data from the URL.
    final response = await http.get(Uri.parse(url));
    if (response.statusCode == 200) {
      // Parse the CSV data.
      List<List<dynamic>> rowsAsListOfValues =
          const CsvToListConverter().convert(response.body);

      // Extract the header row.
      List<String> headerRow = rowsAsListOfValues[0].cast<String>();

      // Convert the CSV data to a List of Maps, excluding the header row.
      List<Map<String, String>> csvDataAsListOfMaps = rowsAsListOfValues
          .sublist(1)
          .map((row) =>
              Map.fromIterables(headerRow, row.map((e) => e.toString())))
          .toList();

      // Return the CSV data.
      return csvDataAsListOfMaps;
    } else {
      throw Exception('Failed to load CSV data');
    }
  }
}

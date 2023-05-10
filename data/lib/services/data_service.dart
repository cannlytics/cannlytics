// Cannlytics Data
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 5/7/2023
// Updated: 5/9/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// import 'dart:io';
import 'dart:convert';
import 'dart:html' as html;
import 'package:http/http.dart' as http;
import 'package:csv/csv.dart';
// import 'dart:io';
// import 'package:flutter/material.dart';
// import 'package:http/http.dart' as http;
// import 'package:path_provider/path_provider.dart';
// import 'package:path/path.dart';

// import 'package:flutter_downloader/flutter_downloader.dart';
import 'package:intl/intl.dart';
// import 'package:excel/excel.dart';

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
    DateTime now = DateTime.now();
    String formattedDateTime = DateFormat('yyyy-MM-dd-HH-mm-ss').format(now);
    String fileName = 'cannlytics-data-$formattedDateTime';
    html.window.open(url, fileName);
  }

  /// Load data from a CSV file.
  static Future<List<Map<String, String>>> fetchCSVFromURL(String url) async {
    // Fetch CSV data from the URL.
    final response = await http.get(Uri.parse(url));
    if (response.statusCode == 200) {
      // Parse the CSV data.
      List<List<dynamic>> rowsAsListOfValues =
          const CsvToListConverter().convert(response.body);
      print('PARSED CSV');

      // Extract the header row.
      List<String> headerRow = rowsAsListOfValues[0].cast<String>();
      print('HEADERS: $headerRow');

      // Convert the CSV data to a List of Maps, excluding the header row.
      List<Map<String, String>> csvDataAsListOfMaps = rowsAsListOfValues
          .sublist(1)
          .map((row) =>
              Map.fromIterables(headerRow, row.map((e) => e.toString())))
          .toList();
      print('CONVERTED TO CSV');

      return csvDataAsListOfMaps;
    } else {
      throw Exception('Failed to load CSV data');
    }
  }

  /* DEV */

  /// Download file from URL.
  /// Example: downloadFile('https://example.com/path/to/file.txt', 'file.txt');
  // static Future<void> downloadFile(String url, String fileName) async {
  //   // Make the network request
  //   final response = await http.get(Uri.parse(url));

  //   // Get the application documents directory
  //   final directory = await getApplicationDocumentsDirectory();

  //   // Create the file and write the bytes
  //   final file = File(join(directory.path, fileName));
  //   await file.writeAsBytes(response.bodyBytes);

  //   print('File downloaded to: ${file.path}');
  // }

  /// Download data to Excel.
  // Future work: Add Copyright / License / Sources sheets.
  // WARNING: May not be able to handle files > 8 MB.
  // static Future<void> downloadDataToExcel(List<List> rows) async {
  //   var excel = Excel.createExcel();
  //   excel.rename('Sheet1', 'Data');
  //   Sheet sheetObject = excel['Data'];
  //   rows.forEach((row) => sheetObject.appendRow(row));
  //   String fileName = DataService.createDataFileName();
  //   try {
  //     // Download on mobile.
  //     var fileBytes = excel.save();
  //     var directory = await getApplicationDocumentsDirectory();
  //     File(join('$directory/$fileName'))
  //       ..createSync(recursive: true)
  //       ..writeAsBytesSync(fileBytes!);
  //   } catch(error) {
  //     // Download on the web.
  //     excel.save(fileName: fileName);
  //   }
  // }

  // static Future<void> downloadFileFromUrl(String url, String fileName) async {
  //   final taskId = await FlutterDownloader.enqueue(
  //     url: 'your download link',
  //     headers: {},
  //     savedDir: 'the path of directory where you want to save downloaded files',
  //     showNotification: true,
  //     openFileFromNotification: true,
  //   );
  //   final tasks = await FlutterDownloader.loadTasks();
  // }

  /// Save a file to the device.
  /// Credit: Kalyan Chandra <https://stackoverflow.com/a/76109537/5021266>
  /// License: CC BY-SA 4.0 <https://creativecommons.org/licenses/by-sa/4.0/>
  // Future<String?> saveFileToDevice(String filename, List<int> data) async {
  //   // // Get the path to the app's documents directory
  //   // var status = await Permission.storage.status;
  //   // if (!status.isGranted) {
  //   //   await Permission.storage.request();
  //   // }
  //   // var dir = Platform.isAndroid
  //   //     ? '/storage/emulated/0/Download'
  //   //     : (await getApplicationDocumentsDirectory()).path;

  //   // Create the file and write the data to it
  //   var file = File('$dir/$filename');

  //   // bool alreadyDownloaded = await file.exists();

  //   // String incrementCount(String fileName) {
  //   //   int dotIndex = fileName.lastIndexOf('.');
  //   //   String newFileName = fileName.substring(0, dotIndex) +
  //   //       "(${count += 1})" +
  //   //       fileName.substring(dotIndex);

  //   //   return newFileName;
  //   // }

  //   // if (alreadyDownloaded) {
  //   //   String newFileName = incrementCount(file.path);

  //   //   var newFile = File('$newFileName');
  //   //   await newFile.writeAsBytes(data, flush: true);

  //   //   String subStringFileName = newFileName.substring(29);
  //   //   CommonWidgets.makeToast(
  //   //       fontSize: 14,
  //   //       toastMsg: '${subStringFileName} saved to Downloads Folder');

  //   //   file = newFile;
  //   //   print('modified updating ....--> $file');
  //   // } else {
  //   await file.writeAsBytes(data, flush: true);
  //   return 'file://${file.path}';
  //   }

  // static getApplicationDocumentsDirectory() {}
}

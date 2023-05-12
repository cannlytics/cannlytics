// Cannlytics Data
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 5/11/2023
// Updated: 5/11/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

import 'dart:async';
import 'dart:io';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:http/http.dart';
import 'package:http_parser/http_parser.dart';

/// Certificate of Analysis (COA) model.
class CoAResult {
  final String sampleId;
  final String productName;
  final String productType;
  final String producer;
  final String dateTested;

  CoAResult({
    required this.sampleId,
    required this.productName,
    required this.productType,
    required this.producer,
    required this.dateTested,
  });
}

/// Data service.
class CoADocService {
  const CoADocService._();

  final defaultImage =
      'https://firebasestorage.googleapis.com/v0/b/cannlytics.appspot.com/o/public%2Fimages%2Fbackgrounds%2Fmisc%2Fsample-placeholder.png?alt=media&token=e8b96368-5d80-49ec-bbd0-3d21654b677f';

  Future<void> uploadCoAFile(File file) async {
    // FIXME:
    // var request = MultipartRequest();

    // // Set your API endpoint
    // request.setUrl('https://cannlytics/api/data/coas');

    // // Add headers
    // request.addHeader('X-CSRFToken', 'your-csrf-token');

    // // Add file
    // request.addFile('file_field_name', file.path,
    //     filename: file.path.split('/').last,
    //     contentType: MediaType('image', 'jpeg'));

    // // Send the request
    // Response response = await request.send();

    // if (response.statusCode == 200) {
    //   // If the server returns a 200 OK response, parse the JSON.
    //   Map<String, dynamic> responseData = response.asJson();

    //   if (responseData['success']) {
    //     print('SUCCESS');
    //   } else {
    //     print('ERROR!');
    //     // ScaffoldMessenger.of(context).showSnackBar(
    //     //   SnackBar(
    //     //     content: const Text(
    //     //       'An error occurred when uploading your CoA for parsing. Please try again later or email support.',
    //     //     ),
    //     //     backgroundColor: Colors.red,
    //     //   ),
    //     // );
    //   }
    // } else {
    //   // If the server returns a response with a status code other than 200,
    //   // throw an exception.
    //   throw Exception('Failed to load API data');
    // }
  }

  Future<void> downloadCoAData(List<Map<String, dynamic>> data) async {
    final postData = {'data': data};
    final timestamp = DateTime.now()
        .toIso8601String()
        .substring(0, 19)
        .replaceAll(RegExp(r'[T:]'), '-');

    final response = await http.post(
      Uri.parse('https://cannlytics/api/data/coas/download'),
      body: postData,
    );

    if (response.statusCode == 200) {
      final blob = response.bodyBytes;
      final filename = 'coa-data-$timestamp.xlsx';

      // FIXME: Request storage permissions
      // if (await Permission.storage.request().isGranted) {
      //   // Get the correct directory
      //   final directory = await getApplicationDocumentsDirectory();
      //   final file = File('${directory.path}/$filename');

      //   // Write the file
      //   await file.writeAsBytes(blob);

      //   ScaffoldMessenger.of(context).showSnackBar(
      //     SnackBar(
      //       content: Text('Downloaded CoA data to $filename'),
      //     ),
      //   );
      // } else {
      //   ScaffoldMessenger.of(context).showSnackBar(
      //     SnackBar(
      //       content: Text('Storage permission is not granted'),
      //       backgroundColor: Colors.red,
      //     ),
      //   );
      // }
    } else {
      print('ERROR!');
      // ScaffoldMessenger.of(context).showSnackBar(
      //   SnackBar(
      //     content: Text(
      //         'Error downloading CoA data. Please try again later and/or contact support.'),
      //     backgroundColor: Colors.red,
      //   ),
      // );
    }
  }
}

// Define a ChangeNotifier Provider for managing CoA results.
class CoAResultsProvider with ChangeNotifier {
  List<CoAResult> _results = [];

  List<CoAResult> get results => _results;

  void addResult(CoAResult result) {
    _results.add(result);
    notifyListeners();
  }

  void removeResult(String sampleId) {
    _results.removeWhere((result) => result.sampleId == sampleId);
    notifyListeners();
  }
}

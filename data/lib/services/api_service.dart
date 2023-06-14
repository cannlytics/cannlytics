// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 2/20/2023
// Updated: 6/14/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Dart imports:
import 'dart:convert';

// Package imports:
import 'package:firebase_auth/firebase_auth.dart';
import 'package:http/http.dart' as http;
import 'package:path/path.dart';

/// Service to interface with the Cannlytics API.
class APIService {
  const APIService._();

  // Define the base URL.
  // FIXME: Smoothly switch between dev and production.
  // static String _baseUrl = 'http://127.0.0.1:8000/api';
  static String _baseUrl = 'https://cannlytics.com/api';

  /// Initialize the API service.
  static void initialize() {
    bool isProduction = bool.fromEnvironment('dart.vm.product');
    if (isProduction) _baseUrl = 'https://cannlytics.com/api';
  }

  /// API base URL.
  static String get baseUrl => _baseUrl;

  /// Get a user's token. Set [refresh] to renew credentials.
  static Future<String> getUserToken({bool refresh = false}) async {
    final tokenResult = FirebaseAuth.instance.currentUser;
    if (tokenResult == null) {
      return '';
    } else {
      return await tokenResult.getIdToken(refresh);
    }
  }

  /// Make an authenticated HTTP request to the Cannlytics API.
  static Future<dynamic> apiRequest(
    String endpoint, {
    dynamic data,
    dynamic files,
    Map? options,
  }) async {
    // Create default body, method, and headers.
    var body;
    var method = 'GET';
    final idToken = await getUserToken();
    final headers = {
      'Content-Type': 'application/json',
      'Authorization': 'Bearer $idToken',
    };

    // Handle post.
    if (data != null) {
      method = 'POST';
      body = jsonEncode(data);
    }

    // Handle options.
    if (options != null) {
      // Handle delete.
      if (options['delete'] == true) {
        method = 'DELETE';
      }

      // Handle query parameters.
      if (options['params'] != null) {
        final url = Uri.parse(endpoint);
        final newUrl = url.replace(queryParameters: options['params']);
        endpoint = newUrl.toString();
      }
    }

    // Format the URL
    final url = endpoint.startsWith(baseUrl)
        ? endpoint
        : '$baseUrl${endpoint.replaceFirst('/api', '')}';

    print('URL: $url');

    // Make the request.
    final client = http.Client();
    final request;
    if (files != null) {
      headers['Content-Type'] = 'application/octet-stream';
      headers['Accept'] = 'application/octet-stream';
      request = http.MultipartRequest('POST', Uri.parse(url))
        ..headers.addAll(headers);
      for (var file in files) {
        request.files.add(await http.MultipartFile.fromPath(
          'file',
          file.path,
          filename: basename(file.path),
        ));
      }
    } else if (body == null) {
      request = http.Request(method, Uri.parse(url))..headers.addAll(headers);
    } else {
      request = http.Request(method, Uri.parse(url))
        ..headers.addAll(headers)
        ..body = body;
    }

    // Get the response.
    final response = await client.send(request).then(http.Response.fromStream);

    // Return the data.
    try {
      var responseData = jsonDecode(response.body);
      return responseData.containsKey('data')
          ? responseData['data']
          : responseData;
    } catch (error) {
      print("Request error: [error=${error.toString()}]");
      return response;
      // try {
      //   final blob = html.Blob([response.bodyBytes]);
      //   final url = html.Url.createObjectUrlFromBlob(blob);
      //   final anchor = html.document.createElement('a') as html.AnchorElement
      //     ..href = url
      //     ..style.display = 'none'
      //     ..download = filename;
      //   html.document.body?.children.add(anchor);
      //   anchor.click();
      //   html.document.body?.children.remove(anchor);
      //   html.Url.revokeObjectUrl(url);
      // } catch (error) {
      //   print("Request error: [error=${error.toString()}]");
      //   return response;
      // }
    }
  }
}

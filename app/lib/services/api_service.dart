// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 2/20/2023
// Updated: 8/24/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Dart imports:
import 'dart:async';
import 'dart:convert';

// Package imports:
import 'package:firebase_auth/firebase_auth.dart';
import 'package:http/http.dart' as http;

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
    if (isProduction) {
      _baseUrl = 'https://cannlytics.com/api';
    }
  }

  /// API base URL.
  static String get baseUrl => _baseUrl;

  /// Get a user's token. Set [refresh] to renew credentials.
  static Future<String> getUserToken({bool refresh = false}) async {
    final tokenResult = FirebaseAuth.instance.currentUser;
    if (tokenResult == null) {
      return '';
    } else {
      return await tokenResult.getIdToken(refresh) ?? '';
    }
  }

  /// Make an authenticated HTTP request to the Cannlytics API.
  static Future<dynamic> apiRequest(
    String endpoint, {
    dynamic data,
    dynamic files,
    dynamic fileNames,
    Map? options,
  }) async {
    // Create default body, method, and headers.
    var body;
    String method = 'GET';
    String idToken = await getUserToken();
    final headers = {
      'Content-Type': 'application/json;charset=UTF-8',
      'Accept': 'application/json',
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
    String url = endpoint.startsWith(baseUrl)
        ? endpoint
        : '$baseUrl${endpoint.replaceFirst('/api', '')}';

    // Make the request.
    final client = http.Client();
    final request;
    if (files != null) {
      // Create a multipart request.
      request = http.MultipartRequest(
        'POST',
        Uri.parse(url),
      )..headers.addAll(headers);

      // Add the files to the request.
      for (var i = 0; i < files.length; i++) {
        var file = files[i];
        var bytes;
        var filename;
        try {
          // PlatformFile to bytes.
          bytes = await file.bytes;
          filename = file.name;
        } catch (error) {
          try {
            // File to bytes.
            bytes = await file.readAsBytes();
            filename = file.name;
          } catch (error) {
            // File already in bytes.
            bytes = file;
            filename = fileNames[i];
          }
        }
        try {
          // Add file from bytes.
          request.files.add(http.MultipartFile.fromBytes(
            'file',
            bytes,
            filename: filename,
          ));
        } catch (error) {
          // Add file from a string.
          request.files.add(http.MultipartFile.fromString(
            'file',
            bytes,
            filename: filename,
          ));
        }
      }
    } else if (body == null) {
      // Create a GET request.
      request = http.Request(method, Uri.parse(url))..headers.addAll(headers);
    } else {
      // Create a POST request.
      request = http.Request(method, Uri.parse(url))
        ..headers.addAll(headers)
        ..body = body;
    }

    // Get the response.
    final response = await client.send(request).then(http.Response.fromStream);

    // Return the data.
    try {
      var responseData = jsonDecode(response.body) as Map<String, dynamic>;
      return responseData.containsKey('data')
          ? responseData['data']
          : responseData;
    } catch (error) {
      return response;
    }
  }
}

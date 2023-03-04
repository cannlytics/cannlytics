// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 2/20/2023
// Updated: 3/3/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Dart imports:
import 'dart:convert';

// Package imports:
import 'package:firebase_auth/firebase_auth.dart';
import 'package:http/http.dart' as http;

class APIService {
  static final String baseUrl = 'https://cannlytics.com/api';

  /// Get a user's token.
  /// Set [refresh] if the credentials should be refreshed.
  static Future<String> getUserToken({bool refresh = false}) async {
    final tokenResult = FirebaseAuth.instance.currentUser!;
    return await tokenResult.getIdToken(refresh);
  }

  /// Make an authenticated HTTP request to the Cannlytics API.
  static Future<dynamic> authRequest(
    String endpoint, {
    dynamic data,
    Map<String, dynamic>? options,
  }) async {
    try {
      // Get the user's session token.
      final idToken = await getUserToken();

      // Make an API request with the token.
      return await apiRequest(
        endpoint,
        data: data,
        options: options,
        idToken: idToken,
      );
    } catch (error) {
      return error;
    }
  }

  /// Make a HTTP request to the Cannlytics API.
  static Future<dynamic> apiRequest(
    String endpoint, {
    dynamic data,
    Map<String, dynamic>? options,
    String? idToken,
  }) async {
    // Format headers.
    final headerAuth = {
      'Content-Type': 'application/json',
      'Authorization': 'Bearer ${idToken ?? ''}',
    };

    // Set defaults.
    var body;
    var method = 'GET';

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
    final url = endpoint.startsWith(baseUrl) ? endpoint : '$baseUrl$endpoint';

    // Make the request.
    final client = http.Client();
    final request = http.Request(method, Uri.parse(url))
      ..headers.addAll(headerAuth)
      ..body = body;
    // final response = await client.send(request).then(http.Response.fromStream);
    final response = await http.Response.fromStream(await client.send(request));

    // Return the data.
    try {
      var responseData = jsonDecode(response.body);
      return responseData.containsKey('data')
          ? responseData['data']
          : responseData;
    } catch (error) {
      return response;
    }
  }
}

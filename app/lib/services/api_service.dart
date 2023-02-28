// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 2/20/2023
// Updated: 2/20/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Dart imports:
import 'dart:convert';

// Package imports:
import 'package:firebase_auth/firebase_auth.dart';
import 'package:http/http.dart' as http;

class APIService {
  final String _baseUrl = 'https://cannlytics.com/api';
  final String _testUrl = '/api';

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
    /**
   * Make an authorized GET or POST request by
   * getting the user's ID token and exchanging it for a session cookie.
   * @param {String} endpoint The API endpoint to which to make an authenticated request.
   * @param {Object} data Any data posted to the API.
   * @param {Object} options Any request options: `delete` (bool) or `params` (Object).
   */
    try {
      final idToken = await getUserToken();
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
    /**
   * Make a request to the Cannlytics API, with an ID token for authentication
   * or without ID token when the user already has an authenticated session.
   * @param {String} endpoint The API endpoint to which to make an authenticated request.
   * @param {Object} data Any data posted to the API.
   * @param {Object} options Any request options: `delete` (bool) or `params` (Object).
   * @param {String} idToken = null
   */
    final headerAuth = {
      'Content-Type': 'application/json',
      'Authorization': 'Bearer ${idToken ?? ''}',
    };
    var method = 'GET';
    var body;
    if (data != null) {
      method = 'POST';
      body = jsonEncode(data);
    }
    if (options != null) {
      if (options['delete'] != null) {
        method = 'DELETE';
      }
      if (options['params'] != null) {
        final url = Uri.parse(endpoint);
        final newUrl = url.replace(queryParameters: options['params']);
        endpoint = newUrl.toString();
      }
    }
    final url =
        endpoint.startsWith('https') ? endpoint : '${Uri.base}$endpoint';
    final response = await http.Response.fromStream(
        await http.Client().send(http.Request(method, Uri.parse(url))
          ..headers.addAll(headerAuth)
          ..body = body));
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

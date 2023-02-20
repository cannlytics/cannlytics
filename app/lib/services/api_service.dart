// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 2/20/2023
// Updated: 2/20/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>
import 'dart:convert';
import 'package:firebase_auth/firebase_auth.dart';
import 'package:http/http.dart' as http;

class APIService {
  final String _baseUrl = 'https://cannlytics.com/api';

  Future<String> getUserToken({bool refresh = false}) async {
    /**
  * Get an auth token for a given user.
  * @param {bool} refresh Whether or not the credentials of the ID token should be refreshed.
  */
    // if (auth.currentUser == null) {
    //   final user = await FirebaseAuth.instance.authStateChanges().listen((firebaseUser) async {
    //     if (user != null) return await user.getIdToken(refresh);
    //   });
    //   return user;
    // } else {
    //   return await auth.currentUser.getIdToken(refresh);
    // }
    final tokenResult = FirebaseAuth.instance.currentUser!;
    return await tokenResult.getIdToken(refresh);
  }

  Future<dynamic> authRequest(
    String endpoint,
    dynamic data, {
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
      return await apiRequest(endpoint, data, options, idToken: idToken);
    } catch (error) {
      return error;
    }
  }

  Future<dynamic> apiRequest(
    String endpoint,
    dynamic data,
    Map<String, dynamic>? options, {
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
      return jsonDecode(response.body);
    } catch (error) {
      return response;
    }
  }
}

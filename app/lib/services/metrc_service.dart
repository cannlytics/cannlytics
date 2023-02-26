// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 2/26/2023
// Updated: 2/26/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Dart imports:
import 'dart:convert';

// Package imports:
import 'package:cannlytics_app/services/api_service.dart';
import 'package:http/http.dart' as http;

class MetrcService {
  // MetrcService();

  // Authorization header for API requests
  // final String _authToken;
  // final String _authToken = await APIService.getUserToken();

  // Base URL.
  static const String _baseUrl = 'https://your-metrc-api-url.com/api/v2';

  // Create a strain in the Metrc API.
  Future<void> createStrain({
    required String name,
    required String testingStatus,
    required double thcLevel,
    required double cbdLevel,
    required double indicaPercentage,
    required double sativaPercentage,
  }) async {
    final data = <String, dynamic>{
      'name': name,
      'testing_status': testingStatus,
      'thc_level': thcLevel,
      'cbd_level': cbdLevel,
      'indica_percentage': indicaPercentage,
      'sativa_percentage': sativaPercentage,
    };

    const url = '$_baseUrl/metrc/strains';
    final String _authToken = await APIService.getUserToken();
    final headers = <String, String>{'Authorization': 'Basic $_authToken'};

    final response = await http.post(Uri.parse(url),
        headers: headers, body: json.encode(data));
    if (response.statusCode != 201) {
      throw Exception('Failed to create strain.');
    }
  }

  Future<List<Map<String, dynamic>>> getStrains() async {
    final url = '$_baseUrl/metrc/strains';
    final String _authToken = await APIService.getUserToken();
    final headers = <String, String>{'Authorization': 'Basic $_authToken'};

    final response = await http.get(Uri.parse(url), headers: headers);
    if (response.statusCode != 200) {
      throw Exception('Failed to get strains.');
    }

    final data = json.decode(response.body);
    return List<Map<String, dynamic>>.from(data['data']);
  }

  Future<void> updateStrain({
    required String id,
    required String name,
    required String testingStatus,
    required double thcLevel,
    required double cbdLevel,
    required double indicaPercentage,
    required double sativaPercentage,
  }) async {
    final data = <String, dynamic>{
      'id': id,
      'name': name,
      'testing_status': testingStatus,
      'thc_level': thcLevel,
      'cbd_level': cbdLevel,
      'indica_percentage': indicaPercentage,
      'sativa_percentage': sativaPercentage,
    };

    final url = '$_baseUrl/metrc/strains';
    final String _authToken = await APIService.getUserToken();
    final headers = <String, String>{'Authorization': 'Basic $_authToken'};

    final response = await http.post(Uri.parse(url),
        headers: headers, body: json.encode(data));
    if (response.statusCode != 200) {
      throw Exception('Failed to update strain.');
    }
  }

  Future<void> deleteStrain({required String id}) async {
    final url = '$_baseUrl/metrc/strains/$id';
    final String _authToken = await APIService.getUserToken();
    final headers = <String, String>{'Authorization': 'Basic $_authToken'};

    final response = await http.delete(Uri.parse(url), headers: headers);
    if (response.statusCode != 200) {
      throw Exception('Failed to delete strain.');
    }
  }
}

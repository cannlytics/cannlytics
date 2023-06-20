// Cannlytics Data
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 6/19/2023
// Updated: 6/19/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// API key service provider.
import 'package:cannlytics_data/services/api_service.dart';
import 'package:cannlytics_data/services/firestore_service.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

final apiKeyService = Provider<APIKeyService>((ref) {
  return APIKeyService(ref.watch(firestoreProvider));
});

/// APIKey service.
class APIKeyService {
  const APIKeyService(this._dataSource);
  final FirestoreService _dataSource;

  // Create API key.
  Future<String> createAPIKey(Map data) async {
    print('Creating API key...');
    String url = '/api/auth/create-key';
    var response = await APIService.apiRequest(url, data: data);
    return response['api_key'];
  }

  // Delete API key.
  Future<void> deleteAPIKey(Map data) async {
    print('Deleting API key...');
    String url = '/api/auth/delete-key';
    await APIService.apiRequest(url, data: data);
  }

  // Get API keys.
  Future<List> getAPIKeys() async {
    print('Getting API keys...');
    String url = '/api/auth/get-keys';
    var response = await APIService.apiRequest(url);
    return response['data'];
  }
}

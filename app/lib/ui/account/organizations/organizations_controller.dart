// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 3/3/2023
// Updated: 3/4/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Package imports:
import 'dart:async';

import 'package:cannlytics_app/models/organization.dart';
import 'package:cannlytics_app/services/api_service.dart';
import 'package:cannlytics_app/services/firestore_service.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

// Project imports:
import 'package:cannlytics_app/services/auth_service.dart';

// Organization licenses provider.
// final organizationsProvider = StreamProvider.autoDispose<Map>((ref) {
//   final user = ref.watch(userProvider).value;
//   final _database = ref.watch(firestoreProvider);
//   // FIXME: Get the current organization ID.
//   final orgId = 'test-company';
//   print('CURRENT USER:');
//   print(user!.uid);
//   print('CURRENT ORGANIZATION:');
//   print(orgId);
//   return _database.watchDocument(
//     path: FirestorePath.organization(orgId),
//     builder: (data, documentId) {
//       return data ?? {};
//     },
//   );
// });

// Organizations provider.
final organizationsProvider =
    AutoDisposeAsyncNotifierProvider<OrganizationsController, void>(
        OrganizationsController.new);

/// Organizations controller.
class OrganizationsController extends AutoDisposeAsyncNotifier<void> {
  @override
  FutureOr<void> build() {}

  /// Get organizations.
  Future<List<Organization>> getOrganizations() async {
    List<Map> response = await APIService.authRequest('/organizations');
    print('RESPONSE:');
    print(response);
    return response.map((org) => Organization.fromMap(org)).toList();
  }
}

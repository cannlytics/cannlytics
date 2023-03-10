// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 3/3/2023
// Updated: 3/9/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Package imports:
import 'package:cannlytics_app/models/metrc/facility.dart';
import 'package:cannlytics_app/services/auth_service.dart';
import 'package:cannlytics_app/ui/business/facilities/facilities_controller.dart';
import 'package:firebase_auth/firebase_auth.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

// Project imports:
import 'package:cannlytics_app/models/common/organization.dart';
import 'package:cannlytics_app/services/api_service.dart';

// User type provider.
final userTypeProvider = StateProvider<String>((ref) => 'business');

// Primary organization provider.
final primaryOrganizationProvider = StateProvider<String?>((ref) => null);

// Primary state.
final primaryStateProvider = StateProvider<String?>((ref) => null);

// Primary license number.
final primaryLicenseProvider = StateProvider<String?>((ref) => null);

// Primary facility ID.
final primaryFacilityProvider = StateProvider<String?>((ref) => null);

// User provider.
final userProvider = StreamProvider<User?>((ref) {
  return ref.watch(authProvider).authStateChanges();
});

/// Organizations provider.
final organizationsProvider =
    FutureProvider.autoDispose<List<Organization>>((ref) async {
  // Get organizations from the API.
  final response = await APIService.apiRequest('/organizations');

  // Convert organizations data into models.
  List<Organization> data = [];
  for (Map item in response) {
    data.add(Organization.fromMap(item));
  }

  // Set the primary organization, license, and state if needed.
  if (data.isNotEmpty) {
    final currentOrg = ref.read(primaryOrganizationProvider);
    final currentLicense = ref.read(primaryLicenseProvider);
    if (currentOrg == null) {
      ref.read(primaryOrganizationProvider.notifier).state = data[0].id;
    }
    if (currentLicense == null) {
      var licenses = data[0].licenses ?? [];
      if (licenses.isNotEmpty) {
        var license = licenses[0];
        ref.read(primaryLicenseProvider.notifier).state =
            license!['license_number'];
        ref.read(primaryStateProvider.notifier).state = license!['state'];
      }
    }
  }

  // Return a list of organizations.
  return data;
});

// DEV:
// /// The main controller for the app.
// class AppController {
//   // Set the primary facility and license number.
//   static void setPrimaryFacility(WidgetRef ref, String? value) {
//     ref.read(primaryFacilityProvider.notifier).state = value!;
//     final facilities = ref.read(facilitiesProvider).value ?? [];
//     for (Facility x in facilities) {
//       if (x.id == value) {
//         ref.read(primaryLicenseProvider.notifier).state = x.licenseNumber;
//       }
//     }
//   }
// }

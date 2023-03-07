// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 3/3/2023
// Updated: 3/6/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Package imports:
import 'package:cannlytics_app/models/organization.dart';
import 'package:cannlytics_app/services/api_service.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

// User type provider.
final userTypeProvider = StateProvider<String>((ref) => 'business');

/// Organizations provider.
final organizationsProvider =
    FutureProvider.autoDispose<List<Organization>>((ref) async {
  final response = await APIService.apiRequest('/organizations');
  List<Organization> data = [];
  for (Map item in response) {
    data.add(Organization.fromMap(item));
  }
  return data;
});

/// TODO: License provider.

/// TODO: Get licenses / facilities.
// final facilitiesProvider =
//     FutureProvider.autoDispose<List<Organization>>((ref) async {
//   final response = await APIService.apiRequest('/organizations');
//   List<Organization> data = [];
//   for (Map item in response) {
//     data.add(Organization.fromMap(item));
//   }
//   return data;
// });


/* WORKING EXAMPLE */

// // Organizations service provider.
// final organizationsServiceProvider = Provider<OrganizationsService>((ref) {
//   return OrganizationsService(ref.watch(firestoreProvider));
// });

// /// Organizations service.
// class OrganizationsService {
//   const OrganizationsService(this._dataSource);
//   final FirestoreService _dataSource;

//   Future<List<dynamic>> getOrganizations() async {
//     final response = await APIService.apiRequest('/organizations');
//     print('RESPONSE:');
//     print(response);
//     List<dynamic> data =
//         response.map((org) => Organization.fromMap(org)).toList();
//     return data;
//   }
// }

/* DEV */

// // Organization management provider.
// final organizationSelectionProvider =
//     ChangeNotifierProvider<OrganizationSelectionProvider>((ref) {
//   return OrganizationSelectionProvider();
// });

// /// License management functionality.
// class OrganizationSelectionProvider extends ChangeNotifier {
//   // Primary license.
//   String _primaryOrganization = 'Organizations';
//   String get primaryOrganization => _primaryOrganization;

//   // User's licenses.
//   // TODO: Somehow populate licenses from Firestore on initialization.
//   List<String> _organizations = ['Organizations'];
//   List<String> get organizations => _organizations;

//   /// Change the user's primary organization.
//   changeOrganization(String value) {
//     if (value.isEmpty) {
//       return _primaryOrganization;
//     }
//     _primaryOrganization = value;
//     return notifyListeners();
//   }

//   /// Change the user's licenses.
//   changeLicenses(List<String> values) {
//     if (values.isEmpty) {
//       return _organizations;
//     }
//     _organizations = values;
//     return notifyListeners();
//   }
// }

// // License management provider.
// final facilitySelectionProvider =
//     ChangeNotifierProvider<FacilitySelectionProvider>((ref) {
//   return FacilitySelectionProvider();
// });

// /// License management functionality.
// class FacilitySelectionProvider extends ChangeNotifier {
//   // Primary license.
//   String _primaryLicense = '+ Add a license';
//   String get primaryLicense => _primaryLicense;

//   // User's licenses.
//   // TODO: Somehow populate licenses from Firestore on initialization.
//   List<String> _licenses = ['+ Add a license'];
//   List<String> get licenses => _licenses;

//   /// Change the user's primary license.
//   changeLicense(String value) {
//     if (value.isEmpty) {
//       return _primaryLicense;
//     }
//     _primaryLicense = value;
//     return notifyListeners();
//   }

//   /// Change the user's licenses.
//   changeLicenses(List<String> values) {
//     if (values.isEmpty) {
//       return _licenses;
//     }
//     _licenses = values;
//     return notifyListeners();
//   }
// }

/* SCRAP */

// /// Organizations stream.
// final organizationsProvider =
//     FutureProvider.autoDispose<List<Organization>>((ref) async {
//   final service = ref.watch(organizationsServiceProvider);
//   return await service.getOrganizations();
// });

// // Organization provider.
// final organizationProvider = StreamProvider.autoDispose<Map>((ref) {
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

/* SCRAP */

// Organization licenses provider.
// final organizationsProvider = StreamProvider.autoDispose<Map>((ref) {
//   final user = ref.watch(userProvider).value;
//   final _database = ref.watch(firestoreProvider);
//   // Get the current organization ID.
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

// // Organizations provider.
// final organizationsProvider =
//     AutoDisposeAsyncNotifierProvider<OrganizationsController, void>(
//         OrganizationsController.new);

// /// Organizations controller.
// class OrganizationsController extends AutoDisposeAsyncNotifier<void> {
//   @override
//   FutureOr<void> build() {}

//   /// Get organizations.
//   Future<List<Organization>> getOrganizations() async {
//     List<Map> response = await APIService.apiRequest('/organizations');
//     print('RESPONSE:');
//     print(response);
//     return response.map((org) => Organization.fromMap(org)).toList();
//   }
// }

// Organizations provider.
// final organizationsProvider = extends AutoDisposeAsyncNotifier<void> {
//   // final user = ref.watch(userProvider).value;
//   // final _database = ref.watch(firestoreProvider);
//   // // Get the current organization ID.
//   // final orgId = 'test-company';
//   // print('CURRENT USER:');
//   // print(user!.uid);
//   // print('CURRENT ORGANIZATION:');
//   // print(orgId);
//   // return _database.watchDocument(
//   //   path: FirestorePath.organization(orgId),
//   //   builder: (data, documentId) {
//   //     return data ?? {};
//   //   },
//   // );
//   List<Map> response = await APIService.apiRequest('/organizations');
//     print('RESPONSE:');
//     print(response);
//     return response.map((org) => Organization.fromMap(org)).toList();
// });

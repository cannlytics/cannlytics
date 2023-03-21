// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 3/3/2023
// Updated: 3/20/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Dart imports:
import 'dart:async';

// Package imports:
import 'package:file_picker/file_picker.dart';
import 'package:firebase_storage/firebase_storage.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

// Project imports:
import 'package:cannlytics_app/models/common/organization.dart';
import 'package:cannlytics_app/services/api_service.dart';
import 'package:cannlytics_app/services/auth_service.dart';
import 'package:cannlytics_app/services/firestore_service.dart';

// Organizations controller.
final organizationsController =
    AutoDisposeAsyncNotifierProvider<OrganizationsController, void>(
        OrganizationsController.new);

/// Manage organizations.
class OrganizationsController extends AutoDisposeAsyncNotifier<void> {
  @override
  FutureOr<void> build() {}

  /// TODO: Create organization.
  Future<void> createOrganization() async {
    state = const AsyncValue.loading();
    // state = await AsyncValue.guard();
  }

  // TODO: Update organization.
  Future<void> updateOrganization() async {
    state = const AsyncValue.loading();
    // state = await AsyncValue.guard();
  }

  // TODO: Delete organization.
  Future<void> deleteOrganization() async {
    state = const AsyncValue.loading();
    // state = await AsyncValue.guard();
  }

  // TODO: Accept team member.
  Future<void> acceptTeamMember() async {
    state = const AsyncValue.loading();
    // state = await AsyncValue.guard();
  }

  // TODO: Invite team member.
  Future<void> inviteTeamMember() async {
    state = const AsyncValue.loading();
    // state = await AsyncValue.guard();
  }

  // TODO: Request to join an organization.
  Future<void> joinOrganization() async {
    state = const AsyncValue.loading();
    // state = await AsyncValue.guard();
  }

  /// Upload an organization photo through the API.
  Future<void> uploadOrganizationPhoto() async {
    // Read the organization ID.
    final orgId = ref.read(organizationName).text;
    print('ORG: $orgId');

    // FIXME: Handle unique organizations IDs:
    // - Check if the organization ID exists.
    // - If it exists and it's not the users, return an error.
    // - If the org does not exist, then temporarily assign it to the user?

    // Allow the user to pick a file.
    var pickedFile = await FilePicker.platform.pickFiles();

    // If the user picks a photo.
    if (pickedFile != null) {
      // Perform pre-post validation.
      List<String> acceptedTypes = ['jpeg', 'jpg', 'png'];
      int photoSize = pickedFile.files.first.size;
      String? photoType = pickedFile.files.first.extension ?? '';
      photoType = photoType.toLowerCase();
      if (photoSize >= 5 * 1024 * 1024) {
        print('FILE TOO LARGE!');
        return;
      } else if (!acceptedTypes.contains(photoType)) {
        print('WRONG FILE TYPE!');
        return;
      }

      // TODO: Test
      print('TODO: UPLOAD FILE...');
      // // Upload the selected photo to Firebase Storage and get its download URL.
      // final String photoRef = 'organizations/$orgId/photo.jpg';
      // final storageRef = FirebaseStorage.instance.ref().child(photoRef);
      // final uploadTask = storageRef.putData(pickedFile.files.first.bytes!);
      // final snapshot = await uploadTask.whenComplete(() {});
      // final downloadURL = await snapshot.ref.getDownloadURL();

      // // Update the user's data in Firestore.
      // final _firestore = ref.read(firestoreProvider);
      // await _firestore.setData(
      //   path: 'organizations/$orgId',
      //   data: {
      //     'photo_uploaded_at': DateTime.now().toIso8601String(),
      //     'photo_size': photoSize,
      //     'photo_type': photoType,
      //     'photo_url': downloadURL,
      //     'photo_ref': photoRef,
      //   },
      // );
    }
    // TODO: Show appropriate notifications.
    //     showNotification('Photo saved', 'Organization photo saved with your organization files.', /* type = */ 'success');
    //     setState(() {
    //       _organizationPhotoUrl = url;
    //     });
    //   } catch (error) {
    //     showNotification('Photo Change Error', 'Error saving photo.', /* type = */ 'error');
    //   }
  }
}

// Organization name field.
final organizationName =
    StateNotifierProvider<OrganizationName, TextEditingController>(
        (ref) => OrganizationName());

class OrganizationName extends StateNotifier<TextEditingController> {
  OrganizationName() : super(TextEditingController());

  @override
  void dispose() {
    state.dispose();
    super.dispose();
  }

  void change(String value) => state.value = TextEditingValue(text: value);
}

// Organization ID field.
final organizationId = StateProvider<String?>((ref) => null);

// Organization image.
final organizationImage = StateProvider<String?>((ref) => null);

/* WORKING */

// // Organizations service provider.
// final organizationsServiceProvider = Provider<OrganizationsService>((ref) {
//   return OrganizationsService(ref.watch(firestoreProvider));
// });

// /// Organizations service.
// class OrganizationsService {
//   const OrganizationsService(this._dataSource);
//   final FirestoreService _dataSource;

//   Future<List<Organization>> getOrganizations() async {
//     List<Map> response = await APIService.apiRequest('/organizations');
//     print('RESPONSE:');
//     print(response);
//     return response.map((org) => Organization.fromMap(org)).toList();
//   }
// }

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

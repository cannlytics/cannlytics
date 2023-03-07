// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 2/18/2023
// Updated: 2/18/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Dart imports:
import 'dart:async';

// Package imports:
import 'package:flutter_riverpod/flutter_riverpod.dart';

// Project imports:
import 'package:cannlytics_app/models/metrc/facility.dart';
import 'package:cannlytics_app/services/auth_service.dart';
import 'package:cannlytics_app/ui/business/facilities/facilities_controller.dart';

class FacilityScreenController extends AutoDisposeAsyncNotifier<void> {
  @override
  FutureOr<void> build() {
    // ok to leave this empty if the return type is FutureOr<void>
  }

  // /// Set data for a facility.
  // Future<bool> setFacility(Facility entry) async {
  //   final currentUser = ref.read(authProvider).currentUser;
  //   if (currentUser == null) {
  //     throw AssertionError('User can\'t be null');
  //   }
  //   final database = ref.read(databaseProvider);
  //   state = const AsyncLoading();
  //   state = await AsyncValue.guard(
  //       () => database.setFacility(uid: currentUser.uid, facility: entry));
  //   return state.hasError == false;
  // }
}

// The facility screen provider.
final facilityScreenControllerProvider =
    AutoDisposeAsyncNotifierProvider<FacilityScreenController, void>(
        FacilityScreenController.new);

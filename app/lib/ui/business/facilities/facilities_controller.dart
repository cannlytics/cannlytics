// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 2/18/2023
// Updated: 3/7/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Package imports:
import 'package:flutter_riverpod/flutter_riverpod.dart';

// Project imports:
import 'package:cannlytics_app/models/metrc/facility.dart';
import 'package:cannlytics_app/services/metrc_service.dart';
import 'package:cannlytics_app/ui/general/app_controller.dart';

// Facilities rows per page provider.
final facilitiesRowsPerPageProvider = StateProvider<int>((ref) => 5);

// Facilities provider.
final facilitiesProvider =
    AsyncNotifierProvider<FacilitiesController, List<Facility>>(() {
  return FacilitiesController();
});

/// Facilities controller.
class FacilitiesController extends AsyncNotifier<List<Facility>> {
  @override
  Future<List<Facility>> build() async {
    // Load initial facilities list from Metrc.
    return _getFacilities();
  }

  /// Get facilities.
  Future<List<Facility>> _getFacilities() async {
    final orgId = ref.watch(primaryOrganizationProvider);
    final state = ref.watch(primaryStateProvider);
    try {
      return await MetrcFacilities.getFacilities(
        orgId: orgId,
        state: state,
      );
    } catch (error, stack) {
      print(stack);
      throw Exception("Error decoding JSON: [error=${error.toString()}]");
    }
  }
}

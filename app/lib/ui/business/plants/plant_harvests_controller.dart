// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 3/9/2023
// Updated: 3/9/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Package imports:
import 'package:flutter_riverpod/flutter_riverpod.dart';

// Project imports:
import 'package:cannlytics_app/models/metrc/plant_harvest.dart';
import 'package:cannlytics_app/services/metrc_service.dart';
import 'package:cannlytics_app/ui/main/app_controller.dart';

// Plants rows per page provider.
final plantHarvestsRowsPerPageProvider = StateProvider<int>((ref) => 5);

// Plants provider.
final plantHarvestsProvider =
    AsyncNotifierProvider<PlantsController, List<Harvest>>(() {
  return PlantsController();
});

/// Plants controller.
class PlantsController extends AsyncNotifier<List<Harvest>> {
  @override
  Future<List<Harvest>> build() async {
    // Load initial data from Metrc.
    return _getPlants();
  }

  /// Get plantHarvests.
  Future<List<Harvest>> _getPlants() async {
    // final licenseNumber = ref.watch(primaryLicenseProvider);
    final licenseNumber = '010-X0001';
    final orgId = ref.watch(primaryOrganizationProvider);
    final state = ref.watch(primaryStateProvider);
    try {
      // FIXME:
      // return await MetrcPlants.getPlants(
      //   licenseNumber: licenseNumber,
      //   orgId: orgId,
      //   state: state,
      // );
      return [];
    } catch (error, stack) {
      print(stack);
      throw Exception("Error decoding JSON: [error=${error.toString()}]");
    }
  }

  // TODO: Get plant harvests.

  // TODO: Create plant harvests.

  // TODO: Update plant harvests.

  // TODO: Delete plant harvests.
}

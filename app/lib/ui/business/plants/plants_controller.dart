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
import 'package:cannlytics_app/models/metrc/plant.dart';
import 'package:cannlytics_app/services/metrc_service.dart';
import 'package:cannlytics_app/ui/general/app_controller.dart';

// Plants rows per page provider.
final plantsRowsPerPageProvider = StateProvider<int>((ref) => 5);

// Plants provider.
final plantsProvider = AsyncNotifierProvider<PlantsController, List<Plant>>(() {
  return PlantsController();
});

/// Plants controller.
class PlantsController extends AsyncNotifier<List<Plant>> {
  @override
  Future<List<Plant>> build() async {
    // Load initial data from Metrc.
    return _getPlants();
  }

  /// Get plants.
  Future<List<Plant>> _getPlants() async {
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

  // TODO: Get plant.

  // TODO: Create plant.

  // TODO: Update plant.

  // TODO: Delete plant.
}

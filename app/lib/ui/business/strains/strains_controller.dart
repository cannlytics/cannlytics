// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 3/8/2023
// Updated: 3/8/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Package imports:
import 'package:flutter_riverpod/flutter_riverpod.dart';

// Project imports:
import 'package:cannlytics_app/models/metrc/strain.dart';
import 'package:cannlytics_app/services/metrc_service.dart';
import 'package:cannlytics_app/ui/main/app_controller.dart';

// Strains rows per page provider.
final strainsRowsPerPageProvider = StateProvider<int>((ref) => 5);

// Strains provider.
final strainsProvider =
    AsyncNotifierProvider<StrainsController, List<Strain>>(() {
  return StrainsController();
});

/// Strains controller.
class StrainsController extends AsyncNotifier<List<Strain>> {
  @override
  Future<List<Strain>> build() async {
    // Load initial data from Metrc.
    return _getStrains();
  }

  /// Get strains.
  Future<List<Strain>> _getStrains() async {
    // final licenseNumber = ref.watch(primaryLicenseProvider);
    final licenseNumber = '010-X0001';
    final orgId = ref.watch(primaryOrganizationProvider);
    final state = ref.watch(primaryStateProvider);
    try {
      // FIXME:
      // return await MetrcStrains.getStrains(
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

  // TODO: Get strain.

  // TODO: Create strain.

  // TODO: Update strain.

  // TODO: Delete strain.
}

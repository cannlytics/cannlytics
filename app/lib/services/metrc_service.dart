// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 2/26/2023
// Updated: 3/9/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Project imports:
import 'package:cannlytics_app/models/metrc/category.dart';
import 'package:cannlytics_app/models/metrc/delivery.dart';
import 'package:cannlytics_app/models/metrc/employee.dart';
import 'package:cannlytics_app/models/metrc/facility.dart';
import 'package:cannlytics_app/models/metrc/item.dart';
import 'package:cannlytics_app/models/metrc/lab_result.dart';
import 'package:cannlytics_app/models/metrc/lab_test.dart';
import 'package:cannlytics_app/models/metrc/location.dart';
import 'package:cannlytics_app/models/metrc/package.dart';
import 'package:cannlytics_app/models/metrc/patient.dart';
import 'package:cannlytics_app/models/metrc/plant.dart';
import 'package:cannlytics_app/models/metrc/plant_batch.dart';
import 'package:cannlytics_app/models/metrc/plant_harvest.dart';
import 'package:cannlytics_app/models/metrc/sales_receipt.dart';
import 'package:cannlytics_app/models/metrc/sales_transaction.dart';
import 'package:cannlytics_app/models/metrc/strain.dart';
import 'package:cannlytics_app/models/metrc/transporter.dart';
import 'package:cannlytics_app/services/api_service.dart';

// TODO: Use models instead of Maps where possible.

class base {}

/// Metrc API service.
/// FIXME: These can't be called.
class Metrc extends base
    with
        MetrcLicenses,
        MetrcEmployees,
        MetrcLocations,
        MetrcStrains,
        MetrcFacilities,
        MetrcPlants,
        MetrcPlantBatches,
        MetrcHarvests,
        MetrcPackages,
        MetrcItems,
        MetrcTransfers,
        MetrcLabTests,
        MetrcPatients,
        MetrcSales,
        MetrcTransactions,
        MetrcDeliveries {
  // Create instances of the classes
  MetrcFacilities facilities = MetrcFacilities();
  MetrcEmployees employees = MetrcEmployees();
  MetrcLicenses licenses = MetrcLicenses();
  MetrcLocations locations = MetrcLocations();
  MetrcStrains strains = MetrcStrains();
  MetrcPlants plants = MetrcPlants();
  MetrcPlantBatches plantBatches = MetrcPlantBatches();
  MetrcHarvests harvests = MetrcHarvests();
  MetrcPackages packages = MetrcPackages();
  MetrcItems items = MetrcItems();
  MetrcTransfers transfers = MetrcTransfers();
  MetrcLabTests labTests = MetrcLabTests();
  MetrcPatients patients = MetrcPatients();
  MetrcSales sales = MetrcSales();
  MetrcTransactions transactions = MetrcTransactions();
  MetrcDeliveries deliveries = MetrcDeliveries();

  // Additional properties and methods
}
// class Metrc {
//   final MetrcFacilities facilities;
//   final MetrcEmployees employees;
//   final MetrcLocations locations;
//   final MetrcLicenses licenses;
//   final MetrcStrains strains;
//   final MetrcPlants plants;
//   final MetrcPlantBatches plantBatches;
//   final MetrcHarvests harvests;
//   final MetrcPackages packages;
//   final MetrcItems items;
//   final MetrcTransfers transfers;
//   final MetrcLabTests labTests;
//   final MetrcPatients patients;
//   final MetrcSales sales;
//   final MetrcTransactions transactions;
//   final MetrcDeliveries deliveries;

//   Metrc()
//       : facilities = MetrcFacilities(),
//         employees = MetrcEmployees(),
//         licenses = MetrcLicenses(),
//         locations = MetrcLocations(),
//         strains = MetrcStrains(),
//         plants = MetrcPlants(),
//         plantBatches = MetrcPlantBatches(),
//         harvests = MetrcHarvests(),
//         packages = MetrcPackages(),
//         items = MetrcItems(),
//         transfers = MetrcTransfers(),
//         labTests = MetrcLabTests(),
//         patients = MetrcPatients(),
//         sales = MetrcSales(),
//         transactions = MetrcTransactions(),
//         deliveries = MetrcDeliveries();
// }

/// Manage Metrc licenses
class MetrcLicenses {
  /// Add Metrc license.
  static Future<void> createLicense(
    String licenseNumber,
    String licenseType,
    String metrcUserApiKey,
    String orgId,
    String state,
  ) async {
    String endpoint = '/api/metrc/admin/create-license';
    Map data = {
      'license_number': licenseNumber,
      'license_type': licenseType,
      'metrc_user_api_key': metrcUserApiKey,
      'org_id': orgId,
      'state': state,
    };
    return await APIService.apiRequest(endpoint, data: data);
  }

  /// Delete Metrc License.
  static Future<void> deleteLicense(
    String licenseNumber,
    String orgId,
    String deletionReason,
  ) async {
    String endpoint = '/api/metrc/admin/delete-license';
    Map data = {
      'license_number': licenseNumber,
      'org_id': orgId,
      'deletion_reason': deletionReason,
    };
    return await APIService.apiRequest(endpoint, data: data);
  }
}

/// Facilities
class MetrcFacilities {
  /// Get facilities.
  static Future<List<Facility>> getFacilities({
    String? orgId,
    String? state,
  }) async {
    String endpoint = '/api/metrc/facilities';
    Map<String, dynamic> options = {
      'params': {'org_id': orgId, 'state': state}
    };
    List<dynamic> response = await APIService.apiRequest(
      endpoint,
      options: options,
    );
    List<Facility> items = [];
    for (var item in response) {
      items.add(Facility.fromMap(item));
    }
    return items;
  }
}

/// Employees
class MetrcEmployees {
  /// Get employees.
  static Future<List<Employee>> getEmployees(String licenseNumber) async {
    String endpoint = '/api/metrc/employees';
    Map params = {'license': licenseNumber};
    List<Employee> items = [];
    List<dynamic> response = await APIService.apiRequest(
      endpoint,
      options: {'params': params},
    );
    for (var item in response) {
      items.add(Employee.fromMap(item));
    }
    return items;
  }
}

/// Locations
class MetrcLocations {
  // Get location types.
  static Future<List> getLocationTypes({String? licenseNumber}) async {
    String endpoint = '/api/metrc/types/locations';
    return await APIService.apiRequest(
      endpoint,
      options: {
        'params': {'license': licenseNumber}
      },
    );
  }

  // Create a location.
  static Future<void> createLocation({
    required String name,
    String? licenseNumber,
    String? locationType,
  }) async {
    String endpoint = '/api/metrc/locations';
    Map data = {
      'name': name,
      'location_type': locationType ?? 'Default Location',
    };
    return await APIService.apiRequest(
      endpoint,
      data: data,
      options: {
        'params': {'license': licenseNumber}
      },
    );
  }

  // Get locations.
  static Future<List<Location>> getLocations({
    String? licenseNumber,
    String? orgId,
    String? state,
  }) async {
    String endpoint = '/api/metrc/locations';
    final response = await APIService.apiRequest(
      endpoint,
      options: {
        'params': {
          'license': licenseNumber,
          'org_id': orgId,
          'state': state,
        }
      },
    );
    List<Location> items = [];
    for (var item in response) {
      items.add(Location.fromMap(item));
    }
    return items;
  }

  // Get a location.
  static Future<Location> getLocation({
    String? licenseNumber,
    String? orgId,
    String? state,
    String? id,
  }) async {
    String endpoint = '/api/metrc/locations/$id';
    return await APIService.apiRequest(
      endpoint,
      options: {
        'params': {
          'license': licenseNumber,
          'org_id': orgId,
          'state': state,
        }
      },
    );
  }

  // Update the name of a location.
  static Future<void> updateLocationName({
    required String id,
    required String name,
    required String locationTypeName,
    String? licenseNumber,
  }) async {
    String endpoint = '/api/metrc/locations/$id';
    Map data = {
      'id': id,
      'name': name,
      'location_type_name': locationTypeName,
    };
    return await APIService.apiRequest(
      endpoint,
      data: data,
      options: {
        'params': {'license': licenseNumber}
      },
    );
  }

  // Delete a location.
  static Future<void> deleteLocation({
    required String id,
    String? licenseNumber,
  }) async {
    String endpoint = '/api/metrc/locations/$id';
    return await APIService.apiRequest(
      endpoint,
      options: {
        'params': {'license': licenseNumber, 'delete': true}
      },
    );
  }
}

/// Strains
class MetrcStrains {
  /// Create a strain in the Metrc API.
  static Future<void> createStrain(
    String licenseNumber, {
    required String name,
    required String testingStatus,
    required double thcLevel,
    required double cbdLevel,
    required double indicaPercentage,
    required double sativaPercentage,
  }) async {
    final data = <String, dynamic>{
      'name': name,
      'testing_status': testingStatus,
      'thc_level': thcLevel,
      'cbd_level': cbdLevel,
      'indica_percentage': indicaPercentage,
      'sativa_percentage': sativaPercentage,
    };
    String endpoint = '/api/metrc/strains';
    await APIService.apiRequest(
      endpoint,
      data: data,
      options: {
        'params': {'license': licenseNumber}
      },
    );
    // TODO: Get the newly created strain's ID.
    // return Strain.fromMap(data, uid);
  }

  /// Get strains.
  static Future<List<Strain>> getStrains(String licenseNumber) async {
    String endpoint = '/api/metrc/strains';
    List<Strain> items = [];
    List<dynamic> response = await APIService.apiRequest(
      endpoint,
      options: {
        'params': {'license': licenseNumber}
      },
    );
    for (var item in response) {
      items.add(Strain.fromMap(item, item['id']));
    }
    return items;
  }

  /// Update a strain.
  static Future<Strain> updateStrain(
    String licenseNumber, {
    required String id,
    required String name,
    required String testingStatus,
    required double thcLevel,
    required double cbdLevel,
    required double indicaPercentage,
    required double sativaPercentage,
  }) async {
    final data = <String, dynamic>{
      'id': id,
      'name': name,
      'testing_status': testingStatus,
      'thc_level': thcLevel,
      'cbd_level': cbdLevel,
      'indica_percentage': indicaPercentage,
      'sativa_percentage': sativaPercentage,
    };
    String endpoint = '/api/metrc/strains';
    await APIService.apiRequest(
      endpoint,
      data: data,
      options: {
        'params': {'license': licenseNumber}
      },
    );
    return Strain.fromMap(data, id);
  }

  /// Delete a strain.
  static Future<void> deleteStrain(
    String licenseNumber, {
    required String id,
  }) async {
    String endpoint = '/api/metrc/strains/$id';
    await APIService.apiRequest(
      endpoint,
      options: {
        'params': {'license': licenseNumber},
        'delete': true,
      },
    );
  }
}

/// Plants
class MetrcPlants {
  /// Create a plant.
  static Future<void> createPlant(
    String licenseNumber,
    Map data,
  ) async {
    String endpoint = '/api/metrc/plants';
    await APIService.apiRequest(
      endpoint,
      // TODO: Make more function like.
      // data: {
      //   'plant_label': 'PLANT_TAG',
      //   'plant_batch_name': batch_name + ' #2',
      //   'plant_batch_type': 'Clone',
      //   'plant_count': 1,
      //   'location_name': test_location,
      //   'strain_name': strain_name,
      //   'patient_license_number': None,
      //   'PackageTag': packageTag,
      //   'actual_date': plantedDate?.toIso8601String(),
      // },
      data: data,
      options: {
        'params': {'license': licenseNumber},
      },
    );
  }

  /// Change the growth phase of a plant
  static Future<void> changePlantGrowthPhase(
    String licenseNumber,
    Map data, {
    String? type,
  }) async {
    String endpoint = '/api/metrc/plants';
    await APIService.apiRequest(
      endpoint,
      data: data,
      options: {
        'params': {'license': licenseNumber},
        'action': type,
      },
    );
  }

  /// Get plants.
  static Future<List<dynamic>> getPlants(
    String licenseNumber, {
    String? type,
    String? start,
    String? end,
  }) async {
    String endpoint = '/api/metrc/plants';
    var response = await APIService.apiRequest(
      endpoint,
      options: {
        'params': {
          'license': licenseNumber,
          'start': start,
          'end': end,
        },
      },
    );
    return response as List<dynamic>;
  }

  /// Move a plant to a different room.
  static Future<void> movePlant(
    String licenseNumber, {
    String? id,
    String? label,
    String? location,
  }) async {
    String endpoint = '/api/metrc/plants';
    await APIService.apiRequest(
      endpoint,
      data: {
        'actual_date': DateTime.now().toIso8601String(),
        'id': id,
        'label': label,
        'location': location,
      },
      options: {
        'params': {'license': licenseNumber},
        'action': 'move',
      },
    );
  }

  /// Add additives to a plant.
  static Future<void> addPlantAdditives(
    String licenseNumber,
    Map data,
  ) async {
    String endpoint = '/api/metrc/plants';
    await APIService.apiRequest(
      endpoint,
      data: data,
      options: {
        'params': {
          'license': licenseNumber,
          'action': 'add-additives',
        }
      },
    );
  }

  /// Manicure a plant.
  static Future<void> manicurePlant(
    String licenseNumber,
    Map data,
  ) async {
    String endpoint = '/api/metrc/plants';
    await APIService.apiRequest(
      endpoint,
      data: data,
      options: {
        'params': {
          'license': licenseNumber,
          'action': 'manicure',
        }
      },
    );
  }

  /// Harvest from a plant.
  static Future<void> harvestPlant(
    String licenseNumber,
    Map data,
  ) async {
    String endpoint = '/api/metrc/plants';
    await APIService.apiRequest(
      endpoint,
      data: data,
      options: {
        'params': {
          'license': licenseNumber,
          'action': 'harvest',
        }
      },
    );
  }

  /// Destroy a plant.
  static Future<void> destroyPlant(
    String licenseNumber,
    String id,
  ) async {
    String endpoint = '/api/metrc/plants/$id';
    await APIService.apiRequest(
      endpoint,
      options: {
        'params': {
          'license': licenseNumber,
          'delete': true,
        }
      },
    );
  }
}

/// Plant batches
class MetrcPlantBatches {
  /// Create a new plant batch.
  static Future<void> createPlantBatch(
    String licenseNumber,
    Map<String, dynamic> data,
  ) async {
    String endpoint = '/api/metrc/batches';
    await APIService.apiRequest(endpoint, data: data, options: {
      'params': {'license': licenseNumber},
    });
  }

  /// Get plant batches by date.
  static Future<List<dynamic>> getPlantBatches(
    String licenseNumber, {
    required String startDate,
    required String endDate,
  }) async {
    String endpoint = '/api/metrc/batches';
    var response = await APIService.apiRequest(endpoint, options: {
      'params': {
        'license': licenseNumber,
        'start': startDate,
        'end': endDate,
      },
    });
    return response as List<dynamic>;
  }

  /// Create a package from a batch.
  static Future<void> createPackageFromBatch(
    String licenseNumber,
    Map<String, dynamic> data,
  ) async {
    String endpoint = '/api/metrc/packages/v1/packages/createfromplantbatch';
    await APIService.apiRequest(endpoint, data: data, options: {
      'params': {'license': licenseNumber},
    });
  }

  /// Flower plants in a batch.
  static Future<void> flowerPlantsBatch(
    String licenseNumber, {
    required String id,
  }) async {
    String endpoint = '/api/metrc/batches';
    await APIService.apiRequest(endpoint, options: {
      'params': {'license': licenseNumber},
      'action': 'flower',
    });
  }

  /// Destroy plants in a batch.
  static Future<void> destroyPlantsBatchPlants(
    String licenseNumber, {
    required String id,
  }) async {
    String endpoint = '/api/metrc/batches';
    await APIService.apiRequest(endpoint, options: {
      'params': {'license': licenseNumber},
      'action': 'destroy-plants',
    });
  }

  /// Add additives.
  static Future<void> addPlantsBatchAdditives(
    String licenseNumber,
    Map data,
  ) async {
    String endpoint = '/api/metrc/batches';
    await APIService.apiRequest(
      endpoint,
      data: data,
      options: {
        'params': {'license': licenseNumber},
        'action': 'add-additives',
      },
    );
  }

  /// Move batch.
  static Future<void> movePlantBatch(
    String licenseNumber, {
    required String name,
    required String location,
  }) async {
    String endpoint = '/api/metrc/batches';
    await APIService.apiRequest(
      endpoint,
      data: {
        'name': name,
        'location': location,
        'move_date': DateTime.now().toIso8601String(),
      },
      options: {
        'params': {'license': licenseNumber},
        'action': 'move',
      },
    );
  }

  /// Split batch.
  static Future<void> splitPlantBatch(
    String licenseNumber, {
    required String name,
    required String newName,
    required int count,
    required String location,
    required String strain,
    String? patientLicenseNumber,
  }) async {
    String endpoint = '/api/metrc/batches';
    await APIService.apiRequest(
      endpoint,
      data: {
        'plant_batch': name,
        'group_name': newName,
        'count': count,
        'location': location,
        'strain': strain,
        'patient_license_number': patientLicenseNumber,
        'actual_date': DateTime.now().toIso8601String(),
      },
      options: {
        'params': {'license': licenseNumber},
        'action': 'split',
      },
    );
  }
}

/// Harvests
class MetrcHarvests {
  /// Get harvests.
  static Future<List<dynamic>> getHarvests(
    String licenseNumber, {
    String? start,
    String? end,
  }) async {
    String endpoint = '/api/metrc/harvests';
    var response = await APIService.apiRequest(
      endpoint,
      options: {
        'params': {
          'license': licenseNumber,
          'start': start,
          'end': end,
        },
      },
    );
    return response as List<dynamic>;
  }

  /// Create a package.
  static Future<void> createPackage(
    String licenseNumber,
    Map<String, dynamic> data,
  ) async {
    String endpoint = '/api/metrc/packages';
    await APIService.apiRequest(
      endpoint,
      data: data,
      options: {
        'params': {'license': licenseNumber},
        'action': 'create-packages',
      },
    );
  }

  /// Create a testing package.
  static Future<void> createTestingPackage(
    String licenseNumber,
    Map<String, dynamic> data,
  ) async {
    String endpoint = '/api/metrc/packages';
    await APIService.apiRequest(
      endpoint,
      data: data,
      options: {
        'params': {'license': licenseNumber},
        'action': 'create-testing-packages',
      },
    );
  }

  /// Remove waste weight from a harvest.
  static Future<void> removeWaste(
    String licenseNumber,
    Map data,
  ) async {
    String endpoint = '/api/metrc/harvests';
    await APIService.apiRequest(
      endpoint,
      data: data,
      options: {
        'params': {'license': licenseNumber},
        'action': 'remove-waste',
      },
    );
  }

  /// Finish a harvest.
  static Future<void> finishHarvest(
    String licenseNumber,
    String harvestId,
  ) async {
    String endpoint = '/api/metrc/harvests';
    await APIService.apiRequest(
      endpoint,
      data: {
        'actual_date': DateTime.now().toIso8601String(),
        'id': harvestId,
      },
      options: {
        'params': {'license': licenseNumber},
        'action': 'finish',
      },
    );
  }

  /// Unfinish a harvest.
  static Future<void> unfinishHarvest(
    String licenseNumber,
    String harvestId,
  ) async {
    String endpoint = '/api/metrc/harvests';
    await APIService.apiRequest(
      endpoint,
      data: {'id': harvestId},
      options: {
        'params': {'license': licenseNumber},
        'action': 'unfinish',
      },
    );
  }
}

/// Packages
class MetrcPackages {
  /// Get packages.
  static Future<List<dynamic>> getPackages(
    String licenseNumber, {
    String? label,
    String? start,
    String? end,
  }) async {
    String endpoint = '/api/metrc/packages';
    if (label != null) label += '/$label';
    var response = await APIService.apiRequest(
      endpoint,
      options: {
        'params': {
          'license': licenseNumber,
          'start': start,
          'end': end,
        },
      },
    );
    return response as List<dynamic>;
  }

  /// Create a package from another package.
  static Future<void> createPackageFromPackage(
    String licenseNumber,
    Map<String, dynamic> data,
  ) async {
    String endpoint = '/api/metrc/packages';
    await APIService.apiRequest(
      endpoint,
      data: data,
      options: {
        'params': {'license': licenseNumber},
      },
    );
  }

  /// Change the item of a package.
  static Future<void> changePackageItem(
    String licenseNumber, {
    required String label,
    required String itemName,
  }) async {
    String endpoint = '/api/metrc/packages';
    await APIService.apiRequest(
      endpoint,
      data: {
        'label': label,
        'item': itemName,
      },
      options: {
        'params': {'license': licenseNumber},
        'action': 'change-package-items',
      },
    );
  }

  /// Change the location of a package.
  static Future<void> changePackageLocation(
    String licenseNumber, {
    required String packageLabel,
    required String location,
  }) async {
    String endpoint = '/api/metrc/packages';
    await APIService.apiRequest(
      endpoint,
      data: {
        'label': packageLabel,
        'location': location,
        'move_date': DateTime.now().toIso8601String(),
      },
      options: {
        'params': {'license': licenseNumber},
        'action': 'move',
      },
    );
  }

  /// Create a plant batch from a package.
  static Future<void> createPlantBatchFromPackage(
    String licenseNumber,
    Map<String, dynamic> data,
  ) async {
    String endpoint = '/api/metrc/packages';
    await APIService.apiRequest(
      endpoint,
      data: data,
      options: {
        'params': {'license': licenseNumber},
        'action': 'create-plant-batches',
      },
    );
  }

  /// Adjust the weight of a package.
  static Future<void> adjustPackageWeight(
    String licenseNumber,
    Map<String, dynamic> data,
  ) async {
    String endpoint = '/api/metrc/packages';
    await APIService.apiRequest(
      endpoint,
      data: data,
      options: {
        'params': {'license': licenseNumber},
        'action': 'adjust',
      },
    );
  }

  /// Finish a package.
  static Future<void> finishPackage(
    String licenseNumber, {
    required String label,
  }) async {
    String endpoint = '/api/metrc/packages';
    await APIService.apiRequest(
      endpoint,
      data: {
        'label': label,
        'actual_date': DateTime.now().toIso8601String(),
      },
      options: {
        'params': {'license': licenseNumber},
        'action': 'finish',
      },
    );
  }

  /// Unfinish a package.
  static Future<void> unfinishPackage(
    String licenseNumber, {
    required String label,
  }) async {
    String endpoint = '/api/metrc/packages';
    await APIService.apiRequest(
      endpoint,
      data: {'label': label},
      options: {
        'params': {'license': licenseNumber},
        'action': 'unfinish',
      },
    );
  }

  /// Remediate a package.
  static Future<void> remediatePackage(
    String licenseNumber,
    Map data,
  ) async {
    String endpoint = '/api/metrc/packages';
    await APIService.apiRequest(
      endpoint,
      data: data,
      options: {
        'params': {'license': licenseNumber},
        'action': 'remediate',
      },
    );
  }

  /// Update the note for a package.
  static Future<void> updatePackageNote(
    String licenseNumber, {
    required String label,
    required String note,
  }) async {
    String endpoint = '/api/metrc/packages';
    await APIService.apiRequest(
      endpoint,
      data: {
        'package_label': label,
        'note': note,
      },
      options: {
        'params': {'license': licenseNumber},
        'action': 'update-package-notes',
      },
    );
  }
}

/// Items
class MetrcItems {
  /// Create items.
  static Future<void> createItems(
    String licenseNumber,
    List<Map<String, dynamic>> data,
  ) async {
    String endpoint = '/api/metrc/items';
    await APIService.apiRequest(
      endpoint,
      data: data,
      options: {
        'params': {'license': licenseNumber}
      },
    );
  }

  /// Get items.
  static Future<List<dynamic>> getItems(
    String licenseNumber, {
    String? id,
    String? start,
    String? end,
  }) async {
    String endpoint = '/api/metrc/items';
    if (id != null) endpoint += '/$id';
    var response = await APIService.apiRequest(
      endpoint,
      options: {
        'params': {
          'license': licenseNumber,
          'start': start,
          'end': end,
        }
      },
    );
    return response as List<dynamic>;
  }

  /// Update an item.
  static Future<void> updateItem(
    String licenseNumber,
    String id,
    Map<String, dynamic> data,
  ) async {
    String endpoint = '/api/metrc/items/$id';
    await APIService.apiRequest(
      endpoint,
      data: data,
      options: {
        'params': {'license': licenseNumber}
      },
    );
  }

  /// Delete an item.
  static Future<void> deleteItem(
    String licenseNumber,
    String id,
  ) async {
    String endpoint = '/api/metrc/items/$id';
    await APIService.apiRequest(
      endpoint,
      options: {
        'params': {'license': licenseNumber},
        'delete': true
      },
    );
  }
}

/// Transfers
class MetrcTransfers {
  /// Set up an external transfer.
  static Future<void> createExternalTransfer(
    String licenseNumber,
    Map<String, dynamic> data,
  ) async {
    String endpoint = '/api/metrc/transfers';
    await APIService.apiRequest(
      endpoint,
      data: data,
      options: {
        'params': {'license': licenseNumber},
      },
    );
  }

  /// Get external transfers.
  static Future<List<dynamic>> getTransactions(
    String licenseNumber, {
    String? id,
    String? type,
  }) async {
    String endpoint = '/api/metrc/transfers';
    if (id != null) endpoint += '/$id';
    var response = await APIService.apiRequest(
      endpoint,
      options: {
        'params': {'license': licenseNumber},
        'type': type,
      },
    );
    return response as List<dynamic>;
  }

  /// Update an external transfer.
  static Future<void> updateExternalTransfer(
    String licenseNumber,
    Map<String, dynamic> data,
  ) async {
    String endpoint = '/api/metrc/transfers';
    await APIService.apiRequest(
      endpoint,
      data: data,
      options: {
        'params': {'license': licenseNumber},
        'action': 'update',
      },
    );
  }

  /// Create a transfer template.
  static Future<void> createTransferTemplate(
    String licenseNumber,
    Map<String, dynamic> data,
  ) async {
    String endpoint = '/api/metrc/transfers/templates';
    await APIService.apiRequest(
      endpoint,
      data: data,
      options: {
        'params': {'license': licenseNumber},
      },
    );
  }

  /// Get transfer templates.
  static Future<List<dynamic>> getTransferTemplates(
    String licenseNumber, {
    String? id,
  }) async {
    String endpoint = '/api/metrc/transactions';
    if (id != null) endpoint += '/$id';
    var response = await APIService.apiRequest(
      endpoint,
      options: {
        'params': {'license': licenseNumber},
      },
    );
    return response as List<dynamic>;
  }

  /// Update a transfer template.
  static Future<void> updateTransferTemplate(
    String licenseNumber,
    String id,
    String data,
  ) async {
    String endpoint = '/api/metrc/transfers/templates/$id';
    await APIService.apiRequest(
      endpoint,
      data: data,
      options: {
        'params': {'license': licenseNumber},
        'action': 'update',
      },
    );
  }

  /// Delete a transfer template.
  Future<void> deleteTransferTemplate(
    String licenseNumber, {
    required String id,
  }) async {
    String endpoint = '/api/metrc/transfers/templates/$id';
    await APIService.apiRequest(
      endpoint,
      options: {
        'params': {'license': licenseNumber},
        'delete': true,
      },
    );
  }
}

/// Lab Tests
class MetrcLabTests {
  /// TODO: Create a lab result record.

  /// TODO: Release lab results.

  /// TODO: Upload a COA.

  /// Get a COA by appending `id` to the URL.
  static Future<dynamic> getCOA(
    String licenseNumber, {
    required String id,
  }) async {
    String endpoint = '/api/metrc/tests/coas/$id';
    var response = await APIService.apiRequest(
      endpoint,
      options: {
        'params': {'license': licenseNumber},
      },
    );
    return response;
    // return LabResult.fromMap(response);
  }
}

/// Patients
class MetrcPatients {
  /// Get active patients.
  static Future<List<Patient>> getPatients(
    String licenseNumber, {
    String? id,
  }) async {
    String endpoint = '/api/metrc/patients';
    if (id != null) endpoint += '/$id';
    var response = await APIService.apiRequest(
      endpoint,
      options: {
        'params': {
          'license': licenseNumber,
        },
      },
    );
    return response as List<Patient>;
  }

  /// Get patient.
  static Future<Patient> getPatient(
    String licenseNumber, {
    String? id,
  }) async {
    List<Patient> response = await getPatients(licenseNumber, id: id);
    return response[0];
  }

  /// Get patient registration locations.
  static Future<List<dynamic>> getPatientLocations(
    String licenseNumber,
  ) async {
    String endpoint = '/api/metrc/patients/locations';
    var response = await APIService.apiRequest(
      endpoint,
      options: {
        'params': {'license': licenseNumber},
      },
    );
    return response as List<dynamic>;
  }

  /// Add a patient.
  static Future<void> addPatient(
    String licenseNumber,
    Map<String, dynamic> data,
  ) async {
    String endpoint = '/api/metrc/patients';
    await APIService.apiRequest(
      endpoint,
      data: data,
      options: {
        'params': {'license': licenseNumber},
      },
    );
  }

  /// Update a patient.
  static Future<void> updatePatient(
    String licenseNumber,
    Map<String, dynamic> data,
  ) async {
    String endpoint = '/api/metrc/patients';
    await APIService.apiRequest(
      endpoint,
      data: data,
      options: {
        'params': {'license': licenseNumber},
        'action': 'update',
      },
    );
  }

  /// Delete a patient.
  static Future<void> deletePatient(
    String licenseNumber, {
    required String id,
  }) async {
    String endpoint = '/api/metrc/patients/$id';
    await APIService.apiRequest(
      endpoint,
      options: {
        'params': {'license': licenseNumber},
        'delete': true,
      },
    );
  }
}

/// Sales
class MetrcSales {
  /// Create a sales receipt for a package.
  static Future<void> createSalesReceipt(
    String licenseNumber,
    Map<String, dynamic> data,
  ) async {
    String endpoint = '/api/metrc/sales';
    await APIService.apiRequest(
      endpoint,
      data: data,
      options: {
        'params': {'license': licenseNumber},
      },
    );
  }

  /// Get sales by date or ID.
  static Future<List<dynamic>> getSalesReceipts(
    String licenseNumber, {
    String? id,
    String? start,
    String? end,
  }) async {
    String endpoint = '/api/metrc/sales';
    if (id != null) endpoint += '/$id';
    var response = await APIService.apiRequest(
      endpoint,
      options: {
        'params': {
          'license': licenseNumber,
          'end': end,
          'start': start,
        },
      },
    );
    return response as List<dynamic>;
  }

  /// Update a sales receipt.
  static Future<void> updateSalesReceipt(
    String licenseNumber,
    Map<String, dynamic> data,
  ) async {
    String endpoint = '/api/metrc/sales';
    await APIService.apiRequest(
      endpoint,
      data: data,
      options: {
        'params': {'license': licenseNumber},
        'action': 'update',
      },
    );
  }

  /// Void a sales receipt.
  static Future<void> voidSalesReceipt(
    String licenseNumber,
    String id,
  ) async {
    String endpoint = '/api/metrc/sales/$id';
    await APIService.apiRequest(
      endpoint,
      options: {
        'params': {'license': licenseNumber},
        'delete': true,
      },
    );
  }
}

/// Transactions
class MetrcTransactions {
  /// Get transactions (daily statistics).
  static Future<List<dynamic>> getTransactions(
    String licenseNumber,
    String start,
    String end,
  ) async {
    String endpoint = '/api/metrc/transactions';
    var response = await APIService.apiRequest(
      endpoint,
      options: {
        'params': {'license': licenseNumber},
        'end': end,
        'start': start,
      },
    );
    return response as List<dynamic>;
  }

  /// Add transactions on a particular day.
  static Future<void> addTransaction(
    String licenseNumber,
    String date,
    Map<String, dynamic> data,
  ) async {
    String endpoint = '/api/metrc/transactions/$date';
    await APIService.apiRequest(
      endpoint,
      data: data,
      options: {
        'params': {'license': licenseNumber},
      },
    );
  }

  /// Update transactions on a particular day.
  static Future<void> updateTransaction(
    String licenseNumber,
    String date,
    Map<String, dynamic> data,
  ) async {
    String endpoint = '/api/metrc/transactions/$date';
    await APIService.apiRequest(
      endpoint,
      data: data,
      options: {
        'params': {'license': licenseNumber},
        'action': 'update',
      },
    );
  }
}

/// Deliveries
class MetrcDeliveries {
  /// Get deliveries.
  static Future<List<dynamic>> getDeliveries(
    String licenseNumber, {
    String? id,
    String? start,
    String? end,
    String? salesStart,
    String? salesEnd,
    String? type,
  }) async {
    String endpoint = '/api/metrc/deliveries';
    if (id != null) endpoint += '/$id';
    var response = await APIService.apiRequest(
      endpoint,
      options: {
        'params': {
          'license': licenseNumber,
          'end': end,
          'start': start,
          'salesStart': salesStart,
          'salesEnd': salesEnd,
          'type': type,
        },
      },
    );
    return response as List<dynamic>;
  }

  /// Create a delivery.
  static Future<void> createDelivery(
    String licenseNumber,
    Map<String, dynamic> data,
  ) async {
    String endpoint = '/api/metrc/deliveries';
    await APIService.apiRequest(
      endpoint,
      data: data,
      options: {
        'params': {'license': licenseNumber}
      },
    );
  }

  /// Update a delivery.
  static Future<void> updateDelivery(
    String licenseNumber,
    Map<String, dynamic> data,
  ) async {
    String endpoint = '/api/metrc/deliveries';
    await APIService.apiRequest(
      endpoint,
      data: data,
      options: {
        'params': {'license': licenseNumber},
        'action': 'update',
      },
    );
  }

  /// Delete a delivery.
  Future<void> deleteDelivery(
    String licenseNumber, {
    required String id,
  }) async {
    String endpoint = '/api/metrc/deliveries/$id';
    await APIService.apiRequest(
      endpoint,
      options: {
        'params': {'license': licenseNumber},
        'delete': true,
      },
    );
  }

  /// Complete a delivery.
  static Future<void> completeDelivery(
    String licenseNumber,
    Map<String, dynamic> data,
  ) async {
    String endpoint = '/api/metrc/deliveries';
    await APIService.apiRequest(
      endpoint,
      data: data,
      options: {
        'params': {'license': licenseNumber},
        'action': 'complete',
      },
    );
  }

  /// Depart a delivery.
  static Future<void> departDelivery(
    String licenseNumber,
    Map<String, dynamic> data,
  ) async {
    String endpoint = '/api/metrc/deliveries';
    await APIService.apiRequest(
      endpoint,
      data: data,
      options: {
        'params': {'license': licenseNumber},
        'action': 'depart',
      },
    );
  }

  /// Restock a delivery.
  static Future<void> restockDelivery(
    String licenseNumber,
    Map<String, dynamic> data,
  ) async {
    String endpoint = '/api/metrc/deliveries';
    await APIService.apiRequest(
      endpoint,
      data: data,
      options: {
        'params': {'license': licenseNumber},
        'action': 'restock',
      },
    );
  }

  /// Deliver a delivery.
  static Future<void> deliverDelivery(
    String licenseNumber,
    Map<String, dynamic> data,
  ) async {
    String endpoint = '/api/metrc/deliveries';
    await APIService.apiRequest(
      endpoint,
      data: data,
      options: {
        'params': {'license': licenseNumber},
        'action': 'deliver',
      },
    );
  }

  /// End a delivery.
  static Future<void> endDelivery(
    String licenseNumber,
    Map<String, dynamic> data,
  ) async {
    String endpoint = '/api/metrc/deliveries';
    await APIService.apiRequest(
      endpoint,
      data: data,
      options: {
        'params': {'license': licenseNumber},
        'action': 'end',
      },
    );
  }

  /// TODO: Get drivers and vehicles.
}

/// Types
class MetrcTypes {
  /// Get adjustment reasons.
  Future<List<dynamic>> getAdjustments() async {
    String endpoint = '/api/metrc/types/adjustments';
    return await APIService.apiRequest(endpoint);
  }

  /// Get batch types.
  Future<List<dynamic>> getBatchTypes() async {
    String endpoint = '/api/metrc/types/batches';
    return await APIService.apiRequest(endpoint);
  }

  /// Get categories.
  Future<List<dynamic>> getCategories() async {
    String endpoint = '/api/metrc/types/categories';
    return await APIService.apiRequest(endpoint);
  }

  /// Get customer types.
  Future<List<dynamic>> getCustomerTypes() async {
    String endpoint = '/api/metrc/types/customers';
    return await APIService.apiRequest(endpoint);
  }

  /// Get growth phases.
  Future<List<dynamic>> getGrowthPhases() async {
    String endpoint = '/api/metrc/types/growth-phases';
    return await APIService.apiRequest(endpoint);
  }

  /// Get location types.
  Future<List<dynamic>> getLocationTypes() async {
    String endpoint = '/api/metrc/types/locations';
    return await APIService.apiRequest(endpoint);
  }

  /// Get package types.
  Future<List<dynamic>> getPackageTypes() async {
    String endpoint = '/api/metrc/types/packages';
    return await APIService.apiRequest(endpoint);
  }

  /// Get package statuses.
  Future<List<dynamic>> getPackageStatuses() async {
    String endpoint = '/api/metrc/types/package-statuses';
    return await APIService.apiRequest(endpoint);
  }

  /// Get return reasons.
  Future<List<dynamic>> getReturnReasons() async {
    String endpoint = '/api/metrc/types/return-reasons';
    return await APIService.apiRequest(endpoint);
  }

  /// Get test statuses.
  Future<List<dynamic>> getTestStatuses() async {
    String endpoint = '/api/metrc/types/test-statuses';
    return await APIService.apiRequest(endpoint);
  }

  /// Get test types.
  Future<List<dynamic>> getTestTypes() async {
    String endpoint = '/api/metrc/types/tests';
    return await APIService.apiRequest(endpoint);
  }

  /// Get transfer types.
  Future<List<dynamic>> getTransferTypes() async {
    String endpoint = '/api/metrc/types/transfers';
    return await APIService.apiRequest(endpoint);
  }

  /// Get units of measure.
  Future<List<dynamic>> getUnitsOfMeasure() async {
    String endpoint = '/api/metrc/types/units';
    return await APIService.apiRequest(endpoint);
  }

  /// Get waste types.
  Future<List<dynamic>> getWasteTypes() async {
    String endpoint = '/api/metrc/types/waste';
    return await APIService.apiRequest(endpoint);
  }

  /// Get waste methods.
  Future<List<dynamic>> getWasteMethods() async {
    String endpoint = '/api/metrc/types/waste-methods';
    return await APIService.apiRequest(endpoint);
  }

  /// Get waste reasons.
  Future<List<dynamic>> getWasteReasons() async {
    String endpoint = '/api/metrc/types/waste-reasons';
    return await APIService.apiRequest(endpoint);
  }
}

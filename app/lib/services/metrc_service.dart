// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 2/26/2023
// Updated: 3/17/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Project imports:
import 'package:cannlytics_app/models/metrc/delivery.dart';
import 'package:cannlytics_app/models/metrc/employee.dart';
import 'package:cannlytics_app/models/metrc/facility.dart';
import 'package:cannlytics_app/models/metrc/item.dart';
import 'package:cannlytics_app/models/metrc/location.dart';
import 'package:cannlytics_app/models/metrc/package.dart';
import 'package:cannlytics_app/models/metrc/patient.dart';
import 'package:cannlytics_app/models/metrc/plant.dart';
import 'package:cannlytics_app/models/metrc/plant_batch.dart';
import 'package:cannlytics_app/models/metrc/plant_harvest.dart';
import 'package:cannlytics_app/models/metrc/sales_receipt.dart';
import 'package:cannlytics_app/models/metrc/sales_transaction.dart';
import 'package:cannlytics_app/models/metrc/strain.dart';
import 'package:cannlytics_app/services/api_service.dart';

/// A helper function to format parameters.
Map getParams(
  String? license,
  String? orgId,
  String? state, {
  String? action,
  bool? delete,
  List<Map>? queries,
}) {
  Map params = {
    'params': {
      'license': license,
      'org_id': orgId,
      'state': state,
    }
  };
  if (delete != null) params['delete'] = delete;
  if (action != null) params['action'] = action;
  if (queries != null) {
    for (Map query in queries) {
      params[query['key']] = query['value'];
    }
  }
  return params;
}

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
    Map options = {
      'params': {
        'org_id': orgId,
        'state': state,
      },
    };
    final response = await APIService.apiRequest(endpoint, options: options);
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
  static Future<List<Employee>> getEmployees({
    String? license,
    String? orgId,
    String? state,
  }) async {
    String endpoint = '/api/metrc/employees';
    List<dynamic> response = await APIService.apiRequest(
      endpoint,
      options: getParams(license, orgId, state),
    );
    List<Employee> items = [];
    for (var item in response) {
      items.add(Employee.fromMap(item));
    }
    return items;
  }

  // Get an employee.
  static Future<Employee> getEmployee({
    required String id,
    String? license,
    String? orgId,
    String? state,
  }) async {
    String endpoint = '/api/metrc/employees/$id';
    final response = await APIService.apiRequest(
      endpoint,
      options: getParams(license, orgId, state),
    );
    return Employee.fromMap(response);
  }
}

/// Locations
class MetrcLocations {
  // Get location types.
  static Future<List<dynamic>> getLocationTypes({
    String? license,
    String? orgId,
    String? state,
  }) async {
    String endpoint = '/api/metrc/types/locations';
    Map options = getParams(license, orgId, state);
    return await APIService.apiRequest(endpoint, options: options);
  }

  // Get locations.
  static Future<List<Location>> getLocations({
    String? license,
    String? orgId,
    String? state,
  }) async {
    String endpoint = '/api/metrc/locations';
    Map options = getParams(license, orgId, state);
    final response = await APIService.apiRequest(endpoint, options: options);
    List<Location> items = [];
    for (var item in response) {
      items.add(Location.fromMap(item));
    }
    return items;
  }

  // Get a location.
  static Future<Location> getLocation({
    required String id,
    String? license,
    String? orgId,
    String? state,
  }) async {
    String endpoint = '/api/metrc/locations/$id';
    Map options = getParams(license, orgId, state);
    final response = await APIService.apiRequest(endpoint, options: options);
    return Location.fromMap(response);
  }

  // Create a location.
  static Future<void> createLocation({
    required String name,
    String? locationTypeName,
    String? license,
    String? orgId,
    String? state,
  }) async {
    String endpoint = '/api/metrc/locations';
    Map data = {
      'name': name,
      'location_type_name': locationTypeName ?? 'Default Location Type',
    };
    Map options = getParams(license, orgId, state);
    return await APIService.apiRequest(endpoint, data: data, options: options);
  }

  // Update the name of a location.
  static Future<void> updateLocation({
    required String id,
    required String name,
    required String locationTypeName,
    String? license,
    String? orgId,
    String? state,
  }) async {
    String endpoint = '/api/metrc/locations/$id';
    Map data = {
      'id': id,
      'name': name,
      'location_type_name': locationTypeName,
    };
    Map options = getParams(license, orgId, state);
    return await APIService.apiRequest(endpoint, data: data, options: options);
  }

  // Delete a location.
  static Future<void> deleteLocation({
    required String id,
    String? license,
    String? orgId,
    String? state,
  }) async {
    String endpoint = '/api/metrc/locations/$id';
    Map options = getParams(license, orgId, state, delete: true);
    return await APIService.apiRequest(endpoint, options: options);
  }
}

/// Strains
class MetrcStrains {
  /// Get strains.
  static Future<List<Strain>> getStrains({
    String? license,
    String? orgId,
    String? state,
  }) async {
    String endpoint = '/api/metrc/strains';
    Map options = getParams(license, orgId, state);
    List<dynamic> response =
        await APIService.apiRequest(endpoint, options: options);
    List<Strain> items = [];
    for (var item in response) {
      items.add(Strain.fromMap(item));
    }
    return items;
  }

  /// Get a strain.
  static Future<Strain> getStrain({
    required String id,
    String? license,
    String? orgId,
    String? state,
  }) async {
    String endpoint = '/api/metrc/strain/$id';
    Map options = getParams(license, orgId, state);
    final response = await APIService.apiRequest(endpoint, options: options);
    return Strain.fromMap(response);
  }

  /// Create a strain in Metrc.
  static Future<void> createStrain({
    required String name,
    required String testingStatus,
    required double thcLevel,
    required double cbdLevel,
    required double indicaPercentage,
    required double sativaPercentage,
    String? license,
    String? orgId,
    String? state,
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
    Map options = getParams(license, orgId, state);
    await APIService.apiRequest(endpoint, data: data, options: options);
    // TODO: Get the newly created strain's ID.
    // return Strain.fromMap(data, uid);
  }

  /// Update a strain.
  static Future<Strain> updateStrain({
    required String id,
    required String name,
    required String testingStatus,
    required double thcLevel,
    required double cbdLevel,
    required double indicaPercentage,
    required double sativaPercentage,
    String? license,
    String? orgId,
    String? state,
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
    Map options = getParams(license, orgId, state);
    await APIService.apiRequest(endpoint, data: data, options: options);
    return Strain.fromMap(data);
  }

  /// Delete a strain.
  static Future<void> deleteStrain({
    required String id,
    String? license,
    String? orgId,
    String? state,
  }) async {
    String endpoint = '/api/metrc/strains/$id';
    Map options = getParams(license, orgId, state, delete: true);
    await APIService.apiRequest(endpoint, options: options);
  }
}

/// Plants
class MetrcPlants {
  /// Create a plant.
  static Future<void> createPlant({
    required Map data,
    String? license,
    String? state,
    String? orgId,
  }) async {
    String endpoint = '/api/metrc/plants';
    Map options = getParams(license, orgId, state);
    await APIService.apiRequest(endpoint,
        // TODO : Make more function like.
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
        options: options);
  }

  /// Change the growth phase of a plant
  static Future<void> changePlantGrowthPhase({
    required Map data,
    String? type,
    String? license,
    String? state,
    String? orgId,
  }) async {
    String endpoint = '/api/metrc/plants';
    Map options = getParams(license, orgId, state, action: type);
    await APIService.apiRequest(endpoint, data: data, options: options);
  }

  /// Get plants.
  static Future<List<Plant>> getPlants({
    String? license,
    String? state,
    String? orgId,
    String? type,
    String? start,
    String? end,
  }) async {
    String endpoint = '/api/metrc/plants';
    List<Map> queries = [
      {'key': 'start', 'value': start},
      {'key': 'end', 'value': end},
    ];
    Map options = getParams(license, orgId, state, queries: queries);
    var response = await APIService.apiRequest(endpoint, options: options);
    List<Plant> items = [];
    for (var item in response) {
      items.add(Plant.fromMap(item));
    }
    return items;
  }

  /// Get a strain.
  static Future<Plant> getPlant({
    required String id,
    String? license,
    String? orgId,
    String? state,
  }) async {
    String endpoint = '/api/metrc/plants/$id';
    Map options = getParams(license, orgId, state);
    final response = await APIService.apiRequest(endpoint, options: options);
    return Plant.fromMap(response);
  }

  /// Move a plant to a different room.
  static Future<void> movePlant({
    String? id,
    String? label,
    String? location,
    String? license,
    String? orgId,
    String? state,
  }) async {
    String endpoint = '/api/metrc/plants';
    Map data = {
      'actual_date': DateTime.now().toIso8601String(),
      'id': id,
      'label': label,
      'location': location,
    };
    Map options = getParams(license, orgId, state, action: 'move');
    await APIService.apiRequest(endpoint, data: data, options: options);
  }

  /// Add additives to a plant.
  static Future<void> addPlantAdditives({
    required Map data,
    String? license,
    String? orgId,
    String? state,
  }) async {
    String endpoint = '/api/metrc/plants';
    Map options = getParams(license, orgId, state, action: 'add-additives');
    await APIService.apiRequest(endpoint, data: data, options: options);
  }

  /// Manicure a plant.
  static Future<void> manicurePlant({
    required Map data,
    String? license,
    String? orgId,
    String? state,
  }) async {
    String endpoint = '/api/metrc/plants';
    Map options = getParams(license, orgId, state, action: 'manicure');
    await APIService.apiRequest(endpoint, data: data, options: options);
  }

  /// Harvest from a plant.
  static Future<void> harvestPlant({
    required Map data,
    String? license,
    String? orgId,
    String? state,
  }) async {
    String endpoint = '/api/metrc/plants';
    Map options = getParams(license, orgId, state, action: 'harvest');
    await APIService.apiRequest(endpoint, data: data, options: options);
  }

  /// Destroy a plant.
  static Future<void> destroyPlant({
    required String id,
    String? license,
    String? orgId,
    String? state,
  }) async {
    String endpoint = '/api/metrc/plants/$id';
    Map options = getParams(license, orgId, state, delete: true);
    await APIService.apiRequest(endpoint, options: options);
  }
}

/// Plant batches
class MetrcPlantBatches {
  /// Create a new plant batch.
  static Future<void> createPlantBatch({
    required Map data,
    String? license,
    String? orgId,
    String? state,
  }) async {
    String endpoint = '/api/metrc/batches';
    Map options = getParams(license, orgId, state);
    await APIService.apiRequest(endpoint, options: options);
  }

  /// Get plant batches by date.
  static Future<List<PlantBatch>> getPlantBatches({
    required String startDate,
    required String endDate,
    String? license,
    String? orgId,
    String? state,
  }) async {
    String endpoint = '/api/metrc/batches';
    Map options = {
      'params': {
        'license': license,
        'org_id': orgId,
        'state': state,
        'start': startDate,
        'end': endDate,
      },
    };
    var response = await APIService.apiRequest(endpoint, options: options);
    List<PlantBatch> items = [];
    for (var item in response) {
      items.add(PlantBatch.fromMap(item));
    }
    return items;
  }

  /// Create a package from a batch.
  static Future<void> createPackageFromBatch({
    required Map data,
    String? license,
    String? orgId,
    String? state,
  }) async {
    String endpoint = '/api/metrc/batches';
    Map options =
        getParams(license, orgId, state, action: 'create-plant-package');
    await APIService.apiRequest(endpoint, options: options);
  }

  /// Flower plants in a batch.
  static Future<void> flowerPlantsBatch({
    required String id,
    String? license,
    String? orgId,
    String? state,
  }) async {
    String endpoint = '/api/metrc/batches';
    Map options = getParams(license, orgId, state, action: 'flower');
    await APIService.apiRequest(endpoint, options: options);
  }

  /// Destroy plants in a batch.
  static Future<void> destroyPlantsBatchPlants({
    required String id,
    String? license,
    String? orgId,
    String? state,
  }) async {
    String endpoint = '/api/metrc/batches';
    Map options = getParams(license, orgId, state, action: 'destroy-plants');
    await APIService.apiRequest(endpoint, options: options);
  }

  /// Add additives.
  static Future<void> addPlantsBatchAdditives({
    required Map data,
    String? license,
    String? orgId,
    String? state,
  }) async {
    String endpoint = '/api/metrc/batches';
    Map options = getParams(license, orgId, state, action: 'add-additives');
    await APIService.apiRequest(endpoint, data: data, options: options);
  }

  /// Move batch.
  static Future<void> movePlantBatch({
    required String name,
    required String location,
    String? license,
    String? orgId,
    String? state,
  }) async {
    String endpoint = '/api/metrc/batches';
    Map data = {
      'name': name,
      'location': location,
      'move_date': DateTime.now().toIso8601String(),
    };
    Map options = getParams(license, orgId, state, action: 'move');
    await APIService.apiRequest(endpoint, data: data, options: options);
  }

  /// Split batch.
  static Future<void> splitPlantBatch({
    required String name,
    required String newName,
    required int count,
    required String location,
    required String strain,
    String? patientLicenseNumber,
    String? license,
    String? orgId,
    String? state,
  }) async {
    String endpoint = '/api/metrc/batches';
    Map data = {
      'plant_batch': name,
      'group_name': newName,
      'count': count,
      'location': location,
      'strain': strain,
      'patient_license_number': patientLicenseNumber,
      'actual_date': DateTime.now().toIso8601String(),
    };
    Map options = getParams(license, orgId, state, action: 'split');
    await APIService.apiRequest(endpoint, data: data, options: options);
  }
}

/// Harvests
class MetrcHarvests {
  /// Get harvests.
  static Future<List<PlantHarvest>> getHarvests({
    String? start,
    String? end,
    String? license,
    String? orgId,
    String? state,
  }) async {
    String endpoint = '/api/metrc/harvests';
    Map options = {
      'params': {
        'license': license,
        'org_id': orgId,
        'state': state,
        'start': start,
        'end': end,
      },
    };
    var response = await APIService.apiRequest(endpoint, options: options);
    List<PlantHarvest> items = [];
    for (var item in response) {
      items.add(PlantHarvest.fromMap(item));
    }
    return items;
  }

  /// Create a package.
  static Future<void> createPackage({
    required Map data,
    String? license,
    String? orgId,
    String? state,
  }) async {
    String endpoint = '/api/metrc/packages';
    Map options = getParams(license, orgId, state, action: 'create-packages');
    await APIService.apiRequest(endpoint, data: data, options: options);
  }

  /// Create a testing package.
  static Future<void> createTestingPackage({
    required Map data,
    String? license,
    String? orgId,
    String? state,
  }) async {
    String endpoint = '/api/metrc/packages';
    Map options =
        getParams(license, orgId, state, action: 'create-testing-packages');
    await APIService.apiRequest(endpoint, data: data, options: options);
  }

  /// Remove waste weight from a harvest.
  static Future<void> removeWaste({
    required Map data,
    String? license,
    String? orgId,
    String? state,
  }) async {
    String endpoint = '/api/metrc/harvests';
    Map options = getParams(license, orgId, state, action: 'remove-waste');
    await APIService.apiRequest(endpoint, data: data, options: options);
  }

  /// Finish a harvest.
  static Future<void> finishHarvest({
    required String id,
    String? license,
    String? orgId,
    String? state,
  }) async {
    String endpoint = '/api/metrc/harvests/$id';
    Map data = {'actual_date': DateTime.now().toIso8601String()};
    Map options = getParams(license, orgId, state, action: 'finish');
    await APIService.apiRequest(endpoint, data: data, options: options);
  }

  /// Unfinish a harvest.
  static Future<void> unfinishHarvest({
    required String id,
    String? license,
    String? orgId,
    String? state,
  }) async {
    String endpoint = '/api/metrc/harvests/$id';
    Map options = getParams(license, orgId, state, action: 'unfinish');
    await APIService.apiRequest(endpoint, options: options);
  }
}

/// Packages
class MetrcPackages {
  /// Get packages.
  static Future<List<Package>> getPackages({
    String? label,
    String? start,
    String? end,
    String? license,
    String? orgId,
    String? state,
  }) async {
    String endpoint = '/api/metrc/packages';
    if (label != null) label += '/$label';
    Map options = {
      'params': {
        'license': license,
        'org_id': orgId,
        'state': state,
        'start': start,
        'end': end,
      },
    };
    var response = await APIService.apiRequest(endpoint, options: options);
    List<Package> items = [];
    for (var item in response) {
      items.add(Package.fromMap(item));
    }
    return items;
  }

  /// Create a package from another package.
  static Future<void> createPackageFromPackage({
    required Map data,
    String? license,
    String? orgId,
    String? state,
  }) async {
    String endpoint = '/api/metrc/packages';
    Map options = getParams(license, orgId, state);
    await APIService.apiRequest(endpoint, data: data, options: options);
  }

  /// Change the item of a package.
  static Future<void> changePackageItem({
    required String label,
    required String itemName,
    String? license,
    String? orgId,
    String? state,
  }) async {
    String endpoint = '/api/metrc/packages';
    Map data = {
      'label': label,
      'item': itemName,
    };
    Map options =
        getParams(license, orgId, state, action: 'change-package-items');
    await APIService.apiRequest(endpoint, data: data, options: options);
  }

  /// Change the location of a package.
  static Future<void> changePackageLocation({
    required String packageLabel,
    required String location,
    String? license,
    String? orgId,
    String? state,
  }) async {
    String endpoint = '/api/metrc/packages';
    Map data = {
      'label': packageLabel,
      'location': location,
      'move_date': DateTime.now().toIso8601String(),
    };
    Map options = getParams(license, orgId, state, action: 'move');
    await APIService.apiRequest(endpoint, data: data, options: options);
  }

  /// Create a plant batch from a package.
  static Future<void> createPlantBatchFromPackage({
    required Map data,
    String? license,
    String? orgId,
    String? state,
  }) async {
    String endpoint = '/api/metrc/packages';
    Map options =
        getParams(license, orgId, state, action: 'create-plant-batches');
    await APIService.apiRequest(endpoint, data: data, options: options);
  }

  /// Adjust the weight of a package.
  static Future<void> adjustPackageWeight({
    required Map data,
    String? license,
    String? orgId,
    String? state,
  }) async {
    String endpoint = '/api/metrc/packages';
    Map options = getParams(license, orgId, state, action: 'adjust');
    await APIService.apiRequest(endpoint, data: data, options: options);
  }

  /// Finish a package.
  static Future<void> finishPackage({
    required String label,
    String? license,
    String? orgId,
    String? state,
  }) async {
    String endpoint = '/api/metrc/packages';
    Map options = getParams(license, orgId, state, action: 'finish');
    Map data = {
      'label': label,
      'actual_date': DateTime.now().toIso8601String(),
    };
    await APIService.apiRequest(endpoint, data: data, options: options);
  }

  /// Unfinish a package.
  static Future<void> unfinishPackage({
    required String label,
    String? license,
    String? orgId,
    String? state,
  }) async {
    String endpoint = '/api/metrc/packages';
    Map data = {'label': label};
    Map options = getParams(license, orgId, state, action: 'unfinish');
    await APIService.apiRequest(endpoint, data: data, options: options);
  }

  /// Remediate a package.
  static Future<void> remediatePackage({
    required Map data,
    String? license,
    String? orgId,
    String? state,
  }) async {
    String endpoint = '/api/metrc/packages';
    Map options = getParams(license, orgId, state, action: 'remediate');
    await APIService.apiRequest(endpoint, data: data, options: options);
  }

  /// Update the note for a package.
  static Future<void> updatePackageNote({
    required String label,
    required String note,
    String? license,
    String? orgId,
    String? state,
  }) async {
    String endpoint = '/api/metrc/packages';
    Map data = {
      'package_label': label,
      'note': note,
    };
    Map options =
        getParams(license, orgId, state, action: 'update-package-notes');
    await APIService.apiRequest(endpoint, data: data, options: options);
  }
}

/// Items
class MetrcItems {
  /// Create items.
  static Future<void> createItems({
    required Map data,
    String? license,
    String? orgId,
    String? state,
  }) async {
    String endpoint = '/api/metrc/items';
    Map options = getParams(license, orgId, state);
    await APIService.apiRequest(endpoint, data: data, options: options);
  }

  /// Get items.
  static Future<List<Item>> getItems({
    String? id,
    String? start,
    String? end,
    String? license,
    String? orgId,
    String? state,
  }) async {
    String endpoint = '/api/metrc/items';
    if (id != null) endpoint += '/$id';
    Map options = {
      'params': {
        'license': license,
        'start': start,
        'end': end,
      }
    };
    var response = await APIService.apiRequest(endpoint, options: options);
    List<Item> items = [];
    for (var item in response) {
      items.add(Item.fromMap(item));
    }
    return items;
  }

  /// Update an item.
  static Future<void> updateItem({
    required String id,
    required Map data,
    String? license,
    String? orgId,
    String? state,
  }) async {
    String endpoint = '/api/metrc/items/$id';
    Map options = getParams(license, orgId, state);
    await APIService.apiRequest(endpoint, data: data, options: options);
  }

  /// Delete an item.
  static Future<void> deleteItem({
    required String id,
    String? license,
    String? orgId,
    String? state,
  }) async {
    String endpoint = '/api/metrc/items/$id';
    Map options = getParams(license, orgId, state, delete: true);
    await APIService.apiRequest(endpoint, options: options);
  }
}

/// Transfers
class MetrcTransfers {
  /// Set up an external transfer.
  static Future<void> createExternalTransfer({
    required Map data,
    String? license,
    String? orgId,
    String? state,
  }) async {
    String endpoint = '/api/metrc/transfers';
    Map options = getParams(license, orgId, state);
    await APIService.apiRequest(endpoint, data: data, options: options);
  }

  /// Get external transfers.
  static Future<List<SalesTransaction>> getTransactions({
    String? id,
    String? type,
    String? license,
    String? orgId,
    String? state,
  }) async {
    String endpoint = '/api/metrc/transfers';
    if (id != null) endpoint += '/$id';
    Map options = {
      'params': {
        'license': license,
        'org_id': orgId,
        'state': state,
      },
      'type': type,
    };
    var response = await APIService.apiRequest(endpoint, options: options);
    List<SalesTransaction> items = [];
    for (var item in response) {
      items.add(SalesTransaction.fromMap(item));
    }
    return items;
  }

  /// Update an external transfer.
  static Future<void> updateExternalTransfer({
    required Map data,
    String? license,
    String? orgId,
    String? state,
  }) async {
    String endpoint = '/api/metrc/transfers';
    Map options = getParams(license, orgId, state, action: 'update');
    await APIService.apiRequest(endpoint, data: data, options: options);
  }

  /// Create a transfer template.
  static Future<void> createTransferTemplate({
    required Map data,
    String? license,
    String? orgId,
    String? state,
  }) async {
    String endpoint = '/api/metrc/transfers/templates';
    Map options = getParams(license, orgId, state);
    await APIService.apiRequest(endpoint, data: data, options: options);
  }

  /// Get transfer templates.
  static Future<List<dynamic>> getTransferTemplates({
    String? id,
    String? license,
    String? orgId,
    String? state,
  }) async {
    String endpoint = '/api/metrc/transactions';
    if (id != null) endpoint += '/$id';
    Map options = getParams(license, orgId, state);
    var response = await APIService.apiRequest(endpoint, options: options);
    // TODO: Use a transfer template model?
    List<Map> items = [];
    for (var item in response) {
      items.add(item);
    }
    return items;
  }

  /// Update a transfer template.
  static Future<void> updateTransferTemplate({
    required String id,
    required Map data,
    String? license,
    String? orgId,
    String? state,
  }) async {
    String endpoint = '/api/metrc/transfers/templates/$id';
    Map options = getParams(license, orgId, state, action: 'update');
    await APIService.apiRequest(endpoint, data: data, options: options);
  }

  /// Delete a transfer template.
  Future<void> deleteTransferTemplate({
    required String id,
    String? license,
    String? orgId,
    String? state,
  }) async {
    String endpoint = '/api/metrc/transfers/templates/$id';
    Map options = getParams(license, orgId, state, delete: true);
    await APIService.apiRequest(endpoint, options: options);
  }
}

/// Lab Tests
class MetrcLabTests {
  /// FIXME: Create a lab result record.

  /// FIXME: Release lab results.

  /// FIXME: Upload a COA.

  /// Get a COA by appending `id` to the URL.
  static Future<dynamic> getCOA({
    required String id,
    String? license,
    String? orgId,
    String? state,
  }) async {
    String endpoint = '/api/metrc/tests/coas/$id';
    Map options = getParams(license, orgId, state);
    var response = await APIService.apiRequest(endpoint, options: options);
    // TODO: Return a custom model.
    // return LabResult.fromMap(response);
    return response;
  }
}

/// Patients
class MetrcPatients {
  /// Get active patients.
  static Future<List<Patient>> getPatients({
    String? id,
    String? license,
    String? orgId,
    String? state,
  }) async {
    String endpoint = '/api/metrc/patients';
    if (id != null) endpoint += '/$id';
    Map options = getParams(license, orgId, state);
    final response = await APIService.apiRequest(endpoint, options: options);
    List<Patient> items = [];
    for (var item in response) {
      items.add(Patient.fromMap(item));
    }
    return items;
  }

  /// Get patient.
  static Future<Patient> getPatient({
    required String id,
    String? license,
    String? orgId,
    String? state,
  }) async {
    String endpoint = '/api/metrc/deliveries/$id';
    Map options = getParams(license, orgId, state);
    final response = await APIService.apiRequest(endpoint, options: options);
    return Patient.fromMap(response);
  }

  /// Get patient registration locations.
  static Future<List<dynamic>> getPatientLocations({
    String? license,
    String? orgId,
    String? state,
  }) async {
    String endpoint = '/api/metrc/patients/locations';
    Map options = getParams(license, orgId, state);
    var response = await APIService.apiRequest(endpoint, options: options);
    // TODO: Use caregiver model?
    List<Map> items = [];
    for (var item in response) {
      items.add(item);
    }
    return items;
  }

  /// Add a patient.
  static Future<void> addPatient({
    required Map data,
    String? license,
    String? orgId,
    String? state,
  }) async {
    String endpoint = '/api/metrc/patients';
    Map options = getParams(license, orgId, state);
    await APIService.apiRequest(endpoint, data: data, options: options);
  }

  /// Update a patient.
  static Future<void> updatePatient({
    required Map data,
    String? license,
    String? orgId,
    String? state,
  }) async {
    String endpoint = '/api/metrc/patients';
    Map options = getParams(license, orgId, state, action: 'update');
    await APIService.apiRequest(endpoint, data: data, options: options);
  }

  /// Delete a patient.
  static Future<void> deletePatient({
    required String id,
    String? license,
    String? orgId,
    String? state,
  }) async {
    String endpoint = '/api/metrc/patients/$id';
    Map options = getParams(license, orgId, state, delete: true);
    await APIService.apiRequest(endpoint, options: options);
  }
}

/// Sales
class MetrcSalesReceipts {
  /// Get sales by date or ID.
  static Future<List<SalesReceipt>> getSalesReceipts({
    String? id,
    String? start,
    String? end,
    String? license,
    String? orgId,
    String? state,
  }) async {
    String endpoint = '/api/metrc/sales';
    if (id != null) endpoint += '/$id';
    Map options = {
      'params': {
        'license': license,
        'org_id': orgId,
        'state': state,
        'end': end,
        'start': start,
      },
    };
    var response = await APIService.apiRequest(endpoint, options: options);
    List<SalesReceipt> items = [];
    for (var item in response) {
      items.add(SalesReceipt.fromMap(item));
    }
    return items;
  }

  /// Create a sales receipt for a package.
  static Future<void> createSalesReceipt({
    required Map data,
    String? license,
    String? orgId,
    String? state,
  }) async {
    String endpoint = '/api/metrc/sales';
    Map options = getParams(license, orgId, state);
    await APIService.apiRequest(endpoint, data: data, options: options);
  }

  /// Update a sales receipt.
  static Future<void> updateSalesReceipt({
    required Map data,
    String? license,
    String? orgId,
    String? state,
  }) async {
    String endpoint = '/api/metrc/sales';
    Map options = getParams(license, orgId, state, action: 'update');
    await APIService.apiRequest(endpoint, data: data, options: options);
  }

  /// Void a sales receipt.
  static Future<void> voidSalesReceipt({
    required String id,
    String? license,
    String? orgId,
    String? state,
  }) async {
    String endpoint = '/api/metrc/sales/$id';
    Map options = getParams(license, orgId, state, delete: true);
    await APIService.apiRequest(endpoint, options: options);
  }
}

/// Transactions
class MetrcSalesTransactions {
  /// Get transactions (daily statistics).
  static Future<List<SalesTransaction>> getTransactions({
    String? license,
    String? orgId,
    String? state,
    String? start,
    String? end,
  }) async {
    String endpoint = '/api/metrc/transactions';
    Map options = {
      'params': {
        'license': license,
        'org_id': orgId,
        'state': state,
        'end': end,
        'start': start,
      },
    };
    var response = await APIService.apiRequest(endpoint, options: options);
    List<SalesTransaction> items = [];
    for (var item in response) {
      items.add(SalesTransaction.fromMap(item));
    }
    return items;
  }

  /// Add transactions on a particular day.
  static Future<void> addTransaction({
    required String date,
    required Map data,
    String? license,
    String? orgId,
    String? state,
  }) async {
    String endpoint = '/api/metrc/transactions/$date';
    Map options = getParams(license, orgId, state);
    await APIService.apiRequest(endpoint, data: data, options: options);
  }

  /// Update transactions on a particular day.
  static Future<void> updateTransaction({
    required String date,
    required Map data,
    String? license,
    String? orgId,
    String? state,
  }) async {
    String endpoint = '/api/metrc/transactions/$date';
    Map options = getParams(license, orgId, state, action: 'update');
    await APIService.apiRequest(endpoint, data: data, options: options);
  }
}

/// Deliveries
class MetrcDeliveries {
  /// Get deliveries.
  static Future<List<Delivery>> getDeliveries({
    String? id,
    String? start,
    String? end,
    String? salesStart,
    String? salesEnd,
    String? type,
    String? license,
    String? orgId,
    String? state,
  }) async {
    String endpoint = '/api/metrc/deliveries';
    if (id != null) endpoint += '/$id';
    Map options = {
      'params': {
        'license': license,
        'org_id': orgId,
        'state': state,
        'end': end,
        'start': start,
        'salesStart': salesStart,
        'salesEnd': salesEnd,
        'type': type,
      },
    };
    var response = await APIService.apiRequest(endpoint, options: options);
    List<Delivery> items = [];
    for (var item in response) {
      items.add(Delivery.fromMap(item));
    }
    return items;
  }

  // Get a location.
  static Future<Delivery> getDelivery({
    required String id,
    String? license,
    String? orgId,
    String? state,
  }) async {
    String endpoint = '/api/metrc/deliveries/$id';
    Map options = getParams(license, orgId, state);
    final response = await APIService.apiRequest(endpoint, options: options);
    return Delivery.fromMap(response);
  }

  /// Create a delivery.
  static Future<void> createDelivery({
    required Map data,
    String? license,
    String? orgId,
    String? state,
  }) async {
    String endpoint = '/api/metrc/deliveries';
    Map options = getParams(license, orgId, state);
    await APIService.apiRequest(endpoint, data: data, options: options);
  }

  /// Update a delivery.
  static Future<void> updateDelivery({
    required Map data,
    String? license,
    String? orgId,
    String? state,
  }) async {
    String endpoint = '/api/metrc/deliveries';
    Map options = getParams(license, orgId, state, action: 'update');
    await APIService.apiRequest(endpoint, data: data, options: options);
  }

  /// Delete a delivery.
  static Future<void> deleteDelivery({
    required String id,
    String? license,
    String? orgId,
    String? state,
  }) async {
    String endpoint = '/api/metrc/deliveries/$id';
    Map options = getParams(license, orgId, state, delete: true);
    await APIService.apiRequest(endpoint, options: options);
  }

  /// Complete a delivery.
  static Future<void> completeDelivery({
    required Map data,
    String? license,
    String? orgId,
    String? state,
  }) async {
    String endpoint = '/api/metrc/deliveries';
    Map options = getParams(license, orgId, state, action: 'complete');
    await APIService.apiRequest(endpoint, data: data, options: options);
  }

  /// Depart a delivery.
  static Future<void> departDelivery({
    required Map data,
    String? license,
    String? orgId,
    String? state,
  }) async {
    String endpoint = '/api/metrc/deliveries';
    Map options = getParams(license, orgId, state, action: 'depart');
    await APIService.apiRequest(endpoint, data: data, options: options);
  }

  /// Restock a delivery.
  static Future<void> restockDelivery({
    required Map data,
    String? license,
    String? orgId,
    String? state,
  }) async {
    String endpoint = '/api/metrc/deliveries';
    Map options = getParams(license, orgId, state, action: 'restock');
    await APIService.apiRequest(endpoint, data: data, options: options);
  }

  /// Deliver a delivery.
  static Future<void> deliverDelivery({
    required Map data,
    String? license,
    String? orgId,
    String? state,
  }) async {
    String endpoint = '/api/metrc/deliveries';
    Map options = getParams(license, orgId, state, action: 'deliver');
    await APIService.apiRequest(endpoint, data: data, options: options);
  }

  /// End a delivery.
  static Future<void> endDelivery({
    required Map data,
    String? license,
    String? orgId,
    String? state,
  }) async {
    String endpoint = '/api/metrc/deliveries';
    Map options = getParams(license, orgId, state, action: 'end');
    await APIService.apiRequest(endpoint, data: data, options: options);
  }

  /// TODO: Get drivers and vehicles.
}

/// Types
class MetrcTypes {
  /// Get adjustment reasons.
  Future<List<dynamic>> getAdjustments({
    String? license,
    String? orgId,
    String? state,
  }) async {
    String endpoint = '/api/metrc/types/adjustments';
    Map options = getParams(license, orgId, state);
    return await APIService.apiRequest(endpoint, options: options);
  }

  /// Get batch types.
  Future<List<dynamic>> getBatchTypes({
    String? license,
    String? orgId,
    String? state,
  }) async {
    String endpoint = '/api/metrc/types/batches';
    Map options = getParams(license, orgId, state);
    return await APIService.apiRequest(endpoint, options: options);
  }

  /// Get categories.
  Future<List<dynamic>> getCategories({
    String? license,
    String? orgId,
    String? state,
  }) async {
    String endpoint = '/api/metrc/types/categories';
    Map options = getParams(license, orgId, state);
    return await APIService.apiRequest(endpoint, options: options);
  }

  /// Get customer types.
  Future<List<dynamic>> getCustomerTypes({
    String? license,
    String? orgId,
    String? state,
  }) async {
    String endpoint = '/api/metrc/types/customers';
    Map options = getParams(license, orgId, state);
    return await APIService.apiRequest(endpoint, options: options);
  }

  /// Get growth phases.
  Future<List<dynamic>> getGrowthPhases({
    String? license,
    String? orgId,
    String? state,
  }) async {
    String endpoint = '/api/metrc/types/growth-phases';
    Map options = getParams(license, orgId, state);
    return await APIService.apiRequest(endpoint, options: options);
  }

  /// Get package types.
  Future<List<dynamic>> getPackageTypes({
    String? license,
    String? orgId,
    String? state,
  }) async {
    String endpoint = '/api/metrc/types/packages';
    Map options = getParams(license, orgId, state);
    return await APIService.apiRequest(endpoint, options: options);
  }

  /// Get package statuses.
  Future<List<dynamic>> getPackageStatuses({
    String? license,
    String? orgId,
    String? state,
  }) async {
    String endpoint = '/api/metrc/types/package-statuses';
    Map options = getParams(license, orgId, state);
    return await APIService.apiRequest(endpoint, options: options);
  }

  /// Get return reasons.
  Future<List<dynamic>> getReturnReasons({
    String? license,
    String? orgId,
    String? state,
  }) async {
    String endpoint = '/api/metrc/types/return-reasons';
    Map options = getParams(license, orgId, state);
    return await APIService.apiRequest(endpoint, options: options);
  }

  /// Get test statuses.
  static Future<List<dynamic>> getTestStatuses({
    String? license,
    String? orgId,
    String? state,
  }) async {
    String endpoint = '/api/metrc/types/test-statuses';
    Map options = getParams(license, orgId, state);
    return await APIService.apiRequest(endpoint, options: options);
  }

  /// Get test types.
  Future<List<dynamic>> getTestTypes({
    String? license,
    String? orgId,
    String? state,
  }) async {
    String endpoint = '/api/metrc/types/tests';
    Map options = getParams(license, orgId, state);
    return await APIService.apiRequest(endpoint, options: options);
  }

  /// Get transfer types.
  Future<List<dynamic>> getTransferTypes({
    String? license,
    String? orgId,
    String? state,
  }) async {
    String endpoint = '/api/metrc/types/transfers';
    Map options = getParams(license, orgId, state);
    return await APIService.apiRequest(endpoint, options: options);
  }

  /// Get units of measure.
  Future<List<dynamic>> getUnitsOfMeasure({
    String? license,
    String? orgId,
    String? state,
  }) async {
    String endpoint = '/api/metrc/types/units';
    Map options = getParams(license, orgId, state);
    return await APIService.apiRequest(endpoint, options: options);
  }

  /// Get waste types.
  Future<List<dynamic>> getWasteTypes({
    String? license,
    String? orgId,
    String? state,
  }) async {
    String endpoint = '/api/metrc/types/waste';
    Map options = getParams(license, orgId, state);
    return await APIService.apiRequest(endpoint, options: options);
  }

  /// Get waste methods.
  Future<List<dynamic>> getWasteMethods({
    String? license,
    String? orgId,
    String? state,
  }) async {
    String endpoint = '/api/metrc/types/waste-methods';
    Map options = getParams(license, orgId, state);
    return await APIService.apiRequest(endpoint, options: options);
  }

  /// Get waste reasons.
  Future<List<dynamic>> getWasteReasons({
    String? license,
    String? orgId,
    String? state,
  }) async {
    String endpoint = '/api/metrc/types/waste-reasons';
    Map options = getParams(license, orgId, state);
    return await APIService.apiRequest(endpoint, options: options);
  }
}

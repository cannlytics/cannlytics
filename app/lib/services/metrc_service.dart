// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 2/26/2023
// Updated: 2/28/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Package imports:
// TODO: Create SaleReceipt, SaleTransaction, Delivery, LabTest models.
// TODO: Use models instead of Maps where possible.

// Project imports:
import 'package:cannlytics_app/models/metrc/employee.dart';
import 'package:cannlytics_app/models/metrc/facility.dart';
import 'package:cannlytics_app/models/metrc/harvest.dart';
import 'package:cannlytics_app/models/metrc/item.dart';
import 'package:cannlytics_app/models/metrc/location.dart';
import 'package:cannlytics_app/models/metrc/package.dart';
import 'package:cannlytics_app/models/metrc/patient.dart';
import 'package:cannlytics_app/models/metrc/plant.dart';
import 'package:cannlytics_app/models/metrc/plant_batch.dart';
import 'package:cannlytics_app/models/metrc/strain.dart';
import 'package:cannlytics_app/models/metrc/transporter.dart';
import 'package:cannlytics_app/services/api_service.dart';

// Base URL.
const String _host = 'https://cannlytics.com';
const String _path = '/api/metrc';

/// Metrc API service.
class Metrc {
  final MetrcFacilities facilities;
  final MetrcEmployees employees;
  final MetrcLocations locations;
  final MetrcStrains strains;
  final MetrcPlants plants;
  final MetrcPlantBatches plantBatches;
  final MetrcHarvests harvests;
  final MetrcPackages packages;
  final MetrcItems items;
  final MetrcTransfers transfers;
  final MetrcLabTests labTests;
  final MetrcPatients patients;
  final MetrcSales sales;
  final MetrcTransactions transactions;
  final MetrcDeliveries deliveries;

  Metrc()
      : facilities = MetrcFacilities(),
        employees = MetrcEmployees(),
        locations = MetrcLocations(),
        strains = MetrcStrains(),
        plants = MetrcPlants(),
        plantBatches = MetrcPlantBatches(),
        harvests = MetrcHarvests(),
        packages = MetrcPackages(),
        items = MetrcItems(),
        transfers = MetrcTransfers(),
        labTests = MetrcLabTests(),
        patients = MetrcPatients(),
        sales = MetrcSales(),
        transactions = MetrcTransactions(),
        deliveries = MetrcDeliveries();
}

/// Facilities
class MetrcFacilities {
  /// Get facilities.
  static Future<List<Facility>> getFacilities() async {
    String endpoint = '$_host$_path/facilities';
    List<Facility> items = [];
    List<dynamic> response = await APIService.authRequest(endpoint);
    for (var item in response) {
      items.add(Facility.fromMap(item, item['id']));
    }
    return items;
  }
}

/// Employees
class MetrcEmployees {
  /// Get employees.
  static Future<List<Employee>> getEmployees(String licenseNumber) async {
    String endpoint = '$_host$_path/employees';
    Map params = {'license': licenseNumber};
    List<Employee> items = [];
    List<dynamic> response = await APIService.authRequest(
      endpoint,
      options: {'params': params},
    );
    for (var item in response) {
      items.add(Employee.fromMap(item, item['id']));
    }
    return items;
  }
}

/// Locations
class MetrcLocations {
  // Get location types.
  static Future<List> getLocationTypes(String licenseNumber) async {
    String endpoint = '$_host$_path/types/locations';
    return await APIService.authRequest(
      endpoint,
      options: {
        'params': {'license': licenseNumber}
      },
    );
  }

  // Create a location.
  static Future<void> createLocation(
    String licenseNumber,
    String name,
    String locationType,
  ) async {
    String endpoint = '$_host$_path/locations';
    Map data = {
      'name': name,
      'location_type': locationType,
    };
    return await APIService.authRequest(
      endpoint,
      data: data,
      options: {
        'params': {'license': licenseNumber}
      },
    );
  }

  // Get a location.
  static Future<void> getLocation(String licenseNumber, String id) async {
    String endpoint = '$_host$_path/locations/$id';
    return await APIService.authRequest(
      endpoint,
      options: {
        'params': {'license': licenseNumber}
      },
    );
  }

  // Update the name of a location.
  static Future<void> updateLocationName(
    String licenseNumber,
    String id,
    String name,
    String locationTypeName,
  ) async {
    String endpoint = '$_host$_path/locations/$id';
    Map data = {
      'id': id,
      'name': name,
      'location_type_name': locationTypeName,
    };
    return await APIService.authRequest(
      endpoint,
      data: data,
      options: {
        'params': {'license': licenseNumber}
      },
    );
  }

  // Delete a location.
  static Future<void> deleteLocation(String licenseNumber, String id) async {
    String endpoint = '$_host$_path/locations/$id';
    return await APIService.authRequest(
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
    String endpoint = '$_host$_path/strains';
    await APIService.authRequest(
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
    String endpoint = '$_host$_path/strains';
    List<Strain> items = [];
    List<dynamic> response = await APIService.authRequest(
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
    String endpoint = '$_host$_path/strains';
    await APIService.authRequest(
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
    String endpoint = '$_host$_path/strains/$id';
    await APIService.authRequest(
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
    String endpoint = '$_host$_path/plants';
    await APIService.authRequest(
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
    String endpoint = '$_host$_path/plants';
    await APIService.authRequest(
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
    String endpoint = '$_host$_path/plants';
    var response = await APIService.authRequest(
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
    String endpoint = '$_host$_path/plants';
    await APIService.authRequest(
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
    String endpoint = '$_host$_path/plants';
    await APIService.authRequest(
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
    String endpoint = '$_host$_path/plants';
    await APIService.authRequest(
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
    String endpoint = '$_host$_path/plants';
    await APIService.authRequest(
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
    String endpoint = '$_host$_path/plants/$id';
    await APIService.authRequest(
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
    String endpoint = '$_host$_path/batches';
    await APIService.authRequest(endpoint, data: data, options: {
      'params': {'license': licenseNumber},
    });
  }

  /// Get plant batches by date.
  static Future<List<dynamic>> getPlantBatches(
    String licenseNumber, {
    required String startDate,
    required String endDate,
  }) async {
    String endpoint = '$_host$_path/batches';
    var response = await APIService.authRequest(endpoint, options: {
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
    String endpoint = '$_host$_path/packages/v1/packages/createfromplantbatch';
    await APIService.authRequest(endpoint, data: data, options: {
      'params': {'license': licenseNumber},
    });
  }

  /// Flower plants in a batch.
  static Future<void> flowerPlantsBatch(
    String licenseNumber, {
    required String id,
  }) async {
    String endpoint = '$_host$_path/batches';
    await APIService.authRequest(endpoint, options: {
      'params': {'license': licenseNumber},
      'action': 'flower',
    });
  }

  /// Destroy plants in a batch.
  static Future<void> destroyPlantsBatchPlants(
    String licenseNumber, {
    required String id,
  }) async {
    String endpoint = '$_host$_path/batches';
    await APIService.authRequest(endpoint, options: {
      'params': {'license': licenseNumber},
      'action': 'destroy-plants',
    });
  }

  /// Add additives.
  static Future<void> addPlantsBatchAdditives(
    String licenseNumber,
    Map data,
  ) async {
    String endpoint = '$_host$_path/batches';
    await APIService.authRequest(
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
    String endpoint = '$_host$_path/batches';
    await APIService.authRequest(
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
    String endpoint = '$_host$_path/batches';
    await APIService.authRequest(
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
    String endpoint = '$_host$_path/harvests';
    var response = await APIService.authRequest(
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
    String endpoint = '$_host$_path/packages';
    await APIService.authRequest(
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
    String endpoint = '$_host$_path/packages';
    await APIService.authRequest(
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
    String endpoint = '$_host$_path/harvests';
    await APIService.authRequest(
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
    String endpoint = '$_host$_path/harvests';
    await APIService.authRequest(
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
    String endpoint = '$_host$_path/harvests';
    await APIService.authRequest(
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
    String endpoint = '$_host$_path/packages';
    if (label != null) label += '/$label';
    var response = await APIService.authRequest(
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
    String endpoint = '$_host$_path/packages';
    await APIService.authRequest(
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
    String endpoint = '$_host$_path/packages';
    await APIService.authRequest(
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
    String endpoint = '$_host$_path/packages';
    await APIService.authRequest(
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
    String endpoint = '$_host$_path/packages';
    await APIService.authRequest(
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
    String endpoint = '$_host$_path/packages';
    await APIService.authRequest(
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
    String endpoint = '$_host$_path/packages';
    await APIService.authRequest(
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
    String endpoint = '$_host$_path/packages';
    await APIService.authRequest(
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
    String endpoint = '$_host$_path/packages';
    await APIService.authRequest(
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
    String endpoint = '$_host$_path/packages';
    await APIService.authRequest(
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
    String endpoint = '$_host$_path/items';
    await APIService.authRequest(
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
    String endpoint = '$_host$_path/items';
    if (id != null) endpoint += '/$id';
    var response = await APIService.authRequest(
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
    String endpoint = '$_host$_path/items/$id';
    await APIService.authRequest(
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
    String endpoint = '$_host$_path/items/$id';
    await APIService.authRequest(
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
    String endpoint = '$_host$_path/transfers';
    await APIService.authRequest(
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
    String endpoint = '$_host$_path/transfers';
    if (id != null) endpoint += '/$id';
    var response = await APIService.authRequest(
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
    String endpoint = '$_host$_path/transfers';
    await APIService.authRequest(
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
    String endpoint = '$_host$_path/transfers/templates';
    await APIService.authRequest(
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
    String endpoint = '$_host$_path/transactions';
    if (id != null) endpoint += '/$id';
    var response = await APIService.authRequest(
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
    String endpoint = '$_host$_path/transfers/templates/$id';
    await APIService.authRequest(
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
    String endpoint = '$_host$_path/transfers/templates/$id';
    await APIService.authRequest(
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
    String endpoint = '$_host$_path/tests/coas/$id';
    var response = await APIService.authRequest(
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
    String endpoint = '$_host$_path/patients';
    if (id != null) endpoint += '/$id';
    var response = await APIService.authRequest(
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
    String endpoint = '$_host$_path/patients/locations';
    var response = await APIService.authRequest(
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
    String endpoint = '$_host$_path/patients';
    await APIService.authRequest(
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
    String endpoint = '$_host$_path/patients';
    await APIService.authRequest(
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
    String endpoint = '$_host$_path/patients/$id';
    await APIService.authRequest(
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
    String endpoint = '$_host$_path/sales';
    await APIService.authRequest(
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
    String endpoint = '$_host$_path/sales';
    if (id != null) endpoint += '/$id';
    var response = await APIService.authRequest(
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
    String endpoint = '$_host$_path/sales';
    await APIService.authRequest(
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
    String endpoint = '$_host$_path/sales/$id';
    await APIService.authRequest(
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
    String endpoint = '$_host$_path/transactions';
    var response = await APIService.authRequest(
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
    String endpoint = '$_host$_path/transactions/$date';
    await APIService.authRequest(
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
    String endpoint = '$_host$_path/transactions/$date';
    await APIService.authRequest(
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
    String endpoint = '$_host$_path/deliveries';
    if (id != null) endpoint += '/$id';
    var response = await APIService.authRequest(
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
    String endpoint = '$_host$_path/deliveries';
    await APIService.authRequest(
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
    String endpoint = '$_host$_path/deliveries';
    await APIService.authRequest(
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
    String endpoint = '$_host$_path/deliveries/$id';
    await APIService.authRequest(
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
    String endpoint = '$_host$_path/deliveries';
    await APIService.authRequest(
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
    String endpoint = '$_host$_path/deliveries';
    await APIService.authRequest(
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
    String endpoint = '$_host$_path/deliveries';
    await APIService.authRequest(
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
    String endpoint = '$_host$_path/deliveries';
    await APIService.authRequest(
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
    String endpoint = '$_host$_path/deliveries';
    await APIService.authRequest(
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
    String endpoint = '$_host$_path/types/adjustments';
    return await APIService.authRequest(endpoint);
  }

  /// Get batch types.
  Future<List<dynamic>> getBatchTypes() async {
    String endpoint = '$_host$_path/types/batches';
    return await APIService.authRequest(endpoint);
  }

  /// Get categories.
  Future<List<dynamic>> getCategories() async {
    String endpoint = '$_host$_path/types/categories';
    return await APIService.authRequest(endpoint);
  }

  /// Get customer types.
  Future<List<dynamic>> getCustomerTypes() async {
    String endpoint = '$_host$_path/types/customers';
    return await APIService.authRequest(endpoint);
  }

  /// Get growth phases.
  Future<List<dynamic>> getGrowthPhases() async {
    String endpoint = '$_host$_path/types/growth-phases';
    return await APIService.authRequest(endpoint);
  }

  /// Get location types.
  Future<List<dynamic>> getLocationTypes() async {
    String endpoint = '$_host$_path/types/locations';
    return await APIService.authRequest(endpoint);
  }

  /// Get package types.
  Future<List<dynamic>> getPackageTypes() async {
    String endpoint = '$_host$_path/types/packages';
    return await APIService.authRequest(endpoint);
  }

  /// Get package statuses.
  Future<List<dynamic>> getPackageStatuses() async {
    String endpoint = '$_host$_path/types/package-statuses';
    return await APIService.authRequest(endpoint);
  }

  /// Get return reasons.
  Future<List<dynamic>> getReturnReasons() async {
    String endpoint = '$_host$_path/types/return-reasons';
    return await APIService.authRequest(endpoint);
  }

  /// Get test statuses.
  Future<List<dynamic>> getTestStatuses() async {
    String endpoint = '$_host$_path/types/test-statuses';
    return await APIService.authRequest(endpoint);
  }

  /// Get test types.
  Future<List<dynamic>> getTestTypes() async {
    String endpoint = '$_host$_path/types/tests';
    return await APIService.authRequest(endpoint);
  }

  /// Get transfer types.
  Future<List<dynamic>> getTransferTypes() async {
    String endpoint = '$_host$_path/types/transfers';
    return await APIService.authRequest(endpoint);
  }

  /// Get units of measure.
  Future<List<dynamic>> getUnitsOfMeasure() async {
    String endpoint = '$_host$_path/types/units';
    return await APIService.authRequest(endpoint);
  }

  /// Get waste types.
  Future<List<dynamic>> getWasteTypes() async {
    String endpoint = '$_host$_path/types/waste';
    return await APIService.authRequest(endpoint);
  }

  /// Get waste methods.
  Future<List<dynamic>> getWasteMethods() async {
    String endpoint = '$_host$_path/types/waste-methods';
    return await APIService.authRequest(endpoint);
  }

  /// Get waste reasons.
  Future<List<dynamic>> getWasteReasons() async {
    String endpoint = '$_host$_path/types/waste-reasons';
    return await APIService.authRequest(endpoint);
  }
}

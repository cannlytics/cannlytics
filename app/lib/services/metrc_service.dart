// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 2/26/2023
// Updated: 2/27/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Dart imports:
import 'dart:convert';

// Package imports:
import 'package:cannlytics_app/models/metrc/employee.dart';
import 'package:cannlytics_app/models/metrc/facility.dart';
import 'package:cannlytics_app/services/api_service.dart';
import 'package:http/http.dart' as http;

// Base URL.
const String _host = 'https://cannlytics.com';
const String _path = '/api/metrc';
const String _baseUrl = 'https://cannlytics.com/api/metrc';

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
  Future<List<Facility>> getFacilities() async {
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
  Future<List<Employee>> getEmployees(String licenseNumber) async {
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
  Future<List> getLocationTypes(String licenseNumber) async {
    String endpoint = '$_host$_path/types/locations';
    return await APIService.authRequest(
      endpoint,
      options: {
        'params': {'license': licenseNumber}
      },
    );
  }

  // Create a location.
  Future<void> createLocation(
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
  Future<void> getLocation(String licenseNumber, String id) async {
    String endpoint = '$_host$_path/locations/$id';
    return await APIService.authRequest(
      endpoint,
      options: {
        'params': {'license': licenseNumber}
      },
    );
  }

  // Update the name of a location.
  Future<void> updateLocationName(
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
  Future<void> deleteLocation(String licenseNumber, String id) async {
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
  Future<void> createStrain({
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

    // FIXME: Re-write with APIService.
    const url = '$_baseUrl/metrc/strains';
    final String _authToken = await APIService.getUserToken();
    final headers = <String, String>{'Authorization': 'Basic $_authToken'};
    final response = await http.post(
      Uri.parse(url),
      headers: headers,
      body: json.encode(data),
    );
    if (response.statusCode != 201) {
      throw Exception('Failed to create strain.');
    }
  }

  /// Get strains.
  Future<List<Map<String, dynamic>>> getStrains() async {
    // FIXME: Re-write with APIService.
    final url = '$_baseUrl/metrc/strains';
    final String _authToken = await APIService.getUserToken();
    final headers = <String, String>{'Authorization': 'Basic $_authToken'};
    final response = await http.get(Uri.parse(url), headers: headers);
    if (response.statusCode != 200) {
      throw Exception('Failed to get strains.');
    }
    final data = json.decode(response.body);
    return List<Map<String, dynamic>>.from(data['data']);
  }

  /// Update a strain.
  Future<void> updateStrain({
    required String id,
    required String name,
    required String testingStatus,
    required double thcLevel,
    required double cbdLevel,
    required double indicaPercentage,
    required double sativaPercentage,
  }) async {
    // FIXME: Re-write with APIService.
    final data = <String, dynamic>{
      'id': id,
      'name': name,
      'testing_status': testingStatus,
      'thc_level': thcLevel,
      'cbd_level': cbdLevel,
      'indica_percentage': indicaPercentage,
      'sativa_percentage': sativaPercentage,
    };

    final url = '$_baseUrl/metrc/strains';
    final String _authToken = await APIService.getUserToken();
    final headers = <String, String>{'Authorization': 'Basic $_authToken'};
    final response = await http.post(Uri.parse(url),
        headers: headers, body: json.encode(data));
    if (response.statusCode != 200) {
      throw Exception('Failed to update strain.');
    }
  }

  /// Delete a strain.
  Future<void> deleteStrain({required String id}) async {
    // FIXME: Re-write with APIService.
    final url = '$_baseUrl/metrc/strains/$id';
    final String _authToken = await APIService.getUserToken();
    final headers = <String, String>{'Authorization': 'Basic $_authToken'};

    final response = await http.delete(Uri.parse(url), headers: headers);
    if (response.statusCode != 200) {
      throw Exception('Failed to delete strain.');
    }
  }
}

/// Plants
class MetrcPlants {
  /// Create a plant.

  /// Get plants by date.

  /// Get growth phases.
}

/// Plant batches
class MetrcPlantBatches {}

/// Harvests
class MetrcHarvests {}

/// Packages
class MetrcPackages {}

/// Items
class MetrcItems {}

/// Transfers
class MetrcTransfers {}

/// Lab Tests
class MetrcLabTests {}

/// Patients
class MetrcPatients {}

/// Sales
class MetrcSales {}

/// Transactions
class MetrcTransactions {}

/// Deliveries
class MetrcDeliveries {}

/// Types
class MetrcTypes {
// Get adjustment reasons.

// Get batch types.

// Get categories.

// Get customer types.

// Get location types.

// Get package types.

// Get package statuses.

// Get return reasons.

// Get test statuses.

// Get test types.

// Get transfer types.

// Get units of measure.

// Get waste types.

// Get waste methods.

// Get waste reasons.
}

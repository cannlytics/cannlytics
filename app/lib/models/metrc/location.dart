// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 2/27/2023
// Updated: 3/7/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Project imports:
import 'package:cannlytics_app/services/metrc_service.dart';

typedef LocationId = String;

/// Model representing a location.
class Location {
  // Initialization.
  const Location({
    required this.id,
    this.name,
    this.locationTypeId,
    this.locationTypeName,
    this.forPlantBatches,
    this.forPlants,
    this.forHarvests,
    this.forPackages,
  });

  // Properties.
  final LocationId id;
  final String? name;
  final String? locationTypeId;
  final String? locationTypeName;
  final bool? forPlantBatches;
  final bool? forPlants;
  final bool? forHarvests;
  final bool? forPackages;

  // Create model.
  factory Location.fromMap(Map<dynamic, dynamic> data) {
    print('id: ${data['id']}');
    print('name: ${data['name']}');
    print('location_type_name: ${data['location_type_name']}');
    return Location(
      id: data['id'].toString(),
      name: data['name'] ?? '',
      locationTypeId: data['location_type_id'].toString(),
      locationTypeName: data['location_type_name'] ?? '',
      forPlantBatches: data['for_plant_batches'] ?? false,
      forPlants: data['for_plants'] ?? false,
      forHarvests: data['for_harvests'] ?? false,
      forPackages: data['for_packages'] ?? false,
    );
  }

  // Create JSON.
  Map<String, dynamic> toMap() {
    return <String, dynamic>{
      'id': id,
      'name': name,
      'location_type_id': locationTypeId,
      'location_type_name': locationTypeName,
      'for_plant_batches': forPlantBatches,
      'for_plants': forPlants,
      'for_harvests': forHarvests,
      'for_packages': forPackages,
    };
  }

  // Create Location.
  Future<void> create() async {
    // Call an API or database to create a new location.
    // await MetrcService.createLocation(this.toMap());
  }

  // Update Location.
  Future<void> update() async {
    // Call an API or database to update the existing location.
    // await MetrcService.updateLocation(this.id, this.toMap());
  }

  // Delete Location.
  Future<void> delete() async {
    // Call an API or database to delete the existing location.
    // await MetrcService.deleteLocation(this.id);
  }
}

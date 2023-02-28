// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 2/27/2023
// Updated: 2/27/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

import 'package:cannlytics_app/services/metrc_service.dart';

typedef LocationId = int;

/// Model representing a location.
class Location {
  // Initialization.
  const Location({
    required this.id,
    required this.name,
    required this.locationTypeId,
    required this.locationTypeName,
    required this.forPlantBatches,
    required this.forPlants,
    required this.forHarvests,
    required this.forPackages,
  });

  // Properties.
  final LocationId id;
  final String name;
  final int locationTypeId;
  final String locationTypeName;
  final bool forPlantBatches;
  final bool forPlants;
  final bool forHarvests;
  final bool forPackages;

  // Create model.
  factory Location.fromMap(Map<String, dynamic> data) {
    return Location(
      id: data['id'] as int,
      name: data['name'] as String,
      locationTypeId: data['location_type_id'] as int,
      locationTypeName: data['location_type_name'] as String,
      forPlantBatches: data['for_plant_batches'] as bool,
      forPlants: data['for_plants'] as bool,
      forHarvests: data['for_harvests'] as bool,
      forPackages: data['for_packages'] as bool,
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

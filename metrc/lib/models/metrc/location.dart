// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 2/27/2023
// Updated: 3/11/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

typedef LocationId = String;

/// Model representing a location.
class Location {
  // Initialization.
  const Location({
    required this.id,
    required this.name,
    this.locationTypeId,
    this.locationTypeName,
    this.forPlantBatches,
    this.forPlants,
    this.forHarvests,
    this.forPackages,
  });

  // Properties.
  final LocationId id;
  final String name;
  final String? locationTypeId;
  final String? locationTypeName;
  final bool? forPlantBatches;
  final bool? forPlants;
  final bool? forHarvests;
  final bool? forPackages;

  // Create model.
  factory Location.fromMap(Map<dynamic, dynamic> data) {
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

  // // Create location in Metrc.
  // Future<void> create(String? licenseNumber) async {
  //   await MetrcLocations.createLocation(
  //     name: this.name,
  //     license: licenseNumber,
  //     locationType: this.locationTypeName,
  //   );
  // }

  // // Update location in Metrc.
  // Future<void> update(String? licenseNumber) async {
  //   await MetrcLocations.updateLocationName(
  //     id: this.id,
  //     name: this.name,
  //     locationTypeName: this.locationTypeName ?? 'Default Location',
  //     license: licenseNumber,
  //   );
  // }

  // // Delete location from Metrc.
  // Future<void> delete(String? licenseNumber) async {
  //   await MetrcLocations.deleteLocation(
  //     id: this.id,
  //     license: licenseNumber,
  //   );
  // }
}

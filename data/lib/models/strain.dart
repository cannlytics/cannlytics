// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 2/25/2023
// Updated: 5/14/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

typedef StrainId = String;

/// Model representing a strain of cannabis.
class Strain {
  // Initialization.
  const Strain({
    required this.id,
    required this.name,
    this.testingStatus,
    this.thcLevel,
    this.cbdLevel,
    this.indicaPercentage,
    this.sativaPercentage,
  });

  // Properties.
  final StrainId id;
  final String name;
  final String? testingStatus;
  final double? thcLevel;
  final double? cbdLevel;
  final double? indicaPercentage;
  final double? sativaPercentage;
  // alias
  // description
  // origin
  // breeder
  // feminized
  // autoflowering
  // avg_flowering_time
  // strain_url
  // avg_yield_indoor
  // avg_yield_outdoor
  // avg_height_indoor
  // avg_height_outdoor
  // location (indoor, outdoor, greenhouse)
  // chemotype (type 1, type 2, type 3)
  // - NOT CBD RICH (< 2% CBD || < approx. 1:8 CBD:THC)
  // - CBD < THC (max. 2:3 CBD:THC)
  // - CBD ≈ THC (min. 2:3 CBD:THC - max. 3:2 CBD:THC)
  // - CBD > THC (min. 3:2 CBD:THC)
  // - CBD ONLY (< 2% THC)
  // lab_results (array of lab results)
  // images (array of images)
  // genealogy (array of parent strains)
  // crossbreeds (array of children)
  // reviews (array of reviews)
  // sources (array of data sources)

  // Create model.
  factory Strain.fromMap(Map<String, dynamic> data) {
    return Strain(
      id: data['id'].toString(),
      name: data['name'] ?? '',
      testingStatus: data['testing_status'],
      thcLevel: data['thc_level'],
      cbdLevel: data['cbd_level'],
      indicaPercentage: data['indica_percentage'],
      sativaPercentage: data['sativa_percentage'],
    );
  }

  // Create JSON.
  Map<String, dynamic> toMap() {
    return <String, dynamic>{
      'id': id,
      'name': name,
      'testing_status': testingStatus,
      'thc_level': thcLevel,
      'cbd_level': cbdLevel,
      'indica_percentage': indicaPercentage,
      'sativa_percentage': sativaPercentage,
    };
  }
}

// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 2/25/2023
// Updated: 6/28/2023
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
  // 'imageUrl': imageUrl,
//   Yield	The average yield of the strain when grown.
// Flowering Time	The average time it takes for the strain to flower.
// Plant Height	The average height of the plant.
// Difficulty Level	The difficulty level to grow the strain (Easy, Moderate, Difficult).
// Awards	Any awards or recognitions the strain has received.
// Availability	Where the strain is available (dispensaries, online, etc.).
// Price	The average price of the strain.
// number of breeders
// ID	A unique identifier for the strain.
// Name	The name of the strain.
// Type	The type of the strain (Indica, Sativa, Hybrid).
// Breeder	The breeder or company that developed the strain.
// Lineage	The genetic lineage of the strain.
// Flavor Profile	The flavor profile of the strain (Earthy, Sweet, Citrus, etc.).
// Effect Profile	The effect profile of the strain (Euphoric, Relaxing, Uplifted, etc.).
// THC Percentage	The percentage of THC in the strain.
// CBD Percentage	The percentage of CBD in the strain.
// Terpene Profile	The terpene profile of the strain.
// Description	A description of the strain, including its appearance, aroma, flavor, and effects.
// Image URL	A URL for an image of the strain.
// Medical Uses	Medical conditions that the strain is commonly used to treat.
// Grow Information	Information about how to grow the strain.
// User Reviews	Reviews from users about the strain.
// Average Rating	The average rating of the strain based on user reviews.
// Flowering Time	The time it takes for the strain to flower when grown.
// Yield	The amount of product that can be expected from the strain when grown.
// Difficulty Level	The difficulty level of growing the strain.
// Plant Height	The average height of the plant when grown.
// Plant Type	The type of plant (auto-flowering, feminized, regular).
// Seed Availability	Whether seeds are available and where.
// Climate	The ideal climate for growing the strain.
// Indoor/Outdoor	Whether the strain is best grown indoors or outdoors.
// Harvest Month	The best month to harvest the strain.
// Soil Type	The best type of soil for growing the strain.
// Nutrient Requirements	The nutrient requirements of the strain.
// Lighting Requirements	The lighting requirements of the strain.
// Watering Schedule	The recommended watering schedule for the strain.
// Pest Resistance	The strain's resistance to common pests.
// Disease Resistance	The strain's resistance to common diseases.
// Mold Resistance	The strain's resistance to mold.
// Flower Appearance	The appearance of the strain's flowers.
// Leaf Appearance	The appearance of the strain's leaves.
// Aroma	The aroma of the strain.
// Parent Strains	The parent strains of
// Child Strains	Any strains that have been bred using this strain as a parent.
// Similar Strains	Strains that are similar in effects, flavor, or genetics.

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

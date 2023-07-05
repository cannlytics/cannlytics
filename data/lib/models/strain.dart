// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 2/25/2023
// Updated: 7/2/2023
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
    this.imageUrl,
    this.images,
    this.comments,
    this.totalFavorites = 0,
  });

  // Properties.
  final StrainId id;
  final String name;
  final String? testingStatus;
  final double? thcLevel;
  final double? cbdLevel;
  final double? indicaPercentage;
  final double? sativaPercentage;
  final String? imageUrl;
  final List<dynamic>? images;
  final List<dynamic>? comments;
  final int totalFavorites;

  // Create model.
  factory Strain.fromMap(Map<dynamic, dynamic> data) {
    return Strain(
      id: data['id'] != null ? data['id'].toString() : '',
      name: data['strain_name'] ?? data['name'] ?? '',
      testingStatus: data['testing_status'],
      thcLevel: data['thc_level'],
      cbdLevel: data['cbd_level'],
      indicaPercentage: data['indica_percentage'],
      sativaPercentage: data['sativa_percentage'],
      imageUrl: data['image_url'],
      images: data['images'] ?? [],
      comments: data['comments'] ?? [],
      totalFavorites: data['total_favorites'] ?? 0,
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
      'image_url': imageUrl,
      'images': images,
      'comments': comments,
      'total_favorites': totalFavorites,
    };
  }
}

// Ideas for fields:
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
  // strain_art_url
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
// Aroma	The aroma profile of the strain.
// Color	The color of the strain's buds.
// Taste	The taste of the strain when smoked or vaporized.
// Parent Strains	The parent strains of
// Child Strains	Any strains that have been bred using this strain as a parent.
// Similar Strains	Strains that are similar in effects, flavor, or genetics.
// Difficulty Level	The difficulty level of growing the strain.
// Plant Height	The average height of the plant when grown.
// Plant Width	The average width of the plant when grown.
// Seed Availability	Whether seeds of the strain are available and where to buy them.
// Clone Availability	Whether clones of the strain are available and where to buy them.
// Phenotypes	Different phenotypes of the strain.
// Genotype	The genotype of the strain.
// Trichome Density	The density of trichomes on the strain's buds.
// Bud Density	The density of the strain's buds.
// Leaf-to-Bud Ratio	The ratio of leaves to buds on the plant.
// CBN Percentage	The percentage of CBN in the strain.
// CBG Percentage	The percentage of CBG in the strain.
// CBC Percentage	The percentage of CBC in the strain.
// THCV Percentage	The percentage of THCV in the strain.
// CBDV Percentage	The percentage of CBDV in the strain.
// CBGV Percentage	The percentage of CBGV in the strain.
// CBCV Percentage	The percentage of CBCV in the strain.
// CBL Percentage	The percentage of CBL in the strain.
// CBT Percentage	The percentage of CBT in the strain.
// CBE Percentage	The percentage of CBE in the strain.
// CBND Percentage	The percentage of CBND in the strain.
// CBF Percentage	The percentage of CBF in the strain.
// Terpinolene Percentage	The percentage of Terpinolene in the strain.
// Myrcene Percentage	The percentage of Myrcene in the strain.
// Limonene Percentage	The percentage of Limonene in the strain.
// Beta-Caryophyllene Percentage	The percentage of Beta-Caryophyllene in the strain.
// Linalool Percentage	The percentage of Linalool in the strain.
// Humulene Percentage	The percentage of Humulene in the strain.
// Ocimene Percentage	The percentage of Ocimene in the strain.
// Alpha-Pinene Percentage	The percentage of Alpha-Pinene in the strain.
// Beta-Pinene Percentage	The percentage of Beta-Pinene in the strain.
// Eucalyptol Percentage	The percentage of Eucalyptol in the strain.
// Camphene Percentage	The percentage of Camphene in the strain.
// Terpinene Percentage	The percentage of Terpinene in the strain.
// Phellandrene Percentage	The percentage of Phellandrene in the strain.
// Carene Percentage	The percentage of Carene in the strain.
// Sabinene Percentage	The percentage of Sabinene in the strain.
// Nerolidol Percentage	The percentage of Nerolidol in the strain.
// Caryophyllene Oxide Percentage	The percentage of Caryophyllene Oxide in the strain.
// Bisabolol Percentage	The percentage of Bisabolol in the strain.
// Pulegone Percentage	The percentage of Pulegone in the strain.
// Guaiol Percentage	The percentage of Guaiol in the strain.
// Isopulegol Percentage	The percentage of Isopulegol in the strain.
// Geraniol Percentage	The percentage of Geraniol in the strain.
// Borneol Percentage	The percentage of Borneol in the strain.
// Terpineol Percentage	The percentage of Terpineol in the strain.
// Valencene Percentage	The percentage of Valencene in the strain.
// Sesquiterpene Percentage	The percentage of Sesquiterpene in the strain.
// Monoterpene Percentage	The percentage of Monoterpene in the strain.
// Bibliographic References	Any bibliographic references related to the plant.
// Patent Information	Any patents related to the plant.
// First Cultivation	The first cultivation of the strain.
// Folklore	Any folklore associated with the strain.
// Etymology	The etymology of the strain's name.

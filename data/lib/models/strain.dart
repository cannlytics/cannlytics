// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 2/25/2023
// Updated: 7/14/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

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
    this.favorite,
    this.description,
    this.imageCaption,
    this.aliases,
    this.origin,
    this.breeder,
    this.chemotype,
    this.firstCultivation,
    this.folklore,
    this.etymology,
    this.seedAvailability,
    this.firstTestedAt,
    this.firstObservedBy,
    this.firstSoldBy,
    this.firstSoldAt,
    this.history,
    this.references,
    this.awards,
    this.avgPricePerGram,
    this.avgTotalThc,
    this.avgTotalCbd,
    this.avgTotalCannabinoids,
    this.avgCbg,
    this.avgCbga,
    this.avgThca,
    this.avgDelta9Thc,
    this.avgThcv,
    this.avgBetaPinene,
    this.avgDLimonene,
    this.avgMyrcene,
    this.avgHumulene,
    this.avgBetaCaryophyllene,
    this.avgTerpinene,
    this.avgLinalool,
    this.avgOcimene,
    this.avgNerolidol,
    this.alphaPinenePercentage,
    this.eucalyptolPercentage,
    this.camphenePercentage,
    this.phellandrenePercentage,
    this.carenePercentage,
    this.sabinenePercentage,
    this.caryophylleneOxidePercentage,
    this.bisabololPercentage,
    this.pulegonePercentage,
    this.guaiolPercentage,
    this.isopulegolPercentage,
    this.geraniolPercentage,
    this.borneolPercentage,
    this.valencenePercentage,
  });

  // Properties.
  final String id;
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
  final bool? favorite;
  final String? description;
  final String? imageCaption;
  final List<String>? aliases;
  final String? origin;
  final String? breeder;
  final String? chemotype;
  final String? firstCultivation;
  final String? folklore;
  final String? etymology;
  final String? seedAvailability;
  final String? firstTestedAt;
  final String? firstObservedBy;
  final String? firstSoldBy;
  final String? firstSoldAt;
  final String? history;
  final List<String>? references;
  final List<String>? awards;
  final double? avgPricePerGram;
  final double? avgTotalThc;
  final double? avgTotalCbd;
  final double? avgTotalCannabinoids;
  final double? avgCbg;
  final double? avgCbga;
  final double? avgThca;
  final double? avgDelta9Thc;
  final double? avgThcv;
  final double? avgBetaPinene;
  final double? avgDLimonene;
  final double? avgMyrcene;
  final double? avgHumulene;
  final double? avgBetaCaryophyllene;
  final double? avgTerpinene;
  final double? avgLinalool;
  final double? avgOcimene;
  final double? avgNerolidol;
  final double? alphaPinenePercentage;
  final double? eucalyptolPercentage;
  final double? camphenePercentage;
  final double? phellandrenePercentage;
  final double? carenePercentage;
  final double? sabinenePercentage;
  final double? caryophylleneOxidePercentage;
  final double? bisabololPercentage;
  final double? pulegonePercentage;
  final double? guaiolPercentage;
  final double? isopulegolPercentage;
  final double? geraniolPercentage;
  final double? borneolPercentage;
  final double? valencenePercentage;

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
      favorite: data['favorite'],
      description: data['description'],
      imageCaption: data['image_caption'],
      aliases:
          data['aliases'] != null ? List<String>.from(data['aliases']) : null,
      origin: data['origin'],
      breeder: data['breeder'],
      chemotype: data['chemotype'],
      firstCultivation: data['first_cultivation'],
      folklore: data['folklore'],
      etymology: data['etymology'],
      seedAvailability: data['seed_availability'],
      firstTestedAt: data['first_tested_at'],
      firstObservedBy: data['first_observed_by'],
      firstSoldBy: data['first_sold_by'],
      firstSoldAt: data['first_sold_at'],
      history: data['history'],
      references: data['references'] != null
          ? List<String>.from(data['references'])
          : null,
      awards: data['awards'] != null ? List<String>.from(data['awards']) : null,
      avgPricePerGram: data['avg_price_per_gram'],
      avgTotalThc: data['avg_total_thc'],
      avgTotalCbd: data['avg_total_cbd'],
      avgTotalCannabinoids: data['avg_total_cannabinoids'],
      avgCbg: data['avg_cbg'],
      avgCbga: data['avg_cbga'],
      avgThca: data['avg_thca'],
      avgDelta9Thc: data['avg_delta_9_thc'],
      avgThcv: data['avg_thcv'],
      avgBetaPinene: data['avg_beta_pinene'],
      avgDLimonene: data['avg_d_limonene'],
      avgMyrcene: data['avg_myrcene'],
      avgHumulene: data['avg_humulene'],
      avgBetaCaryophyllene: data['avg_beta_caryophyllene'],
      avgTerpinene: data['avg_terpinene'],
      avgLinalool: data['avg_linalool'],
      avgOcimene: data['avg_ocimene'],
      avgNerolidol: data['avg_nerolidol'],
      alphaPinenePercentage: data['alpha_pinene_percentage'],
      eucalyptolPercentage: data['eucalyptol_percentage'],
      camphenePercentage: data['camphene_percentage'],
      phellandrenePercentage: data['phellandrene_percentage'],
      carenePercentage: data['carene_percentage'],
      sabinenePercentage: data['sabinene_percentage'],
      caryophylleneOxidePercentage: data['caryophyllene_oxide_percentage'],
      bisabololPercentage: data['bisabolol_percentage'],
      pulegonePercentage: data['pulegone_percentage'],
      guaiolPercentage: data['guaiol_percentage'],
      isopulegolPercentage: data['isopulegol_percentage'],
      geraniolPercentage: data['geraniol_percentage'],
      borneolPercentage: data['borneol_percentage'],
      valencenePercentage: data['valencene_percentage'],
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
      'favorite': favorite,
      'description': description,
      'image_caption': imageCaption,
      'aliases': aliases,
      'origin': origin,
      'breeder': breeder,
      'chemotype': chemotype,
      'first_cultivation': firstCultivation,
      'folklore': folklore,
      'etymology': etymology,
      'seed_availability': seedAvailability,
      'first_tested_at': firstTestedAt,
      'first_observed_by': firstObservedBy,
      'first_sold_by': firstSoldBy,
      'first_sold_at': firstSoldAt,
      'history': history,
      'references': references,
      'awards': awards,
      'avg_price_per_gram': avgPricePerGram,
      'avg_total_thc': avgTotalThc,
      'avg_total_cbd': avgTotalCbd,
      'avg_total_cannabinoids': avgTotalCannabinoids,
      'avg_cbg': avgCbg,
      'avg_cbga': avgCbga,
      'avg_thca': avgThca,
      'avg_delta_9_thc': avgDelta9Thc,
      'avg_thcv': avgThcv,
      'avg_beta_pinene': avgBetaPinene,
      'avg_d_limonene': avgDLimonene,
      'avg_myrcene': avgMyrcene,
      'avg_humulene': avgHumulene,
      'avg_beta_caryophyllene': avgBetaCaryophyllene,
      'avg_terpinene': avgTerpinene,
      'avg_linalool': avgLinalool,
      'avg_ocimene': avgOcimene,
      'avg_nerolidol': avgNerolidol,
      'alpha_pinene_percentage': alphaPinenePercentage,
      'eucalyptol_percentage': eucalyptolPercentage,
      'camphene_percentage': camphenePercentage,
      'phellandrene_percentage': phellandrenePercentage,
      'carene_percentage': carenePercentage,
      'sabinene_percentage': sabinenePercentage,
      'caryophyllene_oxide_percentage': caryophylleneOxidePercentage,
      'bisabolol_percentage': bisabololPercentage,
      'pulegone_percentage': pulegonePercentage,
      'guaiol_percentage': guaiolPercentage,
      'isopulegol_percentage': isopulegolPercentage,
      'geraniol_percentage': geraniolPercentage,
      'borneol_percentage': borneolPercentage,
      'valencene_percentage': valencenePercentage,
    };
  }
}

/// Model representing a comment for a strain of cannabis.
class StrainReview {
  // Initialization.
  const StrainReview({
    required this.strainId,
    required this.strainName,
    required this.user,
    required this.userName,
    required this.userPhotoUrl,
    required this.rating,
    required this.createdAt,
    required this.updatedAt,
    required this.review,
  });

  // Properties.
  final String strainId;
  final String strainName;
  final String user;
  final String userName;
  final String userPhotoUrl;
  final double rating;
  final DateTime createdAt;
  final DateTime updatedAt;
  final String review;

  // Create model.
  factory StrainReview.fromMap(Map<String, dynamic> data) {
    return StrainReview(
      strainId: data['strain_id'],
      strainName: data['strain_name'],
      user: data['user'],
      userName: data['user_name'],
      userPhotoUrl: data['user_photo_url'],
      rating: data['rating'],
      createdAt: DateTime.parse(data['created_at']),
      updatedAt: DateTime.parse(data['updated_at']),
      review: data['review'],
    );
  }

  // Create JSON.
  Map<String, dynamic> toMap() {
    return <String, dynamic>{
      'strain_id': strainId,
      'strain_name': strainName,
      'user': user,
      'user_name': userName,
      'user_photo_url': userPhotoUrl,
      'rating': rating,
      'created_at': createdAt.toIso8601String(),
      'updated_at': updatedAt.toIso8601String(),
      'review': review,
    };
  }
}

/// Model representing an image for a strain of cannabis.
class StrainImage {
  // Initialization.
  const StrainImage({
    required this.user,
    required this.userName,
    required this.userPhotoUrl,
    required this.uploadedAt,
    required this.fileSize,
    required this.fileType,
    required this.fileRef,
    required this.imageUrl,
    required this.shortUrl,
    required this.strainId,
    required this.strainName,
  });

  // Properties.
  final String user;
  final String userName;
  final String userPhotoUrl;
  final DateTime uploadedAt;
  final int fileSize;
  final String fileType;
  final String fileRef;
  final String imageUrl;
  final String shortUrl;
  final String strainId;
  final String strainName;

  // Create model.
  factory StrainImage.fromMap(Map<String, dynamic> data) {
    return StrainImage(
      user: data['user'],
      userName: data['user_name'],
      userPhotoUrl: data['user_photo_url'],
      uploadedAt: DateTime.parse(data['uploaded_at']),
      fileSize: data['file_size'],
      fileType: data['file_type'],
      fileRef: data['file_ref'],
      imageUrl: data['image_url'],
      shortUrl: data['short_url'],
      strainId: data['strain_id'],
      strainName: data['strain_name'],
    );
  }

  // Create JSON.
  Map<String, dynamic> toMap() {
    return <String, dynamic>{
      'user': user,
      'user_name': userName,
      'user_photo_url': userPhotoUrl,
      'uploaded_at': uploadedAt.toIso8601String(),
      'file_size': fileSize,
      'file_type': fileType,
      'file_ref': fileRef,
      'image_url': imageUrl,
      'short_url': shortUrl,
      'strain_id': strainId,
      'strain_name': strainName,
    };
  }
}

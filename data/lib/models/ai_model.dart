// Cannlytics Data
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 4/15/2023
// Updated: 4/15/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

/// Model representing a statistical model.
class AIModel {
  final String? name;
  final String? type;
  final String? description;
  final double? intercept;
  final Map<String, double>? featureCoefficients;
  final Map<String, double>? performanceMetrics;
  final int? trainingDataSize;
  final Map<String, double>? trainTestSplit;
  final String? createdAt;

  AIModel({
    this.name,
    this.type,
    this.description,
    this.intercept,
    this.featureCoefficients,
    this.performanceMetrics,
    this.trainingDataSize,
    this.trainTestSplit,
    this.createdAt,
  });
}

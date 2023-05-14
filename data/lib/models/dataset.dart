// Cannlytics Data
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 4/15/2023
// Updated: 5/14/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Flutter imports:
import 'package:flutter/material.dart';

/// Model representing a dataset.
class Dataset {
  final String? svgSrc;
  final String? title;
  final String? totalStorage;
  final int? numOfFiles;
  final int? percentage;
  final Color? color;

  final String? name;
  final String? description;
  final Size? size;
  final List? observations;
  final List<dynamic>? attributes;
  final String? source;
  final DateTime? lastUpdated;

  Dataset({
    this.svgSrc,
    this.title,
    this.totalStorage,
    this.numOfFiles,
    this.percentage,
    this.color,
    this.name,
    this.description,
    this.size,
    this.observations,
    this.attributes,
    this.source,
    this.lastUpdated,
  });

  factory Dataset.fromJson(Map<String, dynamic> json) {
    return Dataset(
      svgSrc: null,
      title: null,
      totalStorage: null,
      numOfFiles: null,
      percentage: null,
      color: null,
      name: json['dataset']['name'],
      description: json['dataset']['description'],
      size: json['dataset']['size'],
      observations: json['dataset']['observations'],
      attributes: json['dataset']['attributes'],
      source: json['dataset']['source'],
      lastUpdated: DateTime.parse(json['dataset']['last_updated']),
    );
  }
}

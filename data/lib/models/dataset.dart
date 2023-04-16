// Cannlytics Data
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 4/15/2023
// Updated: 4/16/2023
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
  final Observations? observations;
  final List<Attribute>? attributes;
  final Source? source;
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
      size: Size.fromJson(json['dataset']['size']),
      observations: Observations.fromJson(json['dataset']['observations']),
      attributes: List<Attribute>.from(
          json['dataset']['attributes'].map((x) => Attribute.fromJson(x))),
      source: Source.fromJson(json['dataset']['source']),
      lastUpdated: DateTime.parse(json['dataset']['last_updated']),
    );
  }
}

class Size {
  final int bytes;
  final String formatted;

  Size({required this.bytes, required this.formatted});

  factory Size.fromJson(Map<String, dynamic> json) {
    return Size(
      bytes: json['bytes'],
      formatted: json['formatted'],
    );
  }
}

class Observations {
  final int count;
  final String units;

  Observations({required this.count, required this.units});

  factory Observations.fromJson(Map<String, dynamic> json) {
    return Observations(
      count: json['count'],
      units: json['units'],
    );
  }
}

class Attribute {
  final String name;
  final String type;
  final String description;

  Attribute(
      {required this.name, required this.type, required this.description});

  factory Attribute.fromJson(Map<String, dynamic> json) {
    return Attribute(
      name: json['name'],
      type: json['type'],
      description: json['description'],
    );
  }
}

class Source {
  final String name;
  final String url;

  Source({required this.name, required this.url});

  factory Source.fromJson(Map<String, dynamic> json) {
    return Source(
      name: json['name'],
      url: json['url'],
    );
  }
}

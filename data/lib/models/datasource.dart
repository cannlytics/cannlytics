// Cannlytics Data
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 4/15/2023
// Updated: 4/16/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Flutter imports:
import 'package:flutter/material.dart';

/// Model representing a data source.
class DataSource {
  final String? name;
  final String? url;
  final String? state;
  final String? description;
  final String? dataSourceType;
  final String? updateFrequency;
  final String? dataFormat;
  final String? lastUpdated;
  final List<String>? fields;
  final List<String>? tags;
  final String? license;
  final String? source;
  final String? documentation;

  DataSource({
    this.name,
    this.url,
    this.state,
    this.description,
    this.dataSourceType,
    this.updateFrequency,
    this.dataFormat,
    this.lastUpdated,
    this.fields,
    this.tags,
    this.license,
    this.source,
    this.documentation,
  });
}

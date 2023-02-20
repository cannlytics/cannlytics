// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 2/18/2023
// Updated: 2/18/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

class EntriesListTileModel {
  const EntriesListTileModel({
    required this.leadingText,
    required this.trailingText,
    this.middleText,
    this.isHeader = false,
  });
  final String leadingText;
  final String trailingText;
  final String? middleText;
  final bool isHeader;
}

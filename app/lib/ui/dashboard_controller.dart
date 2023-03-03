// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 3/3/2023
// Updated: 3/3/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Package imports:
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

// License management provider.
final licenseProvider = ChangeNotifierProvider<LicenseProvider>((ref) {
  return LicenseProvider();
});

/// License management functionality.
class LicenseProvider extends ChangeNotifier {
  // Primary license.
  String _primaryLicense = '+ Add a license';
  String get primaryLicense => _primaryLicense;

  // User's licenses.
  // TODO: Somehow populate licenses from Firestore on initialization.
  List<String> _licenses = ['+ Add a license'];
  List<String> get licenses => _licenses;

  /// Change the user's primary license.
  changeLicense(String value) {
    if (value.isEmpty) {
      return _primaryLicense;
    }
    _primaryLicense = value;
    return notifyListeners();
  }

  /// Change the user's licenses.
  changeLicenses(List<String> values) {
    if (values.isEmpty) {
      return _licenses;
    }
    _licenses = values;
    return notifyListeners();
  }
}

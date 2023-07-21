// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 3/23/2023
// Updated: 3/23/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Flutter imports:
import 'package:flutter/foundation.dart';
import 'package:flutter/services.dart';

/// Stream app licenses.
Stream<LicenseEntry> renderAppLicenses() async* {
  // Font licenses.
  String _dir = 'assets/fonts';
  yield await getAppLicense('IBM_Plex_Sans', '$_dir/IBM_Plex_Sans/OFL.txt');
  yield await getAppLicense(
      'Cormorant_Garamond', '$_dir/Cormorant_Garamond/OFL.txt');
  yield await getAppLicense(
      'Libre_Baskerville', '$_dir/Libre_Baskerville/OFL.txt');
  yield await getAppLicense(
      'Source_Serif_Pro', '$_dir/Source_Serif_Pro/OFL.txt');

  // Code licenses.
  _dir = 'assets/licenses';
  yield await getAppLicense('starter_architecture_flutter_firebase',
      '$_dir/bizz84-starter_architecture_flutter_firebase.txt');
  yield await getAppLicense(
      'flutter_wonderous_app', '$_dir/flutter-wonderous-app-license.txt');
}

/// Load a license given its name and license location.
Future<LicenseEntryWithLineBreaks> getAppLicense(name, asset) async {
  return LicenseEntryWithLineBreaks([name], await rootBundle.loadString(asset));
}

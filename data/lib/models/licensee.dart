// Cannlytics Data
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 5/7/2023
// Updated: 5/14/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Package imports:

typedef LicenseId = String;

class Licensee {
  // Initialization.
  const Licensee({
    required this.id,
    required this.license,
    required this.licenseType,
    required this.state,
    this.userAPIKey,
    this.prefix,
  });

  // Properties.
  final String id;
  final String license;
  final String licenseType;
  final String state;
  final String? userAPIKey;
  final String? prefix;

  // // Create model.
  // factory License.fromMap(Map<dynamic, dynamic> values) {
  //   return License(
  //     id: values['id'] as String,
  //     license: values['license'] as String,
  //     licenseType: values['license_type'] as String,
  //     state: values['state'] as String,
  //     userAPIKey: values['user_api_key'] as String,
  //     prefix: values['prefix'] as String,
  //   );
  // }

  // // Create JSON.
  // Map<String, dynamic> toMap() {
  //   return <String, dynamic>{
  //     'id': id,
  //     'license': license,
  //     'license_type': licenseType,
  //     'state': state,
  //     'user_api_key': userAPIKey,
  //     'prefix': prefix,
  //   };
  // }
}

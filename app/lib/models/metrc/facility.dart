// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 2/20/2023
// Updated: 3/7/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

typedef FacilityId = String;

/// Model representing an organization.
class Facility {
  // Initialization.
  const Facility({
    required this.id,
    this.alias = '',
    this.credentialedDate = '',
    this.displayName = '',
    this.facilityType = const {},
    this.hireDate = '',
    this.isManager = false,
    this.isOwner = false,
    this.licenseEndDate = '',
    this.licenseNumber = '',
    this.licenseStartDate = '',
    this.licenseType = '',
    this.name = '',
    this.occupations = const [],
    this.supportActivationDate = '',
    this.supportExpirationDate = '',
    this.supportLastPaidDate = '',
  });

  // Properties.
  final FacilityId id;
  final String alias;
  final String credentialedDate;
  final String displayName;
  final String hireDate;
  final Map facilityType;
  final bool isManager;
  final bool isOwner;
  final String licenseEndDate;
  final String licenseNumber;
  final String licenseStartDate;
  final String licenseType;
  final String name;
  final List<dynamic> occupations;
  final String supportActivationDate;
  final String supportExpirationDate;
  final String supportLastPaidDate;

  // Create model.
  factory Facility.fromMap(Map<dynamic, dynamic> data) {
    return Facility(
      id: data['id'] ?? '',
      alias: data['alias'] ?? '',
      credentialedDate: data['credentialed_date'] ?? '',
      displayName: data['display_name'] ?? '',
      facilityType: data['facility_type'] ?? {},
      hireDate: data['hire_date'] ?? '',
      isManager: data['is_manager'] ?? false,
      isOwner: data['is_owner'] ?? false,
      licenseEndDate: data['license']['end_date'] ?? '',
      licenseNumber: data['license']['number'] ?? '',
      licenseStartDate: data['license']['start_date'] ?? '',
      licenseType: data['license']['type'] ?? '',
      name: data['name'] ?? '',
      occupations: List<dynamic>.from(data['occupations'] ?? const []),
      supportActivationDate: data['support_activation_date'] ?? '',
      supportExpirationDate: data['support_expiration_date'] ?? '',
      supportLastPaidDate: data['support_last_paid_date'] ?? '',
    );
  }

  // Create JSON.
  Map<String, dynamic> toMap() {
    return <String, dynamic>{
      'id': id,
      'alias': alias,
      'credentialed_date': credentialedDate,
      'display_name': displayName,
      'facility_type': facilityType,
      'hire_date': hireDate,
      'is_manager': isManager,
      'is_owner': isOwner,
      'license': {
        'end_date': licenseEndDate,
        'number': licenseNumber,
        'start_date': licenseStartDate,
        'type': licenseType,
      },
      'name': name,
      'occupations': occupations,
      'support_activation_date': supportActivationDate,
      'support_expiration_date': supportExpirationDate,
      'support_last_paid_date': supportLastPaidDate,
    };
  }
}

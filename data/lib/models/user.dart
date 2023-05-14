// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 2/20/2023
// Updated: 2/20/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

/// Type defining a user ID from Firebase.
typedef UserID = String;

/// [AppUser] is a simple class representing the user, with UID and email.
class AppUser {
  const AppUser({
    this.uid,
    this.email,
    this.fullName,
    this.licenseNumber,
    this.licenseStartDate,
    this.licenseEndDate,
    this.licenseType,
    this.registrationDate,
    this.licenseEffectiveStartDate,
    this.licenseEffectiveEndDate,
    this.recommendedPlants,
    this.recommendedSmokableQuantity,
    this.hasSalesLimitExemption,
    this.otherFacilitiesCount,
  });
  final String? uid;
  final String? email;
  final String? fullName;
  final String? licenseNumber;
  final String? licenseStartDate;
  final String? licenseEndDate;
  final String? licenseType;
  final String? registrationDate;
  final String? licenseEffectiveStartDate;
  final String? licenseEffectiveEndDate;
  final int? recommendedPlants;
  final double? recommendedSmokableQuantity;
  final bool? hasSalesLimitExemption;
  final int? otherFacilitiesCount;

  @override
  bool operator ==(Object other) {
    if (identical(this, other)) return true;
    return other is AppUser && other.uid == uid && other.email == email;
  }

  @override
  int get hashCode => uid.hashCode ^ email.hashCode;

  @override
  String toString() => 'AppUser(uid: $uid, email: $email)';

  // Create model.
  factory AppUser.fromMap(Map<String, dynamic> data) {
    return AppUser(
      uid: data['uid'] ?? '',
      fullName: data['full_name'] ?? '',
      licenseNumber: data['license']['number'] ?? '',
      licenseStartDate: data['license']['start_date'] ?? '',
      licenseEndDate: data['license']['end_date'] ?? '',
      licenseType: data['license']['license_type'] ?? '',
      registrationDate: data['registration_date'] ?? '',
      licenseEffectiveStartDate: data['license_effective_start_date'] ?? '',
      licenseEffectiveEndDate: data['license_effective_end_date'] ?? '',
      recommendedPlants: data['recommended_plants'] ?? 0,
      recommendedSmokableQuantity: data['recommended_smokable_quantity'] ?? 0,
      hasSalesLimitExemption: data['has_sales_limit_exemption'] ?? false,
      otherFacilitiesCount: data['other_facilities_count'] ?? 0,
    );
  }

  // Create JSON.
  Map<String, dynamic> toMap() {
    // TODO: Conditionally return employee, patient, or app user data.
    return <String, dynamic>{
      'uid': uid,
      'email': email,
      'full_name': fullName,
      'license': {
        'number': licenseNumber,
        'start_date': licenseStartDate,
        'end_date': licenseEndDate,
        'license_type': licenseType,
      },
      'registration_date': registrationDate,
      'license_effective_start_date': licenseEffectiveStartDate,
      'license_effective_end_date': licenseEffectiveEndDate,
      'recommended_plants': recommendedPlants,
      'recommended_smokable_quantity': recommendedSmokableQuantity,
      'has_sales_limit_exemption': hasSalesLimitExemption,
      'other_facilities_count': otherFacilitiesCount,
    };
  }
}

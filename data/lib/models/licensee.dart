// Cannlytics Data
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 5/7/2023
// Updated: 7/3/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

/// Model representing a cannabis licensee.
class Licensee {
  // Initialization.
  const Licensee({
    this.id,
    this.licenseNumber,
    this.licenseStatus,
    this.licenseStatusDate,
    this.licenseTerm,
    this.licenseType,
    this.licenseDesignation,
    this.issueDate,
    this.expirationDate,
    this.licensingAuthorityId,
    this.licensingAuthority,
    this.businessLegalName,
    this.businessDbaName,
    this.businessOwnerName,
    this.businessStructure,
    this.activity,
    this.premiseStreetAddress,
    this.premiseCity,
    this.premiseState,
    this.premiseCounty,
    this.premiseZipCode,
    this.businessEmail,
    this.businessPhone,
    this.businessWebsite,
    this.parcelNumber,
    this.premiseLatitude,
    this.premiseLongitude,
    this.dataRefreshedDate,
  });

  final dynamic id;
  final dynamic licenseNumber;
  final dynamic licenseStatus;
  final dynamic licenseStatusDate;
  final dynamic licenseTerm;
  final dynamic licenseType;
  final dynamic licenseDesignation;
  final dynamic issueDate;
  final dynamic expirationDate;
  final dynamic licensingAuthorityId;
  final dynamic licensingAuthority;
  final dynamic businessLegalName;
  final dynamic businessDbaName;
  final dynamic businessOwnerName;
  final dynamic businessStructure;
  final dynamic activity;
  final dynamic premiseStreetAddress;
  final dynamic premiseCity;
  final dynamic premiseState;
  final dynamic premiseCounty;
  final dynamic premiseZipCode;
  final dynamic businessEmail;
  final dynamic businessPhone;
  final dynamic businessWebsite;
  final dynamic parcelNumber;
  final double? premiseLatitude;
  final double? premiseLongitude;
  final dynamic dataRefreshedDate;

  // Create model.
  factory Licensee.fromMap(Map<dynamic, dynamic> data) {
    return Licensee(
      id: data['id'] ?? '',
      licenseNumber: data['license_number'] ?? '',
      licenseStatus: data['license_status'] ?? '',
      licenseStatusDate: data['license_status_date'],
      licenseTerm: data['license_term'] ?? '',
      licenseType: data['license_type'] ?? '',
      licenseDesignation: data['license_designation'] ?? '',
      issueDate: data['issue_date'],
      expirationDate: data['expiration_date'],
      licensingAuthorityId: data['licensing_authority_id'] ?? '',
      licensingAuthority: data['licensing_authority'] ?? '',
      businessLegalName: data['business_legal_name'] ?? '',
      businessDbaName: data['business_dba_name'] ?? '',
      businessOwnerName: data['business_owner_name'] ?? '',
      businessStructure: data['business_structure'] ?? '',
      activity: data['activity'] ?? '',
      premiseStreetAddress: data['premise_street_address'] ?? '',
      premiseCity: data['premise_city'] ?? '',
      premiseState: data['premise_state'] ?? '',
      premiseCounty: data['premise_county'] ?? '',
      premiseZipCode: data['premise_zip_code'] ?? '',
      businessEmail: data['business_email'] ?? '',
      businessPhone: data['business_phone'] ?? '',
      businessWebsite: data['business_website'] ?? '',
      parcelNumber: data['parcel_number'] ?? '',
      premiseLatitude: data['premise_latitude'],
      premiseLongitude: data['premise_longitude'],
      dataRefreshedDate: data['data_refreshed_date'],
    );
  }

  // Create JSON.
  Map<String, dynamic> toMap() {
    return <String, dynamic>{
      'id': id,
      'license_number': licenseNumber,
      'license_status': licenseStatus,
      'license_status_date': licenseStatusDate,
      'license_term': licenseTerm,
      'license_type': licenseType,
      'license_designation': licenseDesignation,
      'issue_date': issueDate,
      'expiration_date': expirationDate,
      'licensing_authority_id': licensingAuthorityId,
      'licensing_authority': licensingAuthority,
      'business_legal_name': businessLegalName,
      'business_dba_name': businessDbaName,
      'business_owner_name': businessOwnerName,
      'business_structure': businessStructure,
      'activity': activity,
      'premise_street_address': premiseStreetAddress,
      'premise_city': premiseCity,
      'premise_state': premiseState,
      'premise_county': premiseCounty,
      'premise_zip_code': premiseZipCode,
      'business_email': businessEmail,
      'business_phone': businessPhone,
      'business_website': businessWebsite,
      'parcel_number': parcelNumber,
      'premise_latitude': premiseLatitude,
      'premise_longitude': premiseLongitude,
      'data_refreshed_date': dataRefreshedDate,
    };
  }
}

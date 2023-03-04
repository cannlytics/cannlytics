// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 2/20/2023
// Updated: 3/4/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

import 'package:cannlytics_app/services/api_service.dart';
import 'package:cannlytics_app/services/firestore_service.dart';
import 'package:cannlytics_app/utils/strings/string_format.dart';

typedef OrganizationId = String;

/// Model representing an organization.
class Organization {
  // Initialization.
  const Organization({
    required this.id,
    required this.address,
    required this.city,
    required this.country,
    required this.email,
    required this.externalId,
    required this.licenses,
    required this.licenseNumber,
    required this.licenseType,
    required this.state,
    required this.userApiKeySecret,
    required this.projectId,
    required this.secretId,
    required this.versionId,
    required this.linkedin,
    required this.name,
    required this.owner,
    required this.phone,
    required this.public,
    required this.team,
    required this.tradeName,
    required this.type,
    required this.uid,
    required this.website,
    required this.zipCode,
  });

  // Properties.
  final OrganizationId id;
  final String address;
  final String city;
  final String country;
  final String email;
  final String externalId;
  final int licenses;
  final String licenseNumber;
  final String licenseType;
  final String state;
  final String userApiKeySecret;
  final String projectId;
  final String secretId;
  final String versionId;
  final String linkedin;
  final String name;
  final String owner;
  final String phone;
  final bool public;
  final List<String> team;
  final String tradeName;
  final String type;
  final String uid;
  final String website;
  final String zipCode;

  // Create model.
  factory Organization.fromMap(Map<dynamic, dynamic> data) {
    return Organization(
      id: Format.slugify(data['name'] as String),
      address: data['address'] as String,
      city: data['city'] as String,
      country: data['country'] as String,
      email: data['email'] as String,
      externalId: data['external_id'] as String,
      licenses: data['licenses'] as int,
      licenseNumber: data['license_number'] as String,
      licenseType: data['license_type'] as String,
      state: data['state'] as String,
      userApiKeySecret: data['user_api_key_secret'] as String,
      projectId: data['project_id'] as String,
      secretId: data['secret_id'] as String,
      versionId: data['version_id'] as String,
      linkedin: data['linkedin'] as String,
      name: data['name'] as String,
      owner: data['owner'] as String,
      phone: data['phone'] as String,
      public: data['public'] as bool,
      team: data['team'] as List<String>,
      tradeName: data['trade_name'] as String,
      type: data['type'] as String,
      uid: data['uid'] as String,
      website: data['website'] as String,
      zipCode: data['zip_code'] as String,
    );
  }

  // Create JSON.
  Map<String, dynamic> toMap() {
    return <String, dynamic>{
      'id': id,
      'address': address,
      'city': city,
      'country': country,
      'email': email,
      'external_id': externalId,
      'licenses': licenses,
      'license_number': licenseNumber,
      'license_type': licenseType,
      'state': state,
      'user_api_key_secret': userApiKeySecret,
      'project_id': projectId,
      'secret_id': secretId,
      'version_id': versionId,
      'linkedin': linkedin,
      'name': name,
      'owner': owner,
      'phone': phone,
      'public': public,
      'team': team,
      'trade_name': tradeName,
      'type': type,
      'uid': uid,
      'website': website,
      'zip_code': zipCode,
    };
  }

  // Create Organization.
  Future<void> create() async {
    Map data = this.toMap();
    String orgId = Format.slugify(this.name);
    await APIService.authRequest('/organizations/$orgId', data: data);
  }

  // Update Organization.
  Future<void> update() async {
    Map data = this.toMap();
    String orgId = Format.slugify(this.name);
    await APIService.authRequest('/organizations/$orgId', data: data);
  }

  // Delete Organization.
  Future<void> delete() async {
    String orgId = Format.slugify(this.name);
    await APIService.authRequest(
      '/organizations/$orgId',
      options: {'delete': true},
    );
  }

  // TODO: Invite team members.

  // TODO: Remove team members.

  // Get team member logs.
  Future<List<Map>> getTeamMemberLogs({
    required FirestoreService db,
    String? uid,
  }) {
    String orgId = Format.slugify(this.name);
    return db.fetchCollection(
      path: 'organizations/$orgId/logs',
      builder: (data, documentId) => data!,
      queryBuilder:
          uid != null ? (query) => query.where('user', isEqualTo: uid) : null,
      // TODO: Order by created_at
      // sort: (lhs, rhs) => rhs.start.compareTo(lhs.start),
      // TODO: Limit by 100
      // TODO: Order in descending order.
    );
  }

  // TODO: Upload organization photo.

  // TODO: Join organization.
}

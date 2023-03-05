// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 2/20/2023
// Updated: 3/5/2023
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
    this.address = '',
    this.city = '',
    this.country = '',
    this.email = '',
    this.externalId = '',
    this.licenses,
    required this.name,
    required this.owner,
    this.phone = '',
    this.public = false,
    this.state = '',
    required this.team,
    this.tradeName = '',
    this.type = '',
    this.website = '',
    this.zipCode = '',
  });

  // Properties.
  final OrganizationId id;
  final String address;
  final String city;
  final String country;
  final String email;
  final String externalId;
  final List<Map?>? licenses;
  final String name;
  final String owner;
  final String phone;
  final bool public;
  final String state;
  final List<dynamic> team;
  final String tradeName;
  final String type;
  final String website;
  final String zipCode;

  // Create model.
  factory Organization.fromMap(Map<dynamic, dynamic> data) {
    return Organization(
      id: Format.slugify(data['name']),
      address: data['address'],
      city: data['city'],
      country: data['country'],
      email: data['email'],
      externalId: data['external_id'],
      licenses: data['licenses'],
      name: data['name'],
      owner: data['owner'],
      phone: data['phone'],
      public: data['public'],
      state: data['state'],
      team: data['team'],
      tradeName: data['trade_name'],
      type: data['type'],
      website: data['website'],
      zipCode: data['zip_code'],
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
      'name': name,
      'owner': owner,
      'phone': phone,
      'public': public,
      'state': state,
      'team': team,
      'trade_name': tradeName,
      'type': type,
      'website': website,
      'zip_code': zipCode,
    };
  }

  // Create Organization.
  Future<void> create() async {
    Map data = this.toMap();
    String orgId = Format.slugify(this.name);
    await APIService.apiRequest('/organizations/$orgId', data: data);
  }

  // Update Organization.
  Future<void> update() async {
    Map data = this.toMap();
    String orgId = Format.slugify(this.name);
    await APIService.apiRequest('/organizations/$orgId', data: data);
  }

  // Delete Organization.
  Future<void> delete() async {
    String orgId = Format.slugify(this.name);
    await APIService.apiRequest(
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

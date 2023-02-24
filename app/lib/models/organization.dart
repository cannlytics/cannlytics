// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 2/20/2023
// Updated: 2/20/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Package imports:
import 'package:equatable/equatable.dart';

typedef OrganizationId = String;

/// Model representing an organization.
class Organization extends Equatable {
  const Organization({
    required this.uid,
    this.name = '',
  });
  final OrganizationId uid;
  final String name;

  @override
  List<Object?> get props => [uid];

  @override
  bool get stringify => true;

  factory Organization.fromMap(Map<String, dynamic>? data, String uid) {
    return Organization(
      uid: uid,
      name: data!['name'] as String,
    );
  }

  Map<String, dynamic> toMap() {
    return <String, dynamic>{
      'id': uid,
      'name': name,
    };
  }
}

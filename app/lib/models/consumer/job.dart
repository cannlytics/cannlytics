// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 2/20/2023
// Updated: 2/20/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Flutter imports:
import 'package:flutter/foundation.dart';

// Package imports:
import 'package:equatable/equatable.dart';

typedef JobID = String;

@immutable
class Job extends Equatable {
  const Job({
    required this.id,
    required this.name,
    required this.ratePerHour,
  });
  final JobID id;
  final String name;
  final int ratePerHour;

  @override
  List<Object> get props => [id, name, ratePerHour];

  @override
  bool get stringify => true;

  factory Job.fromMap(Map<dynamic, dynamic>? data, String documentId) {
    return Job(
      id: documentId,
      name: data!['name'] as String,
      ratePerHour: data['ratePerHour'] as int,
    );
  }

  Map<String, dynamic> toMap() {
    return {
      'name': name,
      'ratePerHour': ratePerHour,
    };
  }
}

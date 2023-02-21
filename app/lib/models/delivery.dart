// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 2/20/2023
// Updated: 2/20/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>
import 'package:equatable/equatable.dart';

typedef DeliveryId = String;

/// Model representing an organization.
class Delivery extends Equatable {
  const Delivery({
    required this.uid,
    this.label = '',
  });
  final DeliveryId uid;
  final String label;

  @override
  List<Object?> get props => [uid];

  @override
  bool get stringify => true;

  factory Delivery.fromMap(Map<String, dynamic>? data, String uid) {
    return Delivery(
      uid: uid,
      label: data!['label'] as String,
    );
  }

  Map<String, dynamic> toMap() {
    return <String, dynamic>{
      'id': uid,
      'label': label,
    };
  }
}

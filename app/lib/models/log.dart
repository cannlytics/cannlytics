// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 3/3/2023
// Updated: 3/4/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Package imports:
import 'package:intl/intl.dart';

// Project imports:
import 'package:cannlytics_app/services/firestore_service.dart';

typedef LogId = String;

/// Model representing a log.
class Log {
  // Initialization.
  const Log({
    required this.id,
    required this.action,
    required this.changes,
    required this.createdAt,
    required this.key,
    required this.type,
    required this.user,
    required this.userEmail,
    required this.userName,
    required this.userPhotoUrl,
  });

  // Properties.
  final LogId id;
  final String action;
  final List<dynamic> changes;
  final DateTime createdAt;
  final String key;
  final String type;
  final dynamic user;
  final String userEmail;
  final String userName;
  final String userPhotoUrl;

  // Create model.
  factory Log.fromMap(Map<String, dynamic> data, String uid) {
    return Log(
      id: uid,
      action: data['action'] as String,
      changes: data['changes'] as List<dynamic>,
      createdAt: DateTime.parse(data['created_at'] as String),
      key: data['key'] as String,
      type: data['type'] as String,
      user: data['user'] as dynamic,
      userEmail: data['user_email'] as String,
      userName: data['user_name'] as String,
      userPhotoUrl: data['user_photo_url'] as String,
    );
  }

  // Create JSON.
  Map<String, dynamic> toMap({DateTime? time}) {
    String timestamp;
    if (time != null) {
      timestamp = time.toIso8601String();
    } else {
      timestamp = createdAt.toIso8601String();
    }
    return <String, dynamic>{
      'id': id,
      'action': action,
      'changes': changes,
      'created_at': timestamp,
      'key': key,
      'type': type,
      'user': user,
      'user_email': userEmail,
      'user_name': userName,
      'user_photo_url': userPhotoUrl,
    };
  }

  // Save log to Firestore.
  Future<void> create({required FirestoreService db}) async {
    DateTime now = DateTime.now();
    String logId = DateFormat('yyyy-MM-dd_HH-mm-ss').format(now);
    await db.setData(
      path: 'logs/app/$logId',
      data: this.toMap(time: now),
    );
  }
}

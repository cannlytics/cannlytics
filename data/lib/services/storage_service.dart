// Cannlytics Data
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 2/24/2023
// Updated: 5/13/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Package imports:
// import 'dart:io';

// Package imports:
import 'package:firebase_storage/firebase_storage.dart';

// import 'package:path_provider/path_provider.dart';

/// Storage service.
class StorageService {
  const StorageService._();

  // TODO: Upload file(s).

  // TODO: Download file(s).
  // static Future<void> downloadFile(String path) async {
  //   FirebaseStorage storage = FirebaseStorage.instance;
  //   Directory directory = await getApplicationDocumentsDirectory();
  //   File downloadToFile = File('${directory.path}/myimage.jpg');
  //   try {
  //     await storage.ref(path).writeToFile(downloadToFile);
  //   } on FirebaseException catch (e) {
  //     // User likely canceled.
  //   }
  // }

  // Get a download URL.
  static Future<String?> getDownloadUrl(String path) async {
    FirebaseStorage storage = FirebaseStorage.instance;
    try {
      return await storage.ref(path).getDownloadURL();
    } on FirebaseException catch (e) {
      // User likely canceled.
      print(e);
      return null;
    }
  }

  // TODO: Create short URL.

  // TODO: Delete file(s).

  // TODO: Rename file(s).
}

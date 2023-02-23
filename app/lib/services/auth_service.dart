// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 2/18/2023
// Updated: 2/20/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>
import 'dart:io';

import 'package:cannlytics_app/services/firestore_service.dart';
import 'package:firebase_auth/firebase_auth.dart';
import 'package:firebase_storage/firebase_storage.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:image_picker/image_picker.dart';

/// [AuthService] manages authentication with Firebase.
class AuthService {
  AuthService(this._auth, this._firestore);
  final FirebaseAuth _auth;
  final FirestoreService _firestore;

  /// Handle user changes and get the current user.
  Stream<User?> authStateChanges() => _auth.authStateChanges();
  User? get currentUser => _auth.currentUser;

  /// Signs the user in anonymously.
  Future<void> signInAnonymously() {
    return _auth.signInAnonymously();
  }

  /// Sign in with email and password.
  Future<void> signInWithEmailAndPassword(String email, String password) {
    return _auth.signInWithEmailAndPassword(email: email, password: password);
  }

  /// Create a user with email and password.
  Future<void> createUserWithEmailAndPassword(String email, String password) {
    return _auth.createUserWithEmailAndPassword(
        email: email, password: password);
  }

  /// Sign the user out.
  Future<void> signOut() {
    return _auth.signOut();
  }

  /// Change the user's photo.
  Future<void> changePhoto() async {
    // Get the current user.
    User? user = FirebaseAuth.instance.currentUser;
    if (user != null) {
      // Show the image picker to let the user select a new photo.
      final imagePicker = ImagePicker();
      final pickedFile = await imagePicker.pickImage(
        source: ImageSource.gallery,
      );

      // If the user picks a photo.
      if (pickedFile != null) {
        // Upload the selected photo to Firebase Storage and get its download URL.
        final String photoRef = 'users/${user.uid}/photo.jpg';
        final storageRef = FirebaseStorage.instance.ref().child(photoRef);
        final uploadTask = storageRef.putFile(File(pickedFile.path));
        final snapshot = await uploadTask.whenComplete(() {});
        final downloadURL = await snapshot.ref.getDownloadURL();

        // Update the user's data in Firestore.
        await _firestore.setData(
          path: 'users/${user.uid}',
          data: {
            'photo_url': downloadURL,
            'photo_ref': photoRef,
          },
          merge: true,
        );

        // Update the user's photo URL in Firebase Authentication.
        await user.updatePhotoURL(downloadURL);
      }
    }
  }
}

/// An instance of Firebase Authentication provider.
final firebaseAuthProvider =
    Provider<FirebaseAuth>((ref) => FirebaseAuth.instance);

final authServiceProvider = Provider<AuthService>((ref) {
  return AuthService(
    ref.watch(firebaseAuthProvider),
    ref.watch(firestoreDataSourceProvider),
  );
});

final authStateChangesProvider = StreamProvider<User?>((ref) {
  return ref.watch(authServiceProvider).authStateChanges();
});

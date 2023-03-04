// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 2/18/2023
// Updated: 3/3/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Package imports:
import 'package:file_picker/file_picker.dart';
import 'package:firebase_auth/firebase_auth.dart';
import 'package:firebase_storage/firebase_storage.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

// Project imports:
import 'package:cannlytics_app/services/firestore_service.dart';

// Firebase Authentication provider.
final firebaseAuthProvider = Provider<FirebaseAuth>((ref) {
  return FirebaseAuth.instance;
});

// Authentication service provider.
final authProvider = Provider<AuthService>((ref) {
  return AuthService(
    ref.watch(firebaseAuthProvider),
    ref.watch(firestoreProvider),
  );
});

// User provider.
final userProvider = StreamProvider<User?>((ref) {
  return ref.watch(authProvider).authStateChanges();
});

/// [AuthService] manages authentication with Firebase.
class AuthService {
  AuthService(this._auth, this._firestore);
  final FirebaseAuth _auth;
  final FirestoreService _firestore;

  /// Stream the current user.
  Stream<User?> authStateChanges() => _auth.authStateChanges();

  /// Get the current user.
  User? get currentUser => _auth.currentUser;

  /// Signs the user in anonymously.
  Future<void> signInAnonymously() {
    return _auth.signInAnonymously();
  }

  /// Sign in with email and password.
  Future<void> signIn(String email, String password) {
    return _auth.signInWithEmailAndPassword(email: email, password: password);
  }

  /// Create a user with email and password.
  Future<void> createAccount(
    String email,
    String password,
  ) {
    return _auth.createUserWithEmailAndPassword(
      email: email,
      password: password,
    );
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
      var pickedFile = await FilePicker.platform.pickFiles();

      // If the user picks a photo.
      if (pickedFile != null) {
        // Upload the selected photo to Firebase Storage and get its download URL.
        final String photoRef = 'users/${user.uid}/photo.jpg';
        final storageRef = FirebaseStorage.instance.ref().child(photoRef);
        final uploadTask = storageRef.putData(pickedFile.files.first.bytes!);
        final snapshot = await uploadTask.whenComplete(() {});
        final downloadURL = await snapshot.ref.getDownloadURL();

        // Update the user's data in Firestore.
        await _firestore.setData(
          path: 'users/${user.uid}',
          data: {
            'photo_url': downloadURL,
            'photo_ref': photoRef,
          },
        );

        // Update the user's photo URL in Firebase Authentication.
        await user.updatePhotoURL(downloadURL);
        // await user.reload();
      }
    }
  }

  /// TODO: Let the user request a password reset email.
}

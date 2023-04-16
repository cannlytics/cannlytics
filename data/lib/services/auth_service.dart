// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 2/18/2023
// Updated: 4/15/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Package imports:
import 'package:file_picker/file_picker.dart';
import 'package:firebase_auth/firebase_auth.dart';
import 'package:firebase_storage/firebase_storage.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

// Project imports:
import 'package:cannlytics_data/services/firestore_service.dart';

// Firebase Authentication provider.
final firebaseAuth = Provider<FirebaseAuth>((ref) => FirebaseAuth.instance);

// Authentication service provider.
final authProvider = Provider<AuthService>((ref) {
  return AuthService(
    ref.watch(firebaseAuth),
    ref.watch(firestoreProvider),
  );
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

  /// Sign in with email and password.
  Future<String> signIn(
    String email,
    String password,
  ) async {
    try {
      await _auth.signInWithEmailAndPassword(
        email: email,
        password: password,
      );
      return 'success';
    } catch (e) {
      return e.toString();
    }
  }

  /// Create a user with email and password.
  Future<String> signUp(
    String email,
    String password,
  ) async {
    try {
      await _auth.createUserWithEmailAndPassword(
        email: email,
        password: password,
      );
      return 'success';
    } catch (e) {
      return e.toString();
    }
  }

  /// Sign the user out.
  Future<String> signOut() async {
    try {
      await _auth.signOut();
      return 'success';
    } catch (e) {
      return e.toString();
    }
  }

  /// Change the user's photo.
  Future<String> changePhoto() async {
    try {
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
      return 'success';
    } catch (e) {
      return e.toString();
    }
  }

  /// Send the user a password reset email.
  Future<String> resetPassword(String email) async {
    try {
      await _auth.sendPasswordResetEmail(email: email);
      return 'success';
    } catch (e) {
      return e.toString();
    }
  }

  /// Danger zone: Allow the user to delete their account.
  Future<String> deleteAccount() async {
    User? user = FirebaseAuth.instance.currentUser;
    try {
      // Delete the user's data from Firestore.
      _firestore.deleteData(path: 'users/${user?.uid}');
    } catch (e) {
      // Unable to delete user data.
    }
    try {
      // Delete the user's account.
      await user!.delete();
      return 'success';
    } catch (e) {
      return e.toString();
    }
  }
}

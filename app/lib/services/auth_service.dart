// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 2/18/2023
// Updated: 7/14/2023
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
  const AuthService(this._auth, this._firestore);

  // Parameters.
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
      String errorString = e.toString();
      if (errorString.contains('invalid-email')) {
        return 'The email address provided is not valid.';
      } else if (errorString.contains('user-disabled')) {
        return 'The user corresponding to the given email has been disabled.';
      } else if (errorString.contains('user-not-found')) {
        return 'There is no user corresponding to the given email.';
      } else if (errorString.contains('wrong-password')) {
        return 'The password is invalid for the given email, or the account corresponding to the email does not have a password set.';
      } else {
        return 'An unknown error occurred: $errorString';
      }
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
      String errorString = e.toString();
      if (errorString.contains('email-already-in-use')) {
        return 'There already exists an account with the given email address.';
      } else if (errorString.contains('invalid-email')) {
        return 'The email address provided is not valid.';
      } else if (errorString.contains('operation-not-allowed')) {
        return 'Email/password accounts are not enabled. Please enable email/password accounts in the Firebase Console, under the Auth tab.';
      } else if (errorString.contains('weak-password')) {
        return 'The password is not strong enough.';
      } else {
        return 'An unknown error occurred: $errorString';
      }
    }
  }

  /// Sign the user out.
  Future<String> signOut() async {
    try {
      await _auth.signOut();
      return 'success';
    } catch (e) {
      return 'An error occurred: ${e.toString()}';
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
          await _firestore.updateDocument(
            path: 'users/${user.uid}',
            data: {
              'photo_url': downloadURL,
              'photo_ref': photoRef,
            },
          );

          // Update the user's photo URL in their public profile.
          await _firestore.updateDocument(
            path: 'users/${user.uid}/public_user_data/profile',
            data: {'photo_url': downloadURL},
          );

          // Update the user's photo URL in Firebase Authentication.
          await user.updatePhotoURL(downloadURL);
          await user.reload();
        }
      }
      return 'success';
    } catch (e) {
      String errorString = e.toString();
      if (errorString.contains('permission-denied')) {
        return 'You do not have the necessary permissions to change the photo.';
      } else if (errorString.contains('network-request-failed')) {
        return 'Network error occurred while trying to change the photo. Please try again.';
      } else if (errorString.contains('unknown')) {
        return 'An unknown error occurred while trying to change the photo. Please try again.';
      } else {
        return 'An error occurred: $errorString';
      }
    }
  }

  /// Send the user a password reset email.
  Future<String> resetPassword(String email) async {
    try {
      await _auth.sendPasswordResetEmail(email: email);
      return 'success';
    } catch (e) {
      String errorString = e.toString();
      if (errorString.contains('invalid-email')) {
        return 'The email address provided is not valid.';
      } else if (errorString.contains('missing-email')) {
        return 'Email address required.';
      } else if (errorString.contains('missing-android-pkg-name')) {
        return 'An Android package name must be provided if the Android app is required to be installed.';
      } else if (errorString.contains('missing-continue-uri')) {
        return 'A continue URL must be provided in the request.';
      } else if (errorString.contains('missing-ios-bundle-id')) {
        return 'An iOS Bundle ID must be provided if an App Store ID is provided.';
      } else if (errorString.contains('invalid-continue-uri')) {
        return 'The continue URL provided in the request is invalid.';
      } else if (errorString.contains('unauthorized-continue-uri')) {
        return 'The domain of the continue URL is not whitelisted. Please whitelist the domain in the Firebase console.';
      } else if (errorString.contains('user-not-found')) {
        return 'There is no user corresponding to the given email.';
      } else {
        return 'An unknown error occurred: $errorString';
      }
    }
  }

  /// Danger zone: Allow the user to delete their account.
  Future<String> deleteAccount() async {
    User? user = FirebaseAuth.instance.currentUser;
    try {
      // Delete the user's data from Firestore.
      _firestore.deleteDocument(path: 'users/${user?.uid}');
    } catch (e) {
      // Unable to delete user data.
    }
    try {
      // Delete the user's account.
      await user!.delete();
      return 'success';
    } catch (e) {
      String errorString = e.toString();
      if (errorString.contains('requires-recent-login')) {
        return 'Your last sign-in time does not meet the security threshold. Please reauthenticate.';
      } else {
        return 'An unknown error occurred: $errorString';
      }
    }
  }
}

// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 2/18/2023
// Updated: 2/20/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>
import 'package:firebase_auth/firebase_auth.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

/// [AuthService] manages authentication with Firebase.
class AuthService {
  AuthService(this._auth);
  final FirebaseAuth _auth;

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
}

/// An instance of Firebase Authentication provider.
final firebaseAuthProvider =
    Provider<FirebaseAuth>((ref) => FirebaseAuth.instance);

final authServiceProvider = Provider<AuthService>((ref) {
  return AuthService(ref.watch(firebaseAuthProvider));
});

final authStateChangesProvider = StreamProvider<User?>((ref) {
  return ref.watch(authServiceProvider).authStateChanges();
});

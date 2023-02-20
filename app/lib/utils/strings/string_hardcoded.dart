// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 2/17/2023
// Updated: 2/20/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

/// A simple placeholder that can be used to search all the hardcoded strings
/// in the code (useful to identify strings that need to be localized).
extension StringHardcoded on String {
  String get hardcoded => this;
}

/// [Strings] are text found in the app to make localization easier.
///
/// Note: Localization is the translation of text between languages.
/// Future work: Populate strings used in the app for localization.
class Strings {
  static const String account = 'Account';
  static const String accountPage = 'Account Page';
  static const String cancel = 'Cancel';
  static const String goAnonymous = 'Go anonymous';
  static const String home = 'Home';
  static const String logout = 'Logout';
  static const String logoutAreYouSure =
      'Are you sure that you want to logout?';
  static const String logoutFailed = 'Logout failed';
  static const String ok = 'OK';
  static const String or = 'or';
  static const String signIn = 'Sign in';
  static const String signInWithEmailPassword = 'Sign in with email & password';
  static const String signInFailed = 'Sign in failed';
}

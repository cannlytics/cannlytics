// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 2/17/2023
// Updated: 2/19/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>
import 'package:cannlytics_app/utils/strings/string_hardcoded.dart';

/// Form type for email & password authentication
enum SignInFormType { signIn, register }

extension SignInFormTypeX on SignInFormType {
  String get passwordLabelText {
    if (this == SignInFormType.register) {
      return 'Password (8+ characters)'.hardcoded;
    } else {
      return 'Password'.hardcoded;
    }
  }

  // Getters
  String get primaryButtonText {
    if (this == SignInFormType.register) {
      return 'Create an account'.hardcoded;
    } else {
      return 'Sign in'.hardcoded;
    }
  }

  String get secondaryButtonText {
    if (this == SignInFormType.register) {
      return 'Have an account? Sign in'.hardcoded;
    } else {
      return 'Need an account? Register'.hardcoded;
    }
  }

  SignInFormType get secondaryActionFormType {
    if (this == SignInFormType.register) {
      return SignInFormType.signIn;
    } else {
      return SignInFormType.register;
    }
  }

  String get errorAlertTitle {
    if (this == SignInFormType.register) {
      return 'Registration failed'.hardcoded;
    } else {
      return 'Sign in failed'.hardcoded;
    }
  }

  String get title {
    if (this == SignInFormType.register) {
      return 'Register'.hardcoded;
    } else {
      return 'Sign in'.hardcoded;
    }
  }
}

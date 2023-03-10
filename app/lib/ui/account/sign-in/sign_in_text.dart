// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 2/17/2023
// Updated: 3/9/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

/// Form type for email & password authentication
enum SignInFormType { signIn, register }

extension SignInFormTypeX on SignInFormType {
  String get passwordLabelText {
    if (this == SignInFormType.register) {
      return 'Password (8+ characters)';
    } else {
      return 'Password';
    }
  }

  // Getters
  String get primaryButtonText {
    if (this == SignInFormType.register) {
      return 'Create an account';
    } else {
      return 'Sign in';
    }
  }

  String get secondaryButtonText {
    if (this == SignInFormType.register) {
      return 'Have an account? Sign in';
    } else {
      return 'Need an account? Register';
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
      return 'Registration failed';
    } else {
      return 'Sign in failed';
    }
  }

  String get title {
    if (this == SignInFormType.register) {
      return 'Register';
    } else {
      return 'Sign in';
    }
  }
}

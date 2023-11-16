// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 2/18/2023
// Updated: 3/9/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Project imports:
import 'package:cannlytics_app/ui/account/sign-in/sign_in_text.dart';
import 'package:cannlytics_app/utils/validation_utils.dart';

/// Mixin class to be used for client-side email & password validation
mixin EmailAndPasswordValidators {
  final StringValidator emailSubmitValidator = EmailSubmitRegexValidator();
  final StringValidator passwordRegisterSubmitValidator =
      MinLengthStringValidator(8);
  final StringValidator passwordSignInSubmitValidator =
      NonEmptyStringValidator();

  bool canSubmitEmail(String email) {
    return emailSubmitValidator.isValid(email);
  }

  bool canSubmitPassword(String password, SignInFormType formType) {
    if (formType == SignInFormType.register) {
      return passwordRegisterSubmitValidator.isValid(password);
    }
    return passwordSignInSubmitValidator.isValid(password);
  }

  String? emailErrorText(String email) {
    final bool showErrorText = !canSubmitEmail(email);
    final String errorText =
        email.isEmpty ? 'Email can\'t be empty' : 'Invalid email';
    return showErrorText ? errorText : null;
  }

  String? passwordErrorText(String password, SignInFormType formType) {
    final bool showErrorText = !canSubmitPassword(password, formType);
    final String errorText =
        password.isEmpty ? 'Password can\'t be empty' : 'Password is too short';
    return showErrorText ? errorText : null;
  }
}
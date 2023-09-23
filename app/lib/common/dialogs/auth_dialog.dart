// Cannlytics Data
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 4/14/2023
// Updated: 6/24/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Flutter imports:
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

// Package imports:
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_svg/flutter_svg.dart';
import 'package:go_router/go_router.dart';

// Project imports:
import 'package:cannlytics_data/common/buttons/custom_text_button.dart';
import 'package:cannlytics_data/common/buttons/primary_button.dart';
import 'package:cannlytics_data/constants/design.dart';
import 'package:cannlytics_data/constants/theme.dart';
import 'package:cannlytics_data/ui/account/account_controller.dart';
import 'package:cannlytics_data/utils/utils.dart';
import 'package:cannlytics_data/utils/validation_utils.dart';

/// Sign in / create account form.
class SignInDialog extends ConsumerStatefulWidget {
  const SignInDialog({
    super.key,
    required this.isSignUp,
  });

  /// The default form type to use.
  final bool isSignUp;

  @override
  ConsumerState<SignInDialog> createState() => _SignInDialogState();
}

/// Sign in / create account form state.
class _SignInDialogState extends ConsumerState<SignInDialog>
    with EmailAndPasswordValidators {
  // Controllers.
  final _formKey = GlobalKey<FormState>();
  final _node = FocusScopeNode();
  final _emailController = TextEditingController();
  final _passwordController = TextEditingController();

  // State.
  String get email => _emailController.text;
  String get password => _passwordController.text;
  var _submitted = false;
  late var _isSignUp = widget.isSignUp;

  // Dispose controllers.
  @override
  void dispose() {
    _node.dispose();
    _emailController.dispose();
    _passwordController.dispose();
    super.dispose();
  }

  /// Submit the sign-in form if validation passes.
  Future<void> _submit() async {
    setState(() => _submitted = true);
    if (_formKey.currentState!.validate()) {
      // Sign up or sign in.
      final controller = ref.read(signInProvider.notifier);
      var message;
      if (_isSignUp) {
        message = await controller.signUp(email: email, password: password);
      } else {
        message = await controller.signIn(email: email, password: password);
      }
      if (message == 'success') {
        // Close the dialog.
        Navigator.of(context).pop(false);
      } else {
        // Display an error message if an authentication error occurs.
        message = message.replaceAll(RegExp(r'\[.*?\]'), '');
        InterfaceUtils.showAlertDialog(
          context: context,
          title: 'Error',
          content: message,
          primaryActionColor: Colors.redAccent,
        );
      }
    }
  }

  // Indicator if email is entered.
  void _emailEditingComplete() {
    if (canSubmitEmail(email)) {
      _node.nextFocus();
    }
  }

  // Indicator if password is entered.
  void _passwordEditingComplete() {
    if (!canSubmitEmail(email)) {
      _node.previousFocus();
      return;
    }
    _submit();
  }

  // Toggle between register and sign in form, clearing the password field.
  void _updateFormType() {
    setState(() => _isSignUp = !_isSignUp);
    _passwordController.clear();
  }

  // User interface.
  @override
  Widget build(BuildContext context) {
    // Listen to the user's state.
    final state = ref.watch(signInProvider);

    // Get the theme.
    final themeMode = ref.watch(themeModeProvider);
    final bool isDark = themeMode == ThemeMode.dark;

    var column = Column(
      mainAxisSize: MainAxisSize.min,
      crossAxisAlignment: CrossAxisAlignment.center,
      children: <Widget>[
        // Close button.
        Row(
          mainAxisAlignment: MainAxisAlignment.end,
          children: [
            IconButton(
              icon: Icon(Icons.close),
              onPressed: () => Navigator.of(context).pop(false),
            ),
          ],
        ),
        // Logo
        gapH24,
        SizedBox(
          width: 200,
          height: 50,
          child: SvgPicture.asset(
            isDark
                ? 'assets/images/logos/logo_dark.svg'
                : 'assets/images/logos/logo_light.svg',
            semanticsLabel: 'Cannlytics',
          ),
        ),
        gapH6,

        // Title.
        Text(
          (_isSignUp) ? 'Sign Up' : 'Sign In',
          style: Theme.of(context).textTheme.titleLarge!.copyWith(
                color: Theme.of(context).textTheme.titleLarge!.color,
                fontSize: 18,
              ),
        ),
        gapH18,

        // Email field.
        TextFormField(
          controller: _emailController,
          key: Key('email'),
          autofocus: true,
          autocorrect: false,
          autovalidateMode: AutovalidateMode.onUserInteraction,
          validator: (email) =>
              !_submitted ? null : emailErrorText(email ?? ''),
          textInputAction: TextInputAction.next,
          keyboardType: TextInputType.emailAddress,
          keyboardAppearance: Brightness.light,
          onEditingComplete: () => _emailEditingComplete(),
          inputFormatters: <TextInputFormatter>[
            ValidatorInputFormatter(
              editingValidator: EmailEditingRegexValidator(),
            ),
          ],
          style: Theme.of(context).textTheme.titleMedium,
          decoration: InputDecoration(
            labelText: 'Email',
            // hintText: 'test@cannlytics.com',
            enabled: !state.isLoading,
            floatingLabelBehavior: FloatingLabelBehavior.auto,
            contentPadding: EdgeInsets.only(
              top: 18,
              left: 8,
              right: 8,
              bottom: 8,
            ),
          ),
        ),

        // Spacer.
        gapH18,

        // Password field.
        TextFormField(
          key: Key('password'),
          controller: _passwordController,
          obscureText: true,
          autocorrect: false,
          autovalidateMode: AutovalidateMode.onUserInteraction,
          validator: (password) =>
              !_submitted ? null : passwordErrorText(password ?? '', _isSignUp),
          textInputAction: TextInputAction.done,
          keyboardAppearance: Brightness.light,
          onEditingComplete: () => _passwordEditingComplete(),
          style: Theme.of(context).textTheme.titleMedium,
          decoration: InputDecoration(
            labelText: _isSignUp ? 'Password (8+ characters)' : 'Password',
            enabled: !state.isLoading,
            floatingLabelBehavior: FloatingLabelBehavior.auto,
            contentPadding: EdgeInsets.only(
              top: 18,
              left: 8,
              right: 8,
              bottom: 8,
            ),
          ),
        ),

        // Spacer.
        gapH18,

        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            // Reset password button.
            CustomTextButton(
              text: 'Lost Password?',
              onPressed: () {
                context.go('/account/reset-password');
              },
            ),

            // Submit button.
            PrimaryButton(
              text: _isSignUp ? 'Sign Up' : 'Sign In',
              isLoading: state.isLoading,
              onPressed: state.isLoading ? null : () => _submit(),
            ),
          ],
        ),

        // Spacer.
        gapH48,

        // Change forms (sign-in to register) button.
        CustomTextButton(
          text: _isSignUp ? 'Sign In' : 'Register',
          onPressed: state.isLoading ? null : _updateFormType,
        ),
      ],
    );

    // Add an animation to the card.
    return AlertDialog(
      backgroundColor: Theme.of(context).scaffoldBackgroundColor,
      contentPadding: EdgeInsets.all(16.0),
      content: FocusScope(
        node: _node,
        child: Form(
          key: _formKey,
          child: SingleChildScrollView(
            child: column,
          ),
        ),
      ),
    ); // .animate().shimmer(duration: 800.ms)
  }
}

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

  bool canSubmitPassword(String password, bool isSignUp) {
    if (isSignUp) {
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

  String? passwordErrorText(String password, bool isSignUp) {
    final bool showErrorText = !canSubmitPassword(password, isSignUp);
    final String errorText =
        password.isEmpty ? 'Password can\'t be empty' : 'Password is too short';
    return showErrorText ? errorText : null;
  }
}

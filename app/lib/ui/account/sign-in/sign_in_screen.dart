// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 2/18/2023
// Updated: 2/19/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>
import 'package:cannlytics_app/ui/account/onboarding/onboarding_controller.dart';
import 'package:cannlytics_app/utils/strings/string_format.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:cannlytics_app/widgets/custom_text_button.dart';
import 'package:cannlytics_app/widgets/primary_button.dart';
import 'package:cannlytics_app/widgets/responsive_scrollable_card.dart';
import 'package:cannlytics_app/constants/design.dart';
import 'package:cannlytics_app/ui/account/sign-in/sign_in_controller.dart';
import 'package:cannlytics_app/ui/account/sign-in/sign_in_text.dart';
import 'package:cannlytics_app/ui/account/sign-in/sign_in_validators.dart';
import 'package:cannlytics_app/utils/strings/string_validators.dart';
import 'package:cannlytics_app/utils/strings/string_hardcoded.dart';
import 'package:cannlytics_app/utils/dialogs/alert_dialog_ui.dart';

/// Sign in screen.
class EmailPasswordSignInScreen extends ConsumerWidget {
  const EmailPasswordSignInScreen({
    super.key,
    required this.formType,
  });
  final SignInFormType formType;

  // Keys for testing using find.byKey()
  static const emailKey = Key('email');
  static const passwordKey = Key('password');

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final store = ref.watch(onboardingStoreProvider);
    return Scaffold(
      appBar: AppBar(title: Text(Format.capitalize(store.userType()))),
      body: SignInForm(formType: formType),
    );
  }
}

/// Email & password authentication, supporting sign in and create an account.
class SignInForm extends ConsumerStatefulWidget {
  const SignInForm({
    super.key,
    required this.formType,
  });

  /// The default form type to use.
  final SignInFormType formType;
  @override
  ConsumerState<SignInForm> createState() => _SignInFormState();
}

class _SignInFormState extends ConsumerState<SignInForm>
    with EmailAndPasswordValidators {
  // Widget controllers.
  final _formKey = GlobalKey<FormState>();
  final _node = FocusScopeNode();
  final _emailController = TextEditingController();
  final _passwordController = TextEditingController();

  // Widget state.
  String get email => _emailController.text;
  String get password => _passwordController.text;
  var _submitted = false;
  late var _formType = widget.formType;

  // Dispose controllers.
  @override
  void dispose() {
    _node.dispose();
    _emailController.dispose();
    _passwordController.dispose();
    super.dispose();
  }

  // Submit the sign-in form if validation passes.
  Future<void> _submit() async {
    setState(() => _submitted = true);
    if (_formKey.currentState!.validate()) {
      final controller = ref.read(signInProvider.notifier);
      await controller.signIn(
        email: email,
        password: password,
        formType: _formType,
      );
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
    setState(() => _formType = _formType.secondaryActionFormType);
    _passwordController.clear();
  }

  // User interface.
  @override
  Widget build(BuildContext context) {
    ref.listen<AsyncValue>(
      signInProvider,
      (_, state) => state.showAlertDialogOnError(context),
    );
    final state = ref.watch(signInProvider);
    return ResponsiveScrollableCard(
      child: FocusScope(
        node: _node,
        child: Form(
          key: _formKey,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: <Widget>[
              // Spacer.
              gapH8,

              // Email field.
              TextFormField(
                key: EmailPasswordSignInScreen.emailKey,
                controller: _emailController,
                decoration: InputDecoration(
                  labelText: 'Email'.hardcoded,
                  hintText: 'test@test.com'.hardcoded,
                  enabled: !state.isLoading,
                ),
                autovalidateMode: AutovalidateMode.onUserInteraction,
                validator: (email) =>
                    !_submitted ? null : emailErrorText(email ?? ''),
                autocorrect: false,
                textInputAction: TextInputAction.next,
                keyboardType: TextInputType.emailAddress,
                keyboardAppearance: Brightness.light,
                onEditingComplete: () => _emailEditingComplete(),
                inputFormatters: <TextInputFormatter>[
                  ValidatorInputFormatter(
                      editingValidator: EmailEditingRegexValidator()),
                ],
              ),

              // Spacer.
              gapH8,

              // Password field.
              TextFormField(
                key: EmailPasswordSignInScreen.passwordKey,
                controller: _passwordController,
                decoration: InputDecoration(
                  labelText: _formType.passwordLabelText,
                  enabled: !state.isLoading,
                ),
                autovalidateMode: AutovalidateMode.onUserInteraction,
                validator: (password) => !_submitted
                    ? null
                    : passwordErrorText(password ?? '', _formType),
                obscureText: true,
                autocorrect: false,
                textInputAction: TextInputAction.done,
                keyboardAppearance: Brightness.light,
                onEditingComplete: () => _passwordEditingComplete(),
              ),

              // Spacer.
              gapH8,

              // Submit button.
              PrimaryButton(
                text: _formType.primaryButtonText,
                isLoading: state.isLoading,
                onPressed: state.isLoading ? null : () => _submit(),
              ),

              // Spacer.
              gapH8,

              // Change forms (sign-in to register) button.
              CustomTextButton(
                text: _formType.secondaryButtonText,
                onPressed: state.isLoading ? null : _updateFormType,
              ),

              // Spacer.
              gapH8,

              // Anonymous sign-in.
              if (_formType == SignInFormType.signIn)
                CustomTextButton(
                  key: const Key('anonymous'),
                  text: 'Try anonymously',
                  onPressed: state.isLoading
                      ? null
                      : () =>
                          ref.read(signInProvider.notifier).signInAnonymously(),
                ),
            ],
          ),
        ),
      ),
    );
  }
}

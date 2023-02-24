// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 2/18/2023
// Updated: 2/19/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Flutter imports:
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

// Package imports:
import 'package:flutter_riverpod/flutter_riverpod.dart';

// Project imports:
import 'package:cannlytics_app/constants/colors.dart';
import 'package:cannlytics_app/constants/design.dart';
import 'package:cannlytics_app/services/theme_service.dart';
import 'package:cannlytics_app/ui/account/onboarding/onboarding_controller.dart';
import 'package:cannlytics_app/ui/account/sign-in/sign_in_controller.dart';
import 'package:cannlytics_app/ui/account/sign-in/sign_in_text.dart';
import 'package:cannlytics_app/ui/account/sign-in/sign_in_validators.dart';
import 'package:cannlytics_app/utils/dialogs/alert_dialog_ui.dart';
import 'package:cannlytics_app/utils/strings/string_format.dart';
import 'package:cannlytics_app/utils/strings/string_hardcoded.dart';
import 'package:cannlytics_app/utils/strings/string_validators.dart';
import 'package:cannlytics_app/widgets/buttons/custom_text_button.dart';
import 'package:cannlytics_app/widgets/buttons/primary_button.dart';
import 'package:cannlytics_app/widgets/layout/responsive_scrollable_card.dart';

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
    final themeMode = ref.watch(themeModeProvider);
    final bool isDark = themeMode == ThemeMode.dark;
    return Scaffold(
      // appBar: AppBar(title: Text(Format.capitalize(store.userType()))),
      // backgroundColor: AppColors.surface,
      // body: SignInForm(formType: formType),
      body: CustomScrollView(
        slivers: [
          // Light / dark theme toggle.
          const SliverToBoxAdapter(child: ThemeToggle()),

          // Logo.
          SliverToBoxAdapter(child: appLogo(isDark)),

          // User type.
          // FIXME: Allow the user to toggle their type here on sign-in.
          SliverToBoxAdapter(child: userTypeButton(context, store)),

          // Sign in form.
          SliverToBoxAdapter(
            child: SignInForm(formType: formType),
          ),

          // TODO: Terms.

          // TODO: Copyright.
        ],
      ),
    );
  }

  /// A simple logo widget.
  Widget appLogo(bool isDark) {
    return FractionallySizedBox(
      widthFactor: 0.5,
      child: Image.asset(
        isDark
            ? 'assets/images/logos/cannlytics_logo_with_text_light.png'
            : 'assets/images/logos/cannlytics_logo_with_text_dark.png',
        height: 45,
      ),
    );
  }

  /// A simple user type choice widget.
  Widget userTypeButton(BuildContext context, OnboardingStore store) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.symmetric(vertical: 6),
        child: CustomTextButton(
          text: Format.capitalize(store.userType()),
          onPressed: () {
            print(
                'FIXME: Allow the user to toggle between business and consumer.');
            if (store.userType() == 'business') {
              store.setUserType('consumer');
            } else {
              store.setUserType('business');
            }
          },
          style: Theme.of(context).textTheme.titleSmall,
        ),
      ),
    );
  }
}

/// Light / dark theme toggle.
class ThemeToggle extends StatelessWidget {
  const ThemeToggle({super.key});

  @override
  Widget build(BuildContext context) {
    return Consumer(builder: (context, ref, child) {
      final theme = ref.watch(themeModeProvider);
      return Row(
        mainAxisAlignment: MainAxisAlignment.end,
        children: [
          Padding(
            padding: const EdgeInsets.all(6),
            child: IconButton(
              splashRadius: 18,
              onPressed: () {
                // Toggle light / dark theme.
                ref.read(themeModeProvider.notifier).state =
                    theme == ThemeMode.light ? ThemeMode.dark : ThemeMode.light;
              },
              icon: Icon(
                theme == ThemeMode.dark ? Icons.light_mode : Icons.dark_mode,
                color: AppColors.neutral4,
              ),
            ),
          ),
        ],
      );
    });
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
            crossAxisAlignment: CrossAxisAlignment.center,
            children: <Widget>[
              // Spacer.
              gapH8,

              // Email field.
              TextFormField(
                key: EmailPasswordSignInScreen.emailKey,
                controller: _emailController,
                decoration: InputDecoration(
                  labelText: 'Email'.hardcoded,
                  hintText: 'test@cannlytics.com'.hardcoded,
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
              gapH18,

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
                style: Theme.of(context).textTheme.titleSmall,
              ),

              // Anonymous sign-in.
              // gapH8,
              // if (_formType == SignInFormType.signIn)
              //   CustomTextButton(
              //     key: const Key('anonymous'),
              //     text: 'Try anonymously',
              //     onPressed: state.isLoading
              //         ? null
              //         : () =>
              //             ref.read(signInProvider.notifier).signInAnonymously(),
              //   ),
            ],
          ),
        ),
      ),
    );
  }
}

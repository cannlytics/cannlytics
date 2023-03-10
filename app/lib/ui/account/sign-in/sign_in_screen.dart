// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 2/18/2023
// Updated: 3/6/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Flutter imports:
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

// Package imports:
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:toggle_switch/toggle_switch.dart';

// Project imports:
import 'package:cannlytics_app/constants/design.dart';
import 'package:cannlytics_app/constants/theme.dart';
import 'package:cannlytics_app/routing/routes.dart';
import 'package:cannlytics_app/services/theme_service.dart';
import 'package:cannlytics_app/ui/account/sign-in/sign_in_controller.dart';
import 'package:cannlytics_app/ui/account/sign-in/sign_in_text.dart';
import 'package:cannlytics_app/ui/account/sign-in/sign_in_validators.dart';
import 'package:cannlytics_app/ui/general/app_controller.dart';
import 'package:cannlytics_app/ui/general/footer_simple.dart';
import 'package:cannlytics_app/widgets/dialogs/alert_dialog_ui.dart';
import 'package:cannlytics_app/utils/validation_utils.dart';
import 'package:cannlytics_app/widgets/buttons/custom_text_button.dart';
import 'package:cannlytics_app/widgets/buttons/primary_button.dart';
import 'package:cannlytics_app/widgets/buttons/theme_button.dart';
import 'package:cannlytics_app/widgets/images/app_logo.dart';
import 'package:cannlytics_app/widgets/cards/responsive_card.dart';

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
    // Get the theme.
    final themeMode = ref.watch(themeModeProvider);
    final bool isDark = themeMode == ThemeMode.dark;

    // Build the layout.
    return Scaffold(
      body: Container(
        decoration: BoxDecoration(
          gradient: RadialGradient(
            center: Alignment(1, -1),
            radius: 4.0,
            colors: [
              isDark ? Colors.green : AppColors.neutral1,
              isDark ? Colors.transparent : Colors.white,
            ],
          ),
        ),
        child: CustomScrollView(
          slivers: [
            // Light / dark theme toggle.
            SliverToBoxAdapter(child: ThemeToggle(isDark: isDark)),

            // Logo.
            SliverToBoxAdapter(child: ResponsiveAppLogo(isDark: isDark)),

            // User type selection.
            SliverToBoxAdapter(child: UserTypeButton()),

            // Sign in form.
            SliverToBoxAdapter(
              child: SignInForm(formType: formType, isDark: isDark),
            ),

            // Footer
            const SliverToBoxAdapter(child: SimpleFooter()),
          ],
        ),
      ),
    );
  }
}

/// Widget to let the user choose their type: "Consumer" or "Business".
class UserTypeButton extends ConsumerWidget {
  const UserTypeButton({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    // Get the user type.
    final userType = ref.watch(userTypeProvider);

    // Render a toggle switch.
    // FIXME: Use `CupertinoSegmentedControl` instead
    // because it will be 1 less dependency.
    return Padding(
      padding: EdgeInsets.symmetric(vertical: 16),
      child: Center(
        child: ToggleSwitch(
          initialLabelIndex: (userType == 'consumer') ? 0 : 1,
          labels: ['Consumer', 'Business'],
          minHeight: 32,
          customWidths: [100.0, 100.0],
          cornerRadius: 20.0,
          activeFgColor: Colors.white,
          inactiveBgColor: Colors.grey,
          inactiveFgColor: Colors.white,
          totalSwitches: 2,
          // icons: [FontAwesomeIcons.mars, FontAwesomeIcons.venus],
          activeBgColors: [
            [Colors.green],
            [Colors.orange]
          ],
          onToggle: (index) {
            // Switch between user type.
            if (index == 0) {
              ref.read(userTypeProvider.notifier).update((state) => 'consumer');
            } else {
              ref.read(userTypeProvider.notifier).update((state) => 'business');
            }
          },
        ),
      ),
    );
  }
}

/// Sign in / create account form.
class SignInForm extends ConsumerStatefulWidget {
  const SignInForm({
    super.key,
    required this.formType,
    required this.isDark,
  });

  /// The default form type to use.
  final SignInFormType formType;
  final bool isDark;

  @override
  ConsumerState<SignInForm> createState() => _SignInFormState();
}

/// Sign in / create account form state.
class _SignInFormState extends ConsumerState<SignInForm>
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
      context.go('/dashboard');
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
    return ResponsiveCard(
      isDark: widget.isDark,
      child: FocusScope(
        node: _node,
        child: Form(
          key: _formKey,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.center,
            children: <Widget>[
              // Title.
              Text(
                (_formType == SignInFormType.signIn) ? 'Sign In' : 'Sign Up',
                style: Theme.of(context).textTheme.titleLarge!.copyWith(
                      color: Theme.of(context).textTheme.titleLarge!.color,
                    ),
              ),

              // Spacer.
              gapH8,

              // Email field.
              TextFormField(
                key: EmailPasswordSignInScreen.emailKey,
                controller: _emailController,
                decoration: InputDecoration(
                  labelText: 'Email',
                  hintText: 'test@cannlytics.com',
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
                // FIXME: Error color is white!
                // style: TextStyle().copyWith(),
                onEditingComplete: () => _passwordEditingComplete(),
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
                      context.goNamed(AppRoutes.resetPassword.name);
                    },
                  ),

                  // Submit button.
                  PrimaryButton(
                    text: _formType.primaryButtonText,
                    isLoading: state.isLoading,
                    onPressed: state.isLoading ? null : () => _submit(),
                  ),
                ],
              ),

              // Spacer.
              gapH24,

              // Change forms (sign-in to register) button.
              CustomTextButton(
                text: _formType.secondaryButtonText,
                onPressed: state.isLoading ? null : _updateFormType,
              ),

              // TODO: Anonymous sign-in.
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

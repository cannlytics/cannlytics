// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 2/18/2023
// Updated: 3/19/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Flutter imports:
import 'package:cannlytics_app/constants/colors.dart';
import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_animate/flutter_animate.dart';

// Package imports:
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_svg/flutter_svg.dart';
import 'package:go_router/go_router.dart';

// Project imports:
import 'package:cannlytics_app/constants/design.dart';
import 'package:cannlytics_app/routing/routes.dart';
import 'package:cannlytics_app/services/theme_service.dart';
import 'package:cannlytics_app/ui/account/sign-in/sign_in_controller.dart';
import 'package:cannlytics_app/ui/account/sign-in/sign_in_text.dart';
import 'package:cannlytics_app/ui/account/sign-in/sign_in_validators.dart';
import 'package:cannlytics_app/ui/layout/footer_simple.dart';
import 'package:cannlytics_app/ui/main/app_controller.dart';
import 'package:cannlytics_app/utils/validation_utils.dart';
import 'package:cannlytics_app/widgets/buttons/custom_text_button.dart';
import 'package:cannlytics_app/widgets/buttons/primary_button.dart';
import 'package:cannlytics_app/widgets/buttons/theme_button.dart';
import 'package:cannlytics_app/widgets/cards/responsive_card.dart';
import 'package:cannlytics_app/widgets/dialogs/alert_dialog_ui.dart';

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
    return Container(
      decoration: BoxDecoration(
        gradient: RadialGradient(
          center: Alignment(1, -1),
          radius: 4.0,
          colors: [
            isDark ? DarkColors.base : LightColors.base,
            isDark ? DarkColors.crust : LightColors.crust,
          ],
        ),
      ),
      child: CustomScrollView(
        slivers: [
          // Light / dark theme toggle.
          SliverToBoxAdapter(
              child: ThemeToggle(isDark: isDark)
                  .animate()
                  .fadeIn(duration: 2000.ms)),

          // Logo.
          // SliverToBoxAdapter(child: ResponsiveAppLogo(isDark: isDark)),

          // User type selection.
          // SliverToBoxAdapter(child: gapH12),
          // SliverToBoxAdapter(child: UserTypeButton()),

          // Sign in form.
          SliverToBoxAdapter(
            child: SignInForm(formType: formType, isDark: isDark),
          ),

          // Footer
          SliverToBoxAdapter(
              child: SimpleFooter().animate().fadeIn(duration: 2000.ms)),
        ],
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
    // Listen to the user's state.
    ref.listen<AsyncValue>(
      signInProvider,
      (_, state) => state.showAlertDialogOnError(context),
    );
    final state = ref.watch(signInProvider);

    // Get the theme.
    final themeMode = ref.watch(themeModeProvider);
    final bool isDark = themeMode == ThemeMode.dark;

    // Build the form.
    Widget card = ResponsiveCard(
      child: FocusScope(
        node: _node,
        child: Form(
          key: _formKey,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.center,
            children: <Widget>[
              // Logo
              gapH12,
              // ResponsiveAppLogo(isDark: isDark),
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
                (_formType == SignInFormType.signIn) ? 'Sign In' : 'Sign Up',
                style: Theme.of(context).textTheme.titleLarge!.copyWith(
                      color: Theme.of(context).textTheme.titleLarge!.color,
                      fontSize: 18,
                    ),
              ),
              gapH18,

              // Email field.
              TextFormField(
                controller: _emailController,
                key: EmailPasswordSignInScreen.emailKey,
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
                  hintText: 'test@cannlytics.com',
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
                key: EmailPasswordSignInScreen.passwordKey,
                controller: _passwordController,
                obscureText: true,
                autocorrect: false,
                autovalidateMode: AutovalidateMode.onUserInteraction,
                validator: (password) => !_submitted
                    ? null
                    : passwordErrorText(password ?? '', _formType),
                textInputAction: TextInputAction.done,
                keyboardAppearance: Brightness.light,
                onEditingComplete: () => _passwordEditingComplete(),
                style: Theme.of(context).textTheme.titleMedium,
                decoration: InputDecoration(
                  labelText: _formType.passwordLabelText,
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
              gapH48,

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

    // Add an animation to the card.
    return card.animate().fadeIn(duration: 1600.ms);
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
    return Padding(
      padding: EdgeInsets.symmetric(vertical: 16),
      child: Center(
        child: CupertinoSegmentedControl<String>(
          borderColor: (userType == 'consumer') ? Colors.green : Colors.orange,
          selectedColor:
              (userType == 'consumer') ? Colors.green : Colors.orange,
          unselectedColor: Colors.transparent,
          padding: const EdgeInsets.symmetric(horizontal: 12),
          groupValue: userType,
          onValueChanged: (String value) {
            ref.read(userTypeProvider.notifier).update((state) => value);
          },
          children: <String, Widget>{
            'consumer': Padding(
              padding: EdgeInsets.symmetric(horizontal: 20),
              child: Text(
                'Consumer',
                style: Theme.of(context).textTheme.titleMedium!.copyWith(
                      color: Theme.of(context).textTheme.titleLarge!.color,
                    ),
              ),
            ),
            'business': Padding(
              padding: EdgeInsets.symmetric(horizontal: 20),
              child: Text(
                'Business',
                style: Theme.of(context).textTheme.titleMedium!.copyWith(
                      color: Theme.of(context).textTheme.titleLarge!.color,
                    ),
              ),
            ),
          },
        ),
      ),
    );
  }
}
// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 3/6/2023
// Updated: 3/6/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Flutter imports:
import 'package:cannlytics_app/constants/colors.dart';
import 'package:cannlytics_app/ui/main/app_controller.dart';
import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';

// Package imports:
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_svg/flutter_svg.dart';
import 'package:go_router/go_router.dart';

// Project imports:
import 'package:cannlytics_app/constants/design.dart';
import 'package:cannlytics_app/routing/routes.dart';
import 'package:cannlytics_app/services/theme_service.dart';
import 'package:cannlytics_app/ui/account/sign-in/sign_in_validators.dart';
import 'package:cannlytics_app/ui/account/user/account_controller.dart';
import 'package:cannlytics_app/ui/layout/footer_simple.dart';
import 'package:cannlytics_app/widgets/buttons/custom_text_button.dart';
import 'package:cannlytics_app/widgets/buttons/primary_button.dart';
import 'package:cannlytics_app/widgets/buttons/theme_button.dart';
import 'package:cannlytics_app/widgets/cards/responsive_card.dart';
import 'package:cannlytics_app/widgets/dialogs/alert_dialog_ui.dart';
import 'package:cannlytics_app/widgets/dialogs/alert_dialogs.dart';

/// Screen for the user to reset their password.
class ResetPasswordScreen extends ConsumerWidget {
  const ResetPasswordScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    // Get the theme.
    final themeMode = ref.watch(themeModeProvider);
    final bool isDark = themeMode == ThemeMode.dark;

    return Scaffold(
      body: Container(
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
            const SliverToBoxAdapter(child: ThemeToggle()),

            // Logo.
            SliverToBoxAdapter(
              // child: ResponsiveAppLogo(isDark: isDark)
              child: SizedBox(
                width: 200,
                height: 50,
                child: SvgPicture.asset(
                  isDark
                      ? 'assets/images/logos/logo_dark.svg'
                      : 'assets/images/logos/logo_light.svg',
                  semanticsLabel: 'Cannlytics',
                ),
              ),
            ),

            // Account management.
            SliverToBoxAdapter(
                child: ResetPasswordForm(isDark: isDark)
                    .animate()
                    .fadeIn(duration: 1600.ms)),

            // Footer
            const SliverToBoxAdapter(child: SimpleFooter()),
          ],
        ),
      ),
    );
  }
}

/// Reset password form.
class ResetPasswordForm extends ConsumerStatefulWidget {
  const ResetPasswordForm({
    super.key,
    required this.isDark,
  });

  // Properties.
  final bool isDark;

  @override
  ConsumerState<ResetPasswordForm> createState() => _ResetPasswordFormState();
}

/// Reset password form state.
class _ResetPasswordFormState extends ConsumerState<ResetPasswordForm>
    with EmailAndPasswordValidators {
  // Controllers.
  final _formKey = GlobalKey<FormState>();
  final _node = FocusScopeNode();
  final _emailController = TextEditingController();

  // State.
  String get email => _emailController.text;
  // ignore: unused_field
  var _submitted = false;

  // Dispose controllers.
  @override
  void dispose() {
    _node.dispose();
    _emailController.dispose();
    super.dispose();
  }

  // Submit the reset password form if validation passes.
  Future<void> _submit() async {
    setState(() => _submitted = true);
    if (_formKey.currentState!.validate()) {
      final controller = ref.read(accountProvider.notifier);
      await controller.resetPassword(email);
      showExceptionAlertDialog(
        context: context,
        title: 'Password reset email sent',
        exception: 'Check your email for a link to reset your password.',
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    // Listen to the account state.
    final state = ref.watch(accountProvider);
    ref.listen<AsyncValue>(
      accountProvider,
      (_, state) => state.showAlertDialogOnError(context),
    );

    // Get the screen width.
    final screenWidth = MediaQuery.of(context).size.width;

    // Listen to the current user.
    final user = ref.watch(userProvider).value;

    // Render the widget.
    return Padding(
      padding: EdgeInsets.only(
        left: sliverHorizontalPadding(screenWidth),
        right: sliverHorizontalPadding(screenWidth),
        top: 24,
      ),
      child: PreferredSize(
        preferredSize: const Size.fromHeight(130.0),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.start,
          children: [
            ResponsiveCard(
              isDark: widget.isDark,
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
                        key: Key('reset-password-email'),
                        controller: _emailController,
                        // initialValue: user!.email,
                        decoration: InputDecoration(
                          labelText: 'Email',
                          hintText: 'test@cannlytics.com',
                          // enabled: !state.isLoading,
                        ),
                        autocorrect: false,
                        textInputAction: TextInputAction.next,
                        keyboardType: TextInputType.emailAddress,
                        keyboardAppearance: Brightness.light,
                        autovalidateMode: AutovalidateMode.onUserInteraction,
                        // Optional: Add email validation.
                        // validator: (email) =>
                        //     !_submitted ? null : emailErrorText(email ?? ''),
                        // onEditingComplete: () => _emailEditingComplete(),
                        // inputFormatters: <TextInputFormatter>[
                        //   ValidatorInputFormatter(
                        //       editingValidator: EmailEditingRegexValidator()),
                        // ],
                      ),

                      // Spacer.
                      gapH18,

                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          // Back button.
                          CustomTextButton(
                            text: 'Back',
                            onPressed: () {
                              if (user == null) {
                                context.goNamed(AppRoutes.signIn.name);
                              } else {
                                context.pop();
                              }
                            },
                          ),

                          // Submit button.
                          PrimaryButton(
                            text: 'Reset Password',
                            isLoading: state.isLoading,
                            onPressed: state.isLoading ? null : () => _submit(),
                          ),
                        ],
                      ),

                      // Spacer.
                      gapH8,
                    ],
                  ),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

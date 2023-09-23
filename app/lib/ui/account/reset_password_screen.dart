// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 3/6/2023
// Updated: 4/14/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Flutter imports:
import 'package:flutter/material.dart';

// Package imports:
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_svg/flutter_svg.dart';
import 'package:go_router/go_router.dart';

// Project imports:
import 'package:cannlytics_data/common/buttons/custom_text_button.dart';
import 'package:cannlytics_data/common/buttons/primary_button.dart';
import 'package:cannlytics_data/common/buttons/theme_button.dart';
import 'package:cannlytics_data/common/dialogs/auth_dialog.dart';
import 'package:cannlytics_data/constants/colors.dart';
import 'package:cannlytics_data/constants/design.dart';
import 'package:cannlytics_data/constants/theme.dart';
import 'package:cannlytics_data/ui/account/account_controller.dart';
import 'package:cannlytics_data/ui/layout/footer.dart';
import 'package:cannlytics_data/utils/utils.dart';

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
            SliverToBoxAdapter(child: ResetPasswordForm(isDark: isDark)),
            SliverToBoxAdapter(
              child: Container(
                height: MediaQuery.sizeOf(context).height * 0.3,
              ),
            ),

            // Footer
            const SliverToBoxAdapter(child: Footer()),
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
      var message = await controller.resetPassword(email);
      if (message == 'success') {
        InterfaceUtils.showAlertDialog(
          context: context,
          title: 'Password reset email sent',
          content: 'Check your email for a link to reset your password.',
          primaryActionColor:
              widget.isDark ? DarkColors.green : LightColors.green,
        );
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

  @override
  Widget build(BuildContext context) {
    // Listen to the account state.
    final state = ref.watch(accountProvider);

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
        // bottom: 128,
      ),
      child: PreferredSize(
        preferredSize: const Size.fromHeight(130.0),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.start,
          children: [
            SizedBox(
              width: 320,
              child: Card(
                margin: EdgeInsets.symmetric(vertical: 16),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(3),
                ),
                child: Padding(
                  padding: EdgeInsets.symmetric(
                    vertical: 21,
                    horizontal: 16,
                  ),
                  child: FocusScope(
                    node: _node,
                    child: Form(
                      key: _formKey,
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.center,
                        children: <Widget>[
                          // Title.
                          Text(
                            'Reset Password',
                            style: Theme.of(context)
                                .textTheme
                                .titleLarge!
                                .copyWith(
                                  color: Theme.of(context)
                                      .textTheme
                                      .titleLarge!
                                      .color,
                                  fontSize: 18,
                                ),
                          ),
                          gapH18,

                          // Email field.
                          TextFormField(
                            key: Key('reset-password-email'),
                            controller: _emailController,
                            // initialValue: user!.email,
                            style: Theme.of(context).textTheme.titleMedium,
                            decoration: InputDecoration(
                              labelText: 'Email',
                              hintText: 'test@cannlytics.com',
                              // enabled: !state.isLoading,
                              floatingLabelBehavior: FloatingLabelBehavior.auto,
                              contentPadding: EdgeInsets.only(
                                top: 18,
                                left: 8,
                                right: 8,
                                bottom: 8,
                              ),
                            ),
                            autocorrect: false,
                            textInputAction: TextInputAction.next,
                            keyboardType: TextInputType.emailAddress,
                            keyboardAppearance: Brightness.light,
                            autovalidateMode:
                                AutovalidateMode.onUserInteraction,
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
                                text: '← Back',
                                onPressed: () {
                                  if (user == null) {
                                    context.go('/account');
                                  } else {
                                    context.pop();
                                  }
                                },
                              ),

                              // Submit button.
                              PrimaryButton(
                                text: 'Reset Password',
                                isLoading: state.isLoading,
                                onPressed:
                                    state.isLoading ? null : () => _submit(),
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
              ),
            ),
          ],
        ),
      ),
    );
  }
}

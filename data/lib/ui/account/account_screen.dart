// Cannlytics Data
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 2/17/2023
// Updated: 5/4/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Flutter imports:
import 'package:cannlytics_data/constants/theme.dart';
import 'package:cannlytics_data/common/layout/footer.dart';
import 'package:cannlytics_data/common/buttons/custom_text_button.dart';
import 'package:cannlytics_data/common/layout/console.dart';
import 'package:cannlytics_data/ui/account/api_key_management.dart';
import 'package:cannlytics_data/ui/account/subscription_management.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

// Package imports:
import 'package:firebase_auth/firebase_auth.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

// Project imports:
import 'package:cannlytics_data/constants/design.dart';
import 'package:cannlytics_data/services/auth_service.dart';
import 'package:cannlytics_data/ui/account/account_controller.dart';
import 'package:cannlytics_data/utils/utils.dart';
import 'package:cannlytics_data/utils/validation_utils.dart';
import 'package:cannlytics_data/common/buttons/primary_button.dart';
import 'package:cannlytics_data/common/buttons/secondary_button.dart';
import 'package:cannlytics_data/common/cards/wide_card.dart';
import 'package:cannlytics_data/common/dialogs/auth_dialogs.dart';
import 'package:cannlytics_data/common/images/avatar.dart';
import 'package:cannlytics_data/common/layout/header.dart';
import 'package:cannlytics_data/common/layout/sidebar.dart';

// See:
// https://medium.com/flutter-community/paypal-payment-gateway-integration-in-flutter-379fbb3b87f5
// https://stackoverflow.com/questions/57390362/flutter-integrate-paypal-buttons-with-webview
// https://developer.paypal.com/docs/api/subscriptions/v1/#subscriptions_create

/// Account screen.
class AccountScreen extends StatelessWidget {
  const AccountScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      // App bar.
      appBar: DashboardHeader(),

      // Side menu.
      drawer: Responsive.isMobile(context) ? MobileDrawer() : null,

      // Body.
      body: Console(slivers: [
        // Account card.
        SliverToBoxAdapter(child: AccountManagement()),

        // Settings card.
        SliverToBoxAdapter(child: ThemeSettings()),

        // Footer.
        const SliverToBoxAdapter(child: Footer()),
      ]),
    );
  }
}

/// Account management cards.
class AccountManagement extends ConsumerWidget {
  const AccountManagement({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    // Dynamic screen width.
    final screenWidth = MediaQuery.of(context).size.width;

    // Listen to the current user.
    final user = ref.watch(authProvider).currentUser;

    // Render the widget.
    return Padding(
      padding: EdgeInsets.only(
        top: 24,
        left: sliverHorizontalPadding(screenWidth),
        right: sliverHorizontalPadding(screenWidth),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        mainAxisAlignment: MainAxisAlignment.start,
        children: [
          // Sign up prompt.
          if (user == null) _signUpCard(context, screenWidth),

          // Account information.
          if (user != null) AccountForm(key: Key('account-form')),

          // Subscriptions.
          if (user != null) SubscriptionManagement(key: Key('subscriptions')),

          // API keys.
          if (user != null) APIKeyManagement(key: Key('api-keys')),

          // Delete account option.
          if (user != null) _deleteAccount(context, ref, screenWidth),
        ],
      ),
    );
  }

  /// Sign up card.
  Widget _signUpCard(BuildContext context, double screenWidth) {
    return WideCard(
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              SizedBox(
                width: (screenWidth > Breakpoints.tablet) ? null : 275,
                child: Text(
                  'Create an account',
                  style: Theme.of(context).textTheme.titleLarge,
                ),
              ),
              gapH6,
              SizedBox(
                width: (screenWidth > Breakpoints.tablet) ? null : 275,
                child: Text(
                  'Sign up to save and access your data from any device.',
                  style: Theme.of(context).textTheme.titleMedium!.copyWith(
                        color: Theme.of(context).textTheme.titleLarge!.color,
                      ),
                ),
              ),
              gapH18,
              Row(
                children: [
                  // Sign in button.
                  CustomTextButton(
                    text: 'Sign In',
                    onPressed: () {
                      showDialog(
                        context: context,
                        builder: (BuildContext context) {
                          return SignInDialog(isSignUp: false);
                        },
                      );
                    },
                  ),

                  // Spacer.
                  SizedBox(width: 8),
                  PrimaryButton(
                    text: 'Sign up',
                    onPressed: () {
                      showDialog(
                        context: context,
                        builder: (BuildContext context) {
                          return SignInDialog(isSignUp: true);
                        },
                      );
                    },
                  ),
                ],
              ),
            ],
          ),
        ],
      ),
    );
  }

  /// Delete account card.
  Widget _deleteAccount(
    BuildContext context,
    WidgetRef ref,
    double screenWidth,
  ) {
    return WideCard(
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(
            Icons.error_outline,
            color: Colors.red,
          ),
          gapW16,
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                'Danger Zone',
                style: Theme.of(context).textTheme.titleLarge,
              ),
              gapH24,
              SizedBox(
                width: (screenWidth > Breakpoints.tablet) ? null : 275,
                child: Text(
                  'Deleting this account will also remove your account data.',
                  style: Theme.of(context).textTheme.titleMedium!.copyWith(
                        color: Theme.of(context).textTheme.titleLarge!.color,
                      ),
                ),
              ),
              SizedBox(
                width: (screenWidth > Breakpoints.tablet) ? null : 275,
                child: Text(
                  'Make sure that you have exported your data if you want to keep your data.',
                ),
              ),
              gapH12,
              PrimaryButton(
                backgroundColor: Colors.red,
                text: 'Delete account',
                onPressed: () async {
                  final delete = await InterfaceUtils.showAlertDialog(
                    context: context,
                    title: 'Are you sure you want to delete your account?',
                    cancelActionText: 'Cancel',
                    defaultActionText: 'Delete account',
                  );
                  if (delete == true) {
                    await ref.read(authProvider).deleteAccount();
                    context.go('/sign-in');
                  }
                },
              ),
            ],
          ),
        ],
      ),
    );
  }
}

/// Account form.
class AccountForm extends ConsumerStatefulWidget {
  const AccountForm({super.key});
  @override
  ConsumerState<AccountForm> createState() => _AccountFormState();
}

/// Account form state.
class _AccountFormState extends ConsumerState<AccountForm>
    with EmailAndPasswordValidators {
  // Controllers.
  final _formKey = GlobalKey<FormState>();
  final _displayNameController = TextEditingController();
  final _emailController = TextEditingController();

  // State.
  String get displayName => _displayNameController.text;
  String get email => _emailController.text;
  var _submitted = false;

  // Dispose controllers.
  @override
  void dispose() {
    _displayNameController.dispose();
    _emailController.dispose();
    super.dispose();
  }

  // Submit the sign-in form if validation passes.
  Future<void> _submit() async {
    setState(() => _submitted = true);
    if (_formKey.currentState!.validate()) {
      await ref.read(accountProvider.notifier).updateUser(
            email: email,
            displayName: displayName,
          );
      // TODO: Show notification upon save.
    }
  }

  /// Display the user's photo, allowing the user to upload a new photo.
  Widget _userPhoto(
    BuildContext context,
    WidgetRef ref,
    AsyncValue state,
    User? user,
  ) {
    return InkWell(
      customBorder: const CircleBorder(),
      onTap: state.isLoading
          ? null
          : () async {
              String message =
                  await ref.read(accountProvider.notifier).changePhoto();
              if (message != 'success') {
                ScaffoldMessenger.of(context).showSnackBar(
                  SnackBar(
                    backgroundColor: Colors.red.shade300,
                    content: Text('Error changing image!'),
                    duration: Duration(seconds: 4),
                  ),
                );
              }
            },
      child: Avatar(
        photoUrl:
            user!.photoURL ?? 'https://cannlytics.com/robohash/${user.uid}',
        radius: 60,
        borderColor: Theme.of(context).secondaryHeaderColor,
        borderWidth: 1.0,
      ),
    );
  }

  /// Sign out button.
  Widget _signOut(AsyncValue state) {
    return CustomTextButton(
      text: 'Sign out',
      onPressed: state.isLoading
          ? null
          : () async {
              final logout = await InterfaceUtils.showAlertDialog(
                context: context,
                title: 'Are you sure?',
                cancelActionText: 'Cancel',
                defaultActionText: 'Sign out',
              );
              if (logout == true) {
                await ref.read(authProvider).signOut();
                context.go('/sign-in');
              }
            },
    );
  }

  /// Reset password button.
  Widget _resetPassword(AsyncValue state) {
    return SecondaryButton(
      text: 'Reset password',
      onPressed:
          state.isLoading ? null : () => context.go('/account/reset-password'),
    );
  }

  @override
  Widget build(BuildContext context) {
    // FIXME: Listen to errors.
    // ref.listen<AsyncValue>(
    //   accountProvider,
    //   (_, state) => state.showAlertDialogOnError(context),
    // );

    // Listen to the account state.
    final state = ref.watch(accountProvider);

    // Listen to the current user.
    final user = ref.watch(authProvider).currentUser;

    // Set the initial values.
    if (user != null) {
      _displayNameController.text = user.displayName ?? '';
      _emailController.text = user.email ?? '';
    }

    /// Username field.
    Widget _userName() {
      return Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text('Display Name'),
          gapH6,
          SizedBox(
            width: 240,
            child: TextFormField(
              key: Key('displayName'),
              controller: _displayNameController,
              autocorrect: false,
              decoration: InputDecoration(
                enabled: !state.isLoading,
                contentPadding: EdgeInsets.only(
                  top: 18,
                  left: 8,
                  right: 8,
                  bottom: 8,
                ),
              ),
              style: Theme.of(context).textTheme.titleMedium,
              textInputAction: TextInputAction.next,
            ),
          ),
        ],
      );
    }

    /// User email field.
    Widget _userEmail() {
      return Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text('Email'),
          gapH6,
          SizedBox(
            width: 240,
            child: TextFormField(
              key: Key('email'),
              controller: _emailController,
              decoration: InputDecoration(
                labelText: 'Email',
                enabled: !state.isLoading,
                contentPadding: EdgeInsets.only(
                  top: 18,
                  left: 8,
                  right: 8,
                  bottom: 8,
                ),
              ),
              style: Theme.of(context).textTheme.titleMedium,
              autovalidateMode: AutovalidateMode.onUserInteraction,
              validator: (email) =>
                  !_submitted ? null : emailErrorText(email ?? ''),
              autocorrect: false,
              textInputAction: TextInputAction.next,
              keyboardType: TextInputType.emailAddress,
              inputFormatters: <TextInputFormatter>[
                ValidatorInputFormatter(
                    editingValidator: EmailEditingRegexValidator()),
              ],
            ),
          ),
        ],
      );
    }

    /// Save button.
    Widget _saveButton() {
      return PrimaryButton(
        text: 'Save',
        isLoading: state.isLoading,
        onPressed: state.isLoading ? null : () => _submit(),
      );
    }

    // Define the form.
    List<Widget> formFields = <Widget>[
      Form(
        key: _formKey,
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Title
            Text(
              'Account',
              style: Theme.of(context).textTheme.titleLarge,
            ),
            gapH24,

            // User photo.
            _userPhoto(context, ref, state, user),
            gapH24,

            // User name.
            _userName(),
            gapH12,

            // User email.
            _userEmail(),
            gapH12,

            // TODO: User phone.
            // if (user.phoneNumber != null)
            //   Text(
            //     'Phone: ${user.phoneNumber!}',
            //     style: Theme.of(context).textTheme.bodyMedium,
            //   ),

            // TODO: Add phone number.
            // if (user.phoneNumber == null)
            //   CustomTextButton(
            //     text: 'Add phone number',
            //     fontStyle: FontStyle.italic,
            //     onPressed: () {},
            //   ),

            // Save button.
            // gapH8,
            // _saveButton(),
            // gapH12,

            // Additional account options.
            gapH12,
            Row(
              children: [
                // Reset password.
                _resetPassword(state),
                gapW8,

                // Sign out.
                _saveButton(),
              ],
            ),
            gapH24,
          ],
        ),
      ),
    ];

    // Render the form.
    return WideCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: formFields.reversed.toList(),
      ),
    );

    // TODO: Manage additional Firestore user data:
    // - Account created date.
    // - Last sign in date.
    // - View logs.

    // Business:
    // - View / manage organizations and teams.
    // - state (restrict to Cannlytics-verified states)
    // - licenses (/admin/create-license and /admin/delete-license)
    // - license type
  }
}

/// Settings card.
class ThemeSettings extends ConsumerWidget {
  const ThemeSettings({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    // Dynamic screen width.
    final screenWidth = MediaQuery.of(context).size.width;

    // Render the widget.
    return Padding(
      padding: EdgeInsets.only(
        top: 24,
        left: sliverHorizontalPadding(screenWidth),
        right: sliverHorizontalPadding(screenWidth),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        mainAxisAlignment: MainAxisAlignment.start,
        children: [
          // Theme toggle.
          _themeToggle(context, ref, screenWidth),
        ],
      ),
    );
  }

  /// Sign up card.
  Widget _themeToggle(BuildContext context, WidgetRef ref, double screenWidth) {
    // Watch the theme.
    final themeMode = ref.watch(themeModeProvider);
    final bool isDark = themeMode == ThemeMode.dark;
    return WideCard(
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                'Settings',
                style: Theme.of(context).textTheme.titleLarge,
              ),
              gapH6,
              Row(
                children: [
                  CustomTextButton(
                    text: 'Light mode',
                    onPressed: () {
                      ref.read(themeModeProvider.notifier).state =
                          ThemeMode.light;
                      ref
                          .read(accountProvider.notifier)
                          .saveUserData({'theme': 'light'});
                    },
                  ),
                  gapW6,
                  Transform.scale(
                    scale: 0.75,
                    child: Switch(
                      value: themeMode == ThemeMode.dark,
                      activeColor: Theme.of(context).primaryColor,
                      inactiveTrackColor:
                          isDark ? Colors.grey.shade400 : Colors.grey.shade300,
                      activeTrackColor:
                          isDark ? Colors.grey.shade600 : Colors.grey.shade200,
                      inactiveThumbColor: isDark
                          ? Colors.white
                          : Theme.of(context).primaryColor,
                      materialTapTargetSize: MaterialTapTargetSize.shrinkWrap,
                      onChanged: (value) {
                        ref.read(themeModeProvider.notifier).state =
                            value ? ThemeMode.dark : ThemeMode.light;
                        ref
                            .read(accountProvider.notifier)
                            .saveUserData({'theme': value ? 'dark' : 'light'});
                      },
                    ),
                  ),
                  gapW6,
                  CustomTextButton(
                    text: 'Dark mode',
                    onPressed: () {
                      ref.read(themeModeProvider.notifier).state =
                          ThemeMode.dark;
                      ref
                          .read(accountProvider.notifier)
                          .saveUserData({'theme': 'dark'});
                    },
                  ),
                ],
              ),
            ],
          ),
        ],
      ),
    );
  }
}

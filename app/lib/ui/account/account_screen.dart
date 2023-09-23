// Cannlytics Data
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 2/17/2023
// Updated: 8/6/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Flutter imports:
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

// Package imports:
import 'package:firebase_auth/firebase_auth.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:url_launcher/url_launcher.dart';

// Project imports:
import 'package:cannlytics_data/common/buttons/custom_text_button.dart';
import 'package:cannlytics_data/common/buttons/primary_button.dart';
import 'package:cannlytics_data/common/buttons/secondary_button.dart';
import 'package:cannlytics_data/common/cards/wide_card.dart';
import 'package:cannlytics_data/common/dialogs/auth_dialog.dart';
import 'package:cannlytics_data/common/images/avatar.dart';
import 'package:cannlytics_data/constants/colors.dart';
import 'package:cannlytics_data/constants/design.dart';
import 'package:cannlytics_data/constants/theme.dart';
import 'package:cannlytics_data/services/auth_service.dart';
import 'package:cannlytics_data/ui/account/account_controller.dart';
import 'package:cannlytics_data/ui/account/faq.dart';
import 'package:cannlytics_data/ui/account/subscription_management.dart';
import 'package:cannlytics_data/ui/layout/console.dart';
import 'package:cannlytics_data/utils/utils.dart';
import 'package:cannlytics_data/utils/validation_utils.dart';

/// Account screen.
class AccountScreen extends StatelessWidget {
  const AccountScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return ConsoleScreen(
      children: [
        SliverToBoxAdapter(child: AccountManagement()),
      ],
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
    final user = ref.watch(userProvider).value;

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
          if (user == null)
            SubscriptionManagement(key: Key('no_user_subscriptions')),

          // Account information.
          if (user != null) AccountForm(key: Key('account_form')),

          // Subscriptions.
          if (user != null)
            SubscriptionManagement(key: Key('user_subscriptions')),

          // General settings.
          ThemeSettings(key: Key('theme_settings')),

          // API keys.
          if (user != null) APIKeyManagement(key: Key('api_keys')),

          // Delete account option.
          if (user != null) DeleteAccountCard(),

          // FAQ section.
          FAQCard(),
          gapH48,
        ],
      ),
    );
  }
}

/// Form for the user to manage their display name, email, and picture.
class AccountForm extends ConsumerStatefulWidget {
  const AccountForm({Key? key}) : super(key: key);

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
      // Save the user's data.
      String _updateFuture =
          await ref.read(accountProvider.notifier).updateUser(
                email: email,
                displayName: displayName,
              );

      // Get the theme.
      bool isDark = Theme.of(context).brightness == Brightness.dark;

      // Show notification snackbar.
      if (_updateFuture == 'success') {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(
              'Your account has been saved',
              style: Theme.of(context).textTheme.bodyMedium,
            ),
            duration: Duration(seconds: 2),
            backgroundColor: isDark ? DarkColors.green : LightColors.lightGreen,
            showCloseIcon: true,
          ),
        );
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Error saving your account'),
            duration: Duration(seconds: 4),
            backgroundColor:
                isDark ? DarkColors.darkOrange : LightColors.darkOrange,
            showCloseIcon: true,
          ),
        );
      }
    }
  }

  /// Display the user's photo, allowing the user to upload a new photo.
  Widget _userPhoto(
    BuildContext context,
    WidgetRef ref,
    AsyncValue state,
    User user,
  ) {
    return InkWell(
      customBorder: const CircleBorder(),
      onTap: state.isLoading
          ? null
          : () async {
              String message =
                  await ref.read(accountProvider.notifier).changePhoto();
              if (message != 'success') {
                // Display an error message if an authentication error occurs.
                message = message.replaceAll(RegExp(r'\[.*?\]'), '');
                InterfaceUtils.showAlertDialog(
                  context: context,
                  title: 'Error changing image',
                  content: message,
                  primaryActionColor: Colors.redAccent,
                );
              }
            },
      child: Avatar(
        key: Key('user_photo'),
        photoUrl: user.photoURL ??
            'https://firebasestorage.googleapis.com/v0/b/cannlytics.appspot.com/o/assets%2Fimages%2Fplaceholders%2Fhomegrower-placeholder.png?alt=media&token=29331691-c2ef-4bc5-89e8-cec58a7913e4',
        radius: 60,
        borderColor: Theme.of(context).secondaryHeaderColor,
        borderWidth: 1.0,
      ),
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
    // Listen to the account state.
    final state = ref.watch(accountProvider);

    // Listen to the current user.
    final user = ref.watch(userProvider).value;

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
              'Your account',
              style: Theme.of(context).textTheme.titleLarge,
            ),
            gapH24,

            // User photo.
            if (user != null) _userPhoto(context, ref, state, user),
            gapH24,

            // User name.
            _userName(),
            gapH12,

            // User email.
            _userEmail(),
            gapH12,

            // TODO: Add view profile button.

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

    // Optional: Manage additional Firestore user data:
    // - Account created date.
    // - Last sign in date.
    // - View logs.
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
    final themeMode = ref.watch(themeModeProvider);
    final bool isDark = themeMode == ThemeMode.dark;

    // Render the widget.
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

/// Delete account card.
class DeleteAccountCard extends ConsumerWidget {
  DeleteAccountCard({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final screenWidth = MediaQuery.of(context).size.width;
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
              gapH8,
              Container(
                width: (screenWidth < 640) ? 240 : 500,
                child: SelectableText(
                  'Deleting this account will also remove your account data. ' +
                      'Make sure that you have exported your data if you want to keep your data.',
                  style: Theme.of(context).textTheme.bodyMedium!.copyWith(
                        color: Theme.of(context).textTheme.titleLarge!.color,
                      ),
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

/// API key management.
class APIKeyManagement extends ConsumerWidget {
  const APIKeyManagement({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return WideCard(
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Title.
              Text(
                'API Keys',
                style: Theme.of(context).textTheme.titleLarge,
              ),
              SizedBox(height: 8),

              // Manage your account link.
              SecondaryButton(
                text: 'Manage your API keys',
                onPressed: () {
                  const url = 'https://cannlytics.com/account/subscriptions';
                  launchUrl(Uri.parse(url));
                },
              ),
            ],
          ),
        ],
      ),
    );
  }
}

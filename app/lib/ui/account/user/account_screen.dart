// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 2/17/2023
// Updated: 4/2/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Flutter imports:
import 'package:cannlytics_app/ui/main/app_controller.dart';
import 'package:cannlytics_app/widgets/cards/wide_card.dart';
import 'package:cannlytics_app/widgets/layout/main_screen.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

// Package imports:
import 'package:firebase_auth/firebase_auth.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

// Project imports:
import 'package:cannlytics_app/constants/design.dart';
import 'package:cannlytics_app/services/auth_service.dart';
import 'package:cannlytics_app/ui/account/sign-in/sign_in_validators.dart';
import 'package:cannlytics_app/ui/account/user/account_controller.dart';
import 'package:cannlytics_app/ui/layout/header.dart';
import 'package:cannlytics_app/utils/validation_utils.dart';
import 'package:cannlytics_app/widgets/buttons/primary_button.dart';
import 'package:cannlytics_app/widgets/buttons/secondary_button.dart';
import 'package:cannlytics_app/widgets/dialogs/alert_dialog_ui.dart';
import 'package:cannlytics_app/widgets/dialogs/alert_dialogs.dart';
import 'package:cannlytics_app/widgets/images/avatar.dart';
import 'package:cannlytics_app/widgets/layout/shimmer.dart';

/// Account screen.
class AccountScreen extends StatelessWidget {
  const AccountScreen({super.key});

  @override
  Widget build(BuildContext context) {
    // Render the widget.
    return MainScreen(
      slivers: [
        // App header.
        const SliverToBoxAdapter(child: AppHeader()),

        // Account management.
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
        left: sliverHorizontalPadding(screenWidth),
        right: sliverHorizontalPadding(screenWidth),
        top: 24,
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        mainAxisAlignment: MainAxisAlignment.start,
        children: [
          // Account information
          if (user != null) AccountForm(key: Key('account-form')),

          // Delete account option.
          if (user != null) _deleteAccount(context, screenWidth),
          gapH48,
        ],
      ),
    );
  }

  /// Delete account card.
  Widget _deleteAccount(BuildContext context, double screenWidth) {
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
                onPressed: () {
                  print('TODO: DELETE ACCOUNT!');
                  showReauthDialog(
                    context: context,
                    title: 'Reauthenticate',
                    defaultActionText: 'Submit',
                    cancelActionText: 'Cancel',
                    auth: FirebaseAuth.instance,
                    // content: Text('Password'),
                  );
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

  @override
  Widget build(BuildContext context) {
    // Listen to the account state.
    ref.listen<AsyncValue>(
      accountProvider,
      (_, state) => state.showAlertDialogOnError(context),
    );
    final state = ref.watch(accountProvider);

    // Listen to the current user.
    final user = ref.watch(userProvider).value;
    ;

    // Set the initial values.
    if (user != null) {
      _displayNameController.text = user.displayName ?? '';
      _emailController.text = user.email ?? '';
    }

    // Define the profile widget.
    Widget profileWidget = Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // Title
        Text(
          'Profile',
          style: Theme.of(context).textTheme.titleLarge,
        ),
        gapH24,

        // User photo.
        _userPhoto(context, ref, state, user),
        gapH8,

        // Reset password and sign out.
        _accountOptions(context, ref, state),
        gapH24,
      ],
    );

    // Define the form.
    List<Widget> formFields = <Widget>[
      Form(
        key: _formKey,
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Title
            Text(
              'Account Information',
              style: Theme.of(context).textTheme.titleLarge,
            ),
            gapH24,

            // User name.
            Text('Display Name'),
            gapH6,
            SizedBox(
              width: 240,
              child: TextFormField(
                key: Key('displayName'),
                controller: _displayNameController,
                autocorrect: false,
                decoration: InputDecoration(
                  // border: OutlineInputBorder(),
                  // labelText: 'Display Name',
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
            gapH12,

            // Email field.
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
            gapH18,

            // User phone.
            // TODO: Change user phone.
            // if (user.phoneNumber != null)
            //   Text(
            //     'Phone: ${user.phoneNumber!}',
            //     style: Theme.of(context).textTheme.bodyMedium,
            //   ),

            // // Add phone number.
            // if (user.phoneNumber == null)
            //   CustomTextButton(
            //     text: 'Add phone number',
            //     fontStyle: FontStyle.italic,
            //     onPressed: () {
            //       // TODO: Add phone number.
            //     },
            //   ),

            gapH8,
            // Submit button.
            // if (email != user!.email && displayName != user.displayName)
            PrimaryButton(
              text: 'Save',
              isLoading: state.isLoading,
              onPressed: state.isLoading ? null : () => _submit(),
            ),
            gapH12,
          ],
        ),
      ),
    ];

    // Render the form.
    return Column(
      children: [
        // Profile fields.
        WideCard(child: profileWidget),

        // Account fields.
        WideCard(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: formFields.reversed.toList(),
          ),
        ),
      ],
    );

    // TODO: Toggle light / dark theme.
    // ThemeInput(),

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

  /// Display the user's photo, allowing the user to upload a new photo.
  Widget _userPhoto(
    BuildContext context,
    WidgetRef ref,
    AsyncValue state,
    User? user,
  ) {
    return InkWell(
      customBorder: const CircleBorder(),
      // splashColor: AppColors.accent1,
      onTap: state.isLoading
          ? null
          : () async {
              await ref.read(accountProvider.notifier).changePhoto();
            },
      child: ShimmerLoading(
        isLoading: state.isLoading,
        child: Avatar(
          photoUrl:
              user!.photoURL ?? 'https://cannlytics.com/robohash/${user.uid}',
          radius: 60,
          borderColor: Theme.of(context).secondaryHeaderColor,
          borderWidth: 1.0,
        ),
      ),
    );
  }

  /// Reset password and sign out buttons.
  Widget _accountOptions(
    BuildContext context,
    WidgetRef ref,
    AsyncValue state,
  ) {
    return Row(
      children: [
        // Reset password.
        SecondaryButton(
          // isDark: isDark,
          text: 'Reset password',
          onPressed: state.isLoading
              ? null
              : () {
                  context.go('/account/reset-password');
                },
        ),
        gapW8,

        // Sign out.
        SecondaryButton(
          // isDark: isDark,
          text: 'Sign out',
          onPressed: state.isLoading
              ? null
              : () async {
                  final logout = await showAlertDialog(
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
        ),
      ],
    );
  }
}

// Cannlytics Data
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 7/3/2023
// Updated: 8/20/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>
// License: MIT License <https://github.com/bizz84/code_with_andrea_flutter/blob/main/LICENSE.md>

// Flutter imports:
import 'package:flutter/gestures.dart';
import 'package:flutter/material.dart';

// Package imports:
import 'package:go_router/go_router.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:url_launcher/url_launcher.dart';

// Project imports:
import 'package:cannlytics_data/common/buttons/primary_button.dart';
import 'package:cannlytics_data/common/buttons/secondary_button.dart';
import 'package:cannlytics_data/constants/colors.dart';
import 'package:cannlytics_data/constants/design.dart';

/// An age verification screen.
class AgeVerificationScreen extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Center(
        child: AgeCheckDialog(),
      ),
    );
  }
}

/// Age verification dialog.
class AgeCheckDialog extends StatefulWidget {
  @override
  _AgeCheckDialogState createState() => _AgeCheckDialogState();
}

/// Age verification dialog state.
class _AgeCheckDialogState extends State<AgeCheckDialog> {
  // Controllers.
  final TextEditingController _monthController = TextEditingController();
  final TextEditingController _dayController = TextEditingController();
  final TextEditingController _yearController = TextEditingController();

  // Initialization.
  @override
  void initState() {
    super.initState();
    // Check if the user has already confirmed their age.
    _checkAge();
  }

  // Dispose controllers.
  @override
  void dispose() {
    _monthController.dispose();
    _dayController.dispose();
    _yearController.dispose();
    super.dispose();
  }

  /// Check if the user is old enough to access the site.
  Future<void> _checkAge() async {
    SharedPreferences prefs = await SharedPreferences.getInstance();
    bool? isOldEnough = prefs.getBool('isOldEnough');
    if (isOldEnough == null) {
      _showDialog();
    }
  }

  /// Calculate the age and check if the user is old enough.
  void _calculateAgeAndCheck() async {
    // Check if any date input fields are empty.
    bool isDark = Theme.of(context).brightness == Brightness.dark;
    if (_dayController.text.isEmpty ||
        _monthController.text.isEmpty ||
        _yearController.text.isEmpty) {
      final snackBar = SnackBar(
        content: Text('Please enter a valid birthdate.'),
        duration: Duration(seconds: 2),
        backgroundColor:
            isDark ? DarkColors.darkOrange : LightColors.darkOrange,
        showCloseIcon: true,
      );
      ScaffoldMessenger.of(context).showSnackBar(snackBar);
      return;
    }

    // Try to parse the user input into integers.
    int day;
    int month;
    int year;
    try {
      day = int.parse(_dayController.text);
      month = int.parse(_monthController.text);
      year = int.parse(_yearController.text);
    } catch (e) {
      final snackBar = SnackBar(
        content: Text('Please enter a valid birthdate.'),
        duration: Duration(seconds: 2),
        backgroundColor:
            isDark ? DarkColors.darkOrange : LightColors.darkOrange,
        showCloseIcon: true,
      );
      ScaffoldMessenger.of(context).showSnackBar(snackBar);
      return;
    }

    // If the user is old enough, close the dialog.
    DateTime birthDate = DateTime(year, month, day);
    SharedPreferences prefs = await SharedPreferences.getInstance();
    bool isOldEnough = DateTime.now().year - birthDate.year >= 21;
    await prefs.setBool('isOldEnough', isOldEnough);
    if (isOldEnough) {
      Navigator.of(context).pop();
    } else {
      final snackBar = SnackBar(
        content: Text('You must be at least 21 years old to access this site.'),
        duration: Duration(seconds: 2),
        backgroundColor:
            isDark ? DarkColors.darkOrange : LightColors.darkOrange,
        showCloseIcon: true,
      );
      ScaffoldMessenger.of(context).showSnackBar(snackBar);
    }

    // Update the UI.
    setState(() {
      context.go('/');
    });
  }

  /// Show the age verification dialog.
  void _showDialog() {
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (BuildContext context) {
        // bool _isChecked = false;
        return StatefulBuilder(
          builder: (context, setState) {
            return AlertDialog(
              // Title.
              title: Row(
                crossAxisAlignment: CrossAxisAlignment.center,
                children: [
                  Image.network(
                    'https://firebasestorage.googleapis.com/v0/b/cannlytics.appspot.com/o/assets%2Fimages%2Fplaceholders%2Fage-verification-symbol.png?alt=media&token=95abaeee-705e-44e9-841b-e32ac36dd7fe',
                    width: 64,
                    height: 64,
                  ),
                  gapW8,
                  Container(
                    width: 200,
                    child: Text(
                      'Are you 21 or older?',
                      style: Theme.of(context).textTheme.titleLarge,
                    ),
                  ),
                ],
              ),
              content: Container(
                width: 420,
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    // Instructions.
                    Text(
                      'Confirm your birthdate here:',
                      style: Theme.of(context).textTheme.titleMedium,
                    ),
                    gapH8,

                    // Date Picker.
                    Row(
                      children: [
                        Expanded(
                          child: TextFormField(
                            controller: _monthController,
                            decoration: InputDecoration(hintText: 'MM'),
                            keyboardType: TextInputType.number,
                            // focusNode: monthFocus,
                          ),
                        ),
                        gapW8,
                        Expanded(
                          child: TextFormField(
                            controller: _dayController,
                            decoration: InputDecoration(hintText: 'DD'),
                            keyboardType: TextInputType.number,
                            // focusNode: dayFocus,
                          ),
                        ),
                        gapW8,
                        Expanded(
                          child: TextFormField(
                            controller: _yearController,
                            decoration: InputDecoration(hintText: 'YYYY'),
                            keyboardType: TextInputType.number,
                            onFieldSubmitted: (value) {
                              _calculateAgeAndCheck();
                            },
                            // focusNode: yearFocus,
                          ),
                        ),
                      ],
                    ),

                    // Terms.
                    gapH8,
                    RichText(
                      text: TextSpan(
                        style: Theme.of(context).textTheme.bodyLarge,
                        children: <TextSpan>[
                          TextSpan(
                              text: 'By accessing Cannlytics, you accept our '),
                          TextSpan(
                            text: 'terms of use',
                            style: TextStyle(color: Colors.blue),
                            recognizer: TapGestureRecognizer()
                              ..onTap = () {
                                launchUrl(Uri.parse(
                                    'https://docs.cannlytics.com/terms'));
                              },
                          ),
                          TextSpan(
                              text: ' and acknowledge that you have read our '),
                          TextSpan(
                            text: 'privacy policy',
                            style: TextStyle(color: Colors.blue),
                            recognizer: TapGestureRecognizer()
                              ..onTap = () {
                                launchUrl(Uri.parse(
                                    'https://docs.cannlytics.com/privacy'));
                              },
                          ),
                          TextSpan(text: '.'),
                        ],
                      ),
                    ),

                    // Optional: Remember me.
                    // gapH24,
                    // CheckboxListTile(
                    //   title: Text(
                    //     'Remember me for 30 days. I confirm this is not a shared device.',
                    //     style: Theme.of(context).textTheme.bodySmall,
                    //   ),
                    //   value: _isChecked,
                    //   onChanged: (bool? value) {
                    //     setState(() {
                    //       _isChecked = value!;
                    //     });
                    //   },
                    // ),
                  ],
                ),
              ),
              actions: <Widget>[
                // Reject button.
                SecondaryButton(
                  text: 'No, not today',
                  onPressed: () async {
                    SharedPreferences prefs =
                        await SharedPreferences.getInstance();
                    await prefs.setBool('isOldEnough', false);
                    // if (_isChecked) {
                    //   await prefs.setBool('rememberMe', true);
                    // }
                    Navigator.of(context).pop();
                    launchUrl(Uri.parse('https://google.com'));
                  },
                ),

                // Accept button.
                PrimaryButton(
                  text: "Yes, I'm 21+",
                  onPressed: _calculateAgeAndCheck,
                ),
              ],
            );
          },
        );
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    return Container();
  }
}

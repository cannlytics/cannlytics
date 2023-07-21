// Cannlytics Data
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 7/3/2023
// Updated: 7/3/2023
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

/// A dialog that asks the user if they are old enough to access the site.
class AgeCheckDialog extends StatefulWidget {
  @override
  _AgeCheckDialogState createState() => _AgeCheckDialogState();
}

class _AgeCheckDialogState extends State<AgeCheckDialog> {
  @override
  void initState() {
    super.initState();
    _checkAge();
  }

  Future<void> _checkAge() async {
    SharedPreferences prefs = await SharedPreferences.getInstance();
    bool? isOldEnough = prefs.getBool('isOldEnough');

    if (isOldEnough == null) {
      _showDialog();
    }
  }

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
                  Text(
                    'Are you 21 or older?',
                    style: Theme.of(context).textTheme.titleLarge,
                  ),
                ],
              ),
              content: Container(
                width: 420,
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    // Terms.
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
                  text: 'No',
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
                  text: 'Yes',
                  onPressed: () async {
                    SharedPreferences prefs =
                        await SharedPreferences.getInstance();
                    await prefs.setBool('isOldEnough', true);
                    // if (_isChecked) {
                    //   await prefs.setBool('rememberMe', true);
                    // }
                    context.go('/');
                  },
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

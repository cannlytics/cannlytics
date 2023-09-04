// Cannlytics Data
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 9/1/2023
// Updated: 9/3/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Flutter imports:
import 'package:flutter/material.dart';

// Project imports:
import 'package:cannlytics_data/common/buttons/primary_button.dart';
import 'package:cannlytics_data/constants/design.dart';

/// Sign-in placeholder.
class SignInPlaceholder extends StatelessWidget {
  final String? titleText;
  final String? imageUrl;
  final String mainText;
  final String? subTitle;
  final VoidCallback? onButtonPressed;
  final String buttonText;

  SignInPlaceholder({
    this.titleText,
    this.imageUrl,
    required this.mainText,
    this.subTitle,
    required this.onButtonPressed,
    required this.buttonText,
  });

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            // Title.
            if (titleText != null)
              Row(
                children: [
                  SelectableText(
                    titleText!,
                    style: Theme.of(context).textTheme.titleLarge,
                  ),
                ],
              ),
            if (titleText != null) SizedBox(height: 16),

            // Image.
            if (imageUrl != null)
              Padding(
                padding: EdgeInsets.only(top: 16),
                child: Image.network(
                  imageUrl!,
                  // width: 128,
                  height: 128,
                  fit: BoxFit.cover,
                ),
              ),

            // Text.
            Container(
              width: 540,
              child: Column(
                children: <Widget>[
                  SelectableText(
                    mainText,
                    textAlign: TextAlign.center,
                    style: TextStyle(
                        fontSize: 20,
                        color: Theme.of(context).textTheme.titleLarge!.color),
                  ),
                  if (subTitle != null)
                    SelectableText(
                      subTitle!,
                      textAlign: TextAlign.center,
                      style: Theme.of(context).textTheme.bodyMedium,
                    ),
                  gapH12,
                  PrimaryButton(
                    text: buttonText,
                    onPressed: onButtonPressed,
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}

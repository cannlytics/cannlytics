// Cannlytics Data
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 4/14/2023
// Updated: 4/15/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Flutter imports:
import 'package:flutter/material.dart';

// Package imports:
import 'package:flutter_svg/flutter_svg.dart';
import 'package:url_launcher/url_launcher.dart';

// Project imports:
import 'package:cannlytics_data/constants/design.dart';

/// A help dialog with contact links.
class HelpDialog extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      backgroundColor: Theme.of(context).scaffoldBackgroundColor,
      contentPadding: EdgeInsets.all(Defaults.defaultPadding),
      content: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: <Widget>[
          // Close button.
          Row(
            mainAxisAlignment: MainAxisAlignment.start,
            children: [
              SvgPicture.asset(
                'assets/icons/emoji/ring_buoy.svg',
                width: 28,
              ),
              Text(
                'Need help?',
                style: Theme.of(context).textTheme.titleLarge,
              ),
              Spacer(),
              IconButton(
                icon: Icon(Icons.close),
                onPressed: () => Navigator.of(context).pop(false),
              ),
            ],
          ),
          gapH24,
          Text(
            'You can always get help from our team.',
            style: Theme.of(context).textTheme.titleMedium,
          ),
          gapH12,
          Row(
            children: [
              SelectableText(
                'Call: (828) 395-3954',
                style: Theme.of(context).textTheme.titleMedium,
              ),
              IconButton(
                onPressed: () => launchUrl(Uri.parse('tel:(828) 395-3954')),
                icon: Icon(Icons.phone),
              ),
            ],
          ),
          Row(
            children: [
              SelectableText(
                'Email: dev@cannlytics.com',
                style: Theme.of(context).textTheme.titleMedium,
              ),
              IconButton(
                onPressed: () =>
                    launchUrl(Uri.parse('mailto:dev@cannlytics.com')),
                icon: Icon(Icons.email),
              ),
            ],
          ),
          gapH12,
        ],
      ),
    );
  }
}

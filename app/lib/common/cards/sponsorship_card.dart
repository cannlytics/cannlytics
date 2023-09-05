// Cannlytics Data
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 5/9/2023
// Updated: 8/6/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Flutter imports:
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

// Project imports:
import 'package:cannlytics_data/common/buttons/secondary_button.dart';
import 'package:cannlytics_data/constants/colors.dart';
import 'package:cannlytics_data/constants/design.dart';
import 'package:cannlytics_data/services/data_service.dart';

/// Sponsorship card.
class SponsorshipCard extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    final screenWidth = MediaQuery.of(context).size.width;
    return Card(
      margin: EdgeInsets.zero,
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(3)),
      // FIXME: Make this whole area selectable.
      child: Container(
        width: 720,
        padding: EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          mainAxisSize: MainAxisSize.min,
          children: [
            // Title.
            Row(
              mainAxisAlignment: MainAxisAlignment.start,
              children: [
                SelectableText(
                  'Advance cannabis science!',
                  style: Theme.of(context).textTheme.titleLarge,
                ),
              ],
            ),

            // Description.
            Container(
              width: 540,
              child: SelectableText(
                'Cannabis data takes time to collect and statistics take time to calculate. Please consider making a contribution to help expedite the process.',
                style: Theme.of(context).textTheme.bodyMedium,
              ),
            ),

            // Goal.
            gapH12,
            SelectableText.rich(
              TextSpan(
                text: '',
                style: Theme.of(context).textTheme.bodySmall,
                children: [
                  TextSpan(
                    text: '\$1,013',
                    style: TextStyle(fontWeight: FontWeight.bold),
                  ),
                  TextSpan(text: ' USD of '),
                  TextSpan(
                    text: '\$1,420',
                    style: TextStyle(fontWeight: FontWeight.bold),
                  ),
                  TextSpan(text: ' USD / month raised (71%).'),
                ],
              ),
            ),

            // Progress bar.
            gapH4,
            Stack(
              children: [
                Container(
                  height: 24,
                  decoration: BoxDecoration(
                    borderRadius: BorderRadius.circular(4),
                    color: Colors.grey[200],
                  ),
                ),
                FractionallySizedBox(
                  widthFactor: 0.71,
                  child: Container(
                    height: 24,
                    decoration: BoxDecoration(
                      borderRadius: BorderRadius.circular(3),
                      gradient: LinearGradient(
                        colors: [Colors.green, Colors.lightGreen],
                        begin: Alignment.topLeft,
                        end: Alignment.bottomRight,
                      ),
                    ),
                    child: Center(
                        child: Text(
                      '\$1,013 funded',
                      style: Theme.of(context)
                          .textTheme
                          .labelSmall!
                          .copyWith(color: Colors.white),
                    )),
                  ),
                ),
                FractionallySizedBox(
                  widthFactor: 0.925,
                  alignment: Alignment.centerRight,
                  // left: 0.2425,
                  child: Container(
                    height: 24,
                    child: Align(
                        alignment: Alignment.centerRight,
                        child: Text(
                          '\$408 to go!',
                          style: Theme.of(context)
                              .textTheme
                              .labelSmall!
                              .copyWith(color: Color(0xFF6E7681)),
                        )),
                  ),
                ),
              ],
            ),

            // Tiers.
            gapH18,
            if (screenWidth <= Breakpoints.tablet)
              SelectableText(
                'Contribute',
                style: Theme.of(context).textTheme.titleMedium,
              ),
            if (screenWidth <= Breakpoints.tablet) gapH8,
            Container(
              width: double.infinity,
              child: Row(
                mainAxisAlignment: MainAxisAlignment.start,
                children: <Widget>[
                  if (screenWidth > Breakpoints.tablet)
                    SelectableText(
                      'Contribute:',
                      style: Theme.of(context).textTheme.titleMedium,
                    ),
                  gapW8,
                  SecondaryButton(
                    text: '\$1',
                    onPressed: () {
                      DataService.openInANewTab(
                          'https://opencollective.com/cannlytics-company/contribute/seedling-31614/checkout');
                    },
                  ),
                  gapW8,
                  SecondaryButton(
                    text: '\$4.20',
                    onPressed: () {
                      DataService.openInANewTab(
                          'https://opencollective.com/cannlytics-company/contribute/cannabis-data-scientist-29278/checkout');
                    },
                  ),
                  gapW8,
                  SecondaryButton(
                    text: 'Other',
                    onPressed: () {
                      DataService.openInANewTab(
                          'https://opencollective.com/cannlytics-company/donate');
                    },
                  ),
                  gapW8,
                  _shareLink(context),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  /// Share link.
  Widget _shareLink(BuildContext context) {
    // Theme.
    bool isDark = Theme.of(context).brightness == Brightness.dark;

    return InkWell(
      onTap: () async {
        String url = 'https://opencollective.com/cannlytics-company/donate';
        await Clipboard.setData(ClipboardData(text: url));
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(
              'Copied link!',
              style: Theme.of(context).textTheme.bodyMedium,
            ),
            duration: Duration(seconds: 2),
            backgroundColor: isDark ? DarkColors.green : LightColors.lightGreen,
            showCloseIcon: true,
          ),
        );
      },
      child: Padding(
        padding: EdgeInsets.symmetric(vertical: 8, horizontal: 12),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          mainAxisAlignment: MainAxisAlignment.start,
          children: <Widget>[
            Icon(Icons.link, size: 12, color: Colors.green),
            SizedBox(width: 4),
            Text(
              'Share',
              style: TextStyle(
                fontSize: 12,
                fontWeight: FontWeight.bold,
                color: Colors.green,
              ),
            ),
          ],
        ),
      ),
    );
  }
}

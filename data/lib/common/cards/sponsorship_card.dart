// Cannlytics Data
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 5/9/2023
// Updated: 5/9/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Flutter imports:
import 'package:cannlytics_data/common/buttons/secondary_button.dart';
import 'package:cannlytics_data/utils/utils.dart';
import 'package:flutter/material.dart';

// Project imports:
import 'package:cannlytics_data/constants/design.dart';
import 'package:cannlytics_data/services/data_service.dart';
import 'package:flutter/services.dart';
import 'package:fluttertoast/fluttertoast.dart';

/// Sponsorship card.
class SponsorshipCard extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    final screenWidth = MediaQuery.of(context).size.width;
    return Card(
      margin: EdgeInsets.zero,
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(3)),
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
            gapH4,
            SelectableText(
              'Cannabis data takes time to collect and statistics take time to calculate. Please consider making a contribution to help expedite the curation of cannabis data and AI-powered tools.',
              style: Theme.of(context).textTheme.bodyMedium,
            ),

            // Goal.
            gapH12,
            SelectableText.rich(
              TextSpan(
                text: '',
                style: Theme.of(context).textTheme.bodySmall,
                children: [
                  TextSpan(
                    text: '\$1,012',
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
                      '\$1,012 funded',
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
            if (screenWidth <= Breakpoints.mobile)
              SelectableText(
                'Contribute',
                style: Theme.of(context).textTheme.titleMedium,
              ),
            if (screenWidth <= Breakpoints.mobile) gapH8,
            Container(
              width: double.infinity,
              child: Row(
                mainAxisAlignment: MainAxisAlignment.start,
                children: <Widget>[
                  if (screenWidth > Breakpoints.mobile)
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

  Widget _shareLink(BuildContext context) {
    return InkWell(
      onTap: () async {
        String url = 'https://opencollective.com/cannlytics-company/donate';
        await Clipboard.setData(ClipboardData(text: url));
        Fluttertoast.showToast(
          msg: 'Copied link!',
          toastLength: Toast.LENGTH_SHORT,
          gravity: ToastGravity.TOP,
          timeInSecForIosWeb: 2,
          backgroundColor: Theme.of(context).dialogBackgroundColor,
          textColor: Theme.of(context).textTheme.titleLarge!.color,
          fontSize: 16.0,
          webBgColor:
              WebUtils.colorToHexCode(Theme.of(context).dialogBackgroundColor),
          webPosition: 'center',
          webShowClose: true,
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

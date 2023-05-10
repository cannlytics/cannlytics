// Cannlytics Data
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 5/9/2023
// Updated: 5/9/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

import 'package:cannlytics_data/common/buttons/primary_button.dart';
import 'package:cannlytics_data/constants/design.dart';
import 'package:cannlytics_data/services/data_service.dart';
import 'package:flutter/material.dart';

/// Sponsorship card.
class SponsorshipCard extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(3)),
      child: Container(
        width: 720,
        padding: EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          mainAxisSize: MainAxisSize.min,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  'More coming soon!',
                  style: Theme.of(context).textTheme.titleLarge,
                ),
                PrimaryButton(
                  text: 'Contribute',
                  backgroundColor: Colors.green,
                  onPressed: () {
                    DataService.openInANewTab(
                        'https://cannlytics.com/sponsors');
                  },
                ),
              ],
            ),
            SizedBox(height: 8),
            Text(
              'Rich analytics takes time and money to develop. Please consider making a donation to help us reach our funding requirement sooner so that we can offer this feature to you.',
              style: Theme.of(context).textTheme.bodyMedium,
            ),
            SizedBox(height: 8),
            Text(
              'Goal: \$1,420',
              style: Theme.of(context).textTheme.labelLarge,
            ),
            SizedBox(height: 8),
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
                  widthFactor: 0.70,
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
                      '\$1,000 funded',
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
                          '\$420 to go!',
                          style: Theme.of(context).textTheme.labelSmall,
                        )),
                  ),
                ),
              ],
            ),
            gapH8,
          ],
        ),
      ),
    );
  }
}

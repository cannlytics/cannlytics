// Cannlytics Data
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 5/4/2023
// Updated: 5/4/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Flutter imports:
import 'package:flutter/material.dart';

// Package imports:
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_svg/flutter_svg.dart';

// Project imports:
import 'package:cannlytics_data/common/buttons/primary_button.dart';
import 'package:cannlytics_data/common/cards/wide_card.dart';
import 'package:cannlytics_data/constants/design.dart';

/// Subscriptions cards.
class SubscriptionManagement extends ConsumerWidget {
  const SubscriptionManagement({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    // Render the widget.
    return WideCard(
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                'Subscription',
                style: Theme.of(context).textTheme.titleLarge,
              ),
              // TODO: Display the user's current subscription.
              SizedBox(height: 8),
              SubscriptionPlanCards(),
            ],
          ),
        ],
      ),
    );
  }
}

/// Subscription plan cards.
class SubscriptionPlanCards extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    // Dynamic screen width.
    final screenWidth = MediaQuery.of(context).size.width;

    // Subscription cards.
    // TODO: Get from Firestore.
    var cards = [
      SubscriptionCard(
        title: 'Standard Plan',
        price: '\$4.20',
        features: [
          '10,000 API calls',
          '512 MB data storage',
          '2 GB file storage',
        ],
      ),
      SubscriptionCard(
        title: 'Pro Plan',
        price: '\$42.0',
        features: [
          '50,000 API Calls',
          '4 GB data storage',
          '50 GB file storage',
        ],
      ),
      SubscriptionCard(
        title: 'Enterprise Plan',
        price: '\$420',
        features: [
          '1,000,000+ API Calls',
          '50 GB data storage',
          '500 GB file storage',
          '*White-labeling license',
        ],
      ),
    ];

    // * Unless, you purchase a white-labeling license, then you must provide
    // the following copyright and license when you use datasets, AI-generated
    // material, or other services provided by the Cannlytics API.

    // Copyright (c) 2020-2023 Cannlytics and The Cannabis Data Science Team

    // Permission is hereby granted, free of charge, to any person obtaining
    // a copy of this software and associated documentation files (the
    // "Software"), to deal in the Software without restriction, including
    // without limitation the rights to use, copy, modify, merge, publish,
    // distribute, sublicense, and/or sell copies of the Software, and to
    // permit persons to whom the Software is furnished to do so, subject to
    // the following conditions:

    // The above copyright notice and this permission notice shall be
    // included in all copies or substantial portions of the Software.

    // THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
    // EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
    // MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
    // NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
    // LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
    // OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
    // WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

    // Row of cards (column on tablet and mobile).
    return Center(
      child: (screenWidth < Breakpoints.desktop)
          ? Column(
              children: cards,
            )
          : Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: cards,
            ),
    );
  }
}

/// Subscription card.
class SubscriptionCard extends StatelessWidget {
  final String title;
  final String price;
  final List<String> features;

  SubscriptionCard({
    required this.title,
    required this.price,
    required this.features,
  });

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: 260.0,
      child: Card(
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(3),
        ),
        margin: EdgeInsets.symmetric(horizontal: 16, vertical: 8),
        child: Padding(
          padding: EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Title.
              // TODO: Color title depending on plan.
              Text(
                title,
                style: Theme.of(context).textTheme.titleMedium,
              ),

              // Price.
              SizedBox(height: 8),
              Row(
                crossAxisAlignment: CrossAxisAlignment.baseline,
                children: [
                  Text(
                    price,
                    style: Theme.of(context).textTheme.titleLarge,
                  ),
                  Text(
                    ' / month',
                    style: Theme.of(context).textTheme.bodySmall,
                  ),
                ],
              ),
              SizedBox(height: 4),
              Text(
                'Billed monthly',
                style: Theme.of(context).textTheme.bodySmall,
              ),

              // TODO: Display active if this is the user's current plan.

              // TODO: Display a button to upgrade to this plan.
              PrimaryButton(
                text: 'Select Plan',
                // backgroundColor: Colors.green,
              ),

              // Features.
              SizedBox(height: 8),
              ...features.map(
                (feature) => Padding(
                  padding: EdgeInsets.only(bottom: 4),
                  child: Column(
                    children: [
                      Divider(
                        color: Colors.grey,
                        thickness: 1,
                        height: 16,
                      ),
                      Row(
                        children: [
                          SvgPicture.asset(
                            'assets/icons/emoji/green_check.svg',
                            height: 24,
                            width: 24,
                          ),
                          Text(feature),
                        ],
                      ),
                    ],
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

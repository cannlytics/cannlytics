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
    return Column(
      mainAxisAlignment: MainAxisAlignment.start,
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        WideCard(
          color: Theme.of(context).scaffoldBackgroundColor,
          surfaceTintColor: Theme.of(context).scaffoldBackgroundColor,
          child: Column(
            // crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                'Choose a Subscription',
                style: Theme.of(context).textTheme.titleLarge,
              ),
              gapH8,
              Text(
                'Choose the plan that works best for you.',
                style: Theme.of(context).textTheme.titleMedium,
              ),

              // Subscriptions for user's without a subscription.
              gapH8,
              SubscriptionPlanCards(),
              // YearlyMonthlySubscriptions(),

              // TODO: Display the user's current subscription.
            ],
          ),
        ),
      ],
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
          title: 'Free',
          price: '🤗',
          color: Color(0xff16c995),
          features: [
            '10 AI jobs',
            'Personal archive',
            'Access all data',
          ],
          notes: 'No credit card required'),
      SubscriptionCard(
        title: 'Standard Plan',
        price: '\$4.20',
        color: Color(0xffFF7F00),
        features: [
          '100 AI jobs',
          '4.2\u00A2 / additional job',
          'Throttled API',
        ],
      ),
      SubscriptionCard(
        title: 'Pro Plan',
        price: '\$42',
        color: Color(0xff7B4EA8),
        features: [
          '1,250 AI jobs',
          '3.3\u00A2 / additional job',
          '🚀 Unthrottled API',
        ],
      ),
      // SubscriptionCard(
      //   title: 'Enterprise Plan',
      //   price: '\$420',
      //   color: Color(0xff7B4EA8),
      //   features: [
      //     '1,000 AI Jobs',
      //     '40+ hours of AI runtime',
      //     '1,000,000+ API Calls',
      //   ],
      // ),
    ];

    // Row of cards (column on tablet and mobile).
    if (screenWidth < Breakpoints.desktop) {
      return Center(
        child: Column(
          children: cards,
        ),
      );
    } else {
      return Container(
        width: double.infinity,
        child: Row(
          mainAxisAlignment: MainAxisAlignment.spaceEvenly,
          mainAxisSize: MainAxisSize.max,
          children: cards,
        ),
      );
    }
  }
}

/// Subscription card.
/// TODO: Display active if this is the user's current plan.
class SubscriptionCard extends StatelessWidget {
  final String title;
  final String price;
  final List<String> features;
  final Color? color;
  final String? notes;

  SubscriptionCard({
    required this.title,
    required this.price,
    required this.features,
    this.color,
    this.notes,
  });

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: 260.0,
      height: 320,
      child: Card(
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(3),
        ),
        margin: EdgeInsets.symmetric(horizontal: 16, vertical: 8),
        child: Padding(
          padding: EdgeInsets.only(top: 16, left: 16, right: 16),
          child: Column(
            children: [
              // Title.
              Text(
                title,
                textAlign: TextAlign.start,
                style: Theme.of(context).textTheme.titleMedium!.copyWith(
                      color: color,
                      fontWeight: FontWeight.bold,
                    ),
              ),

              // Price.
              SizedBox(height: 8),
              Row(
                mainAxisAlignment: MainAxisAlignment.center,
                crossAxisAlignment: CrossAxisAlignment.baseline,
                textBaseline: TextBaseline.alphabetic,
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

              // Select plan button.
              // TODO: Display a button to upgrade to this plan.
              Container(
                margin: EdgeInsets.symmetric(vertical: 16),
                width: double.infinity,
                child: PrimaryButton(
                  backgroundColor: color,
                  text: 'Select Plan',
                  // backgroundColor: Colors.green,
                  onPressed: () {
                    print('TODO: Proceed to checkout plan: $title');
                  },
                ),
              ),

              // Features.
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

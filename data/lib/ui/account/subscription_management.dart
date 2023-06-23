// Cannlytics Data
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 5/4/2023
// Updated: 6/23/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Flutter imports:
import 'package:cannlytics_data/ui/account/account_controller.dart';
import 'package:flutter/material.dart';

// Package imports:
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_svg/flutter_svg.dart';

// Project imports:
import 'package:cannlytics_data/common/buttons/primary_button.dart';
import 'package:cannlytics_data/common/cards/wide_card.dart';
import 'package:cannlytics_data/constants/design.dart';
import 'package:url_launcher/url_launcher.dart';

/// Subscriptions cards.
class SubscriptionManagement extends ConsumerWidget {
  const SubscriptionManagement({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    // Get subscriptions.
    final asyncSnapshot = ref.watch(userSubscriptionProvider);

    return asyncSnapshot.when(
      data: (data) {
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
                  SubscriptionPlanCards(
                    items: [],
                    activeSubscription: data['support'],
                  ),
                ],
              ),
            ),
          ],
        );
      },
      loading: () => CircularProgressIndicator(),
      error: (error, stack) => Text('Error: $error'),
    );
  }
}

/// Subscription plan cards.
class SubscriptionPlanCards extends StatelessWidget {
  const SubscriptionPlanCards({
    Key? key,
    required this.items,
    this.activeSubscription,
  }) : super(key: key);

  // Parameters.
  final List<Map> items;
  final String? activeSubscription;

  @override
  Widget build(BuildContext context) {
    // Dynamic screen width.
    final screenWidth = MediaQuery.of(context).size.width;

    // Subscription cards.
    // FIXME: Get from Firestore.
    // var cards = items.map((item) {
    //   return SubscriptionCard(
    //     title: item['title'],
    //     price: item['price'],
    //     color: WebUtils.hexCodeToColor(item['color']),
    //     features: item['features'],
    //     notes: item['notes'],
    //   );
    // }).toList();
    var cards = [
      SubscriptionCard(
          active: activeSubscription == 'free',
          title: 'Free',
          price: '\$0',
          color: Color(0xff16c995),
          features: [
            '10 AI jobs',
            'Personal archive',
            'Access all data',
          ],
          notes: 'No credit card required'),
      SubscriptionCard(
        active: activeSubscription == 'premium',
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
        active: activeSubscription == 'pro',
        title: 'Pro Plan',
        price: '\$42',
        color: Color(0xff7B4EA8),
        features: [
          '1,250 AI jobs',
          '3.3\u00A2 / additional job',
          '🚀 Unthrottled API',
        ],
      ),
    ];

    // Row of cards (column on tablet and mobile).
    return GridView.builder(
      shrinkWrap: true,
      gridDelegate: SliverGridDelegateWithMaxCrossAxisExtent(
        maxCrossAxisExtent: (screenWidth < Breakpoints.tablet) ? 460 : 380,
        mainAxisExtent: (screenWidth < Breakpoints.tablet) ? 320 : 340,
        // crossAxisCount: (screenWidth < Breakpoints.tablet) ? 2 : 3,
        // childAspectRatio: 3 / 4,
      ),
      itemCount: cards.length,
      itemBuilder: (context, index) {
        return cards[index];
      },
    );
  }
}

/// Subscription card.
class SubscriptionCard extends StatelessWidget {
  final String title;
  final String price;
  final List<String> features;
  final Color? color;
  final String? notes;
  final bool? active;

  SubscriptionCard({
    required this.title,
    required this.price,
    required this.features,
    this.color,
    this.notes,
    this.active,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(3),
        side: BorderSide(
          color: active! ? Color(0xff16c995) : Colors.transparent,
          width: 2.0,
        ),
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
            Container(
              margin: EdgeInsets.symmetric(vertical: 16),
              width: double.infinity,
              child: PrimaryButton(
                backgroundColor: color,
                text: active! ? 'Cancel' : 'Select Plan',
                onPressed: () async {
                  const url = 'https://cannlytics.com/account/subscriptions';
                  await launchUrl(Uri.parse(url));
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
    );
  }
}

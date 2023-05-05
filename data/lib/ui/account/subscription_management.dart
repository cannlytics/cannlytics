// Cannlytics Data
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 5/4/2023
// Updated: 5/4/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

import 'package:cannlytics_data/common/cards/wide_card.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

/// Subscriptions cards.
class SubscriptionManagement extends ConsumerWidget {
  const SubscriptionManagement({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    // Dynamic screen width.
    final screenWidth = MediaQuery.of(context).size.width;

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
              SizedBox(height: 8),
              SubscriptionPlanCards(),
            ],
          ),
        ],
      ),
    );
  }
}

class SubscriptionPlanCards extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.spaceAround,
        children: [
          SubscriptionCard(
            title: 'Basic Plan',
            price: '\$10',
            features: ['Feature 1', 'Feature 2'],
          ),
          SubscriptionCard(
            title: 'Pro Plan',
            price: '\$20',
            features: ['Feature 1', 'Feature 2', 'Feature 3'],
          ),
          SubscriptionCard(
            title: 'Premium Plan',
            price: '\$30',
            features: ['Feature 1', 'Feature 2', 'Feature 3', 'Feature 4'],
          ),
        ],
      ),
    );
  }
}

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
    return Card(
      margin: EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      child: Padding(
        padding: EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              title,
              style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
            ),
            SizedBox(height: 8),
            Text(
              price,
              style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
            ),
            SizedBox(height: 16),
            Text('Features:'),
            SizedBox(height: 8),
            ...features.map((feature) => Padding(
                  padding: EdgeInsets.only(bottom: 4),
                  child: Text('• $feature'),
                )),
          ],
        ),
      ),
    );
  }
}

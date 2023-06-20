// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 5/5/2023
// Updated: 5/5/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Package imports:
import 'package:cannlytics_data/services/firestore_service.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

/// Stream user results from Firebase.
final appSubscriptions =
    FutureProvider.autoDispose<List<Map<dynamic, dynamic>>>((ref) async {
  final FirestoreService _dataSource = ref.watch(firestoreProvider);
  return await _dataSource.getCollection(
    path: 'public/subscriptions/data_subscriptions',
    builder: (data, documentId) => data!,
    queryBuilder: (query) => query.orderBy('price', descending: true).limit(3),
  );
});

/// Subscriptions provider.
final subscriptionsProvider =
    FutureProvider.autoDispose<List<Map>>((ref) async {
  // FIXME: Get subscriptions from Firestore.
  final _firestore = ref.watch(firestoreProvider);
  print('GETTING DATA FROM FIRESTORE....');
  return await _firestore.getCollection(
    path: 'public/subscriptions/data_subscriptions',
    builder: (data, id) => data!,
  );
  // return [
  //   {
  //     "action": "Launch Now &#128640;",
  //     "attributes": [
  //       "Custom installation",
  //       "Access to admin tools",
  //       "Feature requests",
  //       "Talk with devs"
  //     ],
  //     "color": "purple",
  //     "id": "enterprise",
  //     "name": "Enterprise",
  //     "plan_id": "P-7RM68306C7236770NMDXYEDY",
  //     "plan_name": "Cannlytics Enterprise Subscription",
  //     "price": "\$1,200 / mo.",
  //     "price_now": "\$1,200",
  //     "url": "/contact"
  //   },
  //   {
  //     "action": "Get started &#127939;&#8205;&#9792;&#65039;",
  //     "attributes": [
  //       "Metrc integration",
  //       "Access to dev tools",
  //       "Unlimited data storage",
  //       "Email support"
  //     ],
  //     "color": "orange",
  //     "frequency": "monthly",
  //     "id": "pro",
  //     "name": "Pro",
  //     "plan_description": "The first paid tier of software support.",
  //     "plan_id": "P-22S54953UU465160KMDXYFLI",
  //     "plan_name": "Cannlytics Pro Subscription",
  //     "price": "\$420 / mo.",
  //     "price_now": "\$420",
  //     "short_name": "Pro",
  //     "url": "/contact"
  //   },
  //   {
  //     "action": "Get Started &#9997;",
  //     "attributes": [
  //       "All datasets",
  //       "All videos",
  //       "All whitepapers",
  //       "API access"
  //     ],
  //     "color": "orange",
  //     "frequency": "monthly",
  //     "id": "premium",
  //     "name": "Premium",
  //     "plan_description": "The first paid tier of software support.",
  //     "plan_id": "P-09317319A0968501MMF66YHI",
  //     "plan_name": "Cannlytics Pro Subscription",
  //     "price": "\$4.20 / mo.",
  //     "price_now": "\$4.20",
  //     "short_name": "Premium"
  //   },
  //   {
  //     "action": "Get started &#127939;&#8205;&#9792;&#65039;",
  //     "attributes": [
  //       {"name": "All software", "limited": false},
  //       {"name": "Limited data storage", "limited": true},
  //       {"name": "Limited file storage", "limited": true},
  //       {"name": "Limited API access", "limited": true},
  //       {"name": "GitHub Issues only", "limited": true}
  //     ],
  //     "color": "green",
  //     "frequency": "monthly",
  //     "id": "free",
  //     "name": "free",
  //     "plan_description": "The free tier.",
  //     "plan_id": "",
  //     "plan_name": "Free",
  //     "price": "&#128080;",
  //     "price_now": "",
  //     "short_name": "Free",
  //     "url": "/"
  //   }
  // ];
  // var response;
  // try {
  //   response = await APIService.apiRequest('/organizations');
  // } catch (error) {
  //   print('NO API CONNECTION!');
  //   return [];
  // }
  // return response;
});

/// Subscription provider.
final subscriptionProvider = FutureProvider.autoDispose<Map>((ref) async {
  // FIXME: Get the user's subscription from Firestore.
  return {};
});

/// Subscription service.
class SubscriptionService {
  const SubscriptionService._();

  // TODO: Get user's subscription from Firestore.

  // TODO: Get subscriptions from Firestore.

  // TODO: Change subscription.

  // TODO: Cancel subscription.

  // TODO: Stream usage statistics.

  // TODO: View paid invoices.
}

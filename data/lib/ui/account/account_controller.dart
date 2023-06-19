// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 2/18/2023
// Updated: 4/16/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Dart imports:
import 'dart:async';

// Package imports:
import 'package:cannlytics_data/services/api_service.dart';
import 'package:firebase_auth/firebase_auth.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

// Project imports:
import 'package:cannlytics_data/services/auth_service.dart';
import 'package:cannlytics_data/services/firestore_service.dart';
import 'package:cannlytics_data/ui/dashboard/dashboard_controller.dart';

/* === User === */

// An instance of the account controller to use as a provider.
final accountProvider =
    AutoDisposeAsyncNotifierProvider<AccountController, void>(
        AccountController.new);

/// Controller that manages the user's account.
class AccountController extends AutoDisposeAsyncNotifier<void> {
  @override
  FutureOr<void> build() {}

  /// Change the user's photo.
  Future<String> changePhoto() async {
    final authService = ref.read(authProvider);
    state = const AsyncLoading();
    var message;
    state = const AsyncLoading();
    state = await AsyncValue.guard(() async {
      message = await authService.changePhoto();
    });
    return message;
  }

  /// Send the user a reset password email.
  Future<String> resetPassword(String email) async {
    final authService = ref.read(authProvider);
    var message;
    state = const AsyncLoading();
    state = await AsyncValue.guard(() async {
      message = await authService.resetPassword(email);
    });
    return message;
  }

  /// Sign the user out.
  Future<void> signOut() async {
    final authService = ref.read(authProvider);
    state = const AsyncLoading();
    state = await AsyncValue.guard(authService.signOut);
  }

  /// Update the user's display name and email.
  Future<void> updateUser({
    String? email,
    String? displayName,
    String? phoneNumber,
  }) async {
    // final authService = ref.read(authProvider);
    state = const AsyncLoading();
    state = await AsyncValue.guard(() async {
      final user = ref.read(userProvider).value;
      final _firestore = ref.watch(firestoreProvider);

      if (user != null) {
        if (displayName != null && displayName != user.displayName) {
          await user.updateDisplayName(displayName);
        }

        if (email != null && email != user.email) {
          await user.updateEmail(email);
        }

        if (phoneNumber != null && phoneNumber != user.phoneNumber) {
          // First, create a PhoneAuthCredential with the verification ID and verification code
          // obtained from the user.
          final credential = PhoneAuthProvider.credential(
            verificationId:
                "verificationId", // Replace with your verification ID
            smsCode: "smsCode", // Replace with your verification code
          );

          // Then update the user's phone number with the new phone number.
          await user.updatePhoneNumber(credential);
        }

        // Update the user's data in Firestore.
        await _firestore.setData(
          path: 'users/${user.uid}',
          data: {
            'email': user.email,
            'display_name': user.displayName,
            'phone_number': user.phoneNumber,
          },
        );
      }
    });
  }

  /// Save the user's data.
  Future<void> saveUserData(Map<String, dynamic> data) async {
    final _firestore = ref.watch(firestoreProvider);
    state = const AsyncLoading();
    state = await AsyncValue.guard(() async {
      final user = ref.read(userProvider).value;
      if (user != null) {
        await _firestore.setData(
          path: 'users/${user.uid}',
          data: data,
        );
      }
    });
  }

  /// Get the user's subscription.
  Future<Map> getSubscription() async {
    final _firestore = ref.watch(firestoreProvider);
    var subscription = {};
    state = const AsyncLoading();
    state = await AsyncValue.guard(() async {
      final user = ref.read(userProvider).value;
      if (user != null) {
        String path = 'users/${user.uid}/subscription';
        subscription = await _firestore.getDocument(path: path) ?? {};
      }
    });
    return subscription;
  }

  /// TODO: Subscribe to a paid subscription.
  /// POST /src/payments/subscribe
  /// data = {'email': userEmail, 'plan_name': planName, 'id': planId}
  /// For now, link to: https://cannlytics.com/account/subscriptions

  /// TODO: Unsubscribe from a paid subscription.
  /// POST /src/payments/unsubscribe
  /// data = {'plan_name': planName}

  /// TODO: Get subscription plans.
  /// public/subscriptions/subscription_plans/${name}

  /// TODO: Get API Keys.
  /// GET /api/auth/get-keys

  /// TODO: Create API key.
  /// POST /api/auth/create-key
  /// data = {
  ///   'name': 'My API Key',
  ///   'permissions': ['read', 'write'],
  /// }

  /// TODO: Delete API key.
  /// POST /api/auth/delete-key
  /// data = {'name': 'My API Key'}
}

/* === Subscription === */

// Subscription service provider.
final subscriptionService = Provider<SubscriptionService>((ref) {
  return SubscriptionService();
});

/// Subscription service.
class SubscriptionService {
  const SubscriptionService();

  // Get subscriptions.
  Future<void> getSubscriptions(String uid) async {
    print('Getting subscriptions...');
    String url = '/src/payments/subscriptions';
    var response = await APIService.apiRequest(url, options: {'get': true});
    return response;
  }

  // Unsubscribe from a plan.
  Future<void> unsubscribe(String uid, String planName) async {
    print('Unsubscribing from plan...');
    String url = '/src/payments/unsubscribe';
    await APIService.apiRequest(url, data: {'plan_name': planName});
  }

  // Purchase additional tokens.
  Future<void> purchaseTokens(String uid, int tokenCount) async {
    print('Purchasing tokens...');
    String url = '/src/payments/tokens';
    await APIService.apiRequest(url, data: {'token_count': tokenCount});
  }

  // Purchase additional tokens with PayPal.
  Future<void> purchaseTokensWithPayPal(String uid, int tokenCount) async {
    print('Purchasing tokens with PayPal...');
    // You would need to implement the PayPal payment flow here.
    // This is a placeholder as the implementation would depend on your specific PayPal integration.
  }
}

/* === Invoices === */

/* === API Keys === */

// API Key service provider.
final apiKeyService = Provider<APIKeyService>((ref) {
  return APIKeyService();
});

/// API Key service.
class APIKeyService {
  const APIKeyService();

  // Create API key.
  Future<String> createAPIKey() async {
    print('Creating API key...');
    String url = '/api/auth/create-key';
    var data = {}; // Replace with your form data
    var response = await APIService.apiRequest(url, data: data);
    return response['api_key'];
  }

  // Delete API key.
  Future<void> deleteAPIKey() async {
    print('Deleting API key...');
    String url = '/api/auth/delete-key';
    var data = {}; // Replace with your form data
    var response = await APIService.apiRequest(url, data: data);
    if (!response['success']) {
      print('Error deleting API key: ${response['message']}');
      return;
    }
    print('API key deleted successfully');
  }

  // Get API keys.
  Future<List> getAPIKeys() async {
    print('Getting API keys...');
    String url = '/api/auth/get-keys';
    var response = await APIService.apiRequest(url);
    return response['data'];
  }
}

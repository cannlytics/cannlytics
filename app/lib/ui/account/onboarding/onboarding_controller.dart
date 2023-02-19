// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 2/18/2023
// Updated: 2/19/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>
import 'dart:async';

import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:cannlytics_app/ui/account/onboarding/onboarding_screen.dart';

/// [OnboardingStore] manages onboarding data.
class OnboardingStore {
  // Local user data.
  OnboardingStore(this.localData);
  final SharedPreferences localData;

  // Change onboarding completion
  Future<void> setOnboardingComplete() async {
    await localData.setBool('onboardingComplete', true);
  }

  // Set the type of business.
  Future<void> setUserType(String value) async {
    await localData.setString('userType', value);
  }

  // Whether onboarding is complete or not.
  bool isOnboardingComplete() {
    return localData.getBool('onboardingComplete') ?? false;
  }

  // Whether the user is a business or not.
  String userType() {
    return localData.getString('userType') ?? 'consumer';
  }
}

// An instance of the store.
final onboardingStoreProvider =
    Provider<OnboardingStore>((ref) => throw UnimplementedError());

/// [OnboardingController] manages the [OnboardingScreen].
class OnboardingController extends AutoDisposeAsyncNotifier<void> {
  @override
  FutureOr<void> build() {}

  /// [completeOnboarding] completes the onboarding process, setting user type.
  Future<void> completeOnboarding(String choice) async {
    final onboardingStore = ref.watch(onboardingStoreProvider);
    state = const AsyncLoading();
    state = await AsyncValue.guard(() => onboardingStore.setUserType(choice));
    state = await AsyncValue.guard(onboardingStore.setOnboardingComplete);
  }
}

// A controller instance.
final onboardingController =
    AutoDisposeAsyncNotifierProvider<OnboardingController, void>(
        OnboardingController.new);

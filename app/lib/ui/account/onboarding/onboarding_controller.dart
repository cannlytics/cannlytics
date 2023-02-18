// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 2/18/2023
// Updated: 2/18/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>
import 'dart:async';

import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:cannlytics_app/ui/account/onboarding/onboarding_screen.dart';

/// [OnboardingStore] manages onboarding data.
class OnboardingStore {
  // Preferred data.
  OnboardingStore(this.sharedPreferences);
  final SharedPreferences sharedPreferences;

  // Key for onboarding completion.
  static const onboardingCompleteKey = 'onboardingComplete';

  // Change onboarding completion
  Future<void> setOnboardingComplete() async {
    await sharedPreferences.setBool(onboardingCompleteKey, true);
  }

  // Whether or not onboarding is complete.
  bool isOnboardingComplete() =>
      sharedPreferences.getBool(onboardingCompleteKey) ?? false;
}

/// [OnboardingController] manages the [OnboardingScreen].
class OnboardingController extends AutoDisposeAsyncNotifier<void> {
  @override
  FutureOr<void> build() {}

  /// [completeOnboarding] completes the onboarding process.
  Future<void> completeOnboarding() async {
    final onboardingStore = ref.watch(onboardingStoreProvider);
    state = const AsyncLoading();
    state = await AsyncValue.guard(onboardingStore.setOnboardingComplete);
  }
}

// An instance of the store.
final onboardingStoreProvider =
    Provider<OnboardingStore>((ref) => throw UnimplementedError());

// A controller instance.
final onboardingController =
    AutoDisposeAsyncNotifierProvider<OnboardingController, void>(
        OnboardingController.new);

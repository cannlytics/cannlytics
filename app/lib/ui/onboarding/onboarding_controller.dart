import 'dart:async';

import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:cannlytics_app/services/onboarding_repository.dart';

class OnboardingController extends AutoDisposeAsyncNotifier<void> {
  @override
  FutureOr<void> build() {
    // no op
  }

  Future<void> completeOnboarding() async {
    final onboardingRepository = ref.watch(onboardingRepositoryProvider);
    state = const AsyncLoading();
    state = await AsyncValue.guard(onboardingRepository.setOnboardingComplete);
  }
}

final onboardingControllerProvider =
    AutoDisposeAsyncNotifierProvider<OnboardingController, void>(
        OnboardingController.new);

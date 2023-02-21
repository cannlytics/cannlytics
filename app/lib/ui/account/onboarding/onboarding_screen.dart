// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 2/18/2023
// Updated: 2/19/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>
import 'package:cannlytics_app/constants/design.dart';
import 'package:cannlytics_app/routing/routes.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:cannlytics_app/ui/account/onboarding/onboarding_controller.dart';
import 'package:cannlytics_app/routing/app_router.dart';

/// The initial screen the user sees to choose "Consumer" or "Business".
class OnboardingScreen extends ConsumerWidget {
  const OnboardingScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return Scaffold(
      backgroundColor: Colors.white,
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            appLogo(),
            gapH24,
            const StartChoices(),
          ],
        ),
      ),
    );
  }

  /// A simple logo widget.
  Widget appLogo() {
    return FractionallySizedBox(
      widthFactor: 0.5,
      child: Image.asset(
        'assets/images/logos/cannlytics_logo_with_text_light.png',
        height: 60,
      ),
    );
  }
}

/// A widget that allows the user to choose between "Consumer" and "Business".
class StartChoices extends ConsumerWidget {
  const StartChoices({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final state = ref.watch(onboardingController);
    return Row(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        // Consumer choice.
        Flexible(
          child: Container(
            constraints: const BoxConstraints(maxWidth: 300),
            child: Card(
              elevation: 0,
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(10.0),
                side: const BorderSide(
                  color: Colors.grey,
                  width: 0.1,
                ),
              ),
              child: InkWell(
                borderRadius: BorderRadius.circular(8),
                onTap: state.isLoading
                    ? null
                    : () async {
                        await ref
                            .read(onboardingController.notifier)
                            .completeOnboarding('consumer');
                        context.goNamed(AppRoutes.signIn.name);
                      },
                child: Padding(
                  padding:
                      const EdgeInsets.symmetric(vertical: 24, horizontal: 36),
                  child: Column(
                    children: [
                      Image.asset(
                        'assets/images/icons/figures.png',
                        width: 75,
                      ),
                      const Text('Consumer'),
                    ],
                  ),
                ),
              ),
            ),
          ),
        ),

        // Spacer.
        gapW12,

        // Business choice.
        Flexible(
          child: Container(
            constraints: const BoxConstraints(maxWidth: 300),
            child: Card(
              elevation: 0,
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(10.0),
                side: const BorderSide(
                  color: Colors.grey,
                  width: 0.1,
                ),
              ),
              child: InkWell(
                borderRadius: BorderRadius.circular(8),
                onTap: state.isLoading
                    ? null
                    : () async {
                        await ref
                            .read(onboardingController.notifier)
                            .completeOnboarding('business');
                        context.goNamed(AppRoutes.signIn.name);
                      },
                child: Padding(
                  padding:
                      const EdgeInsets.symmetric(vertical: 24, horizontal: 36),
                  child: Column(
                    children: [
                      Image.asset(
                        'assets/images/icons/organizations.png',
                        width: 75,
                      ),
                      const Text('Business'),
                    ],
                  ),
                ),
              ),
            ),
          ),
        ),
      ],
    );
  }
}

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_svg/flutter_svg.dart';
import 'package:go_router/go_router.dart';
import 'package:cannlytics_app/widgets/primary_button.dart';
import 'package:cannlytics_app/ui/onboarding/onboarding_controller.dart';
import 'package:cannlytics_app/localization/string_hardcoded.dart';
import 'package:cannlytics_app/routing/app_router.dart';

class OnboardingScreen extends ConsumerWidget {
  const OnboardingScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final state = ref.watch(onboardingControllerProvider);
    return Scaffold(
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // App logo.
            FractionallySizedBox(
              widthFactor: 0.5,
              child: Image.asset(
                'assets/images/logos/cannlytics_logo_with_text_light.png',
              ),
            ),

            // Get started button.
            PrimaryButton(
              text: 'Get Started'.hardcoded,
              isLoading: state.isLoading,
              onPressed: state.isLoading
                  ? null
                  : () async {
                      await ref
                          .read(onboardingControllerProvider.notifier)
                          .completeOnboarding();
                      // TODO: Check if mounted
                      // go to sign in page after completing onboarding
                      context.goNamed(AppRoute.signIn.name);
                    },
            ),
          ],
        ),
      ),
    );
  }
}

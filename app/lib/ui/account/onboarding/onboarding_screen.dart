// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 2/18/2023
// Updated: 2/19/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Flutter imports:
import 'package:flutter/material.dart';

// Package imports:
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

// Project imports:
import 'package:cannlytics_app/constants/design.dart';
import 'package:cannlytics_app/routing/app_router.dart';
import 'package:cannlytics_app/routing/routes.dart';
import 'package:cannlytics_app/services/theme_service.dart';
import 'package:cannlytics_app/ui/account/onboarding/onboarding_controller.dart';
import 'package:cannlytics_app/widgets/cards/hover_border.dart';

/// The initial screen the user sees to choose "Consumer" or "Business".
class OnboardingScreen extends ConsumerWidget {
  const OnboardingScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final themeMode = ref.watch(themeModeProvider);
    final bool isDark = themeMode == ThemeMode.dark;
    return Scaffold(
      backgroundColor: Colors.white,
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            appLogo(isDark),
            gapH24,
            const StartChoices(),
          ],
        ),
      ),
    );
  }

  /// A simple logo widget.
  Widget appLogo(bool isDark) {
    return FractionallySizedBox(
      widthFactor: 0.5,
      child: Image.asset(
        isDark
            ? 'assets/images/logos/cannlytics_logo_with_text_light.png'
            : 'assets/images/logos/cannlytics_logo_with_text_dark.png',
        height: 45,
      ),
    );
  }
}

/// A widget that allows the user to choose between "Consumer" and "Business".
class StartChoices extends StatelessWidget {
  const StartChoices({super.key});

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.center,
      children: const [
        // Consumer choice.
        StartingCard(
          title: 'Consumer',
          route: 'consumer',
          imageName: 'assets/images/icons/figures.png',
        ),

        // Spacer.
        gapW12,

        // Business choice.
        StartingCard(
          title: 'Business',
          route: 'business',
          imageName: 'assets/images/icons/organizations.png',
        ),
      ],
    );
  }
}

/// A card to display starting choices.
class StartingCard extends ConsumerWidget {
  const StartingCard({
    super.key,
    required this.title,
    required this.route,
    required this.imageName,
  });
  final String title;
  final String route;
  final String imageName;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final state = ref.watch(onboardingController);
    return Flexible(
      child: Container(
        constraints: const BoxConstraints(maxWidth: 300),
        child: BorderMouseHover(
          builder: (context, value) => InkWell(
            borderRadius: BorderRadius.circular(3),
            onTap: state.isLoading
                ? null
                : () async {
                    await ref
                        .read(onboardingController.notifier)
                        .completeOnboarding(route);
                    context.goNamed(AppRoutes.signIn.name);
                  },
            child: Card(
              elevation: 0,
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(3),
              ),
              child: Padding(
                padding: const EdgeInsets.symmetric(
                  vertical: 24,
                  horizontal: 36,
                ),
                child: Column(
                  children: [
                    Image.asset(
                      imageName,
                      width: 75,
                    ),
                    Text(title),
                  ],
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }
}

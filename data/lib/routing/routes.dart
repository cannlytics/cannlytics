// Cannlytics Data
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 2/18/2023
// Updated: 4/14/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>
// Dart imports:

// Project imports:
import 'package:cannlytics_data/routing/app_router.dart';
import 'package:cannlytics_data/ui/account/account_screen.dart';
import 'package:cannlytics_data/ui/account/reset_password_screen.dart';
import 'package:cannlytics_data/ui/main/dashboard.dart';

// The main app routes.
class Routes {
  static List<AppRoute> mainRoutes = [
    // User account screens.
    AppRoute(
      path: '/account',
      name: 'account',
      builder: (context, state) => AccountScreen(),
      routes: [
        // Reset password screen.
        AppRoute(
          path: 'reset-password',
          name: 'resetPassword',
          builder: (context, state) => ResetPasswordScreen(),
        ),
      ],
    ),

    // Dashboard screen.
    AppRoute(
      path: '/',
      name: 'dashboard',
      builder: (context, state) => DashboardScreen(),
      useFade: true,
    ),

    // TODO:
    // Licensees screen.

    // Strains screen.

    // Products screen.

    // Lab results screen.

    // Sales screen.

    // Research screen.

    // Settings screen.

    // Help screen.
  ];
}

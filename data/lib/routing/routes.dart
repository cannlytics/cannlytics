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
import 'package:cannlytics_data/ui/ai/coa_doc/coa_doc.dart';
import 'package:cannlytics_data/ui/licensees/licensees_screen.dart';
import 'package:cannlytics_data/ui/main/dashboard.dart';
import 'package:cannlytics_data/ui/results/results_screen.dart';
import 'package:cannlytics_data/ui/sales/sales_screen.dart';
import 'package:cannlytics_data/ui/strains/strains_screen.dart';

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

    // Licensees screen.
    AppRoute(
      path: '/licensees',
      name: 'licensees',
      builder: (context, state) => LicenseesScreen(),
      useFade: true,
    ),

    // Strains screen.
    AppRoute(
      path: '/strains',
      name: 'strains',
      builder: (context, state) => StrainsScreen(),
      useFade: true,
    ),

    // Optional: Products screen.
    // AppRoute(
    //   path: '/strains',
    //   name: 'strains',
    //   builder: (context, state) => StrainsScreen(),
    //   useFade: true,
    // ),

    // Lab results screen.
    AppRoute(
      path: '/results',
      name: 'results',
      builder: (context, state) => LabResultsScreen(),
      useFade: true,
    ),

    // Sales screen.
    AppRoute(
      path: '/sales',
      name: 'sales',
      builder: (context, state) => SalesScreen(),
      useFade: true,
    ),

    // // Industry screen.
    // AppRoute(
    //   path: '/production',
    //   name: 'production',
    //   builder: (context, state) => ProductionScreen(),
    //   useFade: true,
    // ),

    // // Research screen.
    // AppRoute(
    //   path: '/research',
    //   name: 'research',
    //   builder: (context, state) => ResearchScreen(),
    //   useFade: true,
    // ),

    // AI Models.
    AppRoute(
      path: '/models',
      name: 'models',
      builder: (context, state) => DashboardScreen(),
      routes: [
        // CoADoc screen.
        AppRoute(
          path: 'coas',
          name: 'CoADoc',
          builder: (context, state) => CoADocScreen(),
        ),

        // SkunkFx screen.
        AppRoute(
          path: 'effects',
          name: 'SkunkFx',
          builder: (context, state) => CoADocScreen(),
        ),
      ],
    ),
  ];
}

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
import 'package:cannlytics_data/ui/dashboard/dashboard.dart';
import 'package:cannlytics_data/ui/licensees/licensee_screen.dart';
import 'package:cannlytics_data/ui/licensees/licensees_screen.dart';
import 'package:cannlytics_data/ui/licensees/state_licensees.dart';
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

        // Subscription screen.

        // API keys screen.

        // Invoices screen.
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
      path: '/licenses',
      name: 'licenses',
      useFade: true,
      builder: (context, state) => LicenseesScreen(),
    ),

    // Licenses by state screen.
    AppRoute(
      path: '/licenses/:state_id',
      name: 'state_licenses',
      useFade: true,
      builder: (context, state) {
        return StateLicensesScreen(id: state.params['state_id']!);
      },
    ),

    // Licensee screen if a license number is passed.
    AppRoute(
      path: '/licenses/:state_id/:license_number',
      builder: (context, state) {
        return LicenseeScreen(
          stateId: state.params['state_id']!,
          licenseId: state.params['license_number']!,
        );
      },
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
      routes: [
        // AppRoute(
        //   path: 'coa',
        //   name: 'results-coa',
        //   builder: (context, state) => COAScreen(),
        //   useFade: true,
        // ),
      ],
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
    // AppRoute(
    //   path: '/models',
    //   name: 'models',
    //   builder: (context, state) => DashboardScreen(),
    //   routes: [
    //     // CoADoc screen.
    //     AppRoute(
    //       path: 'coas',
    //       name: 'CoADoc',
    //       builder: (context, state) => CoADocScreen(),
    //     ),

    //     // SkunkFx screen.
    //     AppRoute(
    //       path: 'effects',
    //       name: 'SkunkFx',
    //       builder: (context, state) => CoADocScreen(),
    //     ),
    //   ],
    // ),
  ];
}

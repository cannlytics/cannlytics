// Cannlytics Data
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 2/18/2023
// Updated: 8/6/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>
// Dart imports:

// Project imports:
import 'package:cannlytics_data/common/dialogs/age_check_dialog.dart';
import 'package:cannlytics_data/routing/app_router.dart';
import 'package:cannlytics_data/ui/account/account_screen.dart';
import 'package:cannlytics_data/ui/account/profile_screen.dart';
import 'package:cannlytics_data/ui/account/reset_password_screen.dart';
import 'package:cannlytics_data/ui/dashboard/dashboard.dart';
import 'package:cannlytics_data/ui/licensees/licensee_screen.dart';
import 'package:cannlytics_data/ui/licensees/licensees_screen.dart';
import 'package:cannlytics_data/ui/licensees/licensees_table.dart';
import 'package:cannlytics_data/ui/results/result_screen.dart';
import 'package:cannlytics_data/ui/results/results_screen.dart';
import 'package:cannlytics_data/ui/sales/receipt_screen.dart';
import 'package:cannlytics_data/ui/sales/receipts_screen.dart';
import 'package:cannlytics_data/ui/strains/strain_screen.dart';
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

    // User profile screen.
    AppRoute(
      path: '/users/:uid',
      builder: (context, state) {
        return UserProfileScreen(
          uid: state.pathParameters['uid']!,
        );
      },
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
        return StateLicensesScreen(stateId: state.pathParameters['state_id']!);
      },
    ),

    // Licensee screen if a license number is passed.
    AppRoute(
      path: '/licenses/:state_id/:license_number',
      builder: (context, state) {
        return LicenseeScreen(
          stateId: state.pathParameters['state_id']!,
          licenseeId: state.pathParameters['license_number']!,
        );
      },
    ),

    // Strains screen.
    AppRoute(
      path: '/strains',
      name: 'strains',
      builder: (context, state) => StrainsScreen(),
      useFade: true,
      routes: [
        // Result screen.
        AppRoute(
          path: ':hash',
          name: 'strain',
          builder: (context, state) {
            return StrainScreen(strainId: state.pathParameters['hash']);
          },
        ),
      ],
    ),

    // Lab results screen.
    AppRoute(
      path: '/results',
      name: 'results',
      builder: (context, state) => LabResultsScreen(),
      useFade: true,
      routes: [
        // Result screen.
        AppRoute(
          path: ':hash',
          name: 'result',
          builder: (context, state) {
            return ResultScreen(labResultId: state.pathParameters['hash']!);
          },
        ),
      ],
    ),

    // Sales screen.
    AppRoute(
      path: '/sales',
      name: 'sales',
      builder: (context, state) => SalesScreen(),
      useFade: true,
      routes: [
        // Result screen.
        AppRoute(
          path: ':hash',
          name: 'receipt',
          builder: (context, state) {
            return ReceiptScreen(salesReceiptId: state.pathParameters['hash']!);
          },
        ),
      ],
    ),

    // Age verification screen.
    AppRoute(
      path: '/age-verification',
      builder: (context, state) {
        return AgeVerificationScreen();
      },
    ),
  ];
}

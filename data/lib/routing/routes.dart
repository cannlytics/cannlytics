// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 2/18/2023
// Updated: 4/9/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>
// Dart imports:

// Project imports:
import 'package:cannlytics_data/routing/app_router.dart';
import 'package:cannlytics_data/ui/main/dashboard.dart';
import 'package:flutter/material.dart';

// The main app routes.
class Routes {
  static List<AppRoute> mainRoutes = [
    // // Sign in screen.
    // AppRoute(
    //   path: '/sign-in',
    //   name: 'signIn',
    //   builder: (context, state) => EmailPasswordSignInScreen(
    //     formType: SignInFormType.signIn,
    //   ),
    // ),

    // // User account screens.
    // AppRoute(
    //   path: '/account',
    //   name: 'account',
    //   builder: (context, state) => AccountScreen(),
    //   routes: [
    //     // Reset password screen.
    //     AppRoute(
    //       path: 'reset-password',
    //       name: 'resetPassword'
    //       builder: (context, state) => ResetPasswordScreen(),
    //     ),
    //   ],
    // ),

    // Dashboard screen.
    AppRoute(
      path: '/dashboard',
      name: 'dashboard',
      builder: (context, state) => DashboardScreen(), // key: Key('dashboard')
    ),
  ];
}

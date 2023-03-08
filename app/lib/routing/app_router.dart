// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 2/18/2023
// Updated: 3/8/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Dart imports:
import 'dart:async';

// Flutter imports:
import 'package:cannlytics_app/ui/account/licenses/add_license_screen.dart';
import 'package:cannlytics_app/ui/account/licenses/licenses_screen.dart';
import 'package:cannlytics_app/ui/account/organizations/organization_screen.dart';
import 'package:cannlytics_app/ui/account/organizations/organizations_screen.dart';
import 'package:cannlytics_app/ui/account/user/reset_password_screen.dart';
import 'package:cannlytics_app/ui/business/locations/location_screen.dart';
import 'package:cannlytics_app/ui/business/locations/locations_screen.dart';
import 'package:flutter/material.dart';

// Package imports:
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

// Project imports:
import 'package:cannlytics_app/models/consumer/entry.dart';
import 'package:cannlytics_app/models/consumer/job.dart';
import 'package:cannlytics_app/routing/routes.dart';
import 'package:cannlytics_app/services/auth_service.dart';
import 'package:cannlytics_app/ui/account/user/account_screen.dart';
import 'package:cannlytics_app/ui/account/sign-in/sign_in_screen.dart';
import 'package:cannlytics_app/ui/account/sign-in/sign_in_text.dart';
import 'package:cannlytics_app/ui/business/facilities/facilities_screen.dart';
import 'package:cannlytics_app/ui/business/facilities/facility_screen.dart';
import 'package:cannlytics_app/ui/business/inventory/items/item_screen.dart';
import 'package:cannlytics_app/ui/business/inventory/items/items_screen.dart';
import 'package:cannlytics_app/ui/business/inventory/packages/package_edit_screen.dart';
import 'package:cannlytics_app/ui/business/inventory/packages/package_items_screen.dart';
import 'package:cannlytics_app/ui/business/inventory/packages/packages_screen.dart';
import 'package:cannlytics_app/ui/general/dashboard.dart';
import 'package:cannlytics_app/ui/general/search_screen.dart';

// Private navigators.
final _rootNavigatorKey = GlobalKey<NavigatorState>();

// Navigation.
final goRouterProvider = Provider<GoRouter>((ref) {
  // Get the authentication state.
  final authService = ref.watch(authProvider);

  // Build the routes.
  return GoRouter(
    initialLocation: '/sign-in',
    navigatorKey: _rootNavigatorKey,
    debugLogDiagnostics: true,
    refreshListenable: GoRouterRefreshStream(authService.authStateChanges()),
    // Optional: Add 404 screen.
    //errorBuilder: (context, state) => const NotFoundScreen(),
    redirect: (context, state) {
      // Determine if the user is logged in.
      final isLoggedIn = authService.currentUser != null;

      // Navigate to either the home screen or the sign in page.
      if (isLoggedIn) {
        if (state.subloc.startsWith('/sign-in')) {
          return '/dashboard';
        }
      } else {
        // if (state.subloc.startsWith('/dashboard') ||
        //     state.subloc.startsWith('/organizations') ||
        //     state.subloc.startsWith('/facilities') ||
        //     state.subloc.startsWith('/locations')) {
        //   return '/sign-in';
        // }
        if (!state.subloc.startsWith('/sign-in') &&
            !state.subloc.startsWith('/account/reset-password')) {
          return '/sign-in';
        }
      }
      return null;
    },
    routes: [
      // Sign in screen.
      AppRoute(
        path: '/sign-in',
        name: AppRoutes.signIn.name,
        builder: (context, state) => EmailPasswordSignInScreen(
          formType: SignInFormType.signIn,
        ),
      ),

      // User account screens.
      GoRoute(
        path: '/account',
        name: AppRoutes.account.name,
        pageBuilder: (context, state) => NoTransitionPage(
          key: state.pageKey,
          child: const AccountScreen(),
        ),
        routes: [
          // Reset password screen.
          GoRoute(
            path: 'reset-password',
            name: AppRoutes.resetPassword.name,
            pageBuilder: (context, state) {
              return MaterialPage(
                key: state.pageKey,
                child: ResetPasswordScreen(),
              );
            },
          ),
        ],
      ),

      // Organizations screen.
      GoRoute(
        path: '/organizations',
        name: AppRoutes.organizations.name,
        pageBuilder: (context, state) => MaterialPage(
          key: state.pageKey,
          child: OrganizationsScreen(),
        ),
        routes: [
          // Organization screen.
          GoRoute(
            path: ':id',
            name: AppRoutes.organization.name,
            pageBuilder: (context, state) {
              return MaterialPage(
                key: state.pageKey,
                child: OrganizationScreen(),
              );
            },
          ),
        ],
      ),

      // License management screen.
      GoRoute(
        path: '/licenses',
        name: AppRoutes.licenses.name,
        pageBuilder: (context, state) => MaterialPage(
          key: state.pageKey,
          child: LicensesScreen(),
        ),
        routes: [
          // Add license screen.
          GoRoute(
            path: 'add',
            name: AppRoutes.addLicense.name,
            pageBuilder: (context, state) {
              return MaterialPage(
                key: state.pageKey,
                child: AddLicenseScreen(),
              );
            },
          ),
        ],
      ),

      // Dashboard screen.
      GoRoute(
        path: '/dashboard',
        name: AppRoutes.dashboard.name,
        pageBuilder: (context, state) => NoTransitionPage(
          key: state.pageKey,
          child: const DashboardScreen(),
        ),
      ),

      // Search screen.
      GoRoute(
        path: '/search',
        name: AppRoutes.search.name,
        pageBuilder: (context, state) => NoTransitionPage(
          key: state.pageKey,
          child: const SearchScreen(),
        ),
      ),

      // Deliveries screens.
      GoRoute(
        path: '/deliveries',
        name: AppRoutes.deliveries.name,
        pageBuilder: (context, state) => NoTransitionPage(
          key: state.pageKey,
          child: const ItemsScreen(),
        ),
      ),

      // TODO: Employees screens.
      // GoRoute(
      //   path: '/employees',
      //   name: AppRoutes.employees.name,
      //   pageBuilder: (context, state) => NoTransitionPage(
      //     key: state.pageKey,
      //     child: const ItemsScreen(),
      //   ),
      //   routes: [
      //     // Employee screen.
      //     GoRoute(
      //       path: ':id',
      //       name: AppRoutes.package.name,
      //       pageBuilder: (context, state) {
      //         final id = state.params['id']!;
      //         return MaterialPage(
      //           key: state.pageKey,
      //           child: JobItemsScreen(jobId: id),
      //         );
      //       },
      //     ),
      //   ],
      // ),

      // Facilities
      GoRoute(
        path: '/facilities',
        name: AppRoutes.facilities.name,
        pageBuilder: (context, state) => NoTransitionPage(
          key: state.pageKey,
          child: const FacilitiesScreen(),
        ),
        routes: [
          // Facility screen.
          GoRoute(
            path: ':id',
            name: AppRoutes.facility.name,
            pageBuilder: (context, state) {
              final id = state.params['id']!;
              return MaterialPage(
                key: state.pageKey,
                child: FacilityScreen(jobId: id),
              );
            },
          ),
        ],
      ),

      // Locations.
      GoRoute(
        path: '/locations',
        name: AppRoutes.locations.name,
        pageBuilder: (context, state) => NoTransitionPage(
          key: state.pageKey,
          child: const LocationsScreen(),
        ),
        routes: [
          // Facility screen.
          GoRoute(
            path: ':id',
            name: AppRoutes.location.name,
            pageBuilder: (context, state) {
              final id = state.params['id']!;
              return MaterialPage(
                key: state.pageKey,
                child: LocationScreen(jobId: id),
              );
            },
          ),
        ],
      ),

      // TODO: patients

      // TODO: plants (plant batches, harvests, waste (methods and reasons),
      //      additives, adjustments, growth phases)

      // TODO: results (test types)

      // TODO: sales (receipts and transactions)

      // TODO: strains

      // TODO: transfers (transfer types)

      // TODO: homegrow

      // TODO: products

      // TODO: results

      // TODO: retailers

      // TODO: spending

      // Items screen.
      GoRoute(
        path: '/items',
        name: AppRoutes.items.name,
        pageBuilder: (context, state) => NoTransitionPage(
          key: state.pageKey,
          child: const ItemsScreen(),
        ),
      ),

      // Packages screens.
      GoRoute(
        path: '/packages',
        name: AppRoutes.packages.name,
        pageBuilder: (context, state) => NoTransitionPage(
          key: state.pageKey,
          child: const PackagesScreen(),
        ),
        routes: [
          // New package screen.
          GoRoute(
            path: 'add',
            name: AppRoutes.addPackage.name,
            parentNavigatorKey: _rootNavigatorKey,
            pageBuilder: (context, state) {
              return MaterialPage(
                key: state.pageKey,
                fullscreenDialog: true,
                child: const EditJobScreen(),
              );
            },
          ),

          // Package screen.
          GoRoute(
            path: ':id',
            name: AppRoutes.package.name,
            pageBuilder: (context, state) {
              final id = state.params['id']!;
              return MaterialPage(
                key: state.pageKey,
                child: JobItemsScreen(jobId: id),
              );
            },

            // Items screens.
            routes: [
              // Add item screen.
              GoRoute(
                path: 'items/add',
                name: AppRoutes.addItem.name,
                parentNavigatorKey: _rootNavigatorKey,
                pageBuilder: (context, state) {
                  final jobId = state.params['id']!;
                  return MaterialPage(
                    key: state.pageKey,
                    fullscreenDialog: true,
                    child: EntryScreen(
                      jobId: jobId,
                    ),
                  );
                },
              ),

              // Item screen.
              GoRoute(
                path: 'items/:uid',
                name: AppRoutes.item.name,
                pageBuilder: (context, state) {
                  final jobId = state.params['id']!;
                  final entryId = state.params['uid']!;
                  final entry = state.extra as Entry?;
                  return MaterialPage(
                    key: state.pageKey,
                    child: EntryScreen(
                      jobId: jobId,
                      entryId: entryId,
                      entry: entry,
                    ),
                  );
                },
              ),

              // Edit item screen.
              GoRoute(
                path: 'edit',
                name: AppRoutes.editItem.name,
                pageBuilder: (context, state) {
                  final jobId = state.params['id'];
                  final job = state.extra as Job?;
                  return MaterialPage(
                    key: state.pageKey,
                    fullscreenDialog: true,
                    child: EditJobScreen(jobId: jobId, job: job),
                  );
                },
              ),
            ],
          ),
        ],
      ),
      //   ],
      // ),
    ],
  );
});

/// Custom GoRoute class to make route declaration easier.
class AppRoute extends GoRoute {
  AppRoute({
    required this.path,
    required this.builder,
    this.useFade = false,
    this.name,
    List<GoRoute> routes = const [],
  }) : super(
          path: path,
          name: name,
          routes: routes,
          pageBuilder: (context, state) {
            final pageContent = Scaffold(
              body: builder(context, state),
              resizeToAvoidBottomInset: false,
            );
            if (useFade) {
              return CustomTransitionPage(
                key: state.pageKey,
                child: pageContent,
                transitionsBuilder: (
                  context,
                  animation,
                  secondaryAnimation,
                  child,
                ) {
                  return FadeTransition(
                    opacity: animation,
                    child: child,
                  );
                },
              );
            }
            return MaterialPage(
              key: state.pageKey,
              child: pageContent,
            );
          },
        );

  // Route properties.
  final bool useFade;
  final String? name;
  final String path;
  final Widget Function(BuildContext, GoRouterState) builder;
}

/// GoRouter stream.
class GoRouterRefreshStream extends ChangeNotifier {
  GoRouterRefreshStream(Stream<dynamic> stream) {
    notifyListeners();
    _subscription = stream.asBroadcastStream().listen((dynamic _) {
      return notifyListeners();
    });
  }

  late final StreamSubscription<dynamic> _subscription;

  @override
  void dispose() {
    _subscription.cancel();
    super.dispose();
  }
}

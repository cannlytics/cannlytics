// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 2/18/2023
// Updated: 3/6/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Dart imports:
import 'dart:async';

// Flutter imports:
import 'package:cannlytics_app/ui/account/licenses/add_license_screen.dart';
import 'package:cannlytics_app/ui/account/licenses/licenses_screen.dart';
import 'package:cannlytics_app/ui/account/organizations/organization_screen.dart';
import 'package:cannlytics_app/ui/account/organizations/organizations_screen.dart';
import 'package:cannlytics_app/ui/account/user/reset_password_screen.dart';
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
// import 'package:cannlytics_app/ui/account/onboarding/onboarding_controller.dart';
// import 'package:cannlytics_app/ui/account/onboarding/onboarding_screen.dart';
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
import 'package:cannlytics_app/ui/general/screen.dart';

// Private navigators.
final _rootNavigatorKey = GlobalKey<NavigatorState>();
final _shellNavigatorKey = GlobalKey<NavigatorState>();

// Navigation.
final goRouterProvider = Provider<GoRouter>((ref) {
  final authService = ref.watch(authProvider);
  // final onboardingRepository = ref.watch(onboardingStoreProvider);
  return GoRouter(
    initialLocation: '/sign-in',
    navigatorKey: _rootNavigatorKey,
    debugLogDiagnostics: true,
    refreshListenable: GoRouterRefreshStream(authService.authStateChanges()),
    //errorBuilder: (context, state) => const NotFoundScreen(),
    redirect: (context, state) {
      // // Determine if the user completed onboarding.
      // final didCompleteOnboarding = onboardingRepository.isOnboardingComplete();

      // // Navigate to onboarding screen if necessary.
      // if (!didCompleteOnboarding) {
      //   if (state.subloc != '/onboarding') {
      //     return '/onboarding';
      //   }
      // }

      // Determine if the user is logged in.
      final isLoggedIn = authService.currentUser != null;

      // Navigate to either the home screen or the sign in page.
      if (isLoggedIn) {
        if (state.subloc.startsWith('/sign-in')) {
          return '/dashboard';
        }
      } else {
        if (!state.subloc.startsWith('/sign-in') &&
            !state.subloc.startsWith('/account/reset-password')) {
          return '/sign-in';
        }
        // if (state.subloc.startsWith('/dashboard') ||
        //     state.subloc.startsWith('/jobs') ||
        //     state.subloc.startsWith('/entries') ||
        //     state.subloc.startsWith('/account')) {
        //   return '/sign-in';
        // }
      }
      return null;
    },
    routes: [
      // // Onboarding screen, allowing user to choose "Consumer" or "Business".
      // GoRoute(
      //   path: '/onboarding',
      //   name: AppRoutes.onboarding.name,
      //   pageBuilder: (context, state) => NoTransitionPage(
      //     key: state.pageKey,
      //     child: const OnboardingScreen(),
      //   ),
      // ),

      // Sign in page.
      GoRoute(
        path: '/sign-in',
        name: AppRoutes.signIn.name,
        pageBuilder: (context, state) => MaterialPage(
          key: state.pageKey,
          fullscreenDialog: true,
          child: const EmailPasswordSignInScreen(
            formType: SignInFormType.signIn,
          ),
        ),
      ),

      // TODO: Reset password page.

      // Main screens.
      ShellRoute(
        navigatorKey: _shellNavigatorKey,
        builder: (context, state, child) {
          return MainScreen(child: child);
        },
        routes: [
          // User account.
          GoRoute(
            path: '/account',
            name: AppRoutes.account.name,
            pageBuilder: (context, state) => NoTransitionPage(
              key: state.pageKey,
              child: const AccountScreen(),
            ),
            routes: [
              // Organization.
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

          // Organizations
          GoRoute(
            path: '/organizations',
            name: AppRoutes.organizations.name,
            pageBuilder: (context, state) => MaterialPage(
              key: state.pageKey,
              child: OrganizationsScreen(),
            ),
            routes: [
              // Organization.
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

          // License management.
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
          // - delivery
          // - delivery items
          // - vehicles
          // - drivers
          GoRoute(
            path: '/deliveries',
            name: AppRoutes.deliveries.name,
            pageBuilder: (context, state) => NoTransitionPage(
              key: state.pageKey,
              child: const ItemsScreen(),
            ),
          ),

          // Employees screens.
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

          // - inventory (packages and items, categories, package statuses)

          // - locations (location types)

          // - patients

          // - plants (plant batches, harvests, waste (methods and reasons),
          //      additives, adjustments, growth phases)

          // - results (test types)

          // - sales (receipts and transactions)

          // - strains

          // - transfers (transfer types)

          // TODO:
          // - homegrow
          // - products
          // - results
          // - retailers
          // - spending

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

              // Job Screen
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

                // Entries screens.
                routes: [
                  // Add entry screen.
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

                  // Entry screen.
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

                  // Edit entry screen.
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
        ],
      ),
    ],
  );
});

/// FIXME: Whire this up for cool transitions.
/// Custom GoRoute sub-class to make the router declaration easier to read
// class AppRoute extends GoRoute {
//   AppRoute(String path, Widget Function(GoRouterState s) builder,
//       {List<GoRoute> routes = const [], this.useFade = false})
//       : super(
//           path: path,
//           routes: routes,
//           pageBuilder: (context, state) {
//             final pageContent = Scaffold(
//               body: builder(state),
//               resizeToAvoidBottomInset: false,
//             );
//             if (useFade) {
//               return CustomTransitionPage(
//                 key: state.pageKey,
//                 child: pageContent,
//                 transitionsBuilder:
//                     (context, animation, secondaryAnimation, child) {
//                   return FadeTransition(
//                     opacity: animation,
//                     child: child,
//                   );
//                 },
//               );
//             }
//             return CupertinoPage(child: pageContent);
//           },
//         );
//   final bool useFade;
// }

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

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
import 'package:cannlytics_app/ui/business/deliveries/deliveries_screen.dart';
import 'package:cannlytics_app/ui/business/deliveries/delivery_screen.dart';
import 'package:cannlytics_app/ui/business/employees/employee_screen.dart';
import 'package:cannlytics_app/ui/business/employees/employees_screen.dart';
import 'package:cannlytics_app/ui/business/locations/location_screen.dart';
import 'package:cannlytics_app/ui/business/locations/locations_screen.dart';
import 'package:cannlytics_app/ui/business/patients/patient_screen.dart';
import 'package:cannlytics_app/ui/business/patients/patients_screen.dart';
import 'package:cannlytics_app/ui/business/strains/strain_screen.dart';
import 'package:cannlytics_app/ui/business/strains/strains_screen.dart';
import 'package:cannlytics_app/ui/business/transfers/transfer_screen.dart';
import 'package:cannlytics_app/ui/business/transfers/transfers_screen.dart';
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
      AppRoute(
        path: '/account',
        name: AppRoutes.account.name,
        builder: (context, state) => AccountScreen(),
        routes: [
          // Reset password screen.
          AppRoute(
            path: 'reset-password',
            name: AppRoutes.resetPassword.name,
            builder: (context, state) => ResetPasswordScreen(),
          ),
        ],
      ),

      // Organizations screen.
      AppRoute(
        path: '/organizations',
        name: AppRoutes.organizations.name,
        builder: (context, state) => OrganizationsScreen(),
        routes: [
          // Organization screen.
          AppRoute(
            path: 'add',
            name: AppRoutes.organization.name,
            builder: (context, state) => OrganizationScreen(),
          ),
        ],
      ),

      // License management screen.
      AppRoute(
        path: '/licenses',
        name: AppRoutes.licenses.name,
        builder: (context, state) => LicensesScreen(),
        routes: [
          // Delivery screen.
          AppRoute(
            path: 'add',
            name: AppRoutes.addLicense.name,
            builder: (context, state) => AddLicenseScreen(),
          ),
        ],
      ),

      // Dashboard screen.
      AppRoute(
        path: '/dashboard',
        name: AppRoutes.dashboard.name,
        builder: (context, state) => DashboardScreen(),
      ),

      // Search screen.
      AppRoute(
        path: '/search',
        name: AppRoutes.search.name,
        builder: (context, state) => SearchScreen(),
      ),

      /* Business screens */

      // Deliveries screens.
      AppRoute(
        path: '/deliveries',
        name: AppRoutes.deliveries.name,
        builder: (context, state) => DeliveriesScreen(),
        routes: [
          // Delivery screen.
          AppRoute(
            path: ':id',
            name: AppRoutes.delivery.name,
            builder: (context, state) {
              final id = state.params['id']!;
              return DeliveryScreen(jobId: id);
            },
          ),
        ],
      ),

      // Employees screens.
      AppRoute(
        path: '/employees',
        name: AppRoutes.employees.name,
        builder: (context, state) => EmployeesScreen(),
        routes: [
          // Employee screen.
          AppRoute(
            path: ':id',
            name: AppRoutes.employee.name,
            builder: (context, state) {
              final id = state.params['id']!;
              return EmployeeScreen(jobId: id);
            },
          ),
        ],
      ),

      // Facilities
      AppRoute(
        path: '/facilities',
        name: AppRoutes.facilities.name,
        builder: (context, state) => FacilitiesScreen(),
        routes: [
          // Facility screen.
          AppRoute(
            path: ':id',
            name: AppRoutes.facility.name,
            builder: (context, state) {
              final id = state.params['id']!;
              return FacilityScreen(jobId: id);
            },
          ),
        ],
      ),

      // Locations.
      AppRoute(
        path: '/locations',
        name: AppRoutes.locations.name,
        builder: (context, state) => LocationsScreen(),
        routes: [
          // Location screen.
          AppRoute(
            path: ':id',
            name: AppRoutes.location.name,
            builder: (context, state) {
              final id = state.params['id']!;
              return LocationScreen(jobId: id);
            },
          ),
        ],
      ),

      // Patients
      AppRoute(
        path: '/patients',
        name: AppRoutes.patients.name,
        builder: (context, state) => PatientsScreen(),
        routes: [
          // Patient screen.
          AppRoute(
            path: ':id',
            name: AppRoutes.patient.name,
            builder: (context, state) {
              final id = state.params['id']!;
              return PatientScreen(jobId: id);
            },
          ),
        ],
      ),

      // TODO: plants
      // - plant batches
      // - harvests

      // TODO: results

      // TODO: sales receipts

      // TODO: sales transactions

      // Strains screen.
      AppRoute(
        path: '/strains',
        name: AppRoutes.strains.name,
        builder: (context, state) => StrainsScreen(),
        routes: [
          // Strain screen.
          AppRoute(
            path: ':id',
            name: AppRoutes.strain.name,
            builder: (context, state) {
              final id = state.params['id']!;
              return StrainScreen(jobId: id);
            },
          ),
        ],
      ),

      // Transfers screen.
      AppRoute(
        path: '/transfers',
        name: AppRoutes.transfers.name,
        builder: (context, state) => TransfersScreen(),
        routes: [
          // Transfer screen.
          AppRoute(
            path: ':id',
            name: AppRoutes.transfer.name,
            builder: (context, state) {
              final id = state.params['id']!;
              return TransferScreen(jobId: id);
            },
          ),
        ],
      ),

      // TODO: Transfer templates screen.

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

      /* Consumer screens */

      // TODO: homegrow

      // TODO: products

      // TODO: retailers

      // TODO: brands

      // TODO: spending
    ],
  );
});

/// Custom GoRoute class to make route declaration easier.
class AppRoute extends GoRoute {
  // Route properties.
  final String? name;
  final String path;
  final Widget Function(BuildContext, GoRouterState) builder;
  final bool noTransition;
  final bool useFade;

  // Route initialization.
  AppRoute({
    required this.path,
    required this.builder,
    this.noTransition = false,
    this.useFade = false,
    this.name,
    List<GoRoute> routes = const [],
  }) : super(
          path: path,
          name: name,
          routes: routes,
          pageBuilder: (context, state) {
            // Screen scaffold.
            final pageContent = Scaffold(
              body: builder(context, state),
              resizeToAvoidBottomInset: false,
            );

            // Fade transition screen.
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

            // No transition screen.
            if (noTransition) {
              return NoTransitionPage(
                key: state.pageKey,
                child: pageContent,
              );
            }

            // Normal screen.
            return MaterialPage(
              key: state.pageKey,
              child: pageContent,
            );
          },
        );
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

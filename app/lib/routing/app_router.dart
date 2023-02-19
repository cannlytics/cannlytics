// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 2/18/2023
// Updated: 2/19/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:cannlytics_app/services/auth_service.dart';
import 'package:cannlytics_app/ui/account/account_screen.dart';
import 'package:cannlytics_app/ui/account/sign-in/sign_in_text.dart';
import 'package:cannlytics_app/ui/account/sign-in/sign_in_screen.dart';
import 'package:cannlytics_app/ui/consumer/spending/entries_screen.dart';
import 'package:cannlytics_app/models/entry.dart';
import 'package:cannlytics_app/models/job.dart';
import 'package:cannlytics_app/ui/consumer/spending/entry_screen.dart';
import 'package:cannlytics_app/ui/consumer/spending/job_entries_screen.dart';
import 'package:cannlytics_app/ui/consumer/spending/edit_job_screen.dart';
import 'package:cannlytics_app/ui/consumer/spending/jobs_screen.dart';
import 'package:cannlytics_app/ui/account/onboarding/onboarding_controller.dart';
import 'package:cannlytics_app/ui/account/onboarding/onboarding_screen.dart';
import 'package:cannlytics_app/routing/go_router_refresh_stream.dart';
import 'package:cannlytics_app/routing/bottom_navigation.dart';

// Private navigators.
final _rootNavigatorKey = GlobalKey<NavigatorState>();
final _shellNavigatorKey = GlobalKey<NavigatorState>();

// Routes.
enum AppRoute {
  onboarding,
  signIn,
  // resetPassword,
  jobs,
  job,
  addJob,
  editJob,
  entry,
  addEntry,
  editEntry,
  entries,
  account,
}

// Navigation.
final goRouterProvider = Provider<GoRouter>((ref) {
  final authService = ref.watch(authServiceProvider);
  final onboardingRepository = ref.watch(onboardingStoreProvider);
  return GoRouter(
    initialLocation: '/sign-in',
    navigatorKey: _rootNavigatorKey,
    debugLogDiagnostics: true,
    refreshListenable: GoRouterRefreshStream(authService.authStateChanges()),
    //errorBuilder: (context, state) => const NotFoundScreen(),
    redirect: (context, state) {
      // Determine if the user completed onboarding.
      final didCompleteOnboarding = onboardingRepository.isOnboardingComplete();

      // Navigate to onboarding screen if necessary.
      if (!didCompleteOnboarding) {
        if (state.subloc != '/onboarding') {
          return '/onboarding';
        }
      }

      // Determine if the user is logged in.
      final isLoggedIn = authService.currentUser != null;

      // Navigate to either the home screen or the sign in page.
      if (isLoggedIn) {
        if (state.subloc.startsWith('/sign-in')) {
          return '/jobs';
        }
      } else {
        // Test if removing this code still works:
        // if (state.subloc.startsWith('/jobs') ||
        //     state.subloc.startsWith('/entries') ||
        //     state.subloc.startsWith('/account')) {
        //   return '/sign-in';
        // }
        if (state.subloc != '/sign-in') {
          return '/sign-in';
        }
      }
      return null;
    },
    routes: [
      // Onboarding screen, allowing user to choose "Consumer" or "Business".
      GoRoute(
        path: '/onboarding',
        name: AppRoute.onboarding.name,
        pageBuilder: (context, state) => NoTransitionPage(
          key: state.pageKey,
          child: const OnboardingScreen(),
        ),
      ),

      // Sign in page.
      GoRoute(
        path: '/sign-in',
        name: AppRoute.signIn.name,
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
          return ScaffoldWithBottomNavBar(child: child);
        },
        routes: [
          // Jobs screens.
          GoRoute(
            path: '/jobs',
            name: AppRoute.jobs.name,
            pageBuilder: (context, state) => NoTransitionPage(
              key: state.pageKey,
              child: const JobsScreen(),
            ),
            routes: [
              // New job screen.
              GoRoute(
                path: 'add',
                name: AppRoute.addJob.name,
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
                name: AppRoute.job.name,
                pageBuilder: (context, state) {
                  final id = state.params['id']!;
                  return MaterialPage(
                    key: state.pageKey,
                    child: JobEntriesScreen(jobId: id),
                  );
                },

                // Entries screens.
                routes: [
                  // Add entry screen.
                  GoRoute(
                    path: 'entries/add',
                    name: AppRoute.addEntry.name,
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
                    path: 'entries/:eid',
                    name: AppRoute.entry.name,
                    pageBuilder: (context, state) {
                      final jobId = state.params['id']!;
                      final entryId = state.params['eid']!;
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
                    name: AppRoute.editJob.name,
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

          // Entries screen.
          GoRoute(
            path: '/entries',
            name: AppRoute.entries.name,
            pageBuilder: (context, state) => NoTransitionPage(
              key: state.pageKey,
              child: const EntriesScreen(),
            ),
          ),

          // Account screen.
          GoRoute(
            path: '/account',
            name: AppRoute.account.name,
            pageBuilder: (context, state) => NoTransitionPage(
              key: state.pageKey,
              child: const AccountScreen(),
            ),
          ),
        ],
      ),
    ],
  );
});

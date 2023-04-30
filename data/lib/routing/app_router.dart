// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 2/18/2023
// Updated: 4/14/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Dart imports:
import 'dart:async';

// Flutter imports:
import 'package:flutter/material.dart';

// Package imports:
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

// Project imports:
import 'package:cannlytics_data/routing/routes.dart';
import 'package:cannlytics_data/services/auth_service.dart';
import 'package:cannlytics_data/ui/dashboard/dashboard_controller.dart';

// Flutter imports:
// import 'package:cannlytics_app/ui/layout/not_found_screen.dart';

// Private navigators.
final _rootNavigatorKey = GlobalKey<NavigatorState>();

// Navigation.
final goRouterProvider = Provider<GoRouter>((ref) {
  // Determine if the user is signed in.
  final authService = ref.watch(authProvider);
  final user = ref.watch(userProvider).value;
  final isLoggedIn = user != null;

  // Build the routes.
  return GoRouter(
    initialLocation: '/',
    navigatorKey: _rootNavigatorKey,
    debugLogDiagnostics: true,
    // errorBuilder: (context, state) => const NotFoundScreen(),
    refreshListenable: GoRouterRefreshStream(authService.authStateChanges()),
    // redirect: (context, state) => routeRedirect(state, isLoggedIn),
    routes: Routes.mainRoutes,
  );
});

// Redirect function.
// First, determine if the user is logged in,
// then navigate to either the dashboard or to sign in.
String? routeRedirect(GoRouterState state, bool isLoggedIn) {
  if (isLoggedIn) {
    if (state.subloc.startsWith('/sign-in')) return '/';
  } else {
    if (!state.subloc.startsWith('/sign-in') &&
        !state.subloc.startsWith('/account/reset-password')) {
      return '/sign-in';
    }
  }
  return null;
}

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

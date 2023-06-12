// Cannlytics Data
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 5/22/2023
// Updated: 5/22/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Flutter imports:
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

// Package imports:
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:fluttertoast/fluttertoast.dart';
import 'package:go_router/go_router.dart';

// Project imports:
import 'package:cannlytics_data/common/cards/wide_card.dart';
import 'package:cannlytics_data/common/forms/form_placeholder.dart';
import 'package:cannlytics_data/ui/layout/breadcrumbs.dart';
import 'package:cannlytics_data/ui/layout/console.dart';
import 'package:cannlytics_data/ui/layout/footer.dart';
import 'package:cannlytics_data/ui/layout/header.dart';
import 'package:cannlytics_data/ui/layout/sidebar.dart';
import 'package:cannlytics_data/constants/design.dart';
import 'package:cannlytics_data/ui/licensees/licensee_map.dart';
import 'package:cannlytics_data/ui/licensees/licensees_controller.dart';
import 'package:cannlytics_data/utils/utils.dart';

/// TODO: Allow users to parse a COA with AI if they have a subscription.
///
/// TODO: Talk with your COA (for pro subscribers).
///
/// TODO: Link to strains where user can find more lab results.

/// Screen.
class ResultScreen extends StatelessWidget {
  const ResultScreen({
    super.key,
    required this.licenseId,
    required this.stateId,
  });

  // Properties.
  final String licenseId;
  final String stateId;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      // App bar.
      appBar: DashboardHeader(),

      // Side menu.
      drawer: Responsive.isMobile(context) ? MobileDrawer() : null,

      // Body.
      body: Console(slivers: [
        // Table.
        SliverToBoxAdapter(
          child: MainContent(
            stateId: stateId,
            licenseId: licenseId,
          ),
        ),

        // Footer.
        const SliverToBoxAdapter(child: Footer()),
      ]),
    );
  }
}

/// Main content.
class MainContent extends ConsumerWidget {
  const MainContent({
    Key? key,
    required this.licenseId,
    required this.stateId,
  }) : super(key: key);

  // Properties.
  final String stateId;
  final String licenseId;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final screenWidth = MediaQuery.of(context).size.width;
    return Padding(
      padding: EdgeInsets.only(
        left: sliverHorizontalPadding(screenWidth) / 2,
        right: sliverHorizontalPadding(screenWidth) / 2,
        top: 24,
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        mainAxisAlignment: MainAxisAlignment.start,
        children: [
          _breadcrumbs(context),
          gapH24,
          LicenseeForm(
            stateId: stateId,
            licenseId: licenseId,
          ),
          gapH48,
        ],
      ),
    );
  }

  /// Page breadcrumbs.
  Widget _breadcrumbs(BuildContext context) {
    return Row(
      children: [
        Breadcrumbs(
          items: [
            BreadcrumbItem(
                title: 'Data',
                onTap: () {
                  context.push('/');
                }),
            BreadcrumbItem(
                title: 'Lab results',
                onTap: () {
                  context.push('/results');
                }),
            BreadcrumbItem(
              title: stateId.toUpperCase(),
              onTap: () {
                context.push('/results/$stateId');
              },
            ),
            BreadcrumbItem(
              title: licenseId,
            ),
          ],
        ),
      ],
    );
  }
}

/// Licensee form.
class LicenseeForm extends ConsumerWidget {
  LicenseeForm({
    super.key,
    required this.licenseId,
    required this.stateId,
  });

  // Properties.
  final String licenseId;
  final String stateId;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    // Listen to the licensee data.
    final asyncData = ref.watch(licenseeProvider);

    // Dynamic form with loading indicator and error message.
    return asyncData.when(
      data: (obj) => _form(context, obj),
      loading: () => _loadingIndicator(),
      error: (error, stack) => _errorMessage(context, error, stack),
    );
  }

  // Form.
  Widget _form(BuildContext context, Map<String, dynamic>? obj) {
    final screenWidth = MediaQuery.of(context).size.width;
    return Column(
      mainAxisAlignment: MainAxisAlignment.start,
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // TODO:
        // - Sample details
        // - analyses and statuses
        // - compound totals
        //
        Text(
          'Results',
          style: Theme.of(context).textTheme.titleLarge,
        ),
      ],
    );
  }

  /// Loading indicator.
  Widget _loadingIndicator() {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(12.0),
        child: Card(
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(3),
          ),
          child: Padding(
            padding: const EdgeInsets.all(8.0),
            child: Center(
              child: CircularProgressIndicator(strokeWidth: 1.42),
            ),
          ),
        ),
      ),
    );
  }

  // Error message.
  Widget _errorMessage(context, error, stack) {
    return FormPlaceholder(
      image: 'assets/images/icons/document.png',
      title: 'Result not found',
      description:
          'This result cannot be found or a technical error occurred. Please contact dev@cannlytics.com',
      onTap: () {
        context.push('/results');
      },
    );
  }
}

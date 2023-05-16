// Cannlytics Data
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 5/15/2023
// Updated: 5/16/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

import 'package:cannlytics_data/common/forms/form_placeholder.dart';
import 'package:cannlytics_data/common/layout/breadcrumbs.dart';
import 'package:cannlytics_data/common/layout/console.dart';
import 'package:cannlytics_data/common/layout/footer.dart';
import 'package:cannlytics_data/common/layout/header.dart';
import 'package:cannlytics_data/common/layout/sidebar.dart';
import 'package:cannlytics_data/constants/design.dart';
import 'package:cannlytics_data/ui/licensees/licensees_controller.dart';
import 'package:cannlytics_data/utils/utils.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:fluttertoast/fluttertoast.dart';
import 'package:go_router/go_router.dart';

/// Screen.
class LicenseeScreen extends StatelessWidget {
  const LicenseeScreen({
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
          child: Container(
            height: 750,
            child: MainContent(
              stateId: stateId,
              licenseId: licenseId,
            ),
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
          gapH8,
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
                title: 'Licenses',
                onTap: () {
                  context.push('/licenses');
                }),
            BreadcrumbItem(
              title: stateId.toUpperCase(),
              onTap: () {
                context.push('/licenses/$stateId');
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
    return Column(
      mainAxisAlignment: MainAxisAlignment.start,
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // Business name.
        Text(
          obj?['business_legal_name'] ?? '',
          style: Theme.of(context).textTheme.titleLarge,
        ),

        // DBA.
        // if (obj?['business_dba_name'] != null &&
        //     obj?['business_dba_name'] != obj?['business_dba_name'])
        Text(
          obj?['business_dba_name'] ?? '',
          style: Theme.of(context).textTheme.titleMedium,
        ),

        // Address.
        Row(
          children: [
            Text('Address'),
            IconButton(
              onPressed: () async {
                // FIXME: This is not the correct address.
                String address = '';
                await Clipboard.setData(ClipboardData(text: address));
                Fluttertoast.showToast(
                  msg: 'Copied link!',
                  toastLength: Toast.LENGTH_SHORT,
                  gravity: ToastGravity.TOP,
                  timeInSecForIosWeb: 2,
                  backgroundColor: Theme.of(context).dialogBackgroundColor,
                  textColor: Theme.of(context).textTheme.titleLarge!.color,
                  fontSize: 16.0,
                  webBgColor: WebUtils.colorToHexCode(
                      Theme.of(context).dialogBackgroundColor),
                  webPosition: 'center',
                  webShowClose: true,
                );
              },
              icon: Icon(Icons.copy),
            ),
          ],
        ),
        Row(
          children: [
            Text('Street'),
            Text(obj?['premise_street_address'] ?? ''),
          ],
        ),
        Row(
          children: [
            Text('City'),
            Text(obj?['premise_city'] ?? ''),
          ],
        ),
        Row(
          children: [
            Text('County'),
            Text(obj?['premise_county'] ?? ''),
          ],
        ),
        Row(
          children: [
            Text('State'),
            Text(obj?['premise_state'] ?? ''),
          ],
        ),
        Row(
          children: [
            Text('Zip code'),
            Text(obj?['premise_zip_code'] ?? ''),
          ],
        ),
      ],

      // TODO: Photos.

      // TODO: Reviews.

      // TODO: Products / sales / strains.
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
      title: 'License not found',
      description:
          'This license is no longer active, does not exist, or a technical error occurred.',
      onTap: () {
        context.push('/licenses');
      },
    );
  }
}

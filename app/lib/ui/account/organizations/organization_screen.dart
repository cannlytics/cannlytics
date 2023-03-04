// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 3/3/2023
// Updated: 3/4/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Dart imports:
import 'dart:async';

// Flutter imports:
import 'package:cannlytics_app/models/metrc/license.dart';
import 'package:cannlytics_app/ui/account/licenses/licenses_controller.dart';
import 'package:cannlytics_app/ui/account/organizations/organizations_controller.dart';
import 'package:flutter/material.dart';

// Package imports:
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

// Project imports:
import 'package:cannlytics_app/utils/dialogs/alert_dialog_ui.dart';

/// Organization screen.
class OrganizationScreen extends ConsumerStatefulWidget {
  const OrganizationScreen({
    super.key,
    this.license,
  });
  final License? license;

  @override
  ConsumerState<OrganizationScreen> createState() => _OrganizationScreenState();
}

/// Organization screen state.
class _OrganizationScreenState extends ConsumerState<OrganizationScreen> {
  // Fields.
  String _license = 'OK';

  // Save the license.
  Future<void> _setOrganizationAndDismiss() async {
    // final license = License(
    //   id: 'test',
    //   license: _license,
    //   licenseType: _licenseType,
    //   state: _state,
    //   userAPIKey: _userAPIKey,
    //   prefix: null,
    // );
    // final success =
    //     await ref.read(licensesProvider.notifier).addLicense(license);
    // if (success && mounted) {
    //   context.pop();
    // }
  }

  // Main widget.
  @override
  Widget build(BuildContext context) {
    ref.listen<AsyncValue>(
      organizationProvider,
      (_, state) => state.showAlertDialogOnError(context),
    );
    return Scaffold(
      // // App bar.
      // appBar: AppBar(
      //   title: Text(widget.license != null ? 'Edit License' : 'New License'),
      //   actions: <Widget>[
      //     TextButton(
      //       child: Text(
      //         widget.license != null ? 'Update' : 'Create',
      //         style: Theme.of(context).textTheme.labelLarge,
      //       ),
      //       onPressed: () => _setOrganizationAndDismiss(),
      //     ),
      //   ],
      // ),

      // Body.
      body: SingleChildScrollView(
        child: Container(
          padding: const EdgeInsets.all(16.0),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: <Widget>[
              // TODO: Team widget

              // TODO: Invite team member widget
              // - email / role

              // TODO: Licenses widget

              // TODO: Add license button

              // TODO: Danger zone: Delete license

              // TODO: Organization details
              // Setup your organization for maximum impact.
              // - name
              // - trade_name
              // - website
              // - email
              // - phone
              // (show more)
              // - address
              // - city
              // - state
              // - country
              // - zip code
              // - external ID

              // TODO: Visibility
              // Decide whether or not to list your organization for discovery by other users.
              // Public
              // Appears in search results. Private
              // Only visible to you.

              // TODO: Organization image
              // Choose an image for your organization, up to 5MB.

              // TODO: Organization Type
              // Select the organization type for your appropriate functionality.
            ],
          ),
        ),
      ),
    );
  }

  // // Start date.
  // Widget _buildStartDate() {
  //   return DateTimePicker(
  //     labelText: 'Start',
  //     selectedDate: _startDate,
  //     selectedTime: _startTime,
  //     onSelectedDate: (date) => setState(() => _startDate = date),
  //     onSelectedTime: (time) => setState(() => _startTime = time),
  //   );
  // }

  // // End date.
  // Widget _buildEndDate() {
  //   return DateTimePicker(
  //     labelText: 'End',
  //     selectedDate: _endDate,
  //     selectedTime: _endTime,
  //     onSelectedDate: (date) => setState(() => _endDate = date),
  //     onSelectedTime: (time) => setState(() => _endTime = time),
  //   );
  // }

  // // Duration.
  // Widget _buildDuration() {
  //   final currentLicense = _licenseFromState();
  //   final durationFormatted = Format.hors(currentLicense.durationInHours);
  //   return Row(
  //     mainAxisAlignment: MainAxisAlignment.end,
  //     children: <Widget>[
  //       Text(
  //         'Duration: $durationFormatted',
  //         style: const TextStyle(
  //           fontSize: 18.0,
  //           fontWeight: FontWeight.w500,
  //         ),
  //         maxLines: 1,
  //         overflow: TextOverflow.ellipsis,
  //       ),
  //     ],
  //   );
  // }

  // // Comment.
  // Widget _buildComment() {
  //   return TextField(
  //     keyboardType: TextInputType.text,
  //     maxLength: 50,
  //     controller: TextEditingController(text: _comment),
  //     decoration: const InputDecoration(
  //       labelText: 'Comment',
  //       labelStyle: TextStyle(
  //         fontSize: 18.0,
  //         fontWeight: FontWeight.w500,
  //       ),
  //     ),
  //     keyboardAppearance: Brightness.light,
  //     style: const TextStyle(
  //       fontSize: 20.0,
  //       color: Colors.black,
  //     ),
  //     maxLines: null,
  //     onChanged: (comment) => _comment = comment,
  //   );
  // }
}

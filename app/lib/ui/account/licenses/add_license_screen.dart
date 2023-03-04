// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 3/3/2023
// Updated: 3/3/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Dart imports:
import 'dart:async';

// Flutter imports:
import 'package:cannlytics_app/models/metrc/license.dart';
import 'package:cannlytics_app/ui/account/licenses/licenses_controller.dart';
import 'package:flutter/material.dart';

// Package imports:
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

// Project imports:
import 'package:cannlytics_app/utils/dialogs/alert_dialog_ui.dart';

/// Add license screen.
class AddLicenseScreen extends ConsumerStatefulWidget {
  const AddLicenseScreen({
    super.key,
    this.license,
  });
  final License? license;

  @override
  ConsumerState<AddLicenseScreen> createState() => _AddLicenseScreenState();
}

/// Add license screen state.
class _AddLicenseScreenState extends ConsumerState<AddLicenseScreen> {
  String _license = 'OK';
  String _licenseType = 'Grower';
  String _state = 'OK';
  String _userAPIKey = '';

  // Save the license.
  Future<void> _setLicenseAndDismiss() async {
    final license = License(
      id: 'test',
      license: _license,
      licenseType: _licenseType,
      state: _state,
      userAPIKey: _userAPIKey,
      prefix: null,
    );
    final success =
        await ref.read(licensesProvider.notifier).addLicense(license);
    if (success && mounted) {
      context.pop();
    }
  }

  // Main widget.
  @override
  Widget build(BuildContext context) {
    ref.listen<AsyncValue>(
      licensesProvider,
      (_, state) => state.showAlertDialogOnError(context),
    );
    return Scaffold(
      // App bar.
      appBar: AppBar(
        title: Text(widget.license != null ? 'Edit License' : 'New License'),
        actions: <Widget>[
          TextButton(
            child: Text(
              widget.license != null ? 'Update' : 'Create',
              style: Theme.of(context).textTheme.labelLarge,
            ),
            onPressed: () => _setLicenseAndDismiss(),
          ),
        ],
      ),

      // Body.
      body: SingleChildScrollView(
        child: Container(
          padding: const EdgeInsets.all(16.0),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: <Widget>[
              // _buildStartDate(),
              // _buildEndDate(),
              // const SizedBox(height: 8.0),
              // _buildDuration(),
              // const SizedBox(height: 8.0),
              // _buildComment(),
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

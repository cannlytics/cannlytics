// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 3/7/2023
// Updated: 3/12/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Dart imports:
import 'dart:async';

// Flutter imports:
import 'package:cannlytics_app/constants/design.dart';
import 'package:cannlytics_app/ui/business/locations/locations_controller.dart';
import 'package:cannlytics_app/ui/layout/footer.dart';
import 'package:cannlytics_app/ui/layout/header.dart';
import 'package:flutter/material.dart';

// Package imports:
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:uuid/uuid.dart';

// Project imports:
import 'package:cannlytics_app/models/metrc/location.dart';
import 'package:cannlytics_app/widgets/dialogs/alert_dialog_ui.dart';

/// Location screen.
class LocationScreen extends ConsumerStatefulWidget {
  const LocationScreen({
    super.key,
    required this.id,
    this.entry,
  });
  final LocationId id;
  final Location? entry;

  @override
  ConsumerState<LocationScreen> createState() => _LocationScreenState();
}

// Location screen state.
class _LocationScreenState extends ConsumerState<LocationScreen> {
  // Fields.
  late String _name;
  late String _locationTypeId;
  late String _locationTypeName;
  late bool _forPlantBatches;
  late bool _forPlants;
  late bool _forHarvests;
  late bool _forPackages;

  // Initialization.
  @override
  void initState() {
    super.initState();
    _name = widget.entry?.name ?? '';
    _locationTypeId = widget.entry?.locationTypeId ?? '';
    _locationTypeName = widget.entry?.locationTypeName ?? '';
    _forPlantBatches = widget.entry?.forPlantBatches ?? false;
    _forPlants = widget.entry?.forPlants ?? false;
    _forHarvests = widget.entry?.forHarvests ?? false;
    _forPackages = widget.entry?.forPackages ?? false;
  }

  // State to model.
  Location _entryFromState() {
    final id = widget.entry?.id ?? _createID();
    return Location(
      id: id,
      name: _name,
      locationTypeId: _locationTypeId,
      locationTypeName: _locationTypeName,
      forPlantBatches: _forPlantBatches,
      forPlants: _forPlants,
      forHarvests: _forHarvests,
      forPackages: _forPackages,
    );
  }

  // Create a time-based UUID.
  String _createID() {
    var uuid = Uuid();
    return uuid.v1();
  }

  // Save the entry and dismiss modal.
  Future<void> _setEntryAndDismiss() async {
    final entry = _entryFromState();
    final success = await ref.read(locationProvider.notifier).create(entry);
    if (success && mounted) {
      context.pop();
    }
  }

  // Build.
  @override
  Widget build(BuildContext context) {
    // Listen for errors.
    ref.listen<AsyncValue>(
      locationProvider,
      (_, state) => state.showAlertDialogOnError(context),
    );

    // Form.
    return Scaffold(
      // App bar.
      appBar: AppBar(
        title: Text(widget.entry != null ? 'Edit Entry' : 'New Entry'),
        actions: <Widget>[
          TextButton(
            child: Text(
              widget.entry != null ? 'Update' : 'Create',
              style: const TextStyle(
                fontSize: 18.0,
                color: Colors.white,
              ),
            ),
            onPressed: () => _setEntryAndDismiss(),
          ),
        ],
      ),

      // Body.
      body: CustomScrollView(
        slivers: [
          // App header.
          const SliverToBoxAdapter(child: AppHeader()),

          // Form.
          SliverToBoxAdapter(
            child: _form(),
          ),

          // Footer
          const SliverToBoxAdapter(child: Footer()),
        ],
      ),
    );
  }

  Widget _form() {
    return Container(
      padding: const EdgeInsets.all(16.0),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: <Widget>[
          // Name field.
          gapH6,
          _nameField(),
          gapH6,

          // TODO: Add additional fields.
        ],
      ),
    );
  }

  // Comment.
  Widget _nameField() {
    return TextField(
      controller: TextEditingController(text: _name),
      decoration: const InputDecoration(
        labelText: 'Name',
        labelStyle: TextStyle(
          fontSize: 18.0,
          fontWeight: FontWeight.w500,
        ),
      ),
      // style: const TextStyle(
      //   fontSize: 20.0,
      //   color: Colors.black,
      // ),
      // keyboardAppearance: Brightness.light,
      keyboardType: TextInputType.text,
      maxLength: 150,
      maxLines: null,
      onChanged: (comment) => _name = comment,
    );
  }
}

// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 3/7/2023
// Updated: 3/12/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Flutter imports:
import 'package:cannlytics_app/constants/design.dart';
import 'package:cannlytics_app/ui/business/locations/locations_controller.dart';
import 'package:cannlytics_app/ui/layout/footer.dart';
import 'package:cannlytics_app/ui/layout/header.dart';
import 'package:flutter/material.dart';

// Package imports:
import 'package:flutter_riverpod/flutter_riverpod.dart';

// Project imports:
import 'package:cannlytics_app/models/metrc/location.dart';

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
// TODO: Handle creating a location.
// TODO: Handle updating a location.
// TODO: Handle deleting an existing location.
class _LocationScreenState extends ConsumerState<LocationScreen> {
  // // Fields.
  // late String _id;
  // late String _name;
  // late String _locationTypeId;
  // late String _locationTypeName;
  // late bool _forPlantBatches;
  // late bool _forPlants;
  // late bool _forHarvests;
  // late bool _forPackages;

  // // Initialization.
  // @override
  // void initState() {
  //   super.initState();
  //   print('LOCATION ID: ${widget.id}');
  //   _id = widget.id;
  //   // Future.microtask(() {
  //   //   print('RETRIEVING LOCATION....');
  //   //   // final location = await ref.read(locationProvider.notifier).get(widget.id);
  //   //   ref.read(locationProvider).get(widget.id).then((item) {
  //   //     print('LOCATION RETRIEVED $item');
  //   //   });
  //   // });
  //   // var item = ref.read(locationProvider.notifier).get(widget.id);
  //   // print('RETRIEVED ITEM:');
  //   // print(item);
  //   // _name = widget.entry?.name ?? '';
  //   // _locationTypeId = widget.entry?.locationTypeId ?? '';
  //   // _locationTypeName = widget.entry?.locationTypeName ?? '';
  //   // _forPlantBatches = widget.entry?.forPlantBatches ?? false;
  //   // _forPlants = widget.entry?.forPlants ?? false;
  //   // _forHarvests = widget.entry?.forHarvests ?? false;
  //   // _forPackages = widget.entry?.forPackages ?? false;
  // }

  // // State to model.
  // Location _entryFromState() {
  //   final id = widget.entry?.id ?? _createID();
  //   return Location(
  //     id: id,
  //     name: _name,
  //     locationTypeId: _locationTypeId,
  //     locationTypeName: _locationTypeName,
  //     forPlantBatches: _forPlantBatches,
  //     forPlants: _forPlants,
  //     forHarvests: _forHarvests,
  //     forPackages: _forPackages,
  //   );
  // }

  // // Create a time-based UUID.
  // String _createID() {
  //   var uuid = Uuid();
  //   return uuid.v1();
  // }

  // // Save the entry and dismiss modal.
  // Future<void> _setEntryAndDismiss() async {
  //   final entry = _entryFromState();
  //   final success = await ref.read(locationProvider.notifier).create(entry);
  //   if (success && mounted) {
  //     context.pop();
  //   }
  // }

  // Build.
  @override
  Widget build(BuildContext context) {
    // Set the ID.
    // ref.read(locationId.notifier).state = widget.id;

    // TODO: Listen for errors.
    // ref.listen<AsyncValue>(
    //   locationProvider(widget.id),
    //   (_, state) => state.showAlertDialogOnError(context),
    // );

    // Listen for the location data.
    final item = ref.watch(locationProvider(widget.id)).value;
    print('LOCATION RETRIEVED:');
    print(item);

    // Body.
    return CustomScrollView(
      slivers: [
        // App header.
        const SliverToBoxAdapter(child: AppHeader()),

        // Form.
        SliverToBoxAdapter(child: _form(item)),

        // Footer
        const SliverToBoxAdapter(child: Footer()),
      ],
    );
  }

  Widget _form(Location? item) {
    return Container(
      padding: const EdgeInsets.all(16.0),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: <Widget>[
          // Name field.
          gapH6,
          _nameField(item),
          gapH6,

          // TODO: Add additional fields.
          // - id (not editable)
          // - locationTypeId (not editable)
          // - locationTypeName (selection)
          // * Get location types
          // - forPlantBatches (checkbox)
          // - forPlants (checkbox)
          // - forHarvests (checkbox)
          // - forPackages (checkbox)
        ],
      ),
    );
  }

  // Name field.
  Widget _nameField(Location? item) {
    final _nameController = ref.watch(nameController);
    if (item == null) return Container();
    if (_nameController.text.isEmpty && item.name.isNotEmpty) {
      ref.read(nameController.notifier).change(item.name);
      print('SET INITIAL NAME');
    }

    return TextField(
      controller: _nameController,
      decoration: const InputDecoration(labelText: 'Name'),
      keyboardType: TextInputType.text,
      maxLength: 150,
      maxLines: null,
      // onChanged: (value) => _nameController.text = value,
    );
  }
}

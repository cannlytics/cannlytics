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
import 'package:cannlytics_app/widgets/inputs/checkbox_input.dart';
import 'package:flutter/material.dart';

// Package imports:
import 'package:flutter_riverpod/flutter_riverpod.dart';

// Project imports:
import 'package:cannlytics_app/models/metrc/location.dart';

/// Location screen.
class LocationScreen extends ConsumerStatefulWidget {
  const LocationScreen({super.key, required this.id, this.entry});

  // Properties.
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
  // Build.
  @override
  Widget build(BuildContext context) {
    // TODO: Listen for errors.
    // ref.listen<AsyncValue>(
    //   locationProvider(widget.id),
    //   (_, state) => state.showAlertDialogOnError(context),
    // );

    // Listen for the location data.
    final item = ref.watch(locationProvider(widget.id)).value;
    ;

    // Body.
    return CustomScrollView(
      slivers: [
        // App header.
        const SliverToBoxAdapter(child: AppHeader()),

        // Form.
        // TODO: Add a loading placeholding.
        if (item == null)
          SliverToBoxAdapter(child: Container())
        else
          SliverToBoxAdapter(child: _form(item)),

        // Footer
        const SliverToBoxAdapter(child: Footer()),
      ],
    );
  }

  Widget _form(Location item) {
    // Get form values.
    // final _forPlants = ref.watch(forPlants(item.forPlants ?? false));

    return Container(
      padding: const EdgeInsets.all(16.0),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: <Widget>[
          // ID.
          _idField(item),

          // Name field.
          gapH6,
          _nameField(item),
          gapH6,

          // FIXME: Location type.
          // - locationTypeId (not editable)
          // - locationTypeName (selection)
          // * Get location types

          // Checkboxes.
          CheckboxField(
            title: 'For Packages',
            value: ref.watch(forPackages(item.forPackages ?? false)),
            onChanged: (bool? newValue) {
              ref
                  .read(forPackages(item.forPackages ?? false).notifier)
                  .change(newValue ?? false);
            },
          ),
          CheckboxField(
            title: 'For Plants',
            value: ref.watch(forPlants(item.forPlants ?? false)),
            onChanged: (bool? newValue) {
              ref
                  .read(forPlants(item.forPlants ?? false).notifier)
                  .change(newValue ?? false);
            },
          ),
          CheckboxField(
            title: 'For Plant Batches',
            value: ref.watch(forPlantBatches(item.forPlantBatches ?? false)),
            onChanged: (bool? newValue) {
              ref
                  .read(forPlantBatches(item.forPlantBatches ?? false).notifier)
                  .change(newValue ?? false);
            },
          ),
          CheckboxField(
            title: 'For Harvests',
            value: ref.watch(forHarvests(item.forHarvests ?? false)),
            onChanged: (bool? newValue) {
              ref
                  .read(forHarvests(item.forHarvests ?? false).notifier)
                  .change(newValue ?? false);
            },
          ),
        ],
      ),
    );
  }

  // ID field.
  Widget _idField(Location? item) {
    return Text(
      (item == null || item.id.isEmpty)
          ? 'New Location'
          : 'Location ${item.id}',
      style: Theme.of(context).textTheme.titleLarge!.copyWith(
            color: Theme.of(context).textTheme.titleLarge!.color,
          ),
    );
  }

  // Name field.
  Widget _nameField(Location item) {
    final _nameController = ref.watch(nameController);
    // if (item == null) return Container();
    if (_nameController.text.isEmpty && item.name.isNotEmpty) {
      ref.read(nameController.notifier).change(item.name);
    }
    return TextField(
      controller: _nameController,
      decoration: const InputDecoration(labelText: 'Name'),
      keyboardType: TextInputType.text,
      maxLength: 150,
      maxLines: null,
    );
  }
}

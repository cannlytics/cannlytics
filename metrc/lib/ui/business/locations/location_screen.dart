// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 3/7/2023
// Updated: 3/16/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Flutter imports:
import 'package:flutter/material.dart';

// Package imports:
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

// Project imports:
import 'package:cannlytics_app/constants/design.dart';
import 'package:cannlytics_app/models/metrc/location.dart';
import 'package:cannlytics_app/ui/business/locations/locations_controller.dart';
import 'package:cannlytics_app/ui/layout/footer.dart';
import 'package:cannlytics_app/ui/layout/header.dart';
import 'package:cannlytics_app/widgets/buttons/custom_text_button.dart';
import 'package:cannlytics_app/widgets/buttons/primary_button.dart';
import 'package:cannlytics_app/widgets/dialogs/alert_dialog_ui.dart';
import 'package:cannlytics_app/widgets/inputs/checkbox_input.dart';
import 'package:cannlytics_app/widgets/layout/form_container.dart';

/// Location screen.
class LocationScreen extends ConsumerStatefulWidget {
  const LocationScreen({super.key, required this.id, this.entry});

  // Properties.
  final LocationId id;
  final Location? entry;

  @override
  ConsumerState<LocationScreen> createState() => _LocationScreenState();
}

/// Location screen state.
class _LocationScreenState extends ConsumerState<LocationScreen> {
  @override
  Widget build(BuildContext context) {
    // Listen for errors.
    ref.listen<AsyncValue>(
      locationProvider(widget.id),
      (_, state) => state.showAlertDialogOnError(context),
    );

    // Listen for the location data.
    final state = ref.watch(locationProvider(widget.id));
    var item = state.value;
    if (item == null) {
      item = Location(id: 'new', name: '');
    }

    // Body.
    return CustomScrollView(
      slivers: [
        // App header.
        const SliverToBoxAdapter(child: AppHeader()),

        // Form.
        SliverToBoxAdapter(
            child: FormContainer(children: _fields(state, item))),

        // Footer
        const SliverToBoxAdapter(child: Footer()),
      ],
    );
  }

  /// Form fields.
  List<Widget> _fields(AsyncValue state, Location item) {
    return <Widget>[
      // Back to locations button.
      CustomTextButton(
        text: '\u2190 Locations',
        onPressed: () {
          context.go('/locations');
          ref.read(nameController.notifier).change('');
        },
        fontStyle: FontStyle.italic,
      ),

      // Title row.
      Row(
        mainAxisAlignment: MainAxisAlignment.end,
        children: [
          // ID.
          _idField(item),

          // Spacer.
          const Spacer(),

          // Actions.
          // Create / update a location.
          PrimaryButton(
            text: (widget.id == 'new') ? 'Create' : 'Save',
            isLoading: state.isLoading,
            onPressed: state.isLoading
                ? null
                : () async {
                    var name = ref.read(nameController).value.text;
                    var update = Location(
                      id: widget.id,
                      name: name,
                      locationTypeName: ref.read(locationType),
                    );
                    if (widget.id == 'new') {
                      await ref
                          .read(locationsProvider.notifier)
                          .createLocations([update]);
                    } else {
                      // FIXME:
                      await ref
                          .read(locationsProvider.notifier)
                          .updateLocations([update]);
                    }
                    context.go('/locations');
                  },
          ),
        ],
      ),

      // Name field.
      gapH18,
      _nameField(item),
      gapH6,

      // Location type name and ID.
      _locationTypeField(item),

      // Checkbox fields.
      ..._checkboxes(item),

      // TODO: Allow user's to save additional data in Firestore:
      // - location_image
      // - created_at
      // - created_by
      // - updated_at
      // - updated_by

      // Lighting Data
      // This information can help optimize the lighting conditions for
      // the specific strain and maximize the yield and potency of the plants.
      // - light intensity and duration.
      // Energy Consumption Data: Cannabis cultivators may want to track
      // energy consumption data, such as electricity usage and costs, to
      // help identify ways to reduce energy consumption and costs.

      // Climate data
      // ensure that the growing environment is optimal for the plants.
      // - temperature, humidity, precipitation, and wind speed

      // Soil and Water Data
      // This information can help optimize the soil conditions and
      // ensure that the plants receive the right nutrients for healthy growth.
      // - pH levels, nutrient content, and salinity levels

      // Pest and Disease Data: Cannabis cultivators may want to track pest
      // and disease data, such as the presence of pests, mold, or fungus.
      // This information can help identify potential problems early on
      // and take corrective action to prevent damage to the plants.

      // Optional: Look at packages / plants at the location.

      // Danger zone : Handle deleting an existing location.
      if (widget.id.isNotEmpty && widget.id != 'new') _deleteOption(state),
    ];
  }

  Widget _deleteOption(AsyncValue state) {
    return Container(
      constraints: BoxConstraints(minWidth: 200), // set minimum width of 200
      child: Card(
        margin: EdgeInsets.only(top: 36, bottom: 48),
        borderOnForeground: true,
        surfaceTintColor: null,
        child: Padding(
          padding: EdgeInsets.all(16),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.start,
            children: [
              Text(
                'Danger Zone',
                style: Theme.of(context).textTheme.titleLarge!.copyWith(
                      color: Theme.of(context).textTheme.titleLarge!.color,
                    ),
              ),
              gapH12,
              PrimaryButton(
                backgroundColor: Colors.red,
                text: 'Delete',
                isLoading: state.isLoading,
                onPressed: state.isLoading
                    ? null
                    : () async {
                        await ref
                            .read(locationsProvider.notifier)
                            .deleteLocations(
                                [Location(id: widget.id, name: '')]);
                        // FIXME: Clear search, etc. to make table load better.
                        context.go('/locations');
                      },
              ),
            ],
          ),
        ),
      ),
    );
  }

  // ID field.
  Widget _idField(Location item) {
    return Text(
      (item.id.isEmpty) ? 'New Location' : 'Location ${item.id}',
      style: Theme.of(context).textTheme.titleLarge!.copyWith(
            color: Theme.of(context).textTheme.titleLarge!.color,
          ),
    );
  }

  // Name field.
  Widget _nameField(Location item) {
    final _nameController = ref.watch(nameController);
    // Hot-fix: Set the initial value.
    if (_nameController.text.isEmpty && item.name.isNotEmpty) {
      ref.read(nameController.notifier).change(item.name);
    } else if (_nameController.text != item.name) {
      ref.read(nameController.notifier).change(item.name);
    }
    final textField = TextField(
      key: Key('name'),
      controller: _nameController,
      decoration: InputDecoration(labelText: 'Name'),
      style: Theme.of(context).textTheme.titleMedium,
      keyboardType: TextInputType.text,
      maxLength: null,
      maxLines: null,
    );
    return ConstrainedBox(
      constraints: BoxConstraints(maxWidth: 300),
      child: textField,
    );
  }

  // Location name field.
  Widget _locationTypeField(Location item) {
    final items = ref.watch(locationTypesProvider).value ?? [];
    final value = ref.watch(locationType);
    if (items.length == 0 || value == null) return Container();
    var dropdown = DropdownButton(
      key: Key('location_type_name'),
      underline: Container(),
      isDense: true,
      isExpanded: true,
      value: value,
      items: items
          .map(
            (item) => DropdownMenuItem<String>(
              onTap: () => item['name'],
              value: item['name'],
              child: ListTile(
                dense: true,
                title: Text(item['name']),
              ),
            ),
          )
          .toList(),
      onChanged: (String? value) {
        ref.read(locationType.notifier).state = value;
        // FIXME: Change location permissions.
      },
    );
    return Column(
      mainAxisAlignment: MainAxisAlignment.start,
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        gapH18,
        Text(
          'Location Type Name',
          style: Theme.of(context).textTheme.titleMedium!.copyWith(
                color: Theme.of(context).textTheme.titleLarge!.color,
              ),
        ),
        gapH6,
        SizedBox(
          height: 36,
          child: ConstrainedBox(
            constraints: BoxConstraints(
              maxWidth: 300,
            ),
            child: dropdown,
          ),
        ),
        gapH6,
      ],
    );
  }

  // Checkbox fields.
  List<Widget> _checkboxes(Location item) {
    final items = ref.watch(locationTypesProvider).value ?? [];
    if (items.length == 0) return [Container()];
    return [
      gapH12,
      Text(
        'Permissions',
        style: Theme.of(context).textTheme.titleMedium!.copyWith(
              color: Theme.of(context).textTheme.titleLarge!.color,
            ),
      ),
      gapH6,
      CheckboxField(
        key: Key('for_packages'),
        title: 'For Packages',
        value: ref.watch(forPackages) ?? false,
      ),
      CheckboxField(
        key: Key('for_plants'),
        title: 'For Plants',
        value: ref.watch(forPlants) ?? false,
      ),
      CheckboxField(
        key: Key('for_plant_batches'),
        title: 'For Plant Batches',
        value: ref.watch(forPlantBatches) ?? false,
      ),
      CheckboxField(
        key: Key('for_harvests'),
        title: 'For Harvests',
        value: ref.watch(forHarvests) ?? false,
      ),
    ];
  }
}
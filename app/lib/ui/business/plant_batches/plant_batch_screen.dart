// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 3/9/2023
// Updated: 3/18/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Dart imports:

// Flutter imports:
import 'package:flutter/material.dart';

// Package imports:
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

// Project imports:
import 'package:cannlytics_app/widgets/dialogs/alert_dialog_ui.dart';

// Flutter imports:
import 'package:cannlytics_app/constants/design.dart';
import 'package:cannlytics_app/ui/business/plant_batches/plant_batches_controller.dart';
import 'package:cannlytics_app/ui/layout/footer.dart';
import 'package:cannlytics_app/ui/layout/header.dart';
import 'package:cannlytics_app/widgets/buttons/custom_text_button.dart';
import 'package:cannlytics_app/widgets/buttons/primary_button.dart';
import 'package:cannlytics_app/widgets/layout/form_container.dart';

// Package imports:

// Project imports:
import 'package:cannlytics_app/models/metrc/plant_batch.dart';

/// PlantBatch screen.
class PlantBatchScreen extends ConsumerStatefulWidget {
  const PlantBatchScreen({super.key, required this.id, this.entry});

  // Properties.
  final PlantBatchId id;
  final PlantBatch? entry;

  @override
  ConsumerState<PlantBatchScreen> createState() => _PlantBatchScreenState();
}

/// PlantBatch screen state.
class _PlantBatchScreenState extends ConsumerState<PlantBatchScreen> {
  @override
  Widget build(BuildContext context) {
    // Listen for errors.
    ref.listen<AsyncValue>(
      plantBatchProvider(widget.id),
      (_, state) => state.showAlertDialogOnError(context),
    );

    // Listen for the plantBatch data.
    var item = ref.watch(plantBatchProvider(widget.id)).value;
    if (item == null) {
      item = PlantBatch(id: 'new', name: '');
    }

    // Body.
    return CustomScrollView(
      slivers: [
        // App header.
        const SliverToBoxAdapter(child: AppHeader()),

        // Form.
        // TODO: Add a loading indicator.
        SliverToBoxAdapter(child: FormContainer(children: _fields(item))),

        // Footer
        const SliverToBoxAdapter(child: Footer()),
      ],
    );
  }

  /// Form fields.
  List<Widget> _fields(PlantBatch item) {
    return <Widget>[
      // Back to plantBatches button.
      CustomTextButton(
        text: 'PlantBatches',
        onPressed: () {
          context.go('/plantBatches');
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
          // Create / update a plantBatch.
          PrimaryButton(
            text: (widget.id == 'new') ? 'Create' : 'Save',
            onPressed: () async {
              // FIXME:
              var name = ref.read(nameController).value.text;
              var update = PlantBatch(
                id: widget.id,
                name: name,
              );
              if (widget.id == 'new') {
                await ref
                    .read(plantBatchesProvider.notifier)
                    .createPlantBatches([update]);
              } else {
                // FIXME:
                await ref
                    .read(plantBatchesProvider.notifier)
                    .updatePlantBatches([update]);
              }
              context.go('/plantBatches');
            },
          ),
        ],
      ),

      // Name field.
      gapH6,
      // _nameField(item),
      gapH6,

      // PlantBatch type name and ID.
      // _plantBatchTypeField(item),

      // Checkbox fields.
      // ..._checkboxes(item),

      // TODO: Allow user's to save additional data in Firestore:
      // - created_at
      // - created_by
      // - updated_at
      // - updated_by

      // Danger zone : Handle deleting an existing plantBatch.
      if (widget.id.isNotEmpty && widget.id != 'new') _deleteOption(),
    ];
  }

  Widget _deleteOption() {
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
                onPressed: () async {
                  await ref
                      .read(plantBatchesProvider.notifier)
                      .deletePlantBatches(
                          [PlantBatch(id: widget.id, name: '')]);
                  // FIXME: Clear search, etc. to make table load better.
                  context.go('/plantBatches');
                },
              ),
            ],
          ),
        ),
      ),
    );
  }

  // ID field.
  Widget _idField(PlantBatch item) {
    return Text(
      (item.id!.isEmpty) ? 'New PlantBatch' : 'PlantBatch ${item.id}',
      style: Theme.of(context).textTheme.titleLarge!.copyWith(
            color: Theme.of(context).textTheme.titleLarge!.color,
          ),
    );
  }

  // Name field.
  // Widget _nameField(PlantBatch item) {
  //   final _nameController = ref.watch(nameController);
  //   // Hot-fix: Set the initial value.
  //   if (_nameController.text.isEmpty && item.name.isNotEmpty) {
  //     ref.read(nameController.notifier).change(item.name);
  //   } else if (_nameController.text != item.name) {
  //     ref.read(nameController.notifier).change(item.name);
  //   }
  //   final textField = TextField(
  //     controller: _nameController,
  //     decoration: const InputDecoration(labelText: 'Name'),
  //     keyboardType: TextInputType.text,
  //     maxLength: null,
  //     maxLines: null,
  //   );
  //   return ConstrainedBox(
  //     constraints: BoxConstraints(maxWidth: 300),
  //     child: textField,
  //   );
  // }

  // PlantBatch name field.
  // Widget _plantBatchTypeField(PlantBatch item) {
  //   final items = ref.watch(plantBatchTypesProvider).value ?? [];
  //   final value = ref.watch(plantBatchType);
  //   if (items.length == 0 || value == null) return Container();
  //   var dropdown = DropdownButton(
  //     underline: Container(),
  //     isDense: true,
  //     isExpanded: true,
  //     value: value,
  //     items: items
  //         .map(
  //           (item) => DropdownMenuItem<String>(
  //             onTap: () => item['name'],
  //             value: item['name'],
  //             child: ListTile(
  //               dense: true,
  //               title: Text(item['name']),
  //             ),
  //           ),
  //         )
  //         .toList(),
  //     onChanged: (String? value) {
  //       ref.read(plantBatchType.notifier).state = value;
  //       // FIXME: Change plantBatch permissions.
  //     },
  //   );
  //   return Column(
  //     mainAxisAlignment: MainAxisAlignment.start,
  //     crossAxisAlignment: CrossAxisAlignment.start,
  //     children: [
  //       gapH18,
  //       Text(
  //         'PlantBatch Type Name',
  //         style: Theme.of(context).textTheme.titleMedium!.copyWith(
  //               color: Theme.of(context).textTheme.titleLarge!.color,
  //             ),
  //       ),
  //       gapH6,
  //       SizedBox(
  //         height: 36,
  //         child: ConstrainedBox(
  //           constraints: BoxConstraints(
  //             maxWidth: 300,
  //           ),
  //           child: dropdown,
  //         ),
  //       ),
  //       gapH6,
  //     ],
  //   );
  // }

  // // Checkbox fields.
  // List<Widget> _checkboxes(PlantBatch item) {
  //   final items = ref.watch(plantBatchTypesProvider).value ?? [];
  //   if (items.length == 0) return [Container()];
  //   return [
  //     gapH12,
  //     Text(
  //       'Permissions',
  //       style: Theme.of(context).textTheme.titleMedium!.copyWith(
  //             color: Theme.of(context).textTheme.titleLarge!.color,
  //           ),
  //     ),
  //     gapH6,
  //     CheckboxField(
  //       title: 'For Packages',
  //       value: ref.watch(forPackages) ?? false,
  //     ),
  //     CheckboxField(
  //       title: 'For Plants',
  //       value: ref.watch(forPlants) ?? false,
  //     ),
  //     CheckboxField(
  //       title: 'For Plant Batches',
  //       value: ref.watch(forPlantBatches) ?? false,
  //     ),
  //     CheckboxField(
  //       title: 'For Harvests',
  //       value: ref.watch(forHarvests) ?? false,
  //     ),
  //   ];
  // }
}

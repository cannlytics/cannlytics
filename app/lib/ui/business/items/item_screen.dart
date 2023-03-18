// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 2/17/2023
// Updated: 2/18/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Flutter imports:
import 'package:flutter/material.dart';

// Package imports:
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

// Project imports:
import 'package:cannlytics_app/constants/design.dart';
import 'package:cannlytics_app/models/metrc/item.dart';
import 'package:cannlytics_app/ui/business/items/items_controller.dart';
import 'package:cannlytics_app/ui/layout/footer.dart';
import 'package:cannlytics_app/ui/layout/header.dart';
import 'package:cannlytics_app/widgets/buttons/custom_text_button.dart';
import 'package:cannlytics_app/widgets/buttons/primary_button.dart';
import 'package:cannlytics_app/widgets/dialogs/alert_dialog_ui.dart';
import 'package:cannlytics_app/widgets/inputs/checkbox_input.dart';
import 'package:cannlytics_app/widgets/layout/form_container.dart';

/// Item screen.
class ItemScreen extends ConsumerStatefulWidget {
  const ItemScreen({super.key, required this.id, this.entry});

  // Properties.
  final String id;
  final Item? entry;

  @override
  ConsumerState<ItemScreen> createState() => _ItemScreenState();
}

/// Item screen state.
class _ItemScreenState extends ConsumerState<ItemScreen> {
  @override
  Widget build(BuildContext context) {
    // Listen for errors.
    ref.listen<AsyncValue>(
      itemProvider(widget.id),
      (_, state) => state.showAlertDialogOnError(context),
    );

    // Listen for the item data.
    var item = ref.watch(itemProvider(widget.id)).value;
    if (item == null) {
      item = Item(id: 'new', name: '');
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
  List<Widget> _fields(Item item) {
    return <Widget>[
      // Back to items button.
      CustomTextButton(
        text: 'Items',
        onPressed: () {
          context.go('/items');
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
          // Create / update a item.
          PrimaryButton(
            text: (widget.id == 'new') ? 'Create' : 'Save',
            onPressed: () async {
              var name = ref.read(nameController).value.text;
              // FIXME:
              var update = Item(
                id: widget.id,
                name: name,
              );
              if (widget.id == 'new') {
                await ref.read(itemsProvider.notifier).createItems([update]);
              } else {
                // FIXME:
                await ref.read(itemsProvider.notifier).updateItems([update]);
              }
              context.go('/items');
            },
          ),
        ],
      ),

      // Name field.
      gapH6,
      // _nameField(item),
      gapH6,

      // Item type name and ID.
      // _itemTypeField(item),

      // Checkbox fields.
      // ..._checkboxes(item),

      // TODO: Allow user's to save additional data in Firestore:
      // - item_image
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

      // Optional: Look at packages / plants at the item.

      // Danger zone : Handle deleting an existing item.
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
                      .read(itemsProvider.notifier)
                      .deleteItems([Item(id: widget.id, name: '')]);
                  // FIXME: Clear search, etc. to make table load better.
                  context.go('/items');
                },
              ),
            ],
          ),
        ),
      ),
    );
  }

  // ID field.
  Widget _idField(Item item) {
    return Text(
      (item.id!.isEmpty) ? 'New Item' : 'Item ${item.id}',
      style: Theme.of(context).textTheme.titleLarge!.copyWith(
            color: Theme.of(context).textTheme.titleLarge!.color,
          ),
    );
  }

  // // Name field.
  // Widget _nameField(Item item) {
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

  // // Item name field.
  // Widget _itemTypeField(Item item) {
  //   final items = ref.watch(itemTypesProvider).value ?? [];
  //   final value = ref.watch(itemType);
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
  //       ref.read(itemType.notifier).state = value;
  //       // FIXME: Change item permissions.
  //     },
  //   );
  //   return Column(
  //     mainAxisAlignment: MainAxisAlignment.start,
  //     crossAxisAlignment: CrossAxisAlignment.start,
  //     children: [
  //       gapH18,
  //       Text(
  //         'Item Type Name',
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
  // List<Widget> _checkboxes(Item item) {
  //   final items = ref.watch(itemTypesProvider).value ?? [];
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

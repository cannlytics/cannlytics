// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 3/7/2023
// Updated: 3/17/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Flutter imports:
import 'package:flutter/material.dart';

// Package imports:
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

// Project imports:
import 'package:cannlytics_app/constants/design.dart';
import 'package:cannlytics_app/models/metrc/delivery.dart';
import 'package:cannlytics_app/ui/business/deliveries/deliveries_controller.dart';
import 'package:cannlytics_app/ui/layout/footer.dart';
import 'package:cannlytics_app/ui/layout/header.dart';
import 'package:cannlytics_app/widgets/buttons/custom_text_button.dart';
import 'package:cannlytics_app/widgets/buttons/primary_button.dart';
import 'package:cannlytics_app/widgets/dialogs/alert_dialog_ui.dart';
import 'package:cannlytics_app/widgets/inputs/checkbox_input.dart';
import 'package:cannlytics_app/widgets/layout/form_container.dart';

/// Delivery screen.
class DeliveryScreen extends ConsumerStatefulWidget {
  const DeliveryScreen({super.key, required this.id, this.entry});

  // Properties.
  final DeliveryId id;
  final Delivery? entry;

  @override
  ConsumerState<DeliveryScreen> createState() => _DeliveryScreenState();
}

/// Delivery screen state.
class _DeliveryScreenState extends ConsumerState<DeliveryScreen> {
  @override
  Widget build(BuildContext context) {
    // Listen for errors.
    ref.listen<AsyncValue>(
      deliveryProvider(widget.id),
      (_, state) => state.showAlertDialogOnError(context),
    );

    // Listen for the delivery data.
    var item = ref.watch(deliveryProvider(widget.id)).value;
    if (item == null) {
      item = Delivery();
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
  List<Widget> _fields(Delivery item) {
    return <Widget>[
      // Back to deliveries button.
      CustomTextButton(
        text: 'Deliveries',
        onPressed: () {
          context.go('/deliveries');
          ref.read(nameController.notifier).change('');
        },
        fontStyle: FontStyle.italic,
      ),

      // Title row.
      Row(
        mainAxisAlignment: MainAxisAlignment.end,
        children: [
          // ID.
          // _idField(item),

          // Spacer.
          const Spacer(),

          // Actions.
          // Create / update a delivery.
          PrimaryButton(
            text: (widget.id == 'new') ? 'Create' : 'Save',
            onPressed: () async {
              var name = ref.read(nameController).value.text;
              var update = Delivery(
                  // id: widget.id,
                  // name: name,
                  // deliveryTypeName: ref.read(deliveryType),
                  );
              if (widget.id == 'new') {
                await ref
                    .read(deliveriesProvider.notifier)
                    .createDeliveries([update]);
              } else {
                // FIXME:
                await ref
                    .read(deliveriesProvider.notifier)
                    .updateDeliveries([update]);
              }
              context.go('/deliveries');
            },
          ),
        ],
      ),

      // Name field.
      gapH6,
      // _nameField(item),
      gapH6,

      // Delivery type name and ID.
      // _deliveryTypeField(item),

      // Checkbox fields.
      // ..._checkboxes(item),

      // TODO: Allow user's to save additional data in Firestore:
      // - created_at
      // - created_by
      // - updated_at
      // - updated_by

      // Optional: Look at packages / items in the delivery.

      // Danger zone : Handle deleting an existing delivery.
      // if (widget.id.isNotEmpty && widget.id != 'new') _deleteOption(),
    ];
  }

  // Widget _deleteOption() {
  //   return Container(
  //     constraints: BoxConstraints(minWidth: 200), // set minimum width of 200
  //     child: Card(
  //       margin: EdgeInsets.only(top: 36, bottom: 48),
  //       borderOnForeground: true,
  //       surfaceTintColor: null,
  //       child: Padding(
  //         padding: EdgeInsets.all(16),
  //         child: Column(
  //           mainAxisAlignment: MainAxisAlignment.start,
  //           children: [
  //             Text(
  //               'Danger Zone',
  //               style: Theme.of(context).textTheme.titleLarge!.copyWith(
  //                     color: Theme.of(context).textTheme.titleLarge!.color,
  //                   ),
  //             ),
  //             gapH12,
  //             PrimaryButton(
  //               backgroundColor: Colors.red,
  //               text: 'Delete',
  //               onPressed: () async {
  //                 await ref
  //                     .read(deliveriesProvider.notifier)
  //                     .deleteDeliveries([Delivery(id: widget.id, name: '')]);
  //                 // FIXME: Clear search, etc. to make table load better.
  //                 context.go('/deliveries');
  //               },
  //             ),
  //           ],
  //         ),
  //       ),
  //     ),
  //   );
  // }

  // // ID field.
  // Widget _idField(Delivery item) {
  //   return Text(
  //     (item.id.isEmpty) ? 'New Delivery' : 'Delivery ${item.id}',
  //     style: Theme.of(context).textTheme.titleLarge!.copyWith(
  //           color: Theme.of(context).textTheme.titleLarge!.color,
  //         ),
  //   );
  // }

  // // Name field.
  // Widget _nameField(Delivery item) {
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

  // // Delivery name field.
  // Widget _deliveryTypeField(Delivery item) {
  //   final items = ref.watch(deliveryTypesProvider).value ?? [];
  //   final value = ref.watch(deliveryType);
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
  //       ref.read(deliveryType.notifier).state = value;
  //       // FIXME: Change delivery permissions.
  //     },
  //   );
  //   return Column(
  //     mainAxisAlignment: MainAxisAlignment.start,
  //     crossAxisAlignment: CrossAxisAlignment.start,
  //     children: [
  //       gapH18,
  //       Text(
  //         'Delivery Type Name',
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
}

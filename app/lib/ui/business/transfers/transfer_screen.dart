// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 3/8/2023
// Updated: 3/8/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Flutter imports:
import 'package:flutter/material.dart';

// Package imports:
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

// Project imports:
import 'package:cannlytics_app/constants/design.dart';
import 'package:cannlytics_app/models/metrc/transfer.dart';
import 'package:cannlytics_app/ui/business/transfers/transfers_controller.dart';
import 'package:cannlytics_app/ui/layout/footer.dart';
import 'package:cannlytics_app/ui/layout/header.dart';
import 'package:cannlytics_app/widgets/buttons/custom_text_button.dart';
import 'package:cannlytics_app/widgets/buttons/primary_button.dart';
import 'package:cannlytics_app/widgets/dialogs/alert_dialog_ui.dart';
import 'package:cannlytics_app/widgets/inputs/checkbox_input.dart';
import 'package:cannlytics_app/widgets/layout/form_container.dart';

/// Transfer screen.
class TransferScreen extends ConsumerStatefulWidget {
  const TransferScreen({super.key, required this.id, this.entry});

  // Properties.
  final TransferId id;
  final Transfer? entry;

  @override
  ConsumerState<TransferScreen> createState() => _TransferScreenState();
}

/// Transfer screen state.
class _TransferScreenState extends ConsumerState<TransferScreen> {
  @override
  Widget build(BuildContext context) {
    // Listen for errors.
    ref.listen<AsyncValue>(
      transferProvider(widget.id),
      (_, state) => state.showAlertDialogOnError(context),
    );

    // Listen for the transfer data.
    var item = ref.watch(transferProvider(widget.id)).value;
    if (item == null) {
      item = Transfer(id: 'new');
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
  List<Widget> _fields(Transfer item) {
    return <Widget>[
      // Back to transfers button.
      CustomTextButton(
        text: 'Transfers',
        onPressed: () {
          context.go('/transfers');
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
          // Create / update a transfer.
          PrimaryButton(
            text: (widget.id == 'new') ? 'Create' : 'Save',
            onPressed: () async {
              // FIXME:
              var name = ref.read(nameController).value.text;
              var update = Transfer(
                id: widget.id,
                name: name,
              );
              if (widget.id == 'new') {
                await ref
                    .read(transfersProvider.notifier)
                    .createTransfers([update]);
              } else {
                // FIXME:
                await ref
                    .read(transfersProvider.notifier)
                    .updateTransfers([update]);
              }
              context.go('/transfers');
            },
          ),
        ],
      ),

      // Name field.
      gapH6,
      _nameField(item),
      gapH6,

      // Transfer type name and ID.
      // _transferTypeField(item),

      // Checkbox fields.
      // ..._checkboxes(item),

      // TODO: Allow user's to save additional data in Firestore:
      // - created_at
      // - created_by
      // - updated_at
      // - updated_by

      // Danger zone : Handle deleting an existing transfer.
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
                      .read(transfersProvider.notifier)
                      .deleteTransfers([Transfer(id: widget.id, name: '')]);
                  // FIXME: Clear search, etc. to make table load better.
                  context.go('/transfers');
                },
              ),
            ],
          ),
        ),
      ),
    );
  }

  // ID field.
  Widget _idField(Transfer item) {
    return Text(
      (item.id!.isEmpty) ? 'New Transfer' : 'Transfer ${item.id}',
      style: Theme.of(context).textTheme.titleLarge!.copyWith(
            color: Theme.of(context).textTheme.titleLarge!.color,
          ),
    );
  }

  // Name field.
  Widget _nameField(Transfer item) {
    final _nameController = ref.watch(nameController);
    // Hot-fix: Set the initial value.
    if (_nameController.text.isEmpty && item.name!.isNotEmpty) {
      ref.read(nameController.notifier).change(item.name ?? '');
    } else if (_nameController.text != item.name) {
      ref.read(nameController.notifier).change(item.name ?? '');
    }
    final textField = TextField(
      controller: _nameController,
      decoration: const InputDecoration(labelText: 'Name'),
      keyboardType: TextInputType.text,
      maxLength: null,
      maxLines: null,
    );
    return ConstrainedBox(
      constraints: BoxConstraints(maxWidth: 300),
      child: textField,
    );
  }

  // Transfer name field.
  // Widget _transferTypeField(Transfer item) {
  //   final items = ref.watch(transferTypesProvider).value ?? [];
  //   final value = ref.watch(transferType);
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
  //       ref.read(transferType.notifier).state = value;
  //       // FIXME: Change transfer permissions.
  //     },
  //   );
  //   return Column(
  //     mainAxisAlignment: MainAxisAlignment.start,
  //     crossAxisAlignment: CrossAxisAlignment.start,
  //     children: [
  //       gapH18,
  //       Text(
  //         'Transfer Type Name',
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

  // Checkbox fields.
  // List<Widget> _checkboxes(Transfer item) {
  //   final items = ref.watch(transferTypesProvider).value ?? [];
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

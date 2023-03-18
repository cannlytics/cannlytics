// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 2/17/2023
// Updated: 3/18/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Flutter imports:
import 'package:flutter/material.dart';

// Package imports:
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

// Project imports:
import 'package:cannlytics_app/constants/design.dart';
import 'package:cannlytics_app/models/metrc/package.dart';
import 'package:cannlytics_app/ui/business/packages/packages_controller.dart';
import 'package:cannlytics_app/ui/layout/footer.dart';
import 'package:cannlytics_app/ui/layout/header.dart';
import 'package:cannlytics_app/widgets/buttons/custom_text_button.dart';
import 'package:cannlytics_app/widgets/buttons/primary_button.dart';
import 'package:cannlytics_app/widgets/dialogs/alert_dialog_ui.dart';
import 'package:cannlytics_app/widgets/inputs/checkbox_input.dart';
import 'package:cannlytics_app/widgets/layout/form_container.dart';

/// Package screen.
class PackageScreen extends ConsumerStatefulWidget {
  const PackageScreen({super.key, required this.id, this.entry});

  // Properties.
  final String id;
  final Package? entry;

  @override
  ConsumerState<PackageScreen> createState() => _PackageScreenState();
}

/// Package screen state.
class _PackageScreenState extends ConsumerState<PackageScreen> {
  @override
  Widget build(BuildContext context) {
    // Listen for errors.
    ref.listen<AsyncValue>(
      packageProvider(widget.id),
      (_, state) => state.showAlertDialogOnError(context),
    );

    // Listen for the package data.
    var item = ref.watch(packageProvider(widget.id)).value;
    if (item == null) {
      item = Package();
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
  List<Widget> _fields(Package item) {
    return <Widget>[
      // Back to packages button.
      CustomTextButton(
        text: 'Packages',
        onPressed: () {
          context.go('/packages');
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
          // Create / update a package.
          PrimaryButton(
            text: (widget.id == 'new') ? 'Create' : 'Save',
            onPressed: () async {
              var name = ref.read(nameController).value.text;
              var update = Package(id: widget.id);
              if (widget.id == 'new') {
                await ref
                    .read(packagesProvider.notifier)
                    .createPackages([update]);
              } else {
                // FIXME:
                await ref
                    .read(packagesProvider.notifier)
                    .updatePackages([update]);
              }
              context.go('/packages');
            },
          ),
        ],
      ),

      // Name field.
      gapH6,
      // _nameField(item),
      gapH6,

      // Package type name and ID.
      // _packageTypeField(item),

      // Checkbox fields.
      // ..._checkboxes(item),

      // TODO: Allow user's to save additional data in Firestore:
      // - package_image
      // - created_at
      // - created_by
      // - updated_at
      // - updated_by

      // Danger zone : Handle deleting an existing package.
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
                      .read(packagesProvider.notifier)
                      .deletePackages([Package(id: widget.id)]);
                  // FIXME: Clear search, etc. to make table load better.
                  context.go('/packages');
                },
              ),
            ],
          ),
        ),
      ),
    );
  }

  // ID field.
  Widget _idField(Package item) {
    return Text(
      (item.id!.isEmpty) ? 'New Package' : 'Package ${item.id}',
      style: Theme.of(context).textTheme.titleLarge!.copyWith(
            color: Theme.of(context).textTheme.titleLarge!.color,
          ),
    );
  }

  // Name field.
  // Widget _nameField(Package item) {
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

  // // Package name field.
  // Widget _packageTypeField(Package item) {
  //   final items = ref.watch(packageTypesProvider).value ?? [];
  //   final value = ref.watch(packageType);
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
  //       ref.read(packageType.notifier).state = value;
  //       // FIXME: Change package permissions.
  //     },
  //   );
  //   return Column(
  //     mainAxisAlignment: MainAxisAlignment.start,
  //     crossAxisAlignment: CrossAxisAlignment.start,
  //     children: [
  //       gapH18,
  //       Text(
  //         'Package Type Name',
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
  // List<Widget> _checkboxes(Package item) {
  //   final items = ref.watch(packageTypesProvider).value ?? [];
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

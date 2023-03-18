// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 3/8/2023
// Updated: 3/13/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Dart imports:
import 'dart:async';

// Flutter imports:
import 'package:cannlytics_app/constants/design.dart';
import 'package:cannlytics_app/models/metrc/strain.dart';
import 'package:cannlytics_app/ui/business/strains/strains_controller.dart';
import 'package:cannlytics_app/ui/layout/footer.dart';
import 'package:cannlytics_app/ui/layout/header.dart';
import 'package:cannlytics_app/widgets/buttons/primary_button.dart';
import 'package:cannlytics_app/widgets/layout/form_container.dart';
import 'package:flutter/material.dart';

// Package imports:
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

// Project imports:
import 'package:cannlytics_app/widgets/dialogs/alert_dialog_ui.dart';

/// Strain screen.
class StrainScreen extends ConsumerStatefulWidget {
  const StrainScreen({super.key, required this.id, this.entry});

  // Properties.
  final StrainId id;
  final Strain? entry;

  @override
  ConsumerState<StrainScreen> createState() => _StrainScreenState();
}

/// Strain screen state.
class _StrainScreenState extends ConsumerState<StrainScreen> {
  @override
  Widget build(BuildContext context) {
    // Listen for errors.
    ref.listen<AsyncValue>(
      strainProvider(widget.id),
      (_, state) => state.showAlertDialogOnError(context),
    );

    // Listen for the strain data.
    var item = ref.watch(strainProvider(widget.id)).value;
    if (item == null) {
      item = Strain(id: 'new', name: '');
    }

    // Body.
    return CustomScrollView(
      slivers: [
        // App header.
        const SliverToBoxAdapter(child: AppHeader()),

        // Form.
        // TODO: Add a loading placeholding.
        // if (item == null)
        //   SliverToBoxAdapter(
        //     child: CustomPlaceholder(
        //       image: 'assets/images/icons/facilities.png',
        //       title: 'Add a strain',
        //       description:
        //           'Strains are used to track packages, items, and plants.',
        //       onTap: () {
        //         context.go('/strains/new');
        //       },
        //     ),
        //   )
        // else
        SliverToBoxAdapter(child: FormContainer(children: _fields(item))),

        // Footer
        const SliverToBoxAdapter(child: Footer()),
      ],
    );
  }

  /// Form fields.
  List<Widget> _fields(Strain item) {
    return <Widget>[
      Row(
        mainAxisAlignment: MainAxisAlignment.end,
        children: [
          // ID.
          _idField(item),

          // Spacer.
          const Spacer(),

          // Actions.
          // TODO: Handle creating / updating a strain.
          PrimaryButton(
            text: (widget.id == 'new') ? 'Create' : 'Save',
            onPressed: () async {
              if (widget.id == 'new') {
                // TODO: Get fields.
                print('FIELDS:');
                var name = ref.read(nameController).value.text;
                var update = Strain(
                  id: widget.id,
                  name: name,
                );
                print('UPDATE:');
                print(update);
                // ref.read(strainsProvider.notifier).createStrains([entry]);
              } else {}
              // context.go('/strains');
            },
          ),
        ],
      ),

      // Name field.
      gapH6,
      _nameField(item),
      gapH6,

      // Strain type name and ID.
      // _strainTypeField(item),

      // Checkbox fields.
      // ..._checkboxes(item),

      // TODO: Allow user's to save additional data in Firestore:
      // - strain_image
      // - created_at
      // - created_by
      // - updated_at
      // - updated_by

      // Danger zone : Handle deleting an existing strain.
      if (widget.id == 'new') _deleteOption(),
    ];
  }

  Widget _deleteOption() {
    return Container(
      constraints: BoxConstraints(minWidth: 200), // set minimum width of 200
      child: Card(
        borderOnForeground: true,
        surfaceTintColor: null,
        child: Padding(
          padding: EdgeInsets.all(16),
          child: Column(
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
                onPressed: () {
                  // FIXME: Actually delete the strain.
                  context.go('/strains');
                },
              ),
            ],
          ),
        ),
      ),
    );
  }

  // ID field.
  Widget _idField(Strain item) {
    return Text(
      (item.id.isEmpty) ? 'New Strain' : 'Strain ${item.id}',
      style: Theme.of(context).textTheme.titleLarge!.copyWith(
            color: Theme.of(context).textTheme.titleLarge!.color,
          ),
    );
  }

  // Name field.
  Widget _nameField(Strain item) {
    final _nameController = ref.watch(nameController);
    if (_nameController.text.isEmpty && item.name.isNotEmpty) {
      ref.read(nameController.notifier).change(item.name);
    }
    final textField = TextField(
      controller: _nameController,
      decoration: const InputDecoration(labelText: 'Name'),
      keyboardType: TextInputType.text,
      maxLength: null,
      maxLines: null,
    );
    return ConstrainedBox(
      constraints: BoxConstraints(
        maxWidth: 300,
      ),
      child: textField,
    );
  }

  // Strain name field.
  // Widget _strainTypeField(Strain item) {
  //   final items = ref.watch(strainTypesProvider).value ?? [];
  //   final value = ref.watch(strainType);
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
  //       ref.read(strainType.notifier).state = value;
  //       // FIXME: Change strain permissions.
  //     },
  //   );
  //   return Column(
  //     mainAxisAlignment: MainAxisAlignment.start,
  //     crossAxisAlignment: CrossAxisAlignment.start,
  //     children: [
  //       gapH18,
  //       Text(
  //         'Strain Type Name',
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
  // List<Widget> _checkboxes(Strain item) {
  //   final items = ref.watch(strainTypesProvider).value ?? [];
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

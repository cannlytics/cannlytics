// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 3/8/2023
// Updated: 3/17/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Flutter imports:
import 'package:cannlytics_app/constants/design.dart';
import 'package:cannlytics_app/ui/business/patients/patients_controller.dart';
import 'package:cannlytics_app/ui/layout/footer.dart';
import 'package:cannlytics_app/ui/layout/header.dart';
import 'package:cannlytics_app/widgets/buttons/custom_text_button.dart';
import 'package:cannlytics_app/widgets/buttons/primary_button.dart';
import 'package:cannlytics_app/widgets/dialogs/alert_dialog_ui.dart';
import 'package:cannlytics_app/widgets/inputs/checkbox_input.dart';
import 'package:cannlytics_app/widgets/layout/form_container.dart';
import 'package:flutter/material.dart';

// Package imports:
import 'package:flutter_riverpod/flutter_riverpod.dart';

// Project imports:
import 'package:cannlytics_app/models/metrc/patient.dart';
import 'package:go_router/go_router.dart';

/// Patient screen.
class PatientScreen extends ConsumerStatefulWidget {
  const PatientScreen({super.key, required this.id, this.entry});

  // Properties.
  final PatientId id;
  final Patient? entry;

  @override
  ConsumerState<PatientScreen> createState() => _PatientScreenState();
}

/// Patient screen state.
class _PatientScreenState extends ConsumerState<PatientScreen> {
  @override
  Widget build(BuildContext context) {
    // Listen for errors.
    ref.listen<AsyncValue>(
      patientProvider(widget.id),
      (_, state) => state.showAlertDialogOnError(context),
    );

    // Listen for the patient data.
    var item = ref.watch(patientProvider(widget.id)).value;
    if (item == null) {
      item = Patient();
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
  List<Widget> _fields(Patient item) {
    return <Widget>[
      // Back to patients button.
      CustomTextButton(
        text: 'Patients',
        onPressed: () {
          context.go('/patients');
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
          // Create / update a patient.
          PrimaryButton(
            text: (widget.id == 'new') ? 'Create' : 'Save',
            onPressed: () async {
              var name = ref.read(nameController).value.text;
              // FIXME: Get the data.
              var update = Patient();
              if (widget.id == 'new') {
                await ref
                    .read(patientsProvider.notifier)
                    .createPatients([update]);
              } else {
                // FIXME:
                await ref
                    .read(patientsProvider.notifier)
                    .updatePatients([update]);
              }
              context.go('/patients');
            },
          ),
        ],
      ),

      // Name field.
      gapH6,
      // _nameField(item),
      gapH6,

      // Patient type name and ID.
      // _patientTypeField(item),

      // Checkbox fields.
      // ..._checkboxes(item),

      // TODO: Allow user's to save additional data in Firestore:
      // - patient_image
      // - created_at
      // - created_by
      // - updated_at
      // - updated_by

      // Danger zone : Handle deleting an existing patient.
      if (widget.id!.isNotEmpty && widget.id != 'new') _deleteOption(),
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
                  // FIXME:
                  // await ref
                  //     .read(patientsProvider.notifier)
                  //     .deletePatients([Patient(id: widget.id, name: '')]);
                  // FIXME: Clear search, etc. to make table load better.
                  context.go('/patients');
                },
              ),
            ],
          ),
        ),
      ),
    );
  }

  // ID field.
  Widget _idField(Patient item) {
    return Text(
      (item.id!.isEmpty) ? 'New Patient' : 'Patient ${item.id}',
      style: Theme.of(context).textTheme.titleLarge!.copyWith(
            color: Theme.of(context).textTheme.titleLarge!.color,
          ),
    );
  }

  // Name field.
  // Widget _nameField(Patient item) {
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

  // Patient name field.
  // Widget _patientTypeField(Patient item) {
  //   final items = ref.watch(patientTypesProvider).value ?? [];
  //   final value = ref.watch(patientType);
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
  //       ref.read(patientType.notifier).state = value;
  //       // FIXME: Change patient permissions.
  //     },
  //   );
  //   return Column(
  //     mainAxisAlignment: MainAxisAlignment.start,
  //     crossAxisAlignment: CrossAxisAlignment.start,
  //     children: [
  //       gapH18,
  //       Text(
  //         'Patient Type Name',
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
  // List<Widget> _checkboxes(Patient item) {
  //   final items = ref.watch(patientTypesProvider).value ?? [];
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

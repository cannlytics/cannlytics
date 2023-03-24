// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 2/23/2023
// Updated: 3/23/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Flutter imports:
import 'package:cannlytics_app/widgets/layout/main_screen.dart';
import 'package:flutter/material.dart';

// Package imports:
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

// Project imports:
import 'package:cannlytics_app/constants/design.dart';
import 'package:cannlytics_app/models/metrc/facility.dart';
import 'package:cannlytics_app/ui/business/facilities/facilities_controller.dart';
import 'package:cannlytics_app/ui/layout/footer.dart';
import 'package:cannlytics_app/ui/layout/header.dart';
import 'package:cannlytics_app/widgets/buttons/custom_text_button.dart';
import 'package:cannlytics_app/widgets/dialogs/alert_dialog_ui.dart';
import 'package:cannlytics_app/widgets/layout/form_container.dart';

/// Facility screen.
class FacilityScreen extends ConsumerStatefulWidget {
  const FacilityScreen({super.key, required this.id, this.entry});

  // Properties.
  final FacilityId id;
  final Facility? entry;

  @override
  ConsumerState<FacilityScreen> createState() => _FacilityScreenState();
}

/// Facility screen state.
class _FacilityScreenState extends ConsumerState<FacilityScreen> {
  @override
  Widget build(BuildContext context) {
    // Listen for errors.
    ref.listen<AsyncValue>(
      facilityProvider(widget.id),
      (_, state) => state.showAlertDialogOnError(context),
    );

    // Listen for the facility data.
    var item = ref.watch(facilityProvider(widget.id)).value;
    if (item == null) {
      item = Facility(id: 'new', name: '');
    }
    print('CURRENT FACILITY:');
    print(item.toMap());

    // Body.
    return MainScreen(
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
  List<Widget> _fields(Facility item) {
    return <Widget>[
      // Back to facilities button.
      CustomTextButton(
        text: '\u2190  Facilities',
        onPressed: () {
          context.go('/facilities');
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
        ],
      ),

      // Name field.
      gapH18,
      _nameField(item),
      gapH6,

      // Alias field
      gapH18,
      _aliasField(item),
      gapH6,

      // Facility type name and ID.
      // _facilityTypeField(item),

      // Checkbox fields.
      // ..._checkboxes(item),

      // TODO: Allow user's to save additional data in Firestore:
      // - facility_image
      // - created_at
      // - created_by
      // - updated_at
      // - updated_by

      // Danger zone : Handle deleting an existing facility.
      // if (widget.id.isNotEmpty && widget.id != 'new') _deleteOption(),
    ];
  }

  // ID field.
  Widget _idField(Facility item) {
    return Text(
      (item.id.isEmpty) ? 'New Facility' : 'Facility ${item.id}',
      style: Theme.of(context).textTheme.titleLarge!.copyWith(
            color: Theme.of(context).textTheme.titleLarge!.color,
          ),
    );
  }

  // Name field.
  Widget _nameField(Facility item) {
    final _nameController = ref.watch(nameController);
    // Hot-fix: Set the initial value.
    if (_nameController.text.isEmpty && item.name.isNotEmpty) {
      ref.read(nameController.notifier).change(item.name);
    } else if (_nameController.text != item.name) {
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
      constraints: BoxConstraints(maxWidth: 300),
      child: textField,
    );
  }

  // Alias field.
  Widget _aliasField(Facility item) {
    final _controller = ref.watch(aliasController);
    // Hot-fix: Set the initial value.
    if (_controller.text.isEmpty && item.alias.isNotEmpty) {
      ref.read(aliasController.notifier).change(item.alias);
    } else if (_controller.text != item.alias) {
      ref.read(aliasController.notifier).change(item.alias);
    }
    final textField = TextField(
      controller: _controller,
      decoration: const InputDecoration(labelText: 'Alias'),
      keyboardType: TextInputType.text,
      maxLength: null,
      maxLines: null,
    );
    return ConstrainedBox(
      constraints: BoxConstraints(maxWidth: 300),
      child: textField,
    );
  }
}

// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 3/8/2023
// Updated: 3/16/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Flutter imports:
import 'package:flutter/material.dart';

// Package imports:
import 'package:flutter_riverpod/flutter_riverpod.dart';

// Project imports:
import 'package:cannlytics_app/constants/design.dart';
import 'package:cannlytics_app/models/metrc/employee.dart';
import 'package:cannlytics_app/ui/business/employees/employees_controller.dart';
import 'package:cannlytics_app/ui/layout/footer.dart';
import 'package:cannlytics_app/ui/layout/header.dart';
import 'package:cannlytics_app/widgets/dialogs/alert_dialog_ui.dart';
import 'package:cannlytics_app/widgets/layout/form_container.dart';

/// Employee screen.
class EmployeeScreen extends ConsumerStatefulWidget {
  const EmployeeScreen({super.key, required this.id, this.entry});

  // Properties
  final String id;
  final Employee? entry;

  @override
  ConsumerState<EmployeeScreen> createState() => _EmployeeScreenState();
}

/// Employee screen state.
class _EmployeeScreenState extends ConsumerState<EmployeeScreen> {
  @override
  Widget build(BuildContext context) {
    // Listen for errors.
    ref.listen<AsyncValue>(
      employeeProvider(widget.id),
      (_, state) => state.showAlertDialogOnError(context),
    );

    // Listen for the employee data.
    var item = ref.watch(employeeProvider(widget.id)).value;
    if (item == null) {
      item = Employee(fullName: '', licenseNumber: '');
    }

    // Body.
    return CustomScrollView(
      slivers: [
        // App header.
        const SliverToBoxAdapter(child: AppHeader()),

        // Form.
        // TODO: Add a loading placeholding.
        SliverToBoxAdapter(child: FormContainer(children: _fields(item))),

        // Footer
        const SliverToBoxAdapter(child: Footer()),
      ],
    );
  }

  /// Form fields.
  List<Widget> _fields(Employee item) {
    return <Widget>[
      Row(
        mainAxisAlignment: MainAxisAlignment.end,
        children: [
          // ID.
          _idField(item),

          // Spacer.
          const Spacer(),

          // Actions.
          // Optional: Handle creating / updating a (non-Metrc) employee.
        ],
      ),

      // Name field.
      gapH12,
      _nameField(item),
      gapH6,

      // Employee type name and ID.
      // _employeeTypeField(item),

      // Checkbox fields.
      // ..._checkboxes(item),

      // Optional: Allow user's to save additional data in Firestore:
      // - employee_image
      // - created_at
      // - created_by
      // - updated_at
      // - updated_by

      // Optional: Handle deleting a non-Metrc employee.
      // if (widget.id == 'new') _deleteOption(),
    ];
  }

  // ID field.
  Widget _idField(Employee item) {
    return Text(
      (item.licenseNumber!.isEmpty)
          ? 'New Employee'
          : 'Employee ${item.licenseNumber}',
      style: Theme.of(context).textTheme.titleLarge!.copyWith(
            color: Theme.of(context).textTheme.titleLarge!.color,
          ),
    );
  }

  // Name field.
  Widget _nameField(Employee item) {
    final _nameController = ref.watch(nameController);
    if (_nameController.text.isEmpty && item.fullName!.isNotEmpty) {
      ref.read(nameController.notifier).change(item.fullName!);
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

  // TODO: licenseStartDate field.

  // TODO: licenseEndDate field.

  // TODO: licenseType field.
}

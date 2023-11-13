// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 3/8/2023
// Updated: 3/22/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Flutter imports:
import 'package:flutter/material.dart';

// Package imports:
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

// Project imports:
import 'package:cannlytics_app/constants/design.dart';
import 'package:cannlytics_app/models/metrc/strain.dart';
import 'package:cannlytics_app/ui/business/strains/strains_controller.dart';
import 'package:cannlytics_app/ui/layout/footer.dart';
import 'package:cannlytics_app/ui/layout/header.dart';
import 'package:cannlytics_app/widgets/buttons/primary_button.dart';
import 'package:cannlytics_app/widgets/dialogs/alert_dialog_ui.dart';
import 'package:cannlytics_app/widgets/layout/form_container.dart';

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

    // FIXME: Listen for the strain data.
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

          // Handle creating / updating a strain.
          PrimaryButton(
            text: (widget.id == 'new') ? 'Create' : 'Save',
            onPressed: () async {
              var update = Strain(
                id: widget.id,
                name: ref.read(nameController).value.text,
                testingStatus: ref.read(testingStatus),
                cbdLevel: ref.read(cbdLevel),
                thcLevel: ref.read(thcLevel),
                indicaPercentage: ref.read(indicaPercentage),
                sativaPercentage: ref.read(sativaPercentage),
              );
              print('FIELDS:');
              print(update.toMap());
              if (widget.id == 'new') {
                await ref
                    .read(strainsProvider.notifier)
                    .createStrains([update]);
              } else {
                await ref
                    .read(strainsProvider.notifier)
                    .updateStrains([update]);
              }
            },
          ),
        ],
      ),

      // Name field.
      gapH6,
      _nameField(item),
      gapH6,

      // Testing status field.
      _testingStatusField(item),

      // THC / CBD levels.
      _cannabinoidFields(item),

      // Indica / Sativa percentages.
      _indicaSativaField(ref.watch(sativaPercentage)),

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

  /// ID field.
  Widget _idField(Strain item) {
    return Text(
      (item.id.isEmpty || item.id == 'new')
          ? 'New Strain'
          : 'Strain ${item.id}',
      style: Theme.of(context).textTheme.titleLarge!.copyWith(
            color: Theme.of(context).textTheme.titleLarge!.color,
          ),
    );
  }

  /// Name field.
  Widget _nameField(Strain item) {
    final _nameController = ref.watch(nameController);
    if (_nameController.text.isEmpty && item.name.isNotEmpty) {
      ref.read(nameController.notifier).change(item.name);
    }
    final textField = TextField(
      controller: _nameController,
      decoration: const InputDecoration(labelText: 'Name'),
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

  /// Testing status input.
  Widget _testingStatusField(Strain item) {
    // FIXME: Implement.
    return Container();
  }

  /// Cannabinoids (THC/CBD) input.
  Widget _cannabinoidFields(Strain item) {
    // FIXME: Implement.
    return Container();
  }

  /// Indica and sativa percentage input.
  Widget _indicaSativaField(double value) {
    return SliderTheme(
      data: SliderThemeData(
        thumbColor: value == 50
            ? Colors.green
            : value > 50
                ? LinearGradient(
                    colors: List<Color>.generate(
                      101,
                      (index) => Color.lerp(
                        Colors.deepOrange,
                        Colors.yellow,
                        index / 100,
                      )!,
                    ),
                  ).colors[(value / 1).round()]
                : LinearGradient(
                    colors: List<Color>.generate(
                      101,
                      (index) => Color.lerp(
                        Colors.indigo,
                        Colors.redAccent,
                        index / 100,
                      )!,
                    ),
                  ).colors[(value / 1).round()],
        thumbShape: RoundSliderThumbShape(enabledThumbRadius: 12),
        trackHeight: 8,
        activeTrackColor: Colors.grey[400],
        inactiveTrackColor: Colors.grey[400],
        overlayColor: Colors.transparent,
      ),
      child: Slider(
        value: ref.watch(sativaPercentage),
        min: 0,
        max: 100,
        divisions: 100,
        onChanged: (double value) {
          ref.read(indicaPercentage.notifier).state = 100 - value;
          ref.read(sativaPercentage.notifier).state = value;
        },
      ),
    );
  }

  /// An option to delete a strain.
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
}

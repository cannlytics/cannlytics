// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 2/18/2023
// Updated: 2/26/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Flutter imports:
import 'package:cannlytics_app/ui/business/facilities/facilities_controller.dart';
import 'package:flutter/material.dart';

// Package imports:
import 'package:flutter_riverpod/flutter_riverpod.dart';

// Project imports:
import 'package:cannlytics_app/widgets/lists/list_items_builder.dart';

/// The facilities screen.
class FacilitiesScreen extends ConsumerWidget {
  const FacilitiesScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return Scaffold(
      // App bar.
      appBar: AppBar(
        title: const Text('Facilities'),
      ),

      // Body.
      body: Consumer(
        builder: (context, ref, child) {
          // Facilities provider.
          final data = ref.watch(facilitiesProvider);

          // Render facilities.
          return ListItemsBuilder<dynamic>(
            data: data,
            itemBuilder: (context, model) => FacilityRow(model: model),
          );
        },
      ),
    );
  }
}

/// Class to display facilities.
class FacilityRowModel {
  const FacilityRowModel({
    required this.leadingText,
    required this.trailingText,
    this.middleText,
    this.isHeader = false,
  });
  final String leadingText;
  final String trailingText;
  final String? middleText;
  final bool isHeader;
}

/// A facility tile.
class FacilityRow extends StatelessWidget {
  const FacilityRow({super.key, required this.model});
  final FacilityRowModel model;

  @override
  Widget build(BuildContext context) {
    const fontSize = 16.0;
    return Container(
      color: model.isHeader ? Colors.indigo[100] : null,
      padding: const EdgeInsets.symmetric(vertical: 8.0, horizontal: 16.0),
      child: Row(
        children: <Widget>[
          // Title.
          Text(
            model.leadingText,
            style: const TextStyle(fontSize: fontSize),
          ),
          Expanded(child: Container()),

          // Description.
          if (model.middleText != null)
            Text(
              model.middleText!,
              style: TextStyle(color: Colors.green[700], fontSize: fontSize),
              textAlign: TextAlign.right,
            ),

          // Actions.
          SizedBox(
            width: 60.0,
            child: Text(
              model.trailingText,
              style: const TextStyle(fontSize: fontSize),
              textAlign: TextAlign.right,
            ),
          ),
        ],
      ),
    );
  }
}

// Cannlytics Data
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 4/16/2023
// Updated: 4/16/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Flutter imports:
import 'package:flutter/material.dart';

// Project imports:
import 'package:cannlytics_data/common/layout/console.dart';

/// CoA Doc screen.
class CoADocScreen extends StatelessWidget {
  const CoADocScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return ConsoleScreen(
      children: [
        SliverToBoxAdapter(child: Text('CoA Doc')),
        SliverToBoxAdapter(
          child: Image.network(
            'https://firebasestorage.googleapis.com/v0/b/cannlytics.appspot.com/o/public%2Fimages%2Flogos%2Fcannlytics_coa_doc.png?alt=media&token=1871dde9-82db-4342-a29d-d373671491b3',
            width: 120,
          ),
        ),
      ],
    );
  }
}

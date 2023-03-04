// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 3/3/2023
// Updated: 3/3/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Flutter imports:
import 'package:cannlytics_app/constants/design.dart';
import 'package:cannlytics_app/services/theme_service.dart';
import 'package:cannlytics_app/ui/account/licenses/licenses_controller.dart';
import 'package:flutter/material.dart';

// Package imports:
import 'package:flutter_riverpod/flutter_riverpod.dart';

// Project imports:
import 'package:cannlytics_app/ui/general/footer.dart';
import 'package:cannlytics_app/ui/general/header.dart';
import 'package:cannlytics_app/widgets/lists/list_items_builder.dart';

/// Licenses screen.
class OrganizationsScreen extends ConsumerWidget {
  const OrganizationsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    // TODO: Get the user's organizations.
    final data = ref.watch(organizationProvider);
    print('ORGANIZATION LICENSES:');
    print(data);

    // Determine the screen size.
    final screenWidth = MediaQuery.of(context).size.width;
    final isWide = screenWidth > Breakpoints.tablet;

    // Get the theme.
    final themeMode = ref.watch(themeModeProvider);
    final bool isDark = themeMode == ThemeMode.dark;

    // Render the widget.
    return Scaffold(
      body: CustomScrollView(
        slivers: [
          // App header.
          const SliverToBoxAdapter(child: AppHeader()),

          // Navigation cards.
          SliverToBoxAdapter(
            child: Consumer(
              builder: (context, ref, child) {
                return Container(
                  color: Theme.of(context).scaffoldBackgroundColor,
                  margin: EdgeInsets.only(top: Insets(1).md),
                  constraints: BoxConstraints(
                    minHeight: 320,
                  ),
                  child: Center(
                    child: SizedBox(
                      width: Breakpoints.desktop.toDouble(),
                      height: MediaQuery.of(context).size.height - 64 - 200,
                      child: Padding(
                        padding: EdgeInsets.symmetric(
                          horizontal: horizontalPadding(screenWidth),
                        ),
                        child: Column(
                          crossAxisAlignment: isWide
                              ? CrossAxisAlignment.start
                              : CrossAxisAlignment.center,
                          children: [
                            OrganizationsTable(),
                            // TODO: Render organizations here.
                            // return ListItemsBuilder<dynamic>(
                            //   data: data,
                            //   itemBuilder: (context, model) => LicenseRow(model: model),
                            // );
                          ],
                        ),
                      ),
                    ),
                  ),
                );
              },
            ),
          ),

          // Footer
          const SliverToBoxAdapter(child: Footer()),
        ],
      ),
    );
  }
}

/// Organizations table.
class OrganizationsTable extends StatelessWidget {
  const OrganizationsTable({super.key});

  @override
  Widget build(BuildContext context) {
    return DataTable(
      columns: const <DataColumn>[
        DataColumn(
          label: Expanded(
            child: Text(
              'Name',
              style: TextStyle(fontStyle: FontStyle.italic),
            ),
          ),
        ),
        DataColumn(
          label: Expanded(
            child: Text(
              'Age',
              style: TextStyle(fontStyle: FontStyle.italic),
            ),
          ),
        ),
        DataColumn(
          label: Expanded(
            child: Text(
              'Role',
              style: TextStyle(fontStyle: FontStyle.italic),
            ),
          ),
        ),
      ],
      rows: const <DataRow>[
        DataRow(
          cells: <DataCell>[
            DataCell(Text('Sarah')),
            DataCell(Text('19')),
            DataCell(Text('Student')),
          ],
        ),
      ],
    );
  }
}

// /// Class to display facilities.
// class LicenseRowModel {
//   const LicenseRowModel({
//     required this.leadingText,
//     required this.trailingText,
//     this.middleText,
//     this.isHeader = false,
//   });
//   final String leadingText;
//   final String trailingText;
//   final String? middleText;
//   final bool isHeader;
// }

// /// A license tile.
// class LicenseRow extends StatelessWidget {
//   const LicenseRow({super.key, required this.model});
//   final LicenseRowModel model;

//   @override
//   Widget build(BuildContext context) {
//     const fontSize = 16.0;
//     return Container(
//       color: model.isHeader ? Colors.indigo[100] : null,
//       padding: const EdgeInsets.symmetric(vertical: 8.0, horizontal: 16.0),
//       child: Row(
//         children: <Widget>[
//           // Title.
//           Text(
//             model.leadingText,
//             style: const TextStyle(fontSize: fontSize),
//           ),
//           Expanded(child: Container()),

//           // Description.
//           if (model.middleText != null)
//             Text(
//               model.middleText!,
//               style: TextStyle(color: Colors.green[700], fontSize: fontSize),
//               textAlign: TextAlign.right,
//             ),

//           // Actions.
//           SizedBox(
//             width: 60.0,
//             child: Text(
//               model.trailingText,
//               style: const TextStyle(fontSize: fontSize),
//               textAlign: TextAlign.right,
//             ),
//           ),
//         ],
//       ),
//     );
//   }
// }

// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 3/3/2023
// Updated: 3/3/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Flutter imports:
import 'package:cannlytics_app/constants/design.dart';
import 'package:cannlytics_app/models/organization.dart';
import 'package:cannlytics_app/services/theme_service.dart';
import 'package:cannlytics_app/ui/account/organizations/organizations_controller.dart';
import 'package:cannlytics_app/ui/general/app_controller.dart';
import 'package:cannlytics_app/widgets/buttons/primary_button.dart';
import 'package:cannlytics_app/widgets/buttons/secondary_button.dart';
import 'package:flutter/material.dart';

// Package imports:
import 'package:flutter_riverpod/flutter_riverpod.dart';

// Project imports:
import 'package:cannlytics_app/ui/general/footer.dart';
import 'package:cannlytics_app/ui/general/header.dart';
import 'package:cannlytics_app/widgets/lists/list_items_builder.dart';
import 'package:go_router/go_router.dart';

/// Licenses screen.
class OrganizationsScreen extends ConsumerWidget {
  const OrganizationsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
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
                            // Table header.
                            Row(
                              children: [
                                // Title
                                Text(
                                  'Organizations',
                                  style: Theme.of(context)
                                      .textTheme
                                      .titleLarge!
                                      .copyWith(
                                        color: Theme.of(context)
                                            .textTheme
                                            .titleLarge!
                                            .color,
                                      ),
                                ),
                                const Spacer(),

                                // Join an organization button.
                                SecondaryButton(
                                  isDark: isDark,
                                  text:
                                      isWide ? 'Join an organization' : 'Join',
                                  onPressed: () {
                                    context.go('/organizations/join');
                                  },
                                ),

                                // Add organization button.
                                gapW6,
                                PrimaryButton(
                                  text: isWide ? 'New organization' : 'New',
                                  onPressed: () {
                                    context.go('/organizations/new');
                                  },
                                ),
                              ],
                            ),

                            // Organizations table.
                            Row(
                              children: [
                                Expanded(
                                  child: SizedBox(
                                    width: MediaQuery.of(context).size.width,
                                    child: OrganizationsTable(),
                                  ),
                                ),
                              ],
                            ),
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
class OrganizationsTable extends ConsumerWidget {
  const OrganizationsTable({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    // Get the user's organizations.
    // final orgs = ref.watch(organizationsProvider).value ?? [];
    final orgs = [];
    print('ORGANIZATION LICENSES:');
    print(orgs);

    // Return a placeholder if no organizations.
    // TODO: Adjust borders, height, font size, image, margins
    if (orgs.length == 0)
      return Placeholder(
        image: 'assets/images/icons/facilities.png',
        title: 'Add an organization',
        description:
            'Create an organization to manage your licenses and traceability data.',
        onTap: () {
          context.go('/organizations/new');
        },
      );

    // Build the data table.
    return DataTable(
      showCheckboxColumn: false,
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
              'ID',
              style: TextStyle(fontStyle: FontStyle.italic),
            ),
          ),
        ),
        DataColumn(
          label: Expanded(
            child: Text(
              'Owner',
              style: TextStyle(fontStyle: FontStyle.italic),
            ),
          ),
        ),
      ],
      rows: <DataRow>[
        for (Organization org in orgs)
          DataRow(
            onSelectChanged: (bool? selected) {
              if (selected!) {
                context.go('/organizations/${org.id}');
              }
            },
            cells: <DataCell>[
              DataCell(Text(org.name)),
              DataCell(Text(org.id)),
              DataCell(Text(org.owner)),
            ],
          ),
      ],
    );
  }
}

class Placeholder extends StatelessWidget {
  const Placeholder({
    Key? key,
    required this.image,
    required this.title,
    required this.description,
    required this.onTap,
  }) : super(key: key);

  final String image;
  final String title;
  final String description;
  final Function()? onTap;

  @override
  Widget build(BuildContext context) {
    return Card(
      child: InkWell(
        onTap: onTap,
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Image.asset(
              image,
              height: 200,
              fit: BoxFit.cover,
            ),
            Padding(
              padding: const EdgeInsets.all(16.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    title,
                    style: Theme.of(context).textTheme.titleMedium,
                  ),
                  SizedBox(height: 8),
                  Text(
                    description,
                    style: Theme.of(context).textTheme.bodyLarge,
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
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

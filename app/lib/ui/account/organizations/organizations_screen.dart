// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 3/3/2023
// Updated: 3/7/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Flutter imports:
import 'package:flutter/material.dart';

// Package imports:
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

// Project imports:
import 'package:cannlytics_app/constants/design.dart';
import 'package:cannlytics_app/models/common/organization.dart';
import 'package:cannlytics_app/services/theme_service.dart';
import 'package:cannlytics_app/ui/main/app_controller.dart';
import 'package:cannlytics_app/ui/layout/footer.dart';
import 'package:cannlytics_app/ui/layout/header.dart';
import 'package:cannlytics_app/widgets/buttons/primary_button.dart';
import 'package:cannlytics_app/widgets/buttons/secondary_button.dart';
import 'package:cannlytics_app/widgets/layout/custom_placeholder.dart';
import 'package:cannlytics_app/widgets/tables/table_form.dart';

/// Organizations screen.
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

    // Table actions.
    var actions = Row(children: [
      // Join an organization button.
      SecondaryButton(
        isDark: isDark,
        text: isWide ? 'Join an organization' : 'Join',
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
    ]);

    // Render the widget.
    return Scaffold(
      body: CustomScrollView(
        slivers: [
          // App header.
          const SliverToBoxAdapter(child: AppHeader()),

          // Form.
          SliverToBoxAdapter(
            child: TableForm(
              title: 'Organizations',
              table: OrganizationsTable(),
              actions: actions,
            ),
          ),
          // SliverToBoxAdapter(
          //   child: Consumer(
          //     builder: (context, ref, child) {
          //       return Container(
          //         color: Theme.of(context).scaffoldBackgroundColor,
          //         margin: EdgeInsets.only(top: Insets(1).md),
          //         constraints: BoxConstraints(
          //           minHeight: 320,
          //         ),
          //         child: Center(
          //           child: SizedBox(
          //             width: Breakpoints.desktop.toDouble(),
          //             height: MediaQuery.of(context).size.height - 64 - 200,
          //             child: Padding(
          //               padding: EdgeInsets.symmetric(
          //                 horizontal: horizontalPadding(screenWidth),
          //               ),
          //               child: Column(
          //                 crossAxisAlignment: isWide
          //                     ? CrossAxisAlignment.start
          //                     : CrossAxisAlignment.center,
          //                 children: [
          //                   // Table header.
          //                   Row(
          //                     children: [
          //                       // Title
          //                       Text(
          //                         'Organizations',
          //                         style: Theme.of(context)
          //                             .textTheme
          //                             .titleLarge!
          //                             .copyWith(
          //                               color: Theme.of(context)
          //                                   .textTheme
          //                                   .titleLarge!
          //                                   .color,
          //                             ),
          //                       ),
          //                       const Spacer(),

          //                       // Join an organization button.
          //                       SecondaryButton(
          //                         isDark: isDark,
          //                         text:
          //                             isWide ? 'Join an organization' : 'Join',
          //                         onPressed: () {
          //                           context.go('/organizations/join');
          //                         },
          //                       ),

          //                       // Add organization button.
          //                       gapW6,
          //                       PrimaryButton(
          //                         text: isWide ? 'New organization' : 'New',
          //                         onPressed: () {
          //                           context.go('/organizations/new');
          //                         },
          //                       ),
          //                     ],
          //                   ),

          //                   // Organizations table.
          //                   Row(
          //                     children: [
          //                       Expanded(
          //                         child: SizedBox(
          //                           width: MediaQuery.of(context).size.width,
          //                           child: OrganizationsTable(),
          //                         ),
          //                       ),
          //                     ],
          //                   ),
          //                 ],
          //               ),
          //             ),
          //           ),
          //         ),
          //       );
          //     },
          //   ),
          // ),

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
    final orgs = ref.watch(organizationsProvider).value ?? [];
    print('ORGANIZATIONS in [OrganizationsTable] widget:');
    print(orgs);

    // Return a placeholder if no organizations.
    if (orgs.length == 0)
      return CustomPlaceholder(
        image: 'assets/images/icons/facilities.png',
        title: 'Add an organization',
        description:
            'Create an organization to manage your licenses and traceability data.',
        onTap: () {
          context.go('/organizations/new');
        },
      );

    // Table headers.
    List<DataColumn> tableHeader = const <DataColumn>[
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
    ];

    // Table rows.
    List<DataRow> tableRows = <DataRow>[
      for (Organization org in orgs)
        DataRow(
          onSelectChanged: (bool? selected) {
            if (selected!) {
              context.go('/organizations/${org.id}');
            }
          },
          cells: <DataCell>[
            DataCell(Text(org.name ?? '')),
            DataCell(Text(org.id)),
            DataCell(Text(org.owner ?? '')),
          ],
        ),
    ];

    // Build the data table.
    return DataTable(
      showCheckboxColumn: false,
      columns: tableHeader,
      rows: tableRows,
    );
  }
}

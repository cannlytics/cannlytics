// Cannlytics Data
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 2/18/2023
// Updated: 4/10/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Flutter imports:
// import 'package:cannlytics_data/widgets/layout/main_screen.dart';

// Flutter imports:
import 'package:cannlytics_data/widgets/cards/fields_card.dart';
import 'package:cannlytics_data/widgets/cards/recent_files_card.dart';
import 'package:cannlytics_data/widgets/cards/storage_details_card.dart';
import 'package:cannlytics_data/widgets/layout/dashboard_header.dart';
import 'package:flutter/material.dart';

// Package imports:
import 'package:flutter_riverpod/flutter_riverpod.dart';

// Project imports:
import 'package:cannlytics_data/constants/design.dart';
import 'package:cannlytics_data/ui/layout/footer.dart';
import 'package:cannlytics_data/ui/layout/header.dart';
import 'package:cannlytics_data/ui/main/dashboard_controller.dart';
import 'package:cannlytics_data/widgets/layout/sidebar.dart';

/// Dashboard screen.
/// The initial screen the user sees after signing in.
// class DashboardScreen extends ConsumerWidget {
//   const DashboardScreen({super.key});

//   @override
//   Widget build(BuildContext context, WidgetRef ref) {
//     // Provider data and dynamic width.
//     final userType = ref.watch(userTypeProvider);
//     final screenWidth = MediaQuery.of(context).size.width;

//     // Body.
//     return MainScreen(
//       slivers: [
//         // App header.
//         // const SliverToBoxAdapter(child: AppHeader()),

//         // TODO: Dashboard.
//         SliverToBoxAdapter(child: Text('DATA HERE!!!')),

//         // Footer
//         const SliverToBoxAdapter(child: Footer()),
//       ],
//     );
//   }
// }
class DashboardScreen extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return SafeArea(
      child: SingleChildScrollView(
        primary: false,
        padding: EdgeInsets.all(Defaults.defaultPadding),
        child: Column(
          children: [
            DashboardHeader(),
            SizedBox(height: Defaults.defaultPadding),
            Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Expanded(
                  flex: 5,
                  child: Column(
                    children: [
                      MyFiles(),
                      SizedBox(height: Defaults.defaultPadding),
                      RecentFiles(),
                      if (Responsive.isMobile(context))
                        SizedBox(height: Defaults.defaultPadding),
                      if (Responsive.isMobile(context)) StarageDetails(),
                    ],
                  ),
                ),
                if (!Responsive.isMobile(context))
                  SizedBox(width: Defaults.defaultPadding),
                // On Mobile means if the screen is less than 850 we dont want to show it
                if (!Responsive.isMobile(context))
                  Expanded(
                    flex: 2,
                    child: StarageDetails(),
                  ),
              ],
            )
          ],
        ),
      ),
    );
  }
}

/// Main screen.
class MainScreen extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      // key: context.read<MenuAppController>().scaffoldKey,
      drawer: SideMenu(),
      body: SafeArea(
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // We want this side menu only for large screen
            // if (Responsive.isDesktop(context))
            // Expanded(child: SideMenu()),
            Expanded(
              flex: 5,
              child: DashboardScreen(),
            ),
          ],
        ),
      ),
    );
  }
}

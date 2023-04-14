// Cannlytics Data
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 2/18/2023
// Updated: 4/13/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Flutter imports:
// import 'package:cannlytics_data/widgets/layout/main_screen.dart';

// Flutter imports:
import 'dart:async';

import 'package:cannlytics_data/services/auth_service.dart';
import 'package:cannlytics_data/widgets/buttons/custom_text_button.dart';
import 'package:cannlytics_data/widgets/cards/fields_card.dart';
import 'package:cannlytics_data/widgets/cards/recent_files_card.dart';
import 'package:cannlytics_data/widgets/cards/storage_details_card.dart';
import 'package:cannlytics_data/widgets/images/avatar.dart';
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

GlobalKey<ScaffoldState> _scaffoldKey = new GlobalKey();

/// Dashboard screen.
class DashboardScreen extends ConsumerWidget {
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    // Listen to the current user.
    final user = ref.watch(authProvider).currentUser;
    print('CURRENT USER: $user');

    // Dashboard widget.
    var dashboard = SafeArea(
      child: SingleChildScrollView(
        primary: false,
        padding: EdgeInsets.all(Defaults.defaultPadding),
        child: Column(
          children: [
            // Header.
            // DashboardHeader(),
            // SizedBox(height: Defaults.defaultPadding),

            // Body.
            Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Sidebar.
                // CollapsibleSidebar(),

                // Components.
                // Expanded(
                //   flex: 5,
                //   child: Column(
                //     children: [
                //       // Files.
                //       // MyFiles(),
                //       SizedBox(height: Defaults.defaultPadding),

                //       // Recent files.
                //       // RecentFiles(),
                //       if (Responsive.isMobile(context))
                //         SizedBox(height: Defaults.defaultPadding),

                //       // Storage details for mobile.
                //       // if (Responsive.isMobile(context)) StarageDetails(),
                //     ],
                //   ),
                // ),

                // Storage details for desktop
                // if (!Responsive.isMobile(context))
                //   SizedBox(width: Defaults.defaultPadding),
                // if (!Responsive.isMobile(context))
                //   Expanded(
                //     flex: 2,
                //     child: StarageDetails(),
                //   ),
              ],
            )
          ],
        ),
      ),
    );
    return Scaffold(
      key: _scaffoldKey,
      appBar: AppBar(
        // automaticallyImplyLeading: false,
        // leading: IconButton(
        //     onPressed: () {
        //       _scaffoldKey.currentState?.openDrawer();
        //     },
        //     icon: Icon(
        //       Icons.menu,
        //     )),
        title: Text(
          'Dashboard',
          style: Theme.of(context).textTheme.titleMedium,
        ),
        actions: [
          if (user == null)
            CustomTextButton(
              text: 'Sign Up',
              onPressed: () {},
            ),
          if (user != null)
            Avatar(
              photoUrl: user!.photoURL ?? 'https://robohash.org/${user.uid}',
              radius: 30,
              borderColor: Theme.of(context).secondaryHeaderColor,
              borderWidth: 1.0,
            ),
          SizedBox(width: 8),
        ],
      ),
      drawer: SideMenu(),
      // drawerEnableOpenDragGesture: false,
      body: dashboard,
    );
  }
}

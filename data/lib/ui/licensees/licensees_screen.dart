// Cannlytics Data
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 4/15/2023
// Updated: 5/9/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Flutter imports:
import 'package:cannlytics_data/common/buttons/secondary_button.dart';
import 'package:cannlytics_data/common/layout/breadcrumbs.dart';
import 'package:cannlytics_data/common/layout/footer.dart';
import 'package:cannlytics_data/common/layout/console.dart';
import 'package:cannlytics_data/services/data_service.dart';
import 'package:cannlytics_data/ui/licensees/usa_map.dart';
import 'package:flutter/gestures.dart';
import 'package:flutter/material.dart';

// Project imports:
import 'package:cannlytics_data/constants/design.dart';
import 'package:cannlytics_data/common/layout/header.dart';
import 'package:cannlytics_data/common/layout/sidebar.dart';
import 'package:go_router/go_router.dart';
import 'package:url_launcher/url_launcher.dart';

/// Screen.
class LicenseesScreen extends StatelessWidget {
  const LicenseesScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      // App bar.
      appBar: DashboardHeader(),

      // Side menu.
      drawer: Responsive.isMobile(context) ? MobileDrawer() : null,

      // Body.
      body: Console(slivers: [
        // Title.
        SliverToBoxAdapter(child: _title(context)),

        // Optional: Toggle between map and master list.

        // Map.
        SliverToBoxAdapter(
          child: Padding(
            padding: EdgeInsets.symmetric(horizontal: 16),
            child: SizedBox(
              height: 540, // Specify the height for the Container
              child: InteractiveMap(),
            ),
          ),
        ),

        // Footnotes.
        SliverToBoxAdapter(child: _footnotes(context)),

        // Footer.
        const SliverToBoxAdapter(child: Footer()),
      ]),
    );
  }

  /// Map title.
  Widget _title(BuildContext context) {
    return Padding(
      padding: EdgeInsets.only(
        top: 24,
        left: 16,
        right: 16,
        bottom: 8,
      ),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Breadcrumbs(
            items: [
              BreadcrumbItem(
                  title: 'Data',
                  onTap: () {
                    context.push('/');
                  }),
              BreadcrumbItem(
                title: 'Licenses',
              ),
            ],
          ),
          SecondaryButton(
            text: 'Download all licenses',
            onPressed: () {
              // FIXME: Require the user to be signed in.
              String url =
                  'https://firebasestorage.googleapis.com/v0/b/cannlytics.appspot.com/o/public%2Fdata%2Flicenses%2Fall%2Flicenses-2022-10-08T14-03-08.csv?alt=media&token=4d9c2350-a901-4846-9a1e-574720ec70d3';
              DataService.openInANewTab(url);
            },
          ),
        ],
      ),
    );
  }

  /// Map footnotes.
  Widget _footnotes(BuildContext context) {
    return Padding(
      padding: EdgeInsets.only(
        top: 12,
        left: 16,
        right: 16,
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          RichText(
            text: TextSpan(
              children: [
                TextSpan(
                  text: 'Map credits: ',
                  style: Theme.of(context).textTheme.titleSmall,
                ),
                _hyperlink(context, 'MapSVG', 'https://mapsvg.com/maps'),
                TextSpan(
                  text: ', ',
                  style: Theme.of(context).textTheme.titleSmall,
                ),
                _hyperlink(context, 'Jamesy0627144',
                    'https://commons.wikimedia.org/wiki/File:Medical_cannabis_%2B_CBD_United_States_map_2.svg'),
              ],
            ),
          ),
          gapH4,
          RichText(
            text: TextSpan(
              children: [
                TextSpan(
                  text: 'Map licenses: ',
                  style: Theme.of(context).textTheme.titleSmall,
                ),
                _hyperlink(
                  context,
                  'CC-BY 4.0',
                  'https://creativecommons.org/licenses/by/4.0/',
                ),
                TextSpan(
                  text: ', ',
                  style: Theme.of(context).textTheme.titleSmall,
                ),
                _hyperlink(
                  context,
                  'CC BY-SA 3.0',
                  'https://creativecommons.org/licenses/by-sa/3.0/',
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  /// Hyperlink.
  TextSpan _hyperlink(BuildContext context, String text, String url) {
    return TextSpan(
      text: text,
      style: Theme.of(context).textTheme.titleSmall!.copyWith(
            color: Colors.blue,
          ),
      recognizer: TapGestureRecognizer()
        ..onTap = () async {
          await launchUrl(Uri.parse(url));
        },
    );
  }
}

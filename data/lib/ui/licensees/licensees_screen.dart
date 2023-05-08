// Cannlytics Data
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 4/15/2023
// Updated: 5/7/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Flutter imports:
import 'package:cannlytics_data/common/layout/footer.dart';
import 'package:cannlytics_data/common/layout/console.dart';
import 'package:cannlytics_data/ui/licensees/usa_map.dart';
import 'package:flutter/gestures.dart';
import 'package:flutter/material.dart';

// Project imports:
import 'package:cannlytics_data/constants/design.dart';
import 'package:cannlytics_data/common/layout/header.dart';
import 'package:cannlytics_data/common/layout/sidebar.dart';
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

        // TODO: Ability to download all licensees.

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
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Licenses by State',
            style: Theme.of(context).textTheme.titleLarge,
          ),
          SizedBox(
            height: 8,
          ),
        ],
      ),
    );
  }

  /// Map footnotes.
  Widget _footnotes(BuildContext context) {
    return Padding(
      padding: EdgeInsets.only(
        top: 24,
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
                  text: 'Map Credit: ',
                  style: Theme.of(context).textTheme.titleSmall,
                ),
                _hyperlink(context, 'MapSVG', 'https://mapsvg.com/maps'),
              ],
            ),
          ),
          RichText(
            text: TextSpan(
              children: [
                TextSpan(
                  text: 'Map License:',
                  style: Theme.of(context).textTheme.titleSmall,
                ),
                _hyperlink(
                  context,
                  'CC-BY 4.0',
                  'https://creativecommons.org/licenses/by/4.0/',
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

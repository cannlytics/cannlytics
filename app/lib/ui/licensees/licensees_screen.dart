// Cannlytics Data
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 4/15/2023
// Updated: 7/3/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Flutter imports:
import 'package:flutter/gestures.dart';
import 'package:flutter/material.dart';

// Package imports:
import 'package:firebase_auth/firebase_auth.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';
import 'package:url_launcher/url_launcher.dart';

// Project imports:
import 'package:cannlytics_data/common/buttons/secondary_button.dart';
import 'package:cannlytics_data/common/cards/card_grid.dart';
import 'package:cannlytics_data/common/cards/stats_model_card.dart';
import 'package:cannlytics_data/common/dialogs/auth_dialog.dart';
import 'package:cannlytics_data/common/layout/breadcrumbs.dart';
import 'package:cannlytics_data/constants/design.dart';
import 'package:cannlytics_data/services/data_service.dart';
import 'package:cannlytics_data/services/storage_service.dart';
import 'package:cannlytics_data/ui/account/account_controller.dart';
import 'package:cannlytics_data/ui/dashboard/dashboard_controller.dart';
import 'package:cannlytics_data/ui/layout/console.dart';
import 'package:cannlytics_data/ui/licensees/usa_map.dart';

/// Screen.
class LicenseesScreen extends ConsumerWidget {
  const LicenseesScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    // Listen to the current user.
    final user = ref.watch(userProvider).value;
    final screenWidth = MediaQuery.of(context).size.width;
    return ConsoleScreen(
      children: [
        // Title.
        SliverToBoxAdapter(child: _title(context, user)),

        // Optional: Toggle between map and master list.

        // DEV: Under development message.
        SliverToBoxAdapter(
          child: Container(
            margin: EdgeInsets.symmetric(horizontal: 16, vertical: 8),
            padding: EdgeInsets.all(8.0),
            color: Colors.yellow[100],
            child: Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: <Widget>[
                Icon(
                  Icons.warning,
                  color: Colors.orange,
                ),
                SizedBox(width: 8.0),
                Flexible(
                  child: Text(
                    'Under development, please stay tuned for this data to be updated.',
                    style: TextStyle(
                      color: Colors.orange[800],
                    ),
                  ),
                ),
              ],
            ),
          ),
        ),

        // Map.
        SliverToBoxAdapter(
          child: Padding(
            padding: EdgeInsets.symmetric(horizontal: 16),
            child: SizedBox(
              height: screenWidth < Breakpoints.tablet ? 420 : 540,
              child: InteractiveMap(),
            ),
          ),
        ),

        // Footnotes.
        SliverToBoxAdapter(child: _footnotes(context)),

        // License datasets.
        _datasetsCards(context, ref),
      ],
    );
  }

  /// Map title.
  Widget _title(BuildContext context, User? user) {
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
          // Breadcrumbs.
          BreadcrumbsRow(
            items: [
              {'label': 'Data', 'path': '/'},
              {'label': 'Licenses', 'path': null},
            ],
          ),

          // Download Button.
          SecondaryButton(
            text: 'Download all licenses',
            onPressed: () async {
              // Note: Requires the user to be signed in.
              if (user == null) {
                showDialog(
                  context: context,
                  builder: (BuildContext context) {
                    return SignInDialog(isSignUp: false);
                  },
                );
                return;
              }
              // Get URL for file in Firebase Storage.
              String? url = await StorageService.getDownloadUrl(
                  'data/licenses/all/licenses-2022-10-08T14-03-08.csv');
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

  /// Dataset cards.
  Widget _datasetsCards(BuildContext context, WidgetRef ref) {
    final mainDatasets = ref.watch(datasetsProvider).value ?? [];
    var datasets = mainDatasets
        .where((element) => element?['type'] == 'licenses')
        .toList();
    final screenWidth = MediaQuery.of(context).size.width;
    final user = ref.watch(userProvider).value;
    return SliverToBoxAdapter(
      child: Padding(
        padding: EdgeInsets.symmetric(
          vertical: 32,
          horizontal: 24,
        ),
        child: Column(children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.start,
            children: [
              Text('Company Datasets',
                  style: Theme.of(context).textTheme.labelLarge!.copyWith(
                      color: Theme.of(context).textTheme.titleLarge!.color)),
            ],
          ),
          gapH12,
          CardGridView(
            crossAxisCount: screenWidth < Breakpoints.desktop ? 1 : 2,
            childAspectRatio: 3,
            items: datasets.map((model) {
              return DatasetCard(
                imageUrl: model?['image_url'],
                title: model?['title'],
                description: model?['description'],
                tier: model?['tier'],
                rows: NumberFormat('#,###').format(model?['observations']) +
                    ' rows',
                columns:
                    NumberFormat('#,###').format(model?['fields']) + ' columns',
                onTap: () async {
                  // Note: Requires the user to be signed in.
                  if (user == null) {
                    showDialog(
                      context: context,
                      builder: (BuildContext context) {
                        return SignInDialog(isSignUp: false);
                      },
                    );
                    return;
                  }
                  // Get URL for file in Firebase Storage.
                  String? url =
                      await StorageService.getDownloadUrl(model?['file_ref']);
                  DataService.openInANewTab(url);
                },
              );
            }).toList(),
          ),
        ]),
      ),
    );
  }
}

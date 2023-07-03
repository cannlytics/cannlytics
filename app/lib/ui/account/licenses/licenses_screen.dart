// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 3/3/2023
// Updated: 3/3/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Flutter imports:
import 'package:flutter/material.dart';

// Package imports:
import 'package:flutter_riverpod/flutter_riverpod.dart';

// Project imports:
import 'package:cannlytics_app/constants/design.dart';
import 'package:cannlytics_app/ui/account/licenses/licenses_controller.dart';
import 'package:cannlytics_app/ui/layout/footer.dart';
import 'package:cannlytics_app/ui/layout/header.dart';

/// Licenses screen.
class LicensesScreen extends ConsumerWidget {
  const LicensesScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    // TODO: Get the user's licenses.
    final data = ref.watch(licensesProvider);
    print('ORGANIZATION LICENSES:');
    print(data);

    // Determine the screen size.
    final screenWidth = MediaQuery.of(context).size.width;
    final isWide = screenWidth > Breakpoints.tablet;

    // Get the theme.
    // final themeMode = ref.watch(themeModeProvider);
    // final bool isDark = themeMode == ThemeMode.dark;

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
                // Render the screen.
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
                            // TODO: Render licenses here.
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

/// Class to display facilities.
class LicenseRowModel {
  const LicenseRowModel({
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

/// A license tile.
class LicenseRow extends StatelessWidget {
  const LicenseRow({super.key, required this.model});
  final LicenseRowModel model;

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

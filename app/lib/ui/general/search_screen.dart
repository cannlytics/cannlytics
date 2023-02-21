// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 2/20/2023
// Updated: 2/20/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>
import 'package:cannlytics_app/routing/menu.dart';
import 'package:cannlytics_app/ui/general/search_controller.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:cannlytics_app/utils/dialogs/alert_dialog_ui.dart';

class SearchScreen extends ConsumerWidget {
  const SearchScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    ref.listen<AsyncValue>(
      searchProvider,
      (_, state) => state.showAlertDialogOnError(context),
    );
    // final state = ref.watch(searchProvider);
    // final user = ref.watch(authServiceProvider).currentUser;
    return const Scaffold(
      body: CustomScrollView(
        slivers: [
          // App header.
          SliverToBoxAdapter(child: AppHeader()),

          // FIXME: Add account management here!
          // Text('What are you searching for?'),
        ],
      ),
    );
  }
}

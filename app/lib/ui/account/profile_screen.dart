// Cannlytics Data
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 7/11/2023
// Updated: 7/11/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Flutter imports:
import 'package:flutter/material.dart';

// Package imports:
import 'package:firebase_ui_firestore/firebase_ui_firestore.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

// Project imports:
import 'package:cannlytics_data/common/cards/wide_card.dart';
import 'package:cannlytics_data/common/images/avatar.dart';
import 'package:cannlytics_data/common/layout/search_placeholder.dart';
import 'package:cannlytics_data/common/tables/log_item.dart';
import 'package:cannlytics_data/constants/design.dart';
import 'package:cannlytics_data/ui/account/account_controller.dart';
import 'package:cannlytics_data/ui/layout/console.dart';

/// User profile screen.
class UserProfileScreen extends StatelessWidget {
  const UserProfileScreen({
    super.key,
    required this.uid,
  });

  // Properties
  final String? uid;

  @override
  Widget build(BuildContext context) {
    return ConsoleScreen(
      children: [
        SliverToBoxAdapter(child: UserProfile(uid: uid)),
      ],
    );
  }
}

/// User profile cards.
class UserProfile extends ConsumerWidget {
  const UserProfile({
    Key? key,
    required this.uid,
  }) : super(key: key);

  // Properties
  final String? uid;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    // Dynamic screen width.
    final screenWidth = MediaQuery.of(context).size.width;

    // Listen to the selected user.
    if (uid == null) return Container();
    final asyncData = ref.watch(userProfileProvider(uid!));

    // Render the widget.
    return asyncData.when(
      loading: () => Center(child: CircularProgressIndicator()),
      error: (error, _) => SelectableText('Error: $error'),
      data: (data) => Padding(
        padding: EdgeInsets.only(
          top: 24,
          left: sliverHorizontalPadding(screenWidth),
          right: sliverHorizontalPadding(screenWidth),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          mainAxisAlignment: MainAxisAlignment.start,
          children: [
            // User information.
            UserProfileForm(
              key: Key('user_form'),
              userData: data ?? {},
            ),

            // User logs.
            UserLogs(uid: uid),
            gapH48,
          ],
        ),
      ),
    );
  }
}

/// Form for the user to view their display name, email, and picture.
class UserProfileForm extends ConsumerStatefulWidget {
  const UserProfileForm({
    Key? key,
    required this.userData,
  }) : super(key: key);

  // Parameters.
  final Map<dynamic, dynamic> userData;

  @override
  ConsumerState<UserProfileForm> createState() => _UserProfileFormState();
}

/// User profile form state.
class _UserProfileFormState extends ConsumerState<UserProfileForm> {
  // Show user's photo.
  Widget _userPhoto(String? url) {
    return Avatar(
      key: Key('user_photo'),
      photoUrl: (url == null || url.isEmpty)
          ? 'https://firebasestorage.googleapis.com/v0/b/cannlytics.appspot.com/o/assets%2Fimages%2Fplaceholders%2Fhomegrower-placeholder.png?alt=media&token=29331691-c2ef-4bc5-89e8-cec58a7913e4'
          : url,
      radius: 60,
      borderColor: Theme.of(context).secondaryHeaderColor,
      borderWidth: 1.0,
    );
  }

  @override
  Widget build(BuildContext context) {
    // Define the form.
    List<Widget> formFields = <Widget>[
      // Title
      Text(
        widget.userData['user_name'] ?? '',
        style: Theme.of(context).textTheme.titleLarge,
      ),
      gapH24,

      // User photo.
      _userPhoto(widget.userData['photo_url']),
      gapH24,
    ];

    // Render the form.
    return WideCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: formFields,
      ),
    );
  }
}

/// User logs.
class UserLogs extends ConsumerWidget {
  UserLogs({
    Key? key,
    required this.uid,
  }) : super(key: key);

  // Properties
  final String? uid;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return SelectionArea(
      child: FirestoreListView<Map<dynamic, dynamic>?>(
        shrinkWrap: true,
        physics: NeverScrollableScrollPhysics(),
        padding: EdgeInsets.only(top: 16, bottom: 48),
        query: ref.watch(userLogsProvider(uid ?? '')),
        pageSize: 20,
        emptyBuilder: (context) => _emptyResults(),
        // _searchTextController.text.isEmpty ? _emptyResults() : _noResults(),
        errorBuilder: (context, error, stackTrace) =>
            _errorPlaceholder(error.toString()),
        loadingBuilder: (context) => _loadingPlaceholder(),
        itemBuilder: (context, doc) {
          final item = doc.data();
          return LogItem(log: item ?? {});
        },
      ),
    );
  }

  /// No results found placeholder.
  Widget _emptyResults() {
    return SearchPlaceholder(
      title: 'No edits.',
      subtitle: 'This user has not made any edits.',
      imageUrl:
          'https://firebasestorage.googleapis.com/v0/b/cannlytics.appspot.com/o/assets%2Fimages%2Flogos%2Fskunkfx_icon.png?alt=media&token=f508470f-5875-4833-b4cd-dc8f633c74b7',
    );
  }

  /// Error placeholder.
  Widget _errorPlaceholder(String error) {
    return SearchPlaceholder(
      title: 'Uh-oh! Something went wrong.',
      subtitle:
          "My apologies, there seems to be an error: $error. Please contact dev@cannlytics.com to get a person on this ASAP.",
      imageUrl:
          'https://firebasestorage.googleapis.com/v0/b/cannlytics.appspot.com/o/assets%2Fimages%2Flogos%2Fskunkfx_icon.png?alt=media&token=f508470f-5875-4833-b4cd-dc8f633c74b7',
    );
  }

  /// Loading results placeholder.
  Widget _loadingPlaceholder() {
    return Padding(
      padding: EdgeInsets.all(16),
      child: Center(
        child: CircularProgressIndicator(strokeWidth: 1.42),
      ),
    );
  }
}

// Cannlytics Data
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 7/2/2023
// Updated: 7/3/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Flutter imports:
import 'package:flutter/material.dart';

// Package imports:
import 'package:firebase_ui_firestore/firebase_ui_firestore.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

// Project imports:
import 'package:cannlytics_data/common/layout/search_placeholder.dart';
import 'package:cannlytics_data/common/tables/log_item.dart';
import 'package:cannlytics_data/ui/results/results_service.dart';

/// Result edit history.
class ResultLogs extends ConsumerWidget {
  ResultLogs({
    Key? key,
    required this.labResultId,
  }) : super(key: key);

  // Properties
  final String labResultId;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return SelectionArea(
      child: FirestoreListView<Map<dynamic, dynamic>?>(
        shrinkWrap: true,
        physics: NeverScrollableScrollPhysics(),
        padding: EdgeInsets.only(top: 16, bottom: 48),
        query: ref.watch(resultLogs(labResultId)),
        pageSize: 20,
        emptyBuilder: (context) => _emptyResults(),
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
      title: 'No edits have been made to this result.',
      subtitle: 'You can update the result data if you are authenticated.',
      imageUrl:
          'https://firebasestorage.googleapis.com/v0/b/cannlytics.appspot.com/o/public%2Fimages%2Flogos%2Fcannlytics_coa_doc.png?alt=media&token=1871dde9-82db-4342-a29d-d373671491b3',
    );
  }

  /// Error placeholder.
  Widget _errorPlaceholder(String error) {
    return SearchPlaceholder(
      title: 'Uh-oh! Something went wrong.',
      subtitle:
          "My apologies, there seems to be an error: $error. Please contact dev@cannlytics.com to get a person on this ASAP.",
      imageUrl:
          'https://firebasestorage.googleapis.com/v0/b/cannlytics.appspot.com/o/public%2Fimages%2Flogos%2Fcannlytics_coa_doc.png?alt=media&token=1871dde9-82db-4342-a29d-d373671491b3',
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

// Cannlytics Data
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 5/23/2023
// Updated: 6/28/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Flutter imports:
import 'package:cannlytics_data/constants/design.dart';
import 'package:cannlytics_data/models/lab_result.dart';
import 'package:cannlytics_data/ui/results/result_list_item.dart';
import 'package:firebase_ui_firestore/firebase_ui_firestore.dart';
import 'package:flutter/material.dart';

// Package imports:
import 'package:hooks_riverpod/hooks_riverpod.dart';

// Project imports:
import 'package:cannlytics_data/ui/results/results_search_controller.dart';

/// Lab results search form.
class LabResultsSearchForm extends HookConsumerWidget {
  LabResultsSearchForm({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    // Listen to the data.
    final asyncData = ref.watch(asyncLabResultsProvider);
    final prodSearchList = asyncData.value ?? [];

    // Search text controller.
    final _searchTextController = ref.read(resultsSearchController);
    final FocusNode _node = FocusNode();

    // Search on enter.
    void _onSubmitted(String value) {
      // ref.watch(asyncLabResultsProvider.notifier).searchLabResults(value);
      ref.read(searchTermProvider.notifier).update((state) => value);
      ref.read(keywordsQuery.notifier).update((state) => state);
    }

    /// Loading results placeholder.
    Widget _loadingResults() {
      return Padding(
        padding: EdgeInsets.all(16),
        child: Center(
          child: CircularProgressIndicator(strokeWidth: 1.42),
        ),
      );
    }

    /// No samples found placeholder.
    Widget _emptyResults() {
      return ResultsSearchPlaceholder(
        title: 'Waiting to get your COAs, boss!\n',
        subtitle:
            'You can search by product name keywords, lab ID, or batch number.',
      );
    }

    /// No samples found placeholder.
    Widget _noResults() {
      return ResultsSearchPlaceholder(
        title: 'No COAs found!\n',
        subtitle:
            "Sorry boss, I couldn't find any results. Please contact dev@cannlytics.com to get a person on this ASAP.",
      );
    }

    /// Results list.
    /// FIXME: Redo as grid of cards?
    /// TODO: Use a Grid / PaginatedDataTable to display the results.
    /// Let the user chose the type of view.
    Widget _resultsList() {
      return SelectionArea(
        child: FirestoreListView<LabResult>(
          shrinkWrap: true,
          physics: NeverScrollableScrollPhysics(),
          padding: EdgeInsets.only(top: 16, bottom: 48),
          query: ref.watch(keywordsQuery),
          pageSize: 20,
          emptyBuilder: (context) => _searchTextController.text.isEmpty
              ? _emptyResults()
              : _noResults(),
          errorBuilder: (context, error, stackTrace) => Text(error.toString()),
          loadingBuilder: (context) => _loadingResults(),
          itemBuilder: (context, doc) {
            final item = doc.data();
            return LabResultItem(labResult: item);
          },
        ),
        // child: ListView.builder(
        //   padding: EdgeInsets.only(top: 16, bottom: 48),
        //   shrinkWrap: true,
        //   physics: NeverScrollableScrollPhysics(),
        //   itemCount: prodSearchList.length,
        //   itemBuilder: (context, i) {
        //     if (_searchTextController.text.isNotEmpty) {
        //       return LabResultItem(labResult: prodSearchList[i]);
        //     } else {
        //       return null;
        //     }
        //   },
        // ),
      );
    }

    /// Search results list.
    Widget _buildSearchResults(BuildContext context) {
      return _resultsList();
      // return asyncData.isLoading
      //     ? _loadingResults()
      //     : (_searchTextController.text.isEmpty && prodSearchList.isEmpty)
      //         ? _emptyResults()
      //         : _searchTextController.text.isNotEmpty && prodSearchList.isEmpty
      //             ? _noResults()
      //             : _resultsList();
    }

    /// Search icon.
    Widget _searchIcon() {
      return asyncData.isLoading
          ? Icon(
              Icons.hourglass_full,
              color: Theme.of(context).textTheme.labelMedium!.color,
            )
          : InkWell(
              onTap: () {
                String value = _searchTextController.text;
                print('Searching for value: $value');
                // ref
                //     .watch(asyncLabResultsProvider.notifier)
                //     .searchLabResults(value);
                ref.read(searchTermProvider.notifier).update((state) => value);
                ref.read(keywordsQuery.notifier).update((state) => state);
              },
              child: Icon(
                Icons.send,
                color: Theme.of(context).textTheme.labelMedium!.color,
              ),
            );
    }

    /// Clear icon.
    Widget? _clearIcon() {
      return _searchTextController.text.isNotEmpty
          ? IconButton(
              onPressed: () {
                // ref.watch(asyncLabResultsProvider.notifier).clearLabResults();
                _searchTextController.clear();
                ref.read(searchTermProvider.notifier).update((state) => '');
                ref.read(keywordsQuery.notifier).update((state) => state);
              },
              icon: Icon(
                Icons.close,
                color: Theme.of(context).textTheme.labelMedium!.color,
              ),
            )
          : null;
    }

    /// Search results text field.
    Widget _buildSearchTextField(BuildContext context) {
      return TextField(
        controller: _searchTextController,
        autocorrect: false,
        focusNode: _node,
        decoration: InputDecoration(
          filled: true,
          fillColor: Theme.of(context).cardColor,
          contentPadding: EdgeInsets.only(
            top: 18,
            left: 8,
            right: 8,
            bottom: 8,
          ),

          // Placeholder text.
          labelText: 'Search',
          labelStyle: TextStyle(
            color: Theme.of(context).textTheme.labelMedium!.color,
          ),

          // Search icon.
          suffixIcon: _searchIcon(),

          // Clear search text icon.
          prefixIcon: _clearIcon(),
        ),

        // Action.
        onSubmitted: _onSubmitted,
      );
    }

    // Main section.
    return SingleChildScrollView(
      child: Column(
        children: [
          // Results list, centered when there are no results, top-aligned otherwise.
          Container(
            height: MediaQuery.of(context).size.height * 0.6,
            child: _searchTextController.text.isNotEmpty &&
                    prodSearchList.isNotEmpty
                ? SingleChildScrollView(
                    child: Column(
                      children: [
                        _buildSearchResults(context),
                      ],
                    ),
                  )
                : Center(
                    child: SingleChildScrollView(
                      child: Column(
                        children: [
                          _buildSearchResults(context),
                        ],
                      ),
                    ),
                  ),
          ),

          // Search field.
          Container(
            height: MediaQuery.of(context).size.height * 0.1,
            padding: EdgeInsets.only(top: 16, left: 24, right: 24),
            child: _buildSearchTextField(context),
          ),

          // Disclaimer.
          gapH8,
          ModelInformationWidget(),
        ],
      ),
    );
  }
}

/// Sample results placeholder.
class ResultsSearchPlaceholder extends StatelessWidget {
  final String title;
  final String subtitle;

  ResultsSearchPlaceholder({required this.title, required this.subtitle});

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          children: [
            // Image.
            Padding(
              padding: EdgeInsets.only(top: 16),
              child: ClipRRect(
                borderRadius: BorderRadius.circular(8),
                child: Image.network(
                  'https://firebasestorage.googleapis.com/v0/b/cannlytics.appspot.com/o/public%2Fimages%2Flogos%2Fcannlytics_coa_doc.png?alt=media&token=1871dde9-82db-4342-a29d-d373671491b3',
                  width: 128,
                  height: 128,
                ),
              ),
            ),
            // Text.
            SelectionArea(
              child: Column(
                children: [
                  Text(
                    title,
                    style: TextStyle(
                      fontSize: 20,
                      color: Theme.of(context).textTheme.titleLarge!.color,
                    ),
                  ),
                  Text(
                    subtitle,
                    style: Theme.of(context).textTheme.bodyMedium,
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}

/// Model information.
class ModelInformationWidget extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Container(
      margin: EdgeInsets.symmetric(horizontal: 24),
      child: Text.rich(
        TextSpan(
          children: [
            TextSpan(
              text: 'This is a test release. ',
              style: Theme.of(context).textTheme.bodySmall!.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
            ),
            TextSpan(
              text:
                  'Please bear in mind that the data is incomplete and not up-to-date. Use at your own discretion.',
            ),
          ],
          style: Theme.of(context).textTheme.bodySmall,
        ),
      ),
    );
  }
}

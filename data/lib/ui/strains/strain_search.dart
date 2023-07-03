// Cannlytics Data
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 6/30/2023
// Updated: 7/3/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Flutter imports:
import 'package:cannlytics_data/constants/design.dart';
import 'package:cannlytics_data/models/strain.dart';
import 'package:cannlytics_data/ui/strains/strains_service.dart';
import 'package:firebase_ui_firestore/firebase_ui_firestore.dart';
import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

// Package imports:
import 'package:hooks_riverpod/hooks_riverpod.dart';

/// Strain search form.
class StrainsSearch extends HookConsumerWidget {
  StrainsSearch({Key? key, this.orderBy}) : super(key: key);

  // Parameters.
  final String? orderBy;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    // Listen to the data.
    // final asyncData = ref.watch(strainsQuery);
    // final prodSearchList = asyncData.value ?? [];

    // Search text controller.
    final _searchTextController = ref.read(strainsSearchController);
    final FocusNode _node = FocusNode();

    // Search on enter.
    void _onSubmitted(String value) {
      ref.read(strainSearchTerm.notifier).update((state) => value);
      // ref.read(strainsQuery.notifier).update((state) => state);
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
        title: 'Get your paws on the latest discovered strains!',
        subtitle: 'You can search by keyword.',
      );
    }

    /// No samples found placeholder.
    Widget _noResults() {
      return ResultsSearchPlaceholder(
        title: 'No strains found!',
        subtitle:
            "Sorry, I couldn't find any strains. Please contact dev@cannlytics.com to get a person on this ASAP.",
      );
    }

    /// Results list.
    Widget _resultsList() {
      return SelectionArea(
        child: FirestoreListView<Strain>(
          shrinkWrap: true,
          physics: NeverScrollableScrollPhysics(),
          padding: EdgeInsets.only(top: 16, bottom: 48),
          query: ref.watch(strainsQuery(orderBy ?? 'updated_at')),
          pageSize: 20,
          emptyBuilder: (context) => _searchTextController.text.isEmpty
              ? _emptyResults()
              : _noResults(),
          errorBuilder: (context, error, stackTrace) => Text(error.toString()),
          loadingBuilder: (context) => _loadingResults(),
          itemBuilder: (context, doc) {
            final item = doc.data();
            return StrainListItem(strain: item);
          },
        ),
      );
    }

    /// Search icon.
    Widget _searchIcon() {
      // return asyncData.isLoading
      //     ? Icon(
      //         Icons.hourglass_full,
      //         color: Theme.of(context).textTheme.labelMedium!.color,
      //       )
      //     :
      return InkWell(
        onTap: () {
          String value = _searchTextController.text;
          print('Searching for value: $value');
          // ref
          //     .watch(asyncLabResultsProvider.notifier)
          //     .searchLabResults(value);
          ref.read(strainSearchTerm.notifier).update((state) => value);
          // ref.read(strainsQuery.notifier).update((state) => state);
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
                ref.read(strainSearchTerm.notifier).update((state) => '');
                // ref.read(strainsQuery.notifier).update((state) => state);
              },
              icon: Icon(
                Icons.close,
                color: Theme.of(context).textTheme.labelMedium!.color,
              ),
            )
          : null;
    }

    /// Search results text field.
    Widget _buildSearchTextField() {
      return TextField(
        controller: _searchTextController,
        autocorrect: false,
        focusNode: _node,
        style: Theme.of(context).textTheme.bodyMedium,
        decoration: InputDecoration(
          contentPadding: EdgeInsets.only(
            top: 18,
            left: 8,
            right: 8,
            bottom: 8,
          ),
          border: OutlineInputBorder(
            borderRadius: BorderRadius.only(
              topLeft: Radius.circular(3),
              bottomLeft: Radius.circular(3),
              topRight: Radius.zero,
              bottomRight: Radius.zero,
            ),
          ),

          // Placeholder text.
          labelText: 'Search by keywords...',
          labelStyle: Theme.of(context).textTheme.bodyMedium,

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
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Title.
          Padding(
            padding: EdgeInsets.only(left: 16, top: 12),
            child: Text(
              'Search strains',
              style: Theme.of(context).textTheme.titleLarge,
            ),
          ),
          // Search field.
          Container(
            height: MediaQuery.of(context).size.height * 0.1,
            padding: EdgeInsets.only(top: 12, left: 16, right: 24),
            child: _buildSearchTextField(),
          ),

          // TODO: Allow the user to Export All of a query.

          // TODO: Allow the user to apply filters:
          // - product type
          // - state

          // Results list, centered when there are no results, top-aligned otherwise.
          Container(
            height: MediaQuery.of(context).size.height * 0.6,
            child: Center(
              child: SingleChildScrollView(
                child: Column(
                  children: [
                    _resultsList(),
                  ],
                ),
              ),
            ),
            // child: _searchTextController.text.isNotEmpty &&
            //         prodSearchList.isNotEmpty
            //     ? SingleChildScrollView(
            //         child: Column(
            //           children: [
            //             _resultsList(),
            //           ],
            //         ),
            //       )
            //     : Center(
            //         child: SingleChildScrollView(
            //           child: Column(
            //             children: [
            //               _resultsList(),
            //             ],
            //           ),
            //         ),
            //       ),
          ),

          // Disclaimer.
          // gapH8,
          // ModelInformationWidget(),
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
                    style: Theme.of(context).textTheme.titleLarge,
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

/// A strain list item.
class StrainListItem extends StatelessWidget {
  StrainListItem({required this.strain});

  // Properties
  final Strain strain;

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: EdgeInsets.symmetric(horizontal: 24),
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(3)),
      color: Theme.of(context).scaffoldBackgroundColor,
      child: InkWell(
        onTap: () {
          context.go('/strains/${strain.id}/');
        },
        child: Container(
          margin: EdgeInsets.all(0),
          padding: EdgeInsets.all(16.0),
          decoration: BoxDecoration(borderRadius: BorderRadius.circular(3.0)),
          child: Row(
            children: [
              // Strain image.
              if (strain.imageUrl != null)
                Padding(
                  padding: EdgeInsets.only(right: 16.0),
                  child: Image.network(
                    strain.imageUrl!,
                    width: 64,
                    height: 64,
                  ),
                ),

              // Strain details.
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    // Strain name.
                    Text(
                      strain.name,
                      style: Theme.of(context).textTheme.labelLarge,
                    ),
                    gapH8,

                    // Strain ID.
                    Text(
                      'ID: ${strain.id}',
                      style: Theme.of(context).textTheme.labelMedium,
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

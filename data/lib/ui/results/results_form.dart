// Cannlytics Data
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 5/23/2023
// Updated: 5/23/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Flutter imports:
import 'package:cannlytics_data/models/lab_result.dart';
import 'package:cannlytics_data/ui/results/results_form_controller.dart';
import 'package:flutter/material.dart';

// Package imports:
import 'package:hooks_riverpod/hooks_riverpod.dart';

// Project imports:
import 'package:url_launcher/url_launcher.dart';

/// Lab results search form.
class LabResultsSearchForm extends HookConsumerWidget {
  LabResultsSearchForm({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    // Listen to data.
    final asyncData = ref.watch(asyncLabResultsProvider);
    final prodSearchList = asyncData.value ?? [];

    // Search text controller.
    final _searchTextController = ref.read(resultsSearchController);
    final FocusNode _node = FocusNode();

    // Search on enter.
    void _onSubmitted(String value) {
      ref.watch(asyncLabResultsProvider.notifier).searchLabResults(value);
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
      return UserResultsPlaceholder(
        title: 'Waiting to get your COAs boss!\n',
        subtitle:
            'You can search by product name keywords, lab ID, or batch number.',
      );
    }

    /// No samples found placeholder.
    Widget _noResults() {
      return UserResultsPlaceholder(
        title: 'No COAs found!\n',
        subtitle:
            "Sorry boss, I couldn't find any results. Please contact dev@cannlytics.com to get a person on this ASAP.",
      );
    }

    /// Results list.
    Widget _resultsList() {
      return ListView.builder(
        shrinkWrap: true,
        physics: NeverScrollableScrollPhysics(),
        itemCount: prodSearchList.length,
        itemBuilder: (context, i) {
          if (_searchTextController.text.isNotEmpty) {
            return LabResultItem(labResult: prodSearchList[i]);
          } else {
            return null;
          }
        },
      );
    }

    /// Search results list.
    Widget _buildSearchResults(BuildContext context) {
      return asyncData.isLoading
          ? _loadingResults()
          : (_searchTextController.text.isEmpty && prodSearchList.isEmpty)
              ? _emptyResults()
              : _searchTextController.text.isNotEmpty && prodSearchList.isEmpty
                  ? _noResults()
                  : _resultsList();
    }

    Widget _searchIcon() {
      return asyncData.isLoading
          ? SizedBox(
              height: 16,
              child: CircularProgressIndicator(strokeWidth: 1.42),
            )
          : InkWell(
              onTap: () {
                String value = _searchTextController.text;
                print('Searching for value: $value');
                ref
                    .watch(asyncLabResultsProvider.notifier)
                    .searchLabResults(value);
              },
              child: Icon(
                Icons.send,
                color: Theme.of(context).textTheme.labelMedium!.color,
              ),
            );
    }

    Widget? _clearIcon() {
      return _searchTextController.text.isNotEmpty
          ? IconButton(
              onPressed: () {
                ref.watch(asyncLabResultsProvider.notifier).clearLabResults();
                _searchTextController.clear();
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
          // Results list.
          Container(
            height: MediaQuery.of(context).size.height * 0.75,
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
            height: MediaQuery.of(context).size.height * 0.15,
            padding: EdgeInsets.all(16),
            child: _buildSearchTextField(context),
          ),
        ],
      ),
    );
  }
}

/// A lab result list item.
class LabResultItem extends StatelessWidget {
  final LabResult labResult;

  LabResultItem({required this.labResult});

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: EdgeInsets.zero,
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(3)),
      child: Container(
        margin: EdgeInsets.all(0),
        padding: EdgeInsets.all(16.0),
        decoration: BoxDecoration(borderRadius: BorderRadius.circular(3.0)),

        // Optional: Add image.

        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: <Widget>[
            // Product name.
            SelectableText(
              'Product: ${labResult.productName}',
              style: Theme.of(context).textTheme.labelLarge,
            ),

            // Producer.
            // Future work: Link to producer website.
            SelectableText(
              'Producer: ${labResult.businessDbaName}',
              style: Theme.of(context).textTheme.labelMedium,
            ),

            // Lab.
            Row(
              children: [
                SelectableText(
                  'Lab: ',
                  style: Theme.of(context).textTheme.labelMedium,
                ),
                GestureDetector(
                  onTap: () {
                    launchUrl(Uri.parse(labResult.labWebsite!));
                  },
                  child: SelectableText(
                    labResult.lab!,
                    style: Theme.of(context).textTheme.labelMedium!.copyWith(
                          color: Colors.blue,
                        ),
                  ),
                ),
              ],
            ),

            // IDs
            SelectableText(
              'ID: ${labResult.labId}',
              style: Theme.of(context).textTheme.labelMedium,
            ),
            SelectableText(
              'Batch: ${labResult.batchNumber}',
              style: Theme.of(context).textTheme.labelMedium,
            ),
          ],
        ),
        // FIXME: Link to COA (download_url).

        // TODO: Copy download COA link to clipboard.
      ),
    );
  }
}

/// Sample results placeholder.
class UserResultsPlaceholder extends StatelessWidget {
  final String? title;
  final String? subtitle;

  UserResultsPlaceholder({this.title, this.subtitle});

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
            RichText(
              textAlign: TextAlign.center,
              text: TextSpan(
                style: DefaultTextStyle.of(context).style,
                children: <TextSpan>[
                  TextSpan(
                      text: title ?? 'Waiting on your COAs boss!\n',
                      style: TextStyle(fontSize: 20)),
                  TextSpan(
                      text: subtitle ??
                          'Drop a CoA PDF, image, or folder to parse.',
                      style: Theme.of(context).textTheme.bodyMedium),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}

// Cannlytics Data
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 5/23/2023
// Updated: 5/24/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Flutter imports:
import 'package:flutter/gestures.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

// Package imports:
import 'package:fluttertoast/fluttertoast.dart';
import 'package:hooks_riverpod/hooks_riverpod.dart';
import 'package:url_launcher/url_launcher.dart';

// Project imports:
import 'package:cannlytics_data/constants/design.dart';
import 'package:cannlytics_data/models/lab_result.dart';
import 'package:cannlytics_data/ui/results/results_form_controller.dart';
import 'package:cannlytics_data/utils/utils.dart';

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
        title: 'Waiting to get your COAs, boss!\n',
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
      return SelectionArea(
        child: ListView.builder(
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
        ),
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

    /// Clear icon.
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
          // Results list, centered when there are no results, top-aligned otherwise.
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
            height: MediaQuery.of(context).size.height * 0.1,
            padding: EdgeInsets.only(top: 16, left: 24, right: 24),
            child: _buildSearchTextField(context),
          ),

          // Disclaimer.
          ModelInformationWidget(),
        ],
      ),
    );
  }
}

/// A lab result list item.
/// Optional: Add image.
class LabResultItem extends StatelessWidget {
  final LabResult labResult;

  LabResultItem({required this.labResult});

  @override
  Widget build(BuildContext context) {
    final screenWidth = MediaQuery.of(context).size.width;
    return Card(
      margin: EdgeInsets.symmetric(horizontal: 24),
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(3)),
      color: Theme.of(context).scaffoldBackgroundColor,
      surfaceTintColor: Theme.of(context).scaffoldBackgroundColor,
      child: Container(
        margin: EdgeInsets.all(0),
        padding: EdgeInsets.all(16.0),
        decoration: BoxDecoration(borderRadius: BorderRadius.circular(3.0)),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: <Widget>[
            // Product name and COA link.
            Row(
              children: [
                if (screenWidth <= Breakpoints.tablet)
                  Expanded(
                    child: Text(
                      labResult.productName ?? 'Unknown',
                      style: Theme.of(context).textTheme.labelLarge,
                    ),
                  ),
                if (screenWidth > Breakpoints.tablet)
                  Text(
                    labResult.productName ?? 'Unknown',
                    style: Theme.of(context).textTheme.labelLarge,
                  ),
                GestureDetector(
                  onTap: () {
                    if (labResult.downloadUrl != null) {
                      launchUrl(Uri.parse(labResult.downloadUrl!));
                    }
                  },
                  child: Icon(
                    Icons.open_in_new,
                    color: Theme.of(context).colorScheme.onSurface,
                    size: 16,
                  ),
                ),
              ],
            ),
            gapH8,

            // Producer.
            // Future work: Link to producer website.
            Text(
              'Producer: ${labResult.businessDbaName}',
              style: Theme.of(context).textTheme.labelMedium,
            ),

            // IDs
            Text(
              'ID: ${labResult.labId}',
              style: Theme.of(context).textTheme.labelMedium,
            ),
            Text(
              'Batch: ${labResult.batchNumber}',
              style: Theme.of(context).textTheme.labelMedium,
            ),

            // Lab.
            Row(
              children: [
                Text(
                  'Lab: ',
                  style: Theme.of(context).textTheme.labelMedium,
                ),
                GestureDetector(
                  onTap: () {
                    launchUrl(Uri.parse(labResult.labWebsite!));
                  },
                  child: Text(
                    labResult.lab!,
                    style: Theme.of(context).textTheme.labelMedium!.copyWith(
                          color: Colors.blue,
                        ),
                  ),
                ),
              ],
            ),

            // Copy COA link.
            if (labResult.downloadUrl != null) gapH4,
            if (labResult.downloadUrl != null)
              _coaLink(context, labResult.downloadUrl!),
          ],
        ),
      ),
    );
  }

  /// Copy COA link.
  Widget _coaLink(BuildContext context, String url) {
    return InkWell(
      onTap: () async {
        await Clipboard.setData(ClipboardData(text: url));
        Fluttertoast.showToast(
          msg: 'Copied link!',
          toastLength: Toast.LENGTH_SHORT,
          gravity: ToastGravity.TOP,
          timeInSecForIosWeb: 2,
          backgroundColor: Theme.of(context).dialogBackgroundColor,
          textColor: Theme.of(context).textTheme.titleLarge!.color,
          fontSize: 16.0,
          webBgColor:
              WebUtils.colorToHexCode(Theme.of(context).dialogBackgroundColor),
          webPosition: 'center',
          webShowClose: true,
        );
      },
      child: Padding(
        padding: EdgeInsets.symmetric(vertical: 8, horizontal: 12),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          mainAxisAlignment: MainAxisAlignment.start,
          children: <Widget>[
            Icon(Icons.link, size: 12, color: Colors.blueAccent),
            SizedBox(width: 4),
            Text(
              'Copy COA link',
              style: TextStyle(
                fontSize: 12,
                fontWeight: FontWeight.bold,
                color: Colors.blueAccent,
              ),
            ),
          ],
        ),
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

/// Model information.
class ModelInformationWidget extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Container(
      // constraints: BoxConstraints(maxWidth: 560),
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

/// Text link.
class LinkTextSpan extends TextSpan {
  LinkTextSpan({TextStyle? style, required String text, required String url})
      : super(
          style: style?.copyWith(
            color: Colors.blue,
            decoration: TextDecoration.underline,
          ),
          text: text,
          recognizer: TapGestureRecognizer()
            ..onTap = () => launchUrl(Uri.parse(url)),
        );
}

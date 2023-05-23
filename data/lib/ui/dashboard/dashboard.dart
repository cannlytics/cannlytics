// Cannlytics Data
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 2/18/2023
// Updated: 5/13/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Flutter imports:
import 'package:cannlytics_data/common/buttons/secondary_button.dart';
import 'package:flutter/material.dart';

// Package imports:
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:intl/intl.dart';

// Project imports:
import 'package:cannlytics_data/common/cards/card_grid.dart';
import 'package:cannlytics_data/common/cards/sponsorship_card.dart';
import 'package:cannlytics_data/common/cards/stats_model_card.dart';
import 'package:cannlytics_data/common/layout/console.dart';
import 'package:cannlytics_data/constants/design.dart';
import 'package:cannlytics_data/ui/dashboard/dashboard_controller.dart';

/// Dashboard screen.
class DashboardScreen extends ConsumerWidget {
  const DashboardScreen({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return ConsoleScreen(
      bottomSearch: true,
      children: [
        // Call for contributions.
        _contributions(context),

        // TODO: Quick actions
        // - Search for a lab result / strain / company
        _search(context),
        // SliverToBoxAdapter(child: ResultsSearch(key: Key('results-search'))),
        // - Archive a COA
        // - Archive a receipt

        // AI tools.
        _aiCards(context),

        // Datasets.
        _datasetsCards(context),

        // TODO: Infinitely scrolling logs of activity.
        // - Show CannBot's activity of data collection.
      ],
    );
  }

  /// Call for contributions card.
  Widget _contributions(BuildContext context) {
    final screenWidth = MediaQuery.of(context).size.width;
    return SliverToBoxAdapter(
      child: Padding(
        padding: EdgeInsets.symmetric(
          vertical: 18,
          horizontal: sliverHorizontalPadding(screenWidth) / 2,
        ),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.start,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            SponsorshipCard(),
          ],
        ),
      ),
    );
  }

  /// Quick actions card.
  Widget _search(BuildContext context) {
    final screenWidth = MediaQuery.of(context).size.width;
    return SliverToBoxAdapter(
      child: Padding(
        padding: EdgeInsets.symmetric(
          vertical: 18,
          horizontal: sliverHorizontalPadding(screenWidth) / 2,
        ),
        child: Column(children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.start,
            children: [
              // Title.
              Text('Cannabis Lab Results',
                  style: Theme.of(context).textTheme.labelLarge!.copyWith(
                      color: Theme.of(context).textTheme.titleLarge!.color)),
            ],
          ),
          gapH8,

          // Search card.
          ResultsSearch(key: Key('results-search')),
        ]),
      ),
    );
  }

  /// AI cards.
  Widget _aiCards(BuildContext context) {
    final screenWidth = MediaQuery.of(context).size.width;
    return SliverToBoxAdapter(
      child: Padding(
        padding: EdgeInsets.symmetric(
          vertical: 18,
          horizontal: sliverHorizontalPadding(screenWidth) / 2,
        ),
        child: Column(children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.start,
            children: [
              Text('AI',
                  style: Theme.of(context).textTheme.labelLarge!.copyWith(
                      color: Theme.of(context).textTheme.titleLarge!.color)),
            ],
          ),
          gapH8,
          CardGridView(
            crossAxisCount: screenWidth < Breakpoints.desktop ? 1 : 2,
            childAspectRatio: 3,
            items: aiModels.map((model) {
              return DatasetCard(
                imageUrl: model['image_url'],
                title: model['title'],
                description: model['description'],
                tier: model['tier'],
                onTap: () => context.push(model['path']),
              );
            }).toList(),
          ),
        ]),
      ),
    );
  }

  /// Dataset cards.
  Widget _datasetsCards(BuildContext context) {
    final screenWidth = MediaQuery.of(context).size.width;
    return SliverToBoxAdapter(
      child: Padding(
        padding: EdgeInsets.symmetric(
          vertical: 18,
          horizontal: sliverHorizontalPadding(screenWidth) / 2,
        ),
        child: Column(children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.start,
            children: [
              Text('Data',
                  style: Theme.of(context).textTheme.labelLarge!.copyWith(
                      color: Theme.of(context).textTheme.titleLarge!.color)),
            ],
          ),
          gapH8,
          CardGridView(
            crossAxisCount: screenWidth < Breakpoints.desktop ? 1 : 2,
            childAspectRatio: 3,
            items: mainDatasets.map((model) {
              return DatasetCard(
                imageUrl: model['image_url'],
                title: model['title'],
                description: model['description'],
                tier: model['tier'],
                rows: NumberFormat('#,###').format(model['observations']) +
                    ' rows',
                columns:
                    NumberFormat('#,###').format(model['fields']) + ' columns',
                onTap: () => context.push(model['path']),
              );
            }).toList(),
          ),
        ]),
      ),
    );
  }
}

/// Results search.
class ResultsSearch extends StatefulWidget {
  ResultsSearch({required Key key}) : super(key: key);

  @override
  _ResultsSearchState createState() => _ResultsSearchState();
}

/// Results search state.
class _ResultsSearchState extends State<ResultsSearch> {
  // Properties.
  TextEditingController _searchController = TextEditingController();
  late List<String> _dataList;
  late List<String> _filteredDataList;

  @override
  void initState() {
    super.initState();
    _dataList = [];
    _filteredDataList = [];
    _searchController.addListener(() {
      searchData();
    });
  }

  @override
  void dispose() {
    _searchController.dispose();
    super.dispose();
  }

  /// Search results.
  searchData() {
    String query = _searchController.text;

    // Handle empty search.
    if (query.trim().isEmpty) {
      if (_filteredDataList.length != _dataList.length) {
        setState(() {
          _filteredDataList = _dataList;
        });
      }
      return;
    }

    // FIXME: Implement search.
    // List<String> filtered = _dataList
    //     .where((element) => element.toLowerCase().contains(query.toLowerCase()))
    //     .toList();
    // _dataList = List<String>.generate(100, (index) => "Item $index");
    // _filteredDataList = _dataList;
    List<String> filtered = [];
    setState(() {
      _filteredDataList = filtered;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: EdgeInsets.zero,
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(3)),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Title
          Padding(
            padding: const EdgeInsets.all(16.0),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.end,
              children: [
                Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Search',
                      style: Theme.of(context).textTheme.labelLarge!.copyWith(
                          color: Theme.of(context).textTheme.titleLarge!.color),
                    ),
                    Text(
                      'You can enter a product name, ID, or generally query for lab results.',
                      style: Theme.of(context).textTheme.bodyMedium,
                    ),
                  ],
                ),
                Spacer(),
                SecondaryButton(
                  leading: Icon(Icons.qr_code),
                  text: 'Scan',
                  onPressed: () {},
                ),
                gapW8,
                SecondaryButton(
                  text: 'Upload',
                  onPressed: () {},
                ),
              ],
            ),
          ),
          gapH8,

          // Text field.
          Padding(
            padding: const EdgeInsets.all(16.0),
            child: TextField(
              controller: _searchController,
              autocorrect: false,
              decoration: InputDecoration(
                labelText: 'Search',
                suffixIcon: Icon(Icons.search),
                contentPadding: EdgeInsets.only(
                  top: 18,
                  left: 8,
                  right: 8,
                  bottom: 8,
                ),
              ),
            ),
            // child: TextFormField(
            //   key: Key('results-search'),
            //   controller: _searchController,
            //   style: Theme.of(context).textTheme.titleMedium,
            //   decoration: InputDecoration(
            //     labelText: 'Search',
            //     suffixIcon: Icon(Icons.search),
            //     floatingLabelBehavior: FloatingLabelBehavior.auto,
            //     contentPadding: EdgeInsets.only(
            //       top: 18,
            //       left: 8,
            //       right: 8,
            //       bottom: 8,
            //     ),
            //   ),
            //   autocorrect: false,
            //   textInputAction: TextInputAction.next,
            //   keyboardType: TextInputType.emailAddress,
            //   keyboardAppearance: Brightness.light,
            //   autovalidateMode: AutovalidateMode.onUserInteraction,
            // ),
          ),

          // TODO: Search button.

          // TODO: Search results.
          // watch(firebaseIdeaProvider).when(
          //   loading: () => const Center(child: CircularProgressIndicator()),
          //   error: (err, stack) => Center(child: Text(err.toString())),
          //   data: (ideas) {
          //     return ListView.builder(
          //       itemCount: ideas.length,
          //       itemBuilder: (_, index) {
          //         return ListTile(
          //           title: Text(ideas[index].toString()),
          //         );
          //       },
          //     );
          //   },
          // ),
        ],
      ),
    );
  }
}

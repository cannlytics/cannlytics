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

        // Quick search.
        _search(context),

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
          vertical: 36,
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
          vertical: 36,
          horizontal: sliverHorizontalPadding(screenWidth) / 2,
        ),
        child: Column(children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.start,
            children: [
              // Title.
              Text('Lab Results',
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
          vertical: 36,
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
          vertical: 36,
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
/// - Search for a lab result / strain / company, etc.
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
    final screenWidth = MediaQuery.of(context).size.width;
    return Card(
      margin: EdgeInsets.zero,
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(3)),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Title
          gapH16,
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 16.0),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.start,
              crossAxisAlignment: screenWidth < Breakpoints.tablet
                  ? CrossAxisAlignment.center
                  : CrossAxisAlignment.end,
              children: [
                Container(
                  width: screenWidth < Breakpoints.tablet ? null : 420,
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.start,
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'Search',
                        style: Theme.of(context).textTheme.labelLarge!.copyWith(
                            color:
                                Theme.of(context).textTheme.titleLarge!.color),
                      ),
                      if (screenWidth >= Breakpoints.tablet)
                        Text(
                          'You can enter a product name, ID, or generally query for lab results.',
                          style: Theme.of(context).textTheme.bodyMedium,
                        ),
                    ],
                  ),
                ),
                if (screenWidth < Breakpoints.tablet) gapW4,
                if (screenWidth < Breakpoints.tablet)
                  Tooltip(
                    message:
                        'You can enter a product name, ID, or generally query for lab results.',
                    child: Icon(
                      Icons.info_outline,
                      size: 16,
                      color: Theme.of(context).textTheme.titleLarge!.color,
                    ),
                  ),
                Spacer(),
                SecondaryButton(
                  leading: Icon(
                    Icons.qr_code,
                    size: 16,
                    color: Theme.of(context).textTheme.titleLarge!.color,
                  ),
                  text: 'Scan',
                  onPressed: () {
                    // TODO: Implement.
                  },
                ),
                gapW8,
                SecondaryButton(
                  leading: Icon(
                    Icons.cloud_upload,
                    size: 16,
                    color: Theme.of(context).textTheme.titleLarge!.color,
                  ),
                  text: 'Upload',
                  onPressed: () {
                    // TODO: Implement.
                  },
                ),
              ],
            ),
          ),

          // Text field.
          gapH8,
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 16.0),
            child: TextField(
              controller: _searchController,
              autocorrect: false,
              decoration: InputDecoration(
                labelText: 'Search',
                labelStyle: TextStyle(
                  color: Theme.of(context).textTheme.labelMedium!.color,
                ),
                suffixIcon: InkWell(
                  onTap: () {
                    // Perform action when the suffix icon is clicked
                    print('Suffix icon clicked');
                  },
                  child: Icon(
                    Icons.send,
                    color: Theme.of(context).textTheme.labelMedium!.color,
                  ),
                ),
                contentPadding: EdgeInsets.only(
                  top: 18,
                  left: 8,
                  right: 8,
                  bottom: 8,
                ),
              ),
            ),
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
          // TODO: Open lab results COA.
          // TODO: Download COA.
          // TODO: Open lab's website.
          gapH16,
        ],
      ),
    );
  }
}

class LabResultItem extends StatelessWidget {
  final Map labResult;

  LabResultItem({required this.labResult});

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: EdgeInsets.all(10.0),
      padding: EdgeInsets.all(10.0),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(10.0),
        boxShadow: [
          BoxShadow(
            color: Colors.grey.withOpacity(0.5),
            spreadRadius: 5,
            blurRadius: 7,
            offset: Offset(0, 3),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: <Widget>[
          Text(
            labResult['product_name'],
            style: TextStyle(fontSize: 20.0, fontWeight: FontWeight.bold),
          ),
          Text(
            'Producer: ${labResult['business_dba_name']}',
            style: TextStyle(fontSize: 16.0),
          ),
          // Text(
          //   'Status: ${labResult['status']}',
          //   style: TextStyle(fontSize: 16.0),
          // ),
          // Text(
          //   'Total Cannabinoids: ${labResult['total_cannabinoids']}',
          //   style: TextStyle(fontSize: 16.0),
          // ),
          // Add more fields as needed
        ],
      ),
    );
  }
}

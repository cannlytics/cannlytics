// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 6/15/2023
// Updated: 6/15/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Flutter imports:
import 'package:flutter/material.dart';

class Tabs extends StatelessWidget {
  final List<Tab> tabs;
  final List<Widget> views;

  const Tabs({
    required this.tabs,
    required this.views,
    Key? key,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return DefaultTabController(
      length: tabs.length,
      child: Column(
        children: <Widget>[
          Container(
            decoration: BoxDecoration(
              color: Colors.transparent,
              borderRadius: BorderRadius.circular(3),
              border: Border.all(
                color: Theme.of(context).dividerColor,
                width: 1,
              ),
            ),
            child: TabBar(
              isScrollable: true,
              // unselectedLabelColor:
              //     Theme.of(context).textTheme.titleSmall!.color,
              labelPadding: EdgeInsets.symmetric(horizontal: 0),
              labelColor: Theme.of(context).textTheme.titleLarge!.color,
              unselectedLabelColor:
                  Theme.of(context).textTheme.titleMedium!.color,
              indicatorSize: TabBarIndicatorSize.label,
              indicator: BoxDecoration(
                borderRadius: BorderRadius.circular(3),
                color: Theme.of(context).dividerColor.withOpacity(0.21),
              ),
              tabs: tabs,
            ),
          ),
          Container(
            height: MediaQuery.of(context).size.height * 0.75,
            child: TabBarView(
              children: views,
            ),
          ),
        ],
      ),
    );
  }
}

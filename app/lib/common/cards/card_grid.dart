// Cannlytics Data
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 4/10/2023
// Updated: 5/8/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Flutter imports:
import 'package:flutter/material.dart';

// Project imports:
import 'package:cannlytics_data/constants/design.dart';

/// General cards.
class CardGrid extends StatelessWidget {
  const CardGrid({
    Key? key,
    required this.items,
    this.title,
  }) : super(key: key);

  final List<dynamic> items;
  final String? title;

  @override
  Widget build(BuildContext context) {
    final screenWidth = MediaQuery.of(context).size.width;
    return Column(
      children: [
        // Title.
        SizedBox(height: Defaults.defaultPadding * 0.5),
        if (title != null)
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                title!,
                style: Theme.of(context).textTheme.labelLarge,
              ),
            ],
          ),
        if (title != null) SizedBox(height: Defaults.defaultPadding),

        // Card grid.
        Responsive(
          mobile: CardGridView(
            items: items,
            crossAxisCount: screenWidth < 650 ? 2 : 4,
            childAspectRatio: screenWidth < 650 && screenWidth > 350 ? 1.3 : 1,
          ),
          tablet: CardGridView(
            items: items,
          ),
          desktop: CardGridView(
            items: items,
            childAspectRatio: screenWidth < 1400 ? 1.1 : 1.4,
          ),
        ),

        // Bottom spacing.
        SizedBox(height: Defaults.defaultPadding * 1.5),
      ],
    );
  }
}

/// Grid view of cards to handle dynamic sizes.
class CardGridView extends StatelessWidget {
  const CardGridView({
    Key? key,
    required this.items,
    this.crossAxisCount = 4,
    this.childAspectRatio = 1,
  }) : super(key: key);

  final List<dynamic> items;
  final int crossAxisCount;
  final double childAspectRatio;

  @override
  Widget build(BuildContext context) {
    return GridView.builder(
      physics: NeverScrollableScrollPhysics(),
      shrinkWrap: true,
      itemCount: items.length,
      gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
        crossAxisCount: crossAxisCount,
        crossAxisSpacing: Defaults.defaultPadding,
        mainAxisSpacing: Defaults.defaultPadding,
        childAspectRatio: childAspectRatio,
      ),
      itemBuilder: (context, index) => items[index],
    );
  }
}

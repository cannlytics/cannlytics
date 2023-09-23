// Cannlytics Data
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 6/18/2023
// Updated: 6/24/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Flutter imports:
import 'package:flutter/material.dart';

// Package imports:
import 'package:go_router/go_router.dart';

// Project imports:
import 'package:cannlytics_data/constants/design.dart';
import 'package:cannlytics_data/models/sales_receipt.dart';
import 'package:cannlytics_data/utils/utils.dart';

/// Receipt card.
class ReceiptCard extends StatelessWidget {
  ReceiptCard({
    required this.item,
    this.onDownload,
    this.onDelete,
  });

  // Properties
  final SalesReceipt item;
  final VoidCallback? onDownload;
  final VoidCallback? onDelete;

  @override
  Widget build(BuildContext context) {
    // Screen width.
    final screenWidth = MediaQuery.of(context).size.width;

    // Render
    return GestureDetector(
      onTap: () {},
      child: Card(
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
              // Product name and options.
              Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Receipt image.
                  if (item.downloadUrl != null)
                    Padding(
                      padding: const EdgeInsets.only(bottom: 8.0),
                      child: MouseRegion(
                        cursor: SystemMouseCursors.click,
                        child: GestureDetector(
                          onTap: () => context.go('/sales/${item.hash}'),
                          child: Image.network(
                            item.downloadUrl!,
                            height: (screenWidth < 720) ? 64 : 128,
                          ),
                        ),
                      ),
                    ),
                  Spacer(),

                  // Menu button here:
                  PopupMenuButton<String>(
                    // shadowColor: Colors.transparent,

                    padding: EdgeInsets.all(2),
                    surfaceTintColor: Colors.transparent,
                    onSelected: (String result) {
                      switch (result) {
                        case 'View':
                          context.go('/sales/${item.hash}');
                          break;
                        case 'Download':
                          onDownload!();
                          break;
                        case 'Delete':
                          onDelete!();
                          break;
                      }
                    },
                    itemBuilder: (BuildContext context) =>
                        <PopupMenuEntry<String>>[
                      PopupMenuItem<String>(
                        value: 'View',
                        child: Text(
                          'View',
                          style: Theme.of(context)
                              .textTheme
                              .bodySmall!
                              .copyWith(
                                  color: Theme.of(context)
                                      .textTheme
                                      .bodyLarge!
                                      .color),
                        ),
                      ),
                      PopupMenuItem<String>(
                        value: 'Download',
                        child: Text(
                          'Download',
                          style: Theme.of(context)
                              .textTheme
                              .bodySmall!
                              .copyWith(
                                  color: Theme.of(context)
                                      .textTheme
                                      .bodyLarge!
                                      .color),
                        ),
                      ),
                      PopupMenuItem<String>(
                        value: 'Delete',
                        child: Text(
                          'Delete',
                          style: Theme.of(context)
                              .textTheme
                              .bodySmall!
                              .copyWith(
                                  color: Theme.of(context)
                                      .textTheme
                                      .bodyLarge!
                                      .color),
                        ),
                      ),
                    ],
                  ),
                ],
              ),
              gapH8,

              // Details.
              SelectionArea(
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.start,
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    // Products.
                    if (item.productNames != null)
                      Text(
                        'Products: ${item.productNames?.join(', ')}',
                        style: Theme.of(context).textTheme.labelMedium,
                      ),
                    Text(
                      'Products types: ${item.productTypes?.join(', ')}',
                      style: Theme.of(context).textTheme.labelMedium,
                    ),

                    // Receipt details.
                    Text(
                      'Retailer: ${item.retailer}',
                      style: Theme.of(context).textTheme.labelMedium,
                    ),
                    Text(
                      'Total: ${item.totalPrice.toString()}',
                      style: Theme.of(context).textTheme.labelMedium,
                    ),

                    // Parsed at time.
                    if (item.parsedAt != null)
                      Text(
                        'Parsed: ${TimeUtils.getReadableTime(item.parsedAt!)}',
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

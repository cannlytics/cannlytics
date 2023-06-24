// Cannlytics Data
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 6/18/2023
// Updated: 6/23/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>
import 'package:cannlytics_data/constants/design.dart';
import 'package:cannlytics_data/models/lab_result.dart';
import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

/// Receipt card.
/// TODO: Add image.
class ResultCard extends StatelessWidget {
  ResultCard({
    required this.item,
    this.onDownload,
    this.onDelete,
  });

  // Properties
  final LabResult item;
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
                          onTap: () => context.go('/results/${item.labId}'),
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
                        case 'Edit':
                          context.go('/results/${item.labId}');
                          break;
                        case 'Download':
                          print('DOWNLOADING...');
                          // FIXME:
                          onDownload!;
                          break;
                        case 'Delete':
                          onDelete!;
                          break;
                      }
                    },
                    itemBuilder: (BuildContext context) =>
                        <PopupMenuEntry<String>>[
                      PopupMenuItem<String>(
                        value: 'Edit',
                        child: Text(
                          'Edit',
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
                    if (item.productName != null)
                      Text(
                        'Products ${item.productName}',
                        style: Theme.of(context).textTheme.labelMedium,
                      ),
                    Text(
                      'Products type: ${item.productType}',
                      style: Theme.of(context).textTheme.labelMedium,
                    ),

                    // Receipt details.
                    Text(
                      'Producer: ${item.producer}',
                      style: Theme.of(context).textTheme.labelMedium,
                    ),
                    Text(
                      'Total THC: ${item.totalThc.toString()}',
                      style: Theme.of(context).textTheme.labelMedium,
                    ),
                    Text(
                      'Total CBD: ${item.totalCbd.toString()}',
                      style: Theme.of(context).textTheme.labelMedium,
                    ),

                    // // Parsed at time.
                    // if (item.dateTested != null)
                    //   Text(
                    //     'Parsed: ${TimeUtils.getReadableTime(item.dateTested!)}',
                    //     style: Theme.of(context).textTheme.labelMedium,
                    //   ),
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

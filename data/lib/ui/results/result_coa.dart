// Cannlytics Data
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 6/11/2023
// Updated: 6/27/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Flutter imports:
import 'package:flutter/material.dart';

// Package imports:
import 'package:pdfx/pdfx.dart';
import 'package:url_launcher/url_launcher.dart';

/// COA PDF.
class CoaPdf extends StatelessWidget {
  CoaPdf({required this.pdfController});

  // Parameters.
  final PdfController pdfController;

  @override
  Widget build(BuildContext context) {
    return Container(
      height: MediaQuery.of(context).size.height * 0.85,
      width: MediaQuery.of(context).size.width * 0.5,
      child: PdfView(
        builders: PdfViewBuilders<DefaultBuilderOptions>(
          options: const DefaultBuilderOptions(),
          documentLoaderBuilder: (_) =>
              const Center(child: CircularProgressIndicator()),
          pageLoaderBuilder: (_) =>
              const Center(child: CircularProgressIndicator()),
          pageBuilder: (BuildContext context, Future<PdfPageImage> pageImage,
              int index, PdfDocument document) {
            return PhotoViewGalleryPageOptions(
              imageProvider: PdfPageImageProvider(
                pageImage,
                index,
                document.id,
              ),
              minScale: PhotoViewComputedScale.contained * 1,
              maxScale: PhotoViewComputedScale.contained * 2,
              initialScale: PhotoViewComputedScale.contained * 1.0,
              heroAttributes:
                  PhotoViewHeroAttributes(tag: '${document.id}-$index'),
            );
          },
        ),
        controller: pdfController,
      ),
    );
  }
}

/// COA PDF actions.
class CoaPdfActions extends StatelessWidget {
  CoaPdfActions({
    required this.pdfController,
    required this.pdfUrl,
  });

  // Parameters.
  final PdfController pdfController;
  final String pdfUrl;

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        // Previous page button.
        IconButton(
          icon: Icon(
            Icons.navigate_before,
            color: Theme.of(context).textTheme.bodySmall?.color,
          ),
          onPressed: () {
            pdfController.previousPage(
              curve: Curves.ease,
              duration: const Duration(milliseconds: 100),
            );
          },
        ),

        // Page number.
        PdfPageNumber(
          controller: pdfController,
          builder: (_, loadingState, page, pagesCount) => Container(
            alignment: Alignment.center,
            child: Text(
              '$page/${pagesCount ?? 0}',
              style: Theme.of(context).textTheme.bodySmall,
            ),
          ),
        ),

        // Next page button.
        IconButton(
          icon: Icon(
            Icons.navigate_next,
            color: Theme.of(context).textTheme.bodySmall?.color,
          ),
          onPressed: () {
            pdfController.nextPage(
              curve: Curves.ease,
              duration: const Duration(milliseconds: 100),
            );
          },
        ),

        // Open PDF button.
        IconButton(
          icon: Icon(
            Icons.open_in_new,
            color: Theme.of(context).textTheme.bodySmall?.color,
            size: 16,
          ),
          onPressed: () {
            launchUrl(Uri.parse(pdfUrl));
          },
        ),

        // TODO: Implement zoom, download, and other actions.
      ],
    );
  }
}

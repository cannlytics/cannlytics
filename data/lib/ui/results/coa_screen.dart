// Cannlytics Data
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 6/11/2023
// Updated: 6/11/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>
import 'package:flutter/material.dart';
import 'package:flutter_form_builder/flutter_form_builder.dart';
import 'package:pdfx/pdfx.dart';
import 'package:internet_file/internet_file.dart';

/// COA screen.
class COAScreen extends StatefulWidget {
  @override
  _COAScreenState createState() => _COAScreenState();
}

class _COAScreenState extends State<COAScreen> {
  static const int _initialPage = 2;
  bool _isSampleDoc = true;
  late PdfController _pdfController;
  late String _pdfUrl;

  // Initialize the PDF document.
  @override
  void initState() {
    super.initState();
    _pdfUrl =
        'https://firebasestorage.googleapis.com/v0/b/cannlytics.appspot.com/o/tests%2Fassets%2Fcoas%2Facs%2F27675_0002355100.pdf?alt=media&token=bc9abde9-4fe6-4a45-8be4-68e92c8ea8f9';
    _pdfController = PdfController(
      document: PdfDocument.openData(InternetFile.get(_pdfUrl)),
      initialPage: _initialPage,
    );
  }

  // Dispose of the PDF.
  @override
  void dispose() {
    _pdfController.dispose();
    super.dispose();
  }

  // Render the screen.
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Column(
        children: [
          // PDF actions.
          _pdfActions(),

          // COA PDF.
          Expanded(
            child: Row(
              children: [
                // COA PDF.
                _coaPDF(),

                // COA fields.
                _coaFields(),
              ],
            ),
          ),
        ],
      ),
    );
  }

  // COA PDF.
  Widget _coaPDF() {
    return Expanded(
      child: PdfView(
        builders: PdfViewBuilders<DefaultBuilderOptions>(
          options: const DefaultBuilderOptions(),
          documentLoaderBuilder: (_) =>
              const Center(child: CircularProgressIndicator()),
          pageLoaderBuilder: (_) =>
              const Center(child: CircularProgressIndicator()),
          pageBuilder: _pageBuilder,
        ),
        controller: _pdfController,
      ),
    );
  }

  // PDF actions.
  Widget _pdfActions() {
    return Row(
      children: [
        // Previous page.
        IconButton(
          icon: const Icon(Icons.navigate_before),
          onPressed: () {
            _pdfController.previousPage(
              curve: Curves.ease,
              duration: const Duration(milliseconds: 100),
            );
          },
        ),

        // Page count.
        PdfPageNumber(
          controller: _pdfController,
          builder: (_, loadingState, page, pagesCount) => Container(
            alignment: Alignment.center,
            child: Text(
              '$page/${pagesCount ?? 0}',
              style: const TextStyle(fontSize: 22),
            ),
          ),
        ),

        // Next page.
        IconButton(
          icon: const Icon(Icons.navigate_next),
          onPressed: () {
            _pdfController.nextPage(
              curve: Curves.ease,
              duration: const Duration(milliseconds: 100),
            );
          },
        ),

        // Refresh button.
        IconButton(
          icon: const Icon(Icons.refresh),
          onPressed: () {
            if (_isSampleDoc) {
              _pdfController.loadDocument(
                  PdfDocument.openData(InternetFile.get(_pdfUrl)));
            } else {
              _pdfController.loadDocument(
                  PdfDocument.openData(InternetFile.get(_pdfUrl)));
            }
            _isSampleDoc = !_isSampleDoc;
          },
        ),
      ],
    );
  }

  // PDF page builder.
  PhotoViewGalleryPageOptions _pageBuilder(
    BuildContext context,
    Future<PdfPageImage> pageImage,
    int index,
    PdfDocument document,
  ) {
    return PhotoViewGalleryPageOptions(
      imageProvider: PdfPageImageProvider(
        pageImage,
        index,
        document.id,
      ),
      minScale: PhotoViewComputedScale.contained * 1,
      maxScale: PhotoViewComputedScale.contained * 2,
      initialScale: PhotoViewComputedScale.contained * 1.0,
      heroAttributes: PhotoViewHeroAttributes(tag: '${document.id}-$index'),
    );
  }

  Widget _coaFields() {
    return Expanded(
      child: SingleChildScrollView(
        child: FormBuilder(
          child: Column(
            children: <Widget>[
              FormBuilderTextField(name: 'Product Name'),
              // Add fields
            ],
          ),
        ),
      ),
    );
  }
}

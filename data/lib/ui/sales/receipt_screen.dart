// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 3/9/2023
// Updated: 6/24/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>
import 'package:cannlytics_data/models/lab_result.dart';
import 'package:flutter/material.dart';
import 'package:pdfx/pdfx.dart';
import 'package:internet_file/internet_file.dart';
import 'package:url_launcher/url_launcher.dart';

// TODO: Ability to download data as an Excel file!!!

/// TODO: Allow user's to link lab results for their products.

/// TODO: Link to strains where user can find more lab results.

/// TODO: Link to producer / retailer / lab.

/// COA screen.
class ResultScreen extends StatefulWidget {
  ResultScreen({required this.labResult});

  // Properties
  final LabResult labResult;

  @override
  _ResultScreenState createState() => _ResultScreenState();
}

class _ResultScreenState extends State<ResultScreen> {
  static const int _initialPage = 1;
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
    return SingleChildScrollView(
      child: Column(
        children: [
          // Results list, centered when there are no results, top-aligned otherwise.
          Container(
            height: MediaQuery.of(context).size.height * 0.75,
            child: SingleChildScrollView(
              child: Card(
                margin: EdgeInsets.only(top: 12),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(3),
                ),
                child: Padding(
                  padding: const EdgeInsets.all(16.0),
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.start,
                    crossAxisAlignment: CrossAxisAlignment.start,
                    mainAxisSize: MainAxisSize.min,
                    children: <Widget>[
                      // PDF actions.
                      _pdfActions(),

                      // COA PDF.
                      Row(
                        children: [
                          // COA PDF.
                          _coaPDF(),

                          // COA fields.
                          _coaFields(),
                        ],
                      ),
                    ],
                  ),
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }

  // COA PDF.
  Widget _coaPDF() {
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

        // TODO: Implement zoom.

        // Refresh button.
        // IconButton(
        //   icon: const Icon(Icons.refresh),
        //   onPressed: () {
        //     _pdfController
        //         .loadDocument(PdfDocument.openData(InternetFile.get(_pdfUrl)));
        //   },
        // ),

        // Open in new button.
        GestureDetector(
          onTap: () {
            launchUrl(Uri.parse(_pdfUrl));
          },
          child: Icon(
            Icons.open_in_new,
            color: Theme.of(context).colorScheme.onSurface,
            size: 16,
          ),
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

  /// Fields.
  Widget _coaFields() {
    return Container(
      height: MediaQuery.of(context).size.height * 0.85,
      width: MediaQuery.of(context).size.width * 0.5,
      child: SingleChildScrollView(
        child: LabResultForm(),
        // child: FormBuilder(
        //   child: Column(
        //     children: <Widget>[
        //       FormBuilderTextField(name: 'Product Name'),
        //       // FIXME: Add fields!!!
        //       Text(widget.labResult.productName ?? ''),
        //     ],
        //   ),
        // ),
      ),
    );
  }
}

/// Lab result form.
class LabResultForm extends StatefulWidget {
  @override
  _LabResultFormState createState() => _LabResultFormState();
}

class _LabResultFormState extends State<LabResultForm> {
  final _formKey = GlobalKey<FormState>();

  final _labIdController = TextEditingController();
  final _batchNumberController = TextEditingController();
  final _productNameController = TextEditingController();
  // ... Add the rest of the TextEditingController for other fields

  @override
  Widget build(BuildContext context) {
    return Form(
      key: _formKey,
      child: Column(
        children: <Widget>[
          TextFormField(
            controller: _labIdController,
            decoration: const InputDecoration(
              labelText: 'Lab ID',
            ),
          ),
          TextFormField(
            controller: _batchNumberController,
            decoration: const InputDecoration(
              labelText: 'Batch Number',
            ),
          ),
          TextFormField(
            controller: _productNameController,
            decoration: const InputDecoration(
              labelText: 'Product Name',
            ),
          ),
          // ... Add the rest of the TextFormFields for other fields
          Padding(
            padding: const EdgeInsets.symmetric(vertical: 16.0),
            child: ElevatedButton(
              onPressed: () {
                if (_formKey.currentState!.validate()) {
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(content: Text('Processing Data')),
                  );
                }
              },
              child: const Text('Submit'),
            ),
          ),
        ],
      ),
    );
  }

  @override
  void dispose() {
    _labIdController.dispose();
    _batchNumberController.dispose();
    _productNameController.dispose();
    // ... Dispose the rest of the TextEditingController for other fields

    super.dispose();
  }
}

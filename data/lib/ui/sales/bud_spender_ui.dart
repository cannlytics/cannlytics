// Cannlytics Data
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 5/13/2023
// Updated: 5/13/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Flutter imports:
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';

// Package imports:
import 'package:dotted_border/dotted_border.dart';
import 'package:file_picker/file_picker.dart';
import 'package:flutter_dropzone/flutter_dropzone.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:fluttertoast/fluttertoast.dart';
import 'package:mobile_scanner/mobile_scanner.dart';

// Project imports:
import 'package:cannlytics_data/common/buttons/primary_button.dart';
import 'package:cannlytics_data/common/buttons/secondary_button.dart';
import 'package:cannlytics_data/constants/design.dart';
import 'package:cannlytics_data/constants/theme.dart';
import 'package:cannlytics_data/services/api_service.dart';

/// CoADoc user interface.
class BudSpenderInterface extends ConsumerWidget {
  const BudSpenderInterface({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      mainAxisAlignment: MainAxisAlignment.start,
      children: [
        // Receipt parser.
        Card(
          margin: EdgeInsets.zero,
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
                // Title.
                Text(
                  'Add receipts',
                  style: Theme.of(context).textTheme.titleLarge,
                ),

                // Receipt upload actions.
                gapH24,
                Row(
                  children: [
                    Text(
                      'File Upload',
                      style: Theme.of(context).textTheme.labelMedium,
                    ),
                    IconButton(
                      icon: Icon(Icons.info_outline),
                      onPressed: () {},
                      tooltip:
                          'We support most image formats: .png, .jpeg, etc.',
                    ),
                    Spacer(),
                    SecondaryButton(
                      text: 'Upload Receipts',
                      onPressed: () async {
                        FilePickerResult? result =
                            await FilePicker.platform.pickFiles(
                          type: FileType.custom,
                          allowedExtensions: ['png', 'jpeg'],
                        );
                        if (result != null) {
                          // FIXME: Handle file
                          print('HANDLE FILE: ${result.files.first.name}');
                        } else {
                          // User canceled the picker
                        }
                      },
                    ),
                  ],
                ),
                gapH4,

                // COA file upload.
                ReceiptUpload(),
                gapH12,
              ],
            ),
          ),
        ),

        // Grid / table of parsed receipts.
        gapH32,
        Card(
          margin: EdgeInsets.zero,
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
                // Title.
                Row(
                  children: [
                    Text(
                      'Your receipts',
                      style: Theme.of(context).textTheme.titleLarge,
                    ),

                    // Results tabs.
                    Spacer(),
                    // TabToggleButtons(),
                  ],
                ),

                // FIXME: Grid of user results.

                // // Sample results options.
                // SampleResultsOptions(),

                // // Sample card template.
                // SampleCardTemplate(),

                // // Sample results.
                // SampleCard(),

                // FIXME: Table of user results.
                UserReceiptsList(),
              ],
            ),
          ),
        ),

        // TODO: User guide.
        // CustomParsingAlgorithms(),

        // TODO: API documentation.
        // CoADocAPI(),

        // TODO: Python SDK documentation.
        // CoADocPythonSDK(),
      ],
    );
  }
}

/// Receipt upload.
class ReceiptUpload extends ConsumerWidget {
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    late DropzoneViewController controller;
    final themeMode = ref.watch(themeModeProvider);
    final bool isDark = themeMode == ThemeMode.dark;
    return Column(
      children: <Widget>[
        Row(
          children: <Widget>[
            // Drag and drop file input
            Expanded(
              child: Column(
                children: [
                  // Drag and drop a file.
                  if (kIsWeb)
                    Container(
                      height: 250,
                      child: DottedBorder(
                        color: isDark ? Color(0xFF6E7681) : Color(0x1b1f2326),
                        strokeWidth: 1,
                        child: Stack(
                          children: [
                            // Drop zone.
                            DropzoneView(
                              operation: DragOperation.copy,
                              cursor: CursorType.grab,
                              onCreated: (ctrl) => controller = ctrl,
                              onError: (e) => print('DropZone error: $e'),
                              onDrop: (ev) async {
                                final bytes = await controller.getFileData(ev);
                                print(bytes.sublist(0, 20));
                              },
                              onDropMultiple: (ev) async {
                                // print('Zone 1 drop multiple: $ev');
                                // final bytes = await controller.getFileData(ev);
                                // final response = await AuthRequestService().authRequest(url);
                                try {
                                  var response = await APIService.apiRequest(
                                      '/api/ai/receipts',
                                      files: ev);
                                  Fluttertoast.showToast(
                                      msg: 'Receipts uploaded for processing.',
                                      toastLength: Toast.LENGTH_SHORT,
                                      gravity: ToastGravity.CENTER,
                                      timeInSecForIosWeb: 1,
                                      backgroundColor: Colors.green,
                                      textColor: Colors.white,
                                      fontSize: 16.0);
                                } catch (error) {
                                  Fluttertoast.showToast(
                                      msg:
                                          'Error uploading receipts. Please contact support and try again later.',
                                      toastLength: Toast.LENGTH_SHORT,
                                      gravity: ToastGravity.CENTER,
                                      timeInSecForIosWeb: 1,
                                      backgroundColor: Colors.red,
                                      textColor: Colors.white,
                                      fontSize: 16.0);
                                }
                              },
                            ),

                            // Text.
                            Center(child: UserReceiptsPlaceholder()),
                          ],
                        ),
                      ),
                    ),

                  // File picker button.
                  if (!kIsWeb)
                    SecondaryButton(
                      text: 'Import your receipts',
                      onPressed: () async {
                        FilePickerResult? result =
                            await FilePicker.platform.pickFiles(
                          type: FileType.custom,
                          allowedExtensions: ['png', 'jpeg'],
                        );
                        if (result != null) {
                          // Handle file
                          print('HANDLE FILE: ${result.files.first.name}');
                        } else {
                          // User canceled the picker
                        }
                      },
                    ),
                ],
              ),
            ),

            // QR code scanner.
            if (!kIsWeb)
              Expanded(
                child: Container(
                  height: 200.0,
                  child: MobileScanner(
                    fit: BoxFit.contain,
                    onDetect: (capture) {
                      final List<Barcode> barcodes = capture.barcodes;
                      final Uint8List? image = capture.image;
                      for (final barcode in barcodes) {
                        debugPrint('Barcode found! ${barcode.rawValue}');
                      }
                    },
                  ),
                ),
              ),
          ],
        ),
      ],
    );
  }
}

/// User receipts placeholder.
class UserReceiptsPlaceholder extends StatelessWidget {
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
                  'https://firebasestorage.googleapis.com/v0/b/cannlytics.appspot.com/o/public%2Fimages%2Flogos%2Fbud_spender.png?alt=media&token=e0de707b-9c18-44b9-9944-b36fcffd9fd3',
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
                      text: 'Happy to organize your receipts,',
                      style: TextStyle(fontSize: 20)),
                  TextSpan(
                      text: ' monsieur.\n',
                      style:
                          TextStyle(fontSize: 20, fontStyle: FontStyle.italic)),
                  TextSpan(
                      text: 'Drop a CoA PDF, image, or folder to parse.',
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

/// List of user's receipts.
class UserReceiptsList extends StatelessWidget {
  final bool isLoading =
      false; // This would typically come from your state management system

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      child: Column(
        children: <Widget>[
          Visibility(
            visible: isLoading,
            child: CircularProgressIndicator(),
          ),
          Visibility(
            visible: !isLoading,
            child: DataTable(
              columns: const <DataColumn>[
                DataColumn(
                  label: Text(
                    'Column A',
                    style: TextStyle(fontStyle: FontStyle.italic),
                  ),
                ),
                DataColumn(
                  label: Text(
                    'Column B',
                    style: TextStyle(fontStyle: FontStyle.italic),
                  ),
                ),
                // Add more DataColumn widgets here for each column in your data
              ],
              rows: const <DataRow>[
                DataRow(
                  cells: <DataCell>[
                    DataCell(Text('Cell A1')),
                    DataCell(Text('Cell B1')),
                  ],
                ),
                // Add more DataRow widgets here for each row in your data
              ],
            ),
          ),
        ],
      ),
    );
  }
}

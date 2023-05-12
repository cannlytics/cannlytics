// Cannlytics Data
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 5/11/2023
// Updated: 5/12/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Flutter imports:
import 'package:cannlytics_data/common/buttons/primary_button.dart';
import 'package:cannlytics_data/common/buttons/secondary_button.dart';
import 'package:cannlytics_data/constants/theme.dart';
import 'package:dotted_border/dotted_border.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:flutter_dropzone/flutter_dropzone.dart';

// Package imports:
import 'package:file_picker/file_picker.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

// Project imports:
import 'package:cannlytics_data/constants/design.dart';
import 'package:mobile_scanner/mobile_scanner.dart';

/// CoADoc user interface.
class CoADocInterface extends ConsumerWidget {
  const CoADocInterface({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      mainAxisAlignment: MainAxisAlignment.start,
      children: [
        // COA parser.
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
                  'Add lab results',
                  style: Theme.of(context).textTheme.titleLarge,
                ),

                // COA search.
                gapH8,
                Row(
                  children: [
                    Text(
                      'Search for lab results',
                      style: Theme.of(context).textTheme.labelMedium,
                    ),
                    IconButton(
                      icon: Icon(Icons.info_outline),
                      onPressed: () {},
                      tooltip: "Enter a URL, ID, or what you want to find.",
                    ),
                  ],
                ),
                CoASearch(),

                // COA upload actions.
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
                          'We support most COA formats: .pdf, .jpeg, .png, .zip',
                    ),
                    Spacer(),
                    SecondaryButton(
                      text: 'Upload COAs',
                      onPressed: () async {
                        FilePickerResult? result =
                            await FilePicker.platform.pickFiles(
                          type: FileType.custom,
                          allowedExtensions: ['pdf', 'zip'],
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
                CoAUpload(),
                gapH12,
              ],
            ),
          ),
        ),

        // Grid / table of parsed lab results.
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
                      'Your lab results',
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
                UserResultsList(),
              ],
            ),
          ),
        ),

        // Grid / table of public lab results.
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
                      'Public lab results',
                      style: Theme.of(context).textTheme.titleLarge,
                    ),

                    // Results tabs.
                    Spacer(),
                    // TabToggleButtons(),
                  ],
                ),

                // FIXME: Grid / table of public lab results.
                UserResultsList(),
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

/// Instructions shown when no lab results have been collected yet.
class CoAParsingInstructions extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Container(
      width: 560,
      child: Row(
        mainAxisAlignment: MainAxisAlignment.start,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: <Widget>[
          Expanded(
            child: Text(
              'Your sample results from uploaded CoAs will render below. At this time, only certificates of analysis (CoAs) from validated labs and LIMS can be parsed. Please see the list of validated labs below.',
              style: Theme.of(context).textTheme.bodyMedium,
            ),
          ),
        ],
      ),
    );
  }
}

/// COA search.
class CoASearch extends StatelessWidget {
  final TextEditingController coaSearchController = TextEditingController();
  final TextEditingController coaUrlController = TextEditingController();

  @override
  Widget build(BuildContext context) {
    return Column(
      children: <Widget>[
        Row(
          children: <Widget>[
            Expanded(
              child: TextFormField(
                key: Key('resultsSearch'),
                controller: coaSearchController,
                autocorrect: false,
                decoration: InputDecoration(
                  // enabled: !state.isLoading,
                  contentPadding: EdgeInsets.only(
                    top: 18,
                    left: 8,
                    right: 8,
                    bottom: 8,
                  ),
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.only(
                      topLeft: Radius.circular(3),
                      bottomLeft: Radius.circular(3),
                      topRight: Radius.zero,
                      bottomRight: Radius.zero,
                    ),
                  ),
                ),
                style: Theme.of(context).textTheme.bodyMedium,
                textInputAction: TextInputAction.next,
              ),
            ),
            SizedBox(
              height: 42,
              child: PrimaryButton(
                inline: true,
                backgroundColor: Colors.green,
                text: 'Get results',
                onPressed: () {
                  // Handle the search action here
                },
              ),
            ),
          ],
        ),
        // Hidden text field
        Offstage(
          offstage: true,
          child: TextField(
            controller: coaUrlController,
          ),
        ),
      ],
    );
  }
}

/// COA upload.
class CoAUpload extends ConsumerWidget {
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
                              onLoaded: () => print('Zone 1 loaded'),
                              onError: (ev) => print('Zone 1 error: $ev'),
                              onHover: () {
                                // print('Zone 1 hovered');
                              },
                              onLeave: () {
                                // print('Zone 1 left');
                              },
                              onDrop: (ev) async {
                                print('Zone 1 drop: ${ev.name}');
                                final bytes = await controller.getFileData(ev);
                                print(bytes.sublist(0, 20));
                              },
                              onDropMultiple: (ev) async {
                                print('Zone 1 drop multiple: $ev');
                              },
                            ),

                            // Text.
                            Center(child: UserResultsPlaceholder()),
                          ],
                        ),
                      ),
                    ),

                  // File picker button.
                  if (!kIsWeb)
                    SecondaryButton(
                      text: 'Import your COAs',
                      onPressed: () async {
                        FilePickerResult? result =
                            await FilePicker.platform.pickFiles(
                          type: FileType.custom,
                          allowedExtensions: ['pdf', 'zip'],
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

/// Sample results placeholder.
class UserResultsPlaceholder extends StatelessWidget {
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
                  'https://firebasestorage.googleapis.com/v0/b/cannlytics.appspot.com/o/public%2Fimages%2Flogos%2Fcannlytics_coa_doc.png?alt=media&token=1871dde9-82db-4342-a29d-d373671491b3',
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
                      text: 'Waiting on your COAs boss!\n',
                      style: TextStyle(fontSize: 20)),
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

/// Results view options.
class TabToggleButtons extends StatefulWidget {
  @override
  _TabToggleButtonsState createState() => _TabToggleButtonsState();
}

class _TabToggleButtonsState extends State<TabToggleButtons> {
  List<bool> _isSelected = [true, false];

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.start,
      children: <Widget>[
        ToggleButtons(
          color: Colors.black,
          selectedColor: Colors.black,
          fillColor: Colors.grey[300],
          borderRadius: BorderRadius.circular(4.0),
          children: <Widget>[
            Icon(Icons.grid_view, size: 21),
            Icon(Icons.list, size: 21),
          ],
          onPressed: (int index) {
            setState(() {
              for (int buttonIndex = 0;
                  buttonIndex < _isSelected.length;
                  buttonIndex++) {
                if (buttonIndex == index) {
                  _isSelected[buttonIndex] = true;
                } else {
                  _isSelected[buttonIndex] = false;
                }
              }
            });
          },
          isSelected: _isSelected,
        ),
      ],
    );
  }
}

/// Sample results options.
class SampleResultsOptions extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.start,
      children: <Widget>[
        TextButton.icon(
          onPressed: () {
            // Handle download results
          },
          icon: Icon(
            Icons.download_sharp,
            color: Theme.of(context).colorScheme.onSurface,
          ),
          label: Text('Download Results'),
        ),
        SizedBox(width: 8.0), // spacing
        TextButton.icon(
          onPressed: () {
            // Handle clear
          },
          icon: Icon(
            Icons.clear,
            color: Theme.of(context).colorScheme.onSurface,
          ),
          label: Text('Clear'),
        ),
      ],
    );
  }
}

/// Sample card.
class SampleCardTemplate extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.all(12.0),
      child: Stack(
        children: <Widget>[
          Card(
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(10.0),
            ),
            child: Padding(
              padding: const EdgeInsets.all(8.0),
              child: Center(
                child: CircularProgressIndicator(),
              ),
            ),
          ),
          Positioned(
            top: 0,
            right: 0,
            child: IconButton(
              icon: Icon(Icons.close),
              onPressed: () {
                // Handle remove sample
              },
            ),
          ),
        ],
      ),
    );
  }
}

/// Sample card.
class SampleCard extends StatelessWidget {
  // These values should be replaced with actual data
  final String productName = '';
  final String productType = '';
  final String producer = '';
  final String dateTested = '';
  final String imageUrl = '';
  final String sampleData = '';

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.all(12.0),
      child: Stack(
        children: <Widget>[
          Card(
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(10.0),
            ),
            child: InkWell(
              onTap: () {
                // Handle card tap
              },
              child: Padding(
                padding: const EdgeInsets.all(8.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: <Widget>[
                    Visibility(
                      visible: imageUrl.isNotEmpty,
                      child: Center(
                        child: Image.network(
                          imageUrl,
                          height: 75,
                        ),
                      ),
                    ),
                    Text(productName,
                        style: TextStyle(
                            fontWeight: FontWeight.bold, fontSize: 20)),
                    Text(productType),
                    Text(producer),
                    Text(dateTested),
                    Visibility(
                      visible: sampleData.isNotEmpty,
                      child: Text(sampleData),
                    ),
                  ],
                ),
              ),
            ),
          ),
          Positioned(
            top: 0,
            right: 0,
            child: IconButton(
              icon: Icon(Icons.close),
              onPressed: () {
                // Handle remove sample
              },
            ),
          ),
        ],
      ),
    );
  }
}

/// List of user's results.
class UserResultsList extends StatelessWidget {
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

/// Sample results modal.
class SampleResultsModal extends StatelessWidget {
  final bool isLoading =
      true; // This should be managed by your state management solution

  void _showModal(BuildContext context) {
    showDialog(
      context: context,
      builder: (BuildContext context) {
        return AlertDialog(
          title: Text('Sample Results'),
          content: Column(
            children: <Widget>[
              isLoading
                  ? CircularProgressIndicator()
                  : Column(
                      children: <Widget>[
                        Image.network('image_url',
                            height:
                                75), // Replace 'image_url' with your actual image URL
                        Text('Product Name'),
                        Text('Product Type'),
                        Text('Producer'),
                        Text('Date Tested'),
                        // Add more details here
                      ],
                    ),
            ],
          ),
          actions: <Widget>[
            TextButton(
              onPressed: () {
                Navigator.of(context).pop();
              },
              child: Text('Close'),
            ),
            // TODO: Add a 'Save' button here
            TextButton(
              onPressed: () {
                // Add your download logic here
              },
              child: Text('Download'),
            ),
          ],
        );
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    return ElevatedButton(
      onPressed: () => _showModal(context),
      child: Text('Show Modal'),
    );
  }
}

/// User guide.
class CustomParsingAlgorithms extends StatelessWidget {
  const CustomParsingAlgorithms({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.all(16.0),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Flexible(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Icon(
                      Icons.emoji_objects_outlined,
                      size: 50,
                    ),
                    Text(
                      "Custom CoA Parsing",
                      style: Theme.of(context).textTheme.titleMedium,
                    ),
                  ],
                ),
                SizedBox(height: 8),
                Text(
                  "At this time, CoADoc can only parse certificates of analysis (CoAs)"
                  " from labs and LIMS with validated parsing algorithms. We've validated:",
                  style: Theme.of(context).textTheme.bodyMedium,
                ),
                SizedBox(height: 16),
                DataTable(
                  columns: const <DataColumn>[
                    DataColumn(
                      label: Text(
                        'Labs',
                      ),
                    ),
                    DataColumn(
                      label: Text(
                        'LIMS',
                      ),
                    ),
                  ],
                  rows: const <DataRow>[
                    DataRow(
                      cells: <DataCell>[
                        DataCell(Text('Anresco Laboratories')),
                        DataCell(Text('Confident Cannabis')),
                      ],
                    ),
                    DataRow(
                      cells: <DataCell>[
                        DataCell(Text('Cannalysis')),
                        DataCell(Text('TagLeaf LIMS')),
                      ],
                    ),
                    // Add more rows here...
                  ],
                ),
                SizedBox(height: 16),
                Text(
                  "If you want your favorite lab or LIMS added, then please email dev@cannlytics.com"
                  " and chances are that they can be included. Alternatively, because Cannlytics is open source,"
                  " you can clone the source code and write a custom parsing algorithm for your lab or LIMS for free!"
                  " It is as easy as 1, 2, 3 to add a new lab.",
                  style: Theme.of(context).textTheme.bodyMedium,
                ),
                ElevatedButton(
                  onPressed: () {
                    // Implement your function
                  },
                  child: const Text('Request a New Lab / LIMS'),
                ),
              ],
            ),
          ),
          SizedBox(width: 16),
          Flexible(
            child: Image.network(
              'https://firebasestorage.googleapis.com/v0/b/cannlytics.appspot.com/o/public%2Fimages%2Fexamples%2Fsample-coa-parse.png?alt=media&token=c9dab916-99c7-439c-9510-03b29bad7bb7',
              fit: BoxFit.cover,
            ),
          ),
        ],
      ),
    );
  }
}

/// API documentation.
class CoADocAPI extends StatelessWidget {
  const CoADocAPI({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.all(16.0),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Flexible(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Icon(
                      Icons.satellite,
                      size: 50,
                    ),
                    Text(
                      "CoADoc API",
                      style: Theme.of(context).textTheme.titleMedium,
                    ),
                  ],
                ),
                SizedBox(height: 8),
                Text(
                  "You can integrate rich lab result data into your app with one quick request to the CoADoc API."
                  " Given a QR code scanner or any other mechanism to input CoA URLs or PDFs,"
                  " make a simple request and you will receive your CoA data neatly organized and ready for your use.",
                  style: Theme.of(context).textTheme.bodyMedium,
                ),
                ElevatedButton(
                  onPressed: () {
                    // Implement your function
                  },
                  child: const Text('Read the docs and get the code'),
                ),
                SizedBox(height: 16),
                Text(
                  "POST https://cannlytics.com/api/data/coas",
                  style: Theme.of(context).textTheme.bodySmall,
                ),
                SizedBox(height: 8),
                Text(
                  "{\n\"urls\": [\"https://cannlytics.page.link/test-coa\"]\n}",
                  style: Theme.of(context).textTheme.bodySmall,
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

/// Python SDK documentation.
class CoADocPythonSDK extends StatelessWidget {
  const CoADocPythonSDK({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.all(16.0),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Flexible(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Icon(
                      Icons.code,
                      size: 50,
                    ),
                    Text(
                      "CoADoc Python SDK",
                      style: Theme.of(context).textTheme.titleMedium,
                    ),
                  ],
                ),
                SizedBox(height: 8),
                Text(
                  "Are you interested in developing a new parsing routine for a lab or LIMS? Then you can easily use CoADoc directly"
                  " with the cannlytics Python package to parse CoAs to your heart's content.",
                  style: Theme.of(context).textTheme.bodyMedium,
                ),
                ElevatedButton(
                  onPressed: () {
                    // Implement your function
                  },
                  child: const Text('Read the docs and get the code'),
                ),
                SizedBox(height: 16),
                Text(
                  "# pip install cannlytics\n"
                  "from cannlytics.data.coas import CoADoc\n\n"
                  "# Parse CoA data.\n"
                  "parser = CoADoc()\n"
                  "urls = [\"https://cannlytics.page.link/test-coa\"]\n"
                  "data = parser.parse(urls)\n"
                  "parser.quit()\n",
                  style: Theme.of(context).textTheme.bodySmall,
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

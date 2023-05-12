// Cannlytics Data
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 5/11/2023
// Updated: 5/11/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Flutter imports:
import 'package:flutter/material.dart';

// Package imports:
import 'package:file_picker/file_picker.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_svg/flutter_svg.dart';
import 'package:go_router/go_router.dart';

// Project imports:
import 'package:cannlytics_data/common/forms/form_placeholder.dart';
import 'package:cannlytics_data/constants/design.dart';

/// CoA Doc.
class CoADocInterface extends ConsumerWidget {
  const CoADocInterface({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Padding(
          padding: EdgeInsets.only(top: 24),
          child: Text(
            'Your lab results',
            style: Theme.of(context).textTheme.titleLarge,
          ),
        ),
        gapH8,

        // Placeholder if no lab results yet.
        // FormPlaceholder(
        //   image: 'assets/images/icons/certificate.png',
        //   title: 'No lab results collected yet.',
        //   description:
        //       'Lab results that you collect will appear here. Upload an image of your labels, receipts, or certificates, or enter the URL of your lab results, and we will do our best to put the results in your hands.',
        //   onTap: () {
        //     context.push('/results/coas');
        //   },
        // ),

        // TODO: Show grid / table of parsed lab results.

        // Parser card.
        AnalysisParserCard(),

        // COA input.
        gapH24,
        COAInputContainer(),

        // Results tabs.
        TabToggleButtons(),

        // Sample results placeholder.
        SampleResultsPlaceholder(),

        // Sample results options.
        SampleResultsOptions(),

        // Sample card template.
        SampleCardTemplate(),

        // Sample results.
        SampleCard(),

        // List of COAs.
        CoaList(),

        // User guide.
        CustomParsingAlgorithms(),

        // API documentation.
        CoADocAPI(),

        // Python SDK documentation.
        CoADocPythonSDK(),
      ],
    );
  }
}

/// Instructions shown when no lab results have been collected yet.
class AnalysisParserCard extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Center(
      child: Card(
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(3),
        ),
        child: Padding(
          padding: const EdgeInsets.all(16.0),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: <Widget>[
              Text(
                'Certificate of Analysis Parser',
                style: TextStyle(
                  fontSize: 20,
                  fontWeight: FontWeight.bold,
                  color: Colors.black,
                ),
              ),
              const SizedBox(height: 8),
              Container(
                width: 560,
                child: Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: <Widget>[
                    Expanded(
                      child: Text(
                        'Your sample results from uploaded CoAs will render below. At this time, only certificates of analysis (CoAs) from validated labs and LIMS can be parsed. Please see the list of validated labs below.',
                        style: TextStyle(
                          fontSize: 16,
                          height: 1.5,
                          color: Colors.black,
                        ),
                      ),
                    ),
                    IconButton(
                      icon: Icon(
                        Icons.info_outline,
                        size: 16,
                        color: Theme.of(context).colorScheme.secondary,
                      ),
                      onPressed: () {
                        // TODO: Implement.
                      },
                      tooltip:
                          'At this time, only certificates of analysis (CoAs) from validated labs and LIMS can be parsed. Please see the list of validated labs below.',
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

/// COA input container.
class COAInputContainer extends StatelessWidget {
  final TextEditingController coaSearchController = TextEditingController();
  final TextEditingController coaUrlController = TextEditingController();

  @override
  Widget build(BuildContext context) {
    return Column(
      children: <Widget>[
        Padding(
          padding: const EdgeInsets.only(top: 16.0),
          child: Row(
            children: <Widget>[
              Expanded(
                child: TextField(
                  controller: coaSearchController,
                  decoration: InputDecoration(
                    labelText: 'Search by CoA URL or Metrc ID...',
                  ),
                ),
              ),
              SizedBox(width: 8),
              ElevatedButton(
                onPressed: () {
                  // Handle the search action here
                },
                child: Text('Search'),
              ),
            ],
          ),
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

/// File input.
class FileInputWidget extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Column(
      children: <Widget>[
        Row(
          children: <Widget>[
            // Drag and drop file input
            Expanded(
              child: Column(
                children: [
                  // Drag and Drop Zone
                  // Here, you would use the flutter_dropzone package or equivalent
                  Container(
                    padding: EdgeInsets.all(16.0),
                    decoration: BoxDecoration(
                      border: Border.all(color: Colors.black),
                    ),
                    child: Text(
                      'Drop a CoA .pdf or a .zip of CoAs to parse.',
                    ),
                  ),
                  // File picker button
                  TextButton(
                    child: Text('Alternatively, import your CoA file'),
                    onPressed: () async {
                      FilePickerResult? result =
                          await FilePicker.platform.pickFiles(
                        type: FileType.custom,
                        allowedExtensions: ['pdf', 'zip'],
                      );
                      if (result != null) {
                        // Handle file
                      } else {
                        // User canceled the picker
                      }
                    },
                  ),
                  // Uploading state
                  // Display these based on your upload status
                  // Text('Uploading…'),
                  // Text('Done!'),
                  // Text('Error!'),
                ],
              ),
            ),
            // QR Code Scanner
            // Use qr_code_scanner package or equivalent here
            Expanded(
              child: Container(
                color: Colors.black,
                height: 200.0, // Adjust this as needed
                // Child would be QRView widget or similar
              ),
            ),
          ],
        ),
      ],
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

/// Sample results placeholder.
class SampleResultsPlaceholder extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: RichText(
          textAlign: TextAlign.center,
          text: TextSpan(
            style: DefaultTextStyle.of(context).style,
            children: <TextSpan>[
              TextSpan(
                  text: '🥸 Waiting on your CoAs Boss!\n',
                  style: TextStyle(fontSize: 20)),
              TextSpan(
                  text: 'Upload your CoAs above to begin parsing.',
                  style: TextStyle(fontSize: 14, fontStyle: FontStyle.italic)),
            ],
          ),
        ),
      ),
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

/// List of COAs.
class CoaList extends StatelessWidget {
  final bool isLoading =
      true; // This would typically come from your state management system

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
                      style: Theme.of(context).textTheme.headline5,
                    ),
                  ],
                ),
                SizedBox(height: 8),
                Text(
                  "At this time, CoADoc can only parse certificates of analysis (CoAs)"
                  " from labs and LIMS with validated parsing algorithms. We've validated:",
                  style: Theme.of(context).textTheme.bodyText2,
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
                  style: Theme.of(context).textTheme.bodyText2,
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
                      style: Theme.of(context).textTheme.headline5,
                    ),
                  ],
                ),
                SizedBox(height: 8),
                Text(
                  "You can integrate rich lab result data into your app with one quick request to the CoADoc API."
                  " Given a QR code scanner or any other mechanism to input CoA URLs or PDFs,"
                  " make a simple request and you will receive your CoA data neatly organized and ready for your use.",
                  style: Theme.of(context).textTheme.bodyText2,
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
                  style: Theme.of(context).textTheme.bodyText1,
                ),
                SizedBox(height: 8),
                Text(
                  "{\n\"urls\": [\"https://cannlytics.page.link/test-coa\"]\n}",
                  style: Theme.of(context).textTheme.bodyText1,
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
                      style: Theme.of(context).textTheme.headline5,
                    ),
                  ],
                ),
                SizedBox(height: 8),
                Text(
                  "Are you interested in developing a new parsing routine for a lab or LIMS? Then you can easily use CoADoc directly"
                  " with the cannlytics Python package to parse CoAs to your heart's content.",
                  style: Theme.of(context).textTheme.bodyText2,
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
                  style: Theme.of(context).textTheme.bodyText1,
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

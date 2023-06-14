// Cannlytics Data
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 5/11/2023
// Updated: 6/14/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Flutter imports:
import 'package:cannlytics_data/models/lab_result.dart';
import 'package:cannlytics_data/ui/results/results_form.dart';
import 'package:cannlytics_data/ui/results/results_service.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';

// Package imports:
import 'package:dotted_border/dotted_border.dart';
import 'package:file_picker/file_picker.dart';
import 'package:flutter_dropzone/flutter_dropzone.dart';
import 'package:hooks_riverpod/hooks_riverpod.dart';
import 'package:mobile_scanner/mobile_scanner.dart';

// Project imports:
import 'package:cannlytics_data/common/buttons/secondary_button.dart';
import 'package:cannlytics_data/constants/design.dart';
import 'package:cannlytics_data/constants/theme.dart';

class CoADocInterface extends HookConsumerWidget {
  CoADocInterface({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    // Listen the the COA parser provider.
    final asyncResults = ref.watch(coaParser);

    // Dynamic rendering.
    return asyncResults.when(
      // Data loaded state.
      data: (items) => (items.length == 0)
          ? _body(context, ref, child: CoAUpload())
          : Card(
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
                    // Title.
                    Row(
                      children: [
                        Text(
                          'Parsed lab results',
                          style: Theme.of(context).textTheme.titleLarge,
                        ),
                        Spacer(),
                        IconButton(
                          icon: const Icon(Icons.refresh),
                          onPressed: () {
                            ref.read(coaParser.notifier).clearResults();
                          },
                        ),
                      ],
                    ),
                    gapH16,

                    // List of parsed lab results.
                    Expanded(
                      child: ListView(
                        shrinkWrap: true,
                        children: [
                          for (final item in items)
                            LabResultItem(
                              labResult: LabResult.fromMap(item ?? {}),
                            ),
                        ],
                      ),
                    ),
                  ],
                ),
              ),
            ),

      // Loading state.
      loading: () => _body(context, ref, child: ParsingResultsPlaceholder()),

      // Error state.
      error: (err, stack) => _errorMessage(context),
    );
  }

  /// Message displayed when an error occurs.
  Widget _errorMessage(BuildContext context) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            // Image.
            Padding(
              padding: EdgeInsets.only(top: 16),
              child: ClipOval(
                child: Image.network(
                  'https://firebasestorage.googleapis.com/v0/b/cannlytics.appspot.com/o/assets%2Fimages%2Fai%2FCannlytics_a_scroll_with_robot_arms_and_a_disguise_for_a_face_a_57549317-7365-4350-9b7b-84fd7421b103.png?alt=media&token=72631010-56c8-4981-a936-58b89294f336',
                  width: 128,
                  height: 128,
                  fit: BoxFit.cover,
                ),
              ),
            ),
            // Text.
            Container(
              width: 540,
              child: Column(
                children: <Widget>[
                  SelectableText(
                    'An error occurred while parsing your COAs',
                    textAlign: TextAlign.center,
                    style: TextStyle(
                        fontSize: 20,
                        color: Theme.of(context).textTheme.titleLarge!.color),
                  ),
                  SelectableText(
                    'An unknown error occurred while parsing your COAs. Please report this issue on GitHub or to dev@cannlytics.com to get a human to help ASAP.',
                    textAlign: TextAlign.center,
                    style: Theme.of(context).textTheme.bodySmall,
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  /// The main dynamic body of the screen.
  Widget _body(BuildContext context, WidgetRef ref, {required Widget child}) {
    return SingleChildScrollView(
      child: Column(
        children: [
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
                      // Title.
                      Text(
                        'Parse lab results',
                        style: Theme.of(context).textTheme.titleLarge,
                      ),

                      // Parse COA URL textfield.
                      gapH12,
                      SizedBox(
                        height: 42,
                        child: COASearch(),
                      ),

                      // COA upload actions.
                      gapH24,
                      Row(
                        children: [
                          // Subtitle.
                          Text(
                            'File Upload',
                            style: Theme.of(context).textTheme.labelMedium,
                          ),

                          // Tooltip.
                          IconButton(
                            icon: Icon(Icons.info_outline),
                            onPressed: () {},
                            tooltip:
                                'We support most COA formats: .pdf, .png, .jpeg, and .jpg',
                          ),
                          Spacer(),

                          // Upload COAs button.
                          // FIXME: Make disabled when parsing.
                          SecondaryButton(
                            text: 'Upload COAs',
                            onPressed: () async {
                              FilePickerResult? result =
                                  await FilePicker.platform.pickFiles(
                                type: FileType.custom,
                                allowedExtensions: [
                                  'pdf',
                                  'zip',
                                  'jpeg',
                                  'png'
                                ],
                              );
                              if (result != null) {
                                // Parse COAs.
                                ref
                                    .read(coaParser.notifier)
                                    .parseCOAs(result.files);
                              } else {
                                // User canceled the picker
                              }
                            },
                          ),
                        ],
                      ),

                      // Dynamic widget.
                      gapH4,
                      child,
                      gapH12,
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
}

/// COA upload.
class CoAUpload extends ConsumerWidget {
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    // ignore: unused_local_variable
    late DropzoneViewController controller;
    final themeMode = ref.watch(themeModeProvider);
    final bool isDark = themeMode == ThemeMode.dark;
    return Column(
      children: <Widget>[
        Row(
          children: <Widget>[
            // Drag and drop file input.
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
                              // onLoaded: () => print('Zone 1 loaded'),
                              // onError: (ev) => print('Zone 1 error: $ev'),
                              // onHover: () {
                              //   // print('Zone 1 hovered');
                              // },
                              // onLeave: () {
                              //   // print('Zone 1 left');
                              // },
                              // onDrop: (ev) async {
                              //   print('Zone 1 drop: ${ev.name}');
                              //   final bytes = await controller.getFileData(ev);
                              //   print(bytes.sublist(0, 20));
                              // },
                              onDropMultiple: (files) async {
                                if (files!.isNotEmpty)
                                  ref.read(coaParser.notifier).parseCOAs(files);
                              },
                            ),

                            // Text.
                            Center(child: LabResultsPlaceholder()),
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
                          allowedExtensions: ['pdf', 'zip', 'jpeg', 'png'],
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
                      // final Uint8List? image = capture.image;
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

/// Lab results placeholder.
class LabResultsPlaceholder extends StatelessWidget {
  final String? title;
  final String? subtitle;

  LabResultsPlaceholder({this.title, this.subtitle});

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
                      text: title ?? 'Waiting on your COAs boss!\n',
                      style: TextStyle(
                          fontSize: 20,
                          color:
                              Theme.of(context).textTheme.titleLarge!.color)),
                  TextSpan(
                      text: subtitle ??
                          'Drop a CoA PDF, image, or folder to parse.',
                      style: Theme.of(context).textTheme.bodySmall),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}

/// Parsing results placeholder.
class ParsingResultsPlaceholder extends StatefulWidget {
  final String? title;
  final String? subtitle;

  ParsingResultsPlaceholder({this.title, this.subtitle});

  @override
  _ParsingResultsPlaceholderState createState() =>
      _ParsingResultsPlaceholderState();
}

class _ParsingResultsPlaceholderState extends State<ParsingResultsPlaceholder>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _opacityAnimation;

  @override
  void initState() {
    super.initState();

    _controller = AnimationController(
      vsync: this,
      duration: const Duration(seconds: 2),
    )..repeat(reverse: true);

    _opacityAnimation =
        Tween<double>(begin: 0.33, end: 0.88).animate(_controller);
  }

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            // Image.
            Padding(
              padding: EdgeInsets.only(top: 16),
              child: AnimatedBuilder(
                animation: _opacityAnimation,
                builder: (context, child) => Opacity(
                  opacity: _opacityAnimation.value,
                  child: child,
                ),
                child: ClipOval(
                  child: Image.network(
                    'https://firebasestorage.googleapis.com/v0/b/cannlytics.appspot.com/o/assets%2Fimages%2Fai%2FCannlytics_Portrait_of_an_old_republic_data_parser_wizard_in_th_2ccc0074-2eba-4b05-b642-c0f648e266b6.png?alt=media&token=9e409eb8-de58-4528-b395-5c32c4f4a488',
                    width: 128,
                    height: 128,
                    fit: BoxFit.cover,
                  ),
                ),
              ),
            ),
            // Text.
            Container(
              width: 540,
              child: Column(
                children: <Widget>[
                  SelectableText(
                    widget.title ?? 'Parsing your COAs!',
                    textAlign: TextAlign.center,
                    style: TextStyle(
                        fontSize: 20,
                        color: Theme.of(context).textTheme.titleLarge!.color),
                  ),
                  SelectableText(
                    widget.subtitle ??
                        'Parsing results can take a while. Results from validated labs and LIMS will be parsed faster and with a high-degree of accuracy while all other results are parsed with AI. Results parsed with AI take longer, have uncertain results, and should be validated.',
                    textAlign: TextAlign.center,
                    style: Theme.of(context).textTheme.bodySmall,
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }
}

/// COA search.
class COASearch extends ConsumerWidget {
  final TextEditingController coaSearchController = TextEditingController();
  final TextEditingController coaUrlController = TextEditingController();

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return Column(
      children: <Widget>[
        Stack(
          alignment: Alignment.centerRight,
          children: <Widget>[
            TextFormField(
              key: Key('resultsSearch'),
              controller: coaSearchController,
              autocorrect: false,
              decoration: InputDecoration(
                // FIXME: Disable when parsing.
                // enabled: !state.isLoading,
                hintText: 'Enter a URL to parse...',
                contentPadding: EdgeInsets.only(
                  top: 18,
                  left: 8,
                  right: 50, // space for the search icon
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
              onFieldSubmitted: (value) {
                // Parse a COA URL.
                ref.read(coaParser.notifier).parseUrl(value);
              },
            ),
            _searchIcon(context, ref),
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

  /// Search icon.
  Widget _searchIcon(BuildContext context, WidgetRef ref) {
    return Padding(
      padding: const EdgeInsets.only(right: 10.0),
      child: InkWell(
        onTap: () {
          // Parse a COA URL.
          String value = coaSearchController.text;
          ref.read(coaParser.notifier).parseUrl(value);
        },
        child: Icon(
          Icons.search_sharp,
          color: Theme.of(context).textTheme.labelMedium!.color,
        ),
      ),
    );
  }
}

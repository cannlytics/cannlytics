// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 6/15/2023
// Updated: 7/2/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Flutter imports:
import 'package:cannlytics_data/models/sales_receipt.dart';
import 'package:cannlytics_data/ui/sales/receipt_card.dart';
import 'package:cannlytics_data/ui/sales/receipts_service.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';

// Package imports:
import 'package:dotted_border/dotted_border.dart';
import 'package:file_picker/file_picker.dart';
import 'package:flutter_dropzone/flutter_dropzone.dart';
import 'package:hooks_riverpod/hooks_riverpod.dart';

// Project imports:
import 'package:cannlytics_data/common/buttons/secondary_button.dart';
import 'package:cannlytics_data/constants/design.dart';
import 'package:cannlytics_data/constants/theme.dart';

/// Receipts parser interface.
class ReceiptsParserInterface extends HookConsumerWidget {
  ReceiptsParserInterface({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    // Listen the the receipts parser provider.
    final asyncData = ref.watch(receiptParser);

    // Dynamic rendering.
    return asyncData.when(
      // Loading state.
      loading: () => _body(context, ref, child: ParsingPlaceholder()),

      // Error state.
      error: (err, stack) => _errorMessage(context, ref, err.toString()),

      // Data loaded state.
      data: (items) => (items.length == 0)
          ? _body(context, ref, child: ReceiptUpload())
          : ReceiptsParserForm(items: items, ref: ref),
    );
  }

  /// Message displayed when an error occurs.
  Widget _errorMessage(BuildContext context, WidgetRef ref, String? message) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            // Reset button.
            Row(
              mainAxisAlignment: MainAxisAlignment.end,
              children: [
                IconButton(
                  icon: Icon(
                    Icons.refresh,
                    color: Theme.of(context).textTheme.bodyMedium!.color,
                  ),
                  onPressed: () {
                    ref.read(receiptParser.notifier).clear();
                  },
                ),
              ],
            ),

            // Image.
            Padding(
              padding: EdgeInsets.only(top: 16),
              child: ClipOval(
                child: Image.network(
                  'https://firebasestorage.googleapis.com/v0/b/cannlytics.appspot.com/o/public%2Fimages%2Flogos%2Fbud_spender.png?alt=media&token=e0de707b-9c18-44b9-9944-b36fcffd9fd3',
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
                    'An error occurred while parsing your receipts',
                    textAlign: TextAlign.center,
                    style: TextStyle(
                        fontSize: 20,
                        color: Theme.of(context).textTheme.titleLarge!.color),
                  ),
                  // DEV:
                  SelectableText(
                    message ?? '',
                    textAlign: TextAlign.center,
                    style: Theme.of(context).textTheme.bodyMedium,
                  ),
                  // PRODUCTION:
                  // SelectableText(
                  //   'An unknown error occurred while parsing your receipts. Please report this issue on GitHub or to dev@cannlytics.com to get a human to help ASAP.',
                  //   textAlign: TextAlign.center,
                  //   style: Theme.of(context).textTheme.bodyMedium,
                  // ),
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
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.start,
          crossAxisAlignment: CrossAxisAlignment.start,
          mainAxisSize: MainAxisSize.min,
          children: <Widget>[
            // Title.
            Text(
              'Parse receipts',
              style: Theme.of(context).textTheme.titleLarge,
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
                      'We support most image formats: .png, .jpeg, and .jpg',
                ),
                Spacer(),

                // Upload receipts button.
                // TODO: Make disabled when parsing.
                SecondaryButton(
                  text: 'Upload receipts',
                  onPressed: () async {
                    FilePickerResult? result =
                        await FilePicker.platform.pickFiles(
                      type: FileType.custom,
                      allowedExtensions: ['jpg', 'jpeg', 'png'],
                      withData: true,
                      withReadStream: false,
                    );
                    if (result != null) {
                      ref
                          .read(receiptParser.notifier)
                          .parseImages(result.files);
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
    );
  }
}

/// Receipt parsing form
class ReceiptsParserForm extends StatelessWidget {
  ReceiptsParserForm({required this.items, required this.ref});

  // Parameters.
  final List<Map<dynamic, dynamic>?> items;
  final WidgetRef ref;

  @override
  Widget build(BuildContext context) {
    return Card(
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
                SelectableText(
                  'Parsed receipts',
                  style: Theme.of(context).textTheme.titleLarge,
                ),
                Spacer(),
                IconButton(
                  icon: Icon(
                    Icons.refresh,
                    color: Theme.of(context).textTheme.bodyMedium!.color,
                  ),
                  onPressed: () {
                    ref.read(receiptParser.notifier).clear();
                  },
                ),
              ],
            ),
            gapH16,

            // Grid of parsed receipts.
            Expanded(
              child: ListView(
                shrinkWrap: true,
                children: [
                  for (final item in items)
                    ReceiptCard(
                      item: SalesReceipt.fromMap(item ?? {}),
                    ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}

/// Receipt upload.
class ReceiptUpload extends ConsumerWidget {
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    // ignore: unused_local_variable
    late DropzoneViewController controller;
    final themeMode = ref.watch(themeModeProvider);
    final bool isDark = themeMode == ThemeMode.dark;

    // Dropzone.
    _dropzone() {
      return DropzoneView(
        operation: DragOperation.copy,
        cursor: CursorType.grab,
        onCreated: (ctrl) => controller = ctrl,
        onDropMultiple: (files) async {
          if (files!.isNotEmpty) {
            var imageFilesFutures = <Future>[];
            var fileNamesFutures = <Future>[];
            for (var file in files) {
              imageFilesFutures.add(controller.getFileData(file));
              fileNamesFutures.add(controller.getFilename(file));
            }
            var imageBytes = await Future.wait(imageFilesFutures);
            var fileNames = await Future.wait(fileNamesFutures);
            List<List<int>> imageFiles = imageBytes.map<List<int>>((item) {
              return item as List<int>;
            }).toList();
            ref
                .read(receiptParser.notifier)
                .parseImages(imageFiles, fileNames: fileNames);
          }
        },
      );
    }

    // Render the widget.
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
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
                            _dropzone(),

                            // Text.
                            Center(child: ReceiptsPlaceholder()),
                          ],
                        ),
                      ),
                    ),
                ],
              ),
            ),
          ],
        ),

        // Notes informing user of data usage.
        gapH24,
        Container(
          width: 540,
          child: SelectableText(
            'Note: Data extraction can take a while. Please note that receipts are parsed with AI and the data is an approximation, may contain incorrect values, and should be validated. Your data is private, but may be used to calculate aggregate statistics while preserving your anonymity.',
            textAlign: TextAlign.start,
            style: Theme.of(context).textTheme.bodyMedium,
          ),
        ),
      ],
    );
  }
}

/// Receipts placeholder.
class ReceiptsPlaceholder extends StatelessWidget {
  ReceiptsPlaceholder({this.title, this.subtitle});

  // Parameters.
  final String? title;
  final String? subtitle;

  @override
  Widget build(BuildContext context) {
    // Dynamic image size.
    final screenWidth = MediaQuery.of(context).size.width;
    final double imageSize = screenWidth < 600 ? 96 : 128;

    // Render.
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          children: [
            // Image.
            ClipRRect(
              borderRadius: BorderRadius.circular(8),
              child: Image.network(
                'https://firebasestorage.googleapis.com/v0/b/cannlytics.appspot.com/o/public%2Fimages%2Flogos%2Fbud_spender.png?alt=media&token=e0de707b-9c18-44b9-9944-b36fcffd9fd3',
                width: imageSize,
                height: imageSize,
              ),
            ),
            // Text.
            RichText(
              textAlign: TextAlign.center,
              text: TextSpan(
                style: DefaultTextStyle.of(context).style,
                children: <TextSpan>[
                  TextSpan(
                      text: title ??
                          'Happy to organize your receipts, monsieur.\n',
                      style: TextStyle(
                          fontSize: 20,
                          color:
                              Theme.of(context).textTheme.titleLarge!.color)),
                  TextSpan(
                      text: subtitle ?? 'You may add your receipt images here.',
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

/// Parsing receipts placeholder.
class ParsingPlaceholder extends StatefulWidget {
  ParsingPlaceholder({this.title, this.subtitle});

  // Parameters.
  final String? title;
  final String? subtitle;

  @override
  _ParsingPlaceholderState createState() => _ParsingPlaceholderState();
}

/// Parsing receipts placeholder state.
class _ParsingPlaceholderState extends State<ParsingPlaceholder>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _opacityAnimation;

  @override
  void initState() {
    super.initState();

    // Fade the image in and out.
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
                    'https://firebasestorage.googleapis.com/v0/b/cannlytics.appspot.com/o/public%2Fimages%2Flogos%2Fbud_spender.png?alt=media&token=e0de707b-9c18-44b9-9944-b36fcffd9fd3',
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
                    widget.title ?? 'Parsing your receipts',
                    textAlign: TextAlign.center,
                    style: TextStyle(
                        fontSize: 20,
                        color: Theme.of(context).textTheme.titleLarge!.color),
                  ),
                  SelectableText(
                    widget.subtitle ??
                        'Data extraction can take a while. Please note that receipts are parsed with AI and the data is an approximation, may contain incorrect values, and should be validated.',
                    textAlign: TextAlign.center,
                    style: Theme.of(context).textTheme.bodyMedium,
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

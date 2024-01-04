// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 6/15/2023
// Updated: 9/10/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Flutter imports:
import 'package:cannlytics_data/utils/utils.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:path/path.dart' as path;

// Package imports:
import 'package:dotted_border/dotted_border.dart';
import 'package:file_picker/file_picker.dart';
import 'package:flutter_dropzone/flutter_dropzone.dart';
import 'package:hooks_riverpod/hooks_riverpod.dart';

// Project imports:
import 'package:cannlytics_data/common/buttons/primary_button.dart';
import 'package:cannlytics_data/common/dialogs/auth_dialog.dart';
import 'package:cannlytics_data/common/forms/job_list.dart';
import 'package:cannlytics_data/common/layout/sign_in_placeholder.dart';
import 'package:cannlytics_data/constants/design.dart';
import 'package:cannlytics_data/constants/theme.dart';
import 'package:cannlytics_data/ui/account/account_controller.dart';
import 'package:cannlytics_data/ui/sales/receipts_service.dart';

/// Receipts parser interface.
class ReceiptsParserInterface extends HookConsumerWidget {
  ReceiptsParserInterface({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    // Listen the the receipts parser provider.
    final asyncData = ref.watch(receiptParser);

    // No-user interface.
    final user = ref.watch(userProvider).value;
    if (user == null) return _noUser(context);

    // Dynamic rendering.
    return asyncData.when(
      data: (items) => _dataLoaded(context, ref, items: items),
      loading: () => _body(context, ref, child: ParsingPlaceholder()),
      error: (err, stack) => _errorMessage(context, ref, err.toString()),
    );
  }

  /// Data loaded interface.
  Widget _dataLoaded(BuildContext context, WidgetRef ref, {dynamic items}) {
    final asyncJobs = ref.watch(receiptJobsProvider);
    return asyncJobs.when(
      data: (jobs) => _parsingJobs(
        context,
        ref,
        items: jobs.where((job) => job != null).toList(),
      ),
      error: (err, stack) => Padding(
        padding: const EdgeInsets.all(16.0),
        child: Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.start,
            children: <Widget>[
              Icon(Icons.error, color: Colors.red, size: 48.0),
              SizedBox(height: 16),
              SelectableText(
                'An error occurred while loading jobs: $err',
                textAlign: TextAlign.center,
                style: Theme.of(context).textTheme.titleMedium,
              ),
            ],
          ),
        ),
      ),
      loading: () => Padding(
        padding: const EdgeInsets.all(16.0),
        child: Center(
          child: CircularProgressIndicator(),
        ),
      ),
    );
    // return Column(
    //   mainAxisAlignment: MainAxisAlignment.start,
    //   crossAxisAlignment: CrossAxisAlignment.start,
    //   mainAxisSize: MainAxisSize.min,
    //   children: [
    //     _body(context, ref, child: ReceiptUpload()),
    //   ],
    // );
  }

  /// No user interface.
  Widget _noUser(BuildContext context) {
    return Column(
      mainAxisAlignment: MainAxisAlignment.start,
      crossAxisAlignment: CrossAxisAlignment.start,
      mainAxisSize: MainAxisSize.min,
      children: [
        SignInPlaceholder(
          titleText: 'Parse receipts',
          imageUrl:
              'https://firebasestorage.googleapis.com/v0/b/cannlytics.appspot.com/o/public%2Fimages%2Flogos%2Fbud_spender.png?alt=media&token=e0de707b-9c18-44b9-9944-b36fcffd9fd3',
          mainText: 'Sign in to parse your receipts',
          subTitle:
              'If you are signed in, then you can extract data from your receipts.',
          onButtonPressed: () {
            showDialog(
              context: context,
              builder: (BuildContext context) => SignInDialog(isSignUp: false),
            );
          },
          buttonText: 'Sign in',
        ),
      ],
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

  /// Parsing jobs.
  Widget _parsingJobs(BuildContext context, WidgetRef ref, {required items}) {
    JobConfig receiptsConfig = JobConfig(
      title: 'Receipt: ',
      downloadApiPath: '/api/data/receipts/download',
      deleteJobFunction: (uid, jobId) =>
          ref.read(receiptParser.notifier).deleteJob(uid, jobId),
      retryJobFunction: (uid, jobId) =>
          ref.read(receiptParser.notifier).retryJob(uid, jobId),
    );
    // return Padding(
    //   padding: const EdgeInsets.all(16.0),
    //   child: Column(
    //     mainAxisAlignment: MainAxisAlignment.start,
    //     crossAxisAlignment: CrossAxisAlignment.start,
    //     mainAxisSize: MainAxisSize.min,
    //     children: <Widget>[
    return SingleChildScrollView(
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          children: [
            // Receipt upload.
            _body(context, ref, child: ReceiptUpload()),

            // Parsing jobs.
            gapH16,
            Row(
              children: [
                Text(
                  'Parsing jobs',
                  style: Theme.of(context).textTheme.titleLarge,
                ),
                Spacer(),
              ],
            ),
            gapH16,

            // List of parsed lab results.
            items.isEmpty
                ? _placeholder(context, ref)
                : ListView(
                    shrinkWrap: true,
                    children: [
                      for (final item in items)
                        JobItem(item: item, config: receiptsConfig),
                    ],
                  ),
          ],
        ),
      ),
    );
  }

  /// Message displayed when there are no jobs.
  Widget _placeholder(BuildContext context, WidgetRef ref) {
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
                  'https://firebasestorage.googleapis.com/v0/b/cannlytics.appspot.com/o/assets%2Fimages%2Ficons%2Fai-icons%2Fcannabis-receipt.png?alt=media&token=f56d630d-1f4a-4024-bd2c-899fc1f924f4',
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
                    'No current jobs',
                    textAlign: TextAlign.center,
                    style: TextStyle(
                        fontSize: 20,
                        color: Theme.of(context).textTheme.titleLarge!.color),
                  ),
                  SelectableText(
                    'You can monitor your receipt parsing jobs here.',
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

  /// The main dynamic body of the screen.
  Widget _body(BuildContext context, WidgetRef ref, {required Widget child}) {
    return Column(
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
              tooltip: 'We support most image formats: .png, .jpeg, and .jpg',
            ),
            Spacer(),

            // Upload receipts button.
            // TODO: Make disabled when parsing.
            PrimaryButton(
              text: 'Upload receipts',
              onPressed: () async {
                FilePickerResult? result = await FilePicker.platform.pickFiles(
                  type: FileType.custom,
                  allowedExtensions: ['jpg', 'jpeg', 'png'],
                  withData: true,
                  withReadStream: false,
                );
                if (result != null) {
                  List<String> extensions = result.files
                      .map((file) => path.extension(file.name).substring(1))
                      .toList();

                  List<String> fileNames =
                      result.files.map((file) => file.name).toList();

                  // This gives a list of Uint8List for each file
                  List<List<int>> imageFiles =
                      result.files.map((file) => file.bytes!).toList();

                  ref.read(receiptParser.notifier).parseImages(
                        imageFiles,
                        fileNames: fileNames,
                        extensions: extensions,
                      );
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
            // Get file data.
            var imageFilesFutures = <Future>[];
            var fileNamesFutures = <Future>[];
            var mimeTypesFutures = <Future>[];
            for (var file in files) {
              imageFilesFutures.add(controller.getFileData(file));
              fileNamesFutures.add(controller.getFilename(file));
              mimeTypesFutures.add(controller.getFileMIME(file));
            }
            var imageBytes = await Future.wait(imageFilesFutures);
            var fileNames = await Future.wait(fileNamesFutures);
            var mimeTypes = await Future.wait(mimeTypesFutures);
            List<String> extensions =
                mimeTypes.map(ApiUtils.getExtensionFromMimeType).toList();

            // Convert files to lists of bytes.
            List<List<int>> imageFiles = imageBytes.map<List<int>>((item) {
              return item as List<int>;
            }).toList();

            // Parse files.
            ref.read(receiptParser.notifier).parseImages(
                  imageFiles,
                  fileNames: fileNames,
                  extensions: extensions,
                );
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

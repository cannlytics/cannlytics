// Cannlytics Data
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 6/11/2023
// Updated: 9/12/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Flutter imports:
import 'dart:convert';

import 'package:cannlytics_data/common/layout/search_placeholder.dart';
import 'package:cannlytics_data/ui/account/account_controller.dart';
import 'package:cannlytics_data/ui/results/result_coa.dart';
import 'package:flutter/material.dart';
import 'package:flutter_material_color_picker/flutter_material_color_picker.dart';

// Package imports:
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:internet_file/internet_file.dart';
import 'package:pdfx/pdfx.dart';
import 'package:url_launcher/url_launcher.dart';

// Project imports:
import 'package:cannlytics_data/common/buttons/download_button.dart';
import 'package:cannlytics_data/common/buttons/primary_button.dart';
import 'package:cannlytics_data/common/buttons/secondary_button.dart';
import 'package:cannlytics_data/common/forms/custom_text_field.dart';
import 'package:cannlytics_data/common/forms/forms.dart';
import 'package:cannlytics_data/common/layout/breadcrumbs.dart';
import 'package:cannlytics_data/common/layout/loading_placeholder.dart';
import 'package:cannlytics_data/common/layout/pill_tab.dart';
import 'package:cannlytics_data/common/tables/key_value_datatable.dart';
import 'package:cannlytics_data/constants/colors.dart';
import 'package:cannlytics_data/constants/design.dart';
import 'package:cannlytics_data/models/lab_result.dart';
import 'package:cannlytics_data/ui/layout/console.dart';
import 'package:cannlytics_data/ui/results/result_table.dart';
import 'package:cannlytics_data/ui/results/results_service.dart';
import 'package:cannlytics_data/utils/utils.dart';

/* === Logic ===*/

/// PDF URL provider.
final pdfUrlProvider = StateProvider<String>((ref) => '');

/// PDF controller provider.
final pdfControllerProvider =
    FutureProvider.family.autoDispose<PdfController?, String>((ref, url) async {
  // String url = ref.watch(pdfUrlProvider);
  if (url.isEmpty) return null;
  var data = await InternetFile.get(url);
  return PdfController(document: PdfDocument.openData(data));
});

/* === UI ===*/

/// Result screen.
class ResultScreen extends ConsumerStatefulWidget {
  ResultScreen({
    Key? key,
    this.labResult,
    this.labResultId,
  }) : super(key: key);

  // Properties
  final LabResult? labResult;
  final String? labResultId;

  @override
  _ResultScreenState createState() => _ResultScreenState();
}

/// Result screen state.
class _ResultScreenState extends ConsumerState<ResultScreen>
    with SingleTickerProviderStateMixin {
  // State.
  bool _isEditing = false;
  // static const int _initialPage = 1;
  late PdfController? _pdfController;
  late String? _pdfUrl;
  late final TabController _tabController;
  int _tabCount = 3;
  String? _updateFuture;

  // Initialize.
  @override
  void initState() {
    super.initState();

    // Initialize tabs.
    _tabController = TabController(length: _tabCount, vsync: this);
    _tabController.addListener(() => setState(() {}));
  }

  // Dispose of the controllers.
  @override
  void dispose() {
    _pdfController?.dispose();
    _tabController.dispose();
    super.dispose();
  }

  // Render the screen.
  @override
  Widget build(BuildContext context) {
    if (widget.labResult != null) return _form(widget.labResult);
    final asyncData = ref.watch(labResultProvider(widget.labResultId!));
    return asyncData.when(
      // Loading UI.
      loading: () => MainContent(
        child: LoadingPlaceholder(),
        fillRemaining: true,
      ),

      // Error UI.
      error: (err, stack) {
        return MainContent(
          child: SelectableText('Error: $err'),
        );
      },

      // Data loaded UI.
      data: (labResult) => _form(labResult),
    );
  }

  /// Form.
  Widget _form(LabResult? labResult) {
    // Style.
    bool isDark = Theme.of(context).brightness == Brightness.dark;
    var labelPadding = EdgeInsets.only(left: 16, right: 16, top: 16, bottom: 8);
    var labelStyle = Theme.of(context).textTheme.labelMedium?.copyWith(
          fontWeight: FontWeight.bold,
        );

    // Screen size.
    bool isMobile = MediaQuery.of(context).size.width < 600;

    /// Edit a field.
    void _onEdit(key, value) {
      ref.read(updatedLabResult.notifier).update((state) {
        var update = state?.toMap() ?? {};
        var parsedValue = double.tryParse(value);
        update[key] = parsedValue ?? value;
        List<Map<String, dynamic>> mapResults =
            ref.read(analysisResults).map((result) => result!.toMap()).toList();
        String jsonEncodedResults = jsonEncode(mapResults);
        update['results'] = jsonEncodedResults;
        return LabResult.fromMap(update);
      });
    }

    /// Cancel edit.
    void _cancelEdit() {
      // Reset analysis results.
      ref.read(analysisResults.notifier).update(labResult?.results ?? []);

      // Cancel editing.
      setState(() {
        _isEditing = !_isEditing;
      });
    }

    /// Save edit.
    void _saveEdit() async {
      // Update any modified details.
      var update = ref.read(updatedLabResult)?.toMap() ?? {};

      // // Update any modified results.
      // List<Map<String, dynamic>> mapResults =
      //     ref.read(analysisResults).map((result) => result!.toMap()).toList();
      // String jsonEncodedResults = jsonEncode(mapResults);
      // update['results'] = jsonEncodedResults;

      // Update the data in Firestore.
      update['updated_at'] = DateTime.now().toUtc().toIso8601String();
      _updateFuture = await ref.read(resultService).updateResult(
            widget.labResultId ?? widget.labResult?.sampleId ?? '',
            update,
          );

      // TODO: Create a log.

      // Show notification snackbar.
      if (_updateFuture == 'success') {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(
              'Lab result saved',
              style: Theme.of(context).textTheme.bodyMedium,
            ),
            duration: Duration(seconds: 2),
            backgroundColor: isDark ? DarkColors.green : LightColors.lightGreen,
            showCloseIcon: true,
          ),
        );
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Error saving lab result'),
            duration: Duration(seconds: 4),
            backgroundColor:
                isDark ? DarkColors.darkOrange : LightColors.darkOrange,
            showCloseIcon: true,
          ),
        );
      }

      // Finish editing.
      setState(() {
        _isEditing = !_isEditing;
        _updateFuture = null;
      });
    }

    // Breadcrumbs.
    var _breadcrumbs = SliverToBoxAdapter(
      child: BreadcrumbsRow(
        items: [
          {'label': 'Data', 'path': '/'},
          {'label': 'Lab Results', 'path': '/results'},
          {'label': 'Result', 'path': '/results/${labResult?.sampleId}'},
        ],
      ),
    );

    // Detail data table.
    var fieldStyle = Theme.of(context).textTheme.bodySmall;
    var fields = [
      // Sample data.
      KeyValueDataTable(
        tableName: 'Sample',
        labels: [
          'Product Name',
          'Strain Name',
          'Product Type',
          'Traceability IDs',
        ],
        values: [
          Text('${labResult?.productName}', style: fieldStyle),
          InkWell(
            child: Text('${labResult?.strainName}', style: fieldStyle),
            onTap: () {
              var publicKey = labResult?.strainName;
              var hash = DataUtils.createHash(publicKey, privateKey: '');
              context.go('/strains/$hash');
            },
          ),
          Text('${labResult?.productType}', style: fieldStyle),
          Wrap(
            spacing: 4.0,
            children: labResult?.traceabilityIds != null
                ? labResult?.traceabilityIds
                    .map<Widget>((x) => Text('${x}', style: fieldStyle))
                    .toList()
                : [Container()],
          ),
        ],
      ),
      gapH24,

      // Compound details.
      KeyValueDataTable(
        tableName: 'Metrics',
        labels: [
          'Total Cannabinoids',
          'Total THC',
          'Total CBD',
          'Total Terpenes',
          'Product Size',
          'Serving Size',
          'Servings Per Package',
        ],
        values: [
          Text('${labResult?.totalCannabinoids}', style: fieldStyle),
          Text('${labResult?.totalThc}', style: fieldStyle),
          Text('${labResult?.totalCbd}', style: fieldStyle),
          Text('${labResult?.totalTerpenes}', style: fieldStyle),
          Text('${labResult?.productSize}', style: fieldStyle),
          Text('${labResult?.servingSize}', style: fieldStyle),
          Text('${labResult?.servingsPerPackage}', style: fieldStyle),
        ],
      ),
      gapH24,

      // Analytics data.
      KeyValueDataTable(
        tableName: 'Analytics',
        labels: ['Cannabinoid Type'],
        values: <Widget>[
          Text('${labResult?.cannabinoidType}', style: fieldStyle),
        ],
      ),
      gapH24,

      // Analysis data.
      KeyValueDataTable(
        tableName: 'Analysis',
        labels: [
          'Status',
          'Analyses',
          'Batch Number',
          'Date Tested',
          'Date Received',
          'Sample Weight',
        ],
        values: <Widget>[
          StatusPill(labResult?.status ?? ''),
          Wrap(
            spacing: 4.0,
            children: labResult?.analyses != null
                ? labResult?.analyses
                    .map<Widget>((analysis) => AnalysisPill(analysis))
                    .toList()
                : [Container()],
          ),
          Text('${labResult?.batchNumber}', style: fieldStyle),
          Text('${labResult?.dateTested}', style: fieldStyle),
          Text('${labResult?.dateReceived}', style: fieldStyle),
          Text('${labResult?.sampleWeight}', style: fieldStyle),
        ],
      ),
      gapH24,

      // Producer details.
      KeyValueDataTable(
        tableName: 'Producer',
        labels: [
          'Producer',
          'Producer Address',
          'Producer License Number',
        ],
        values: [
          InkWell(
            child: Text('${labResult?.producer}', style: fieldStyle),
            onTap: () {
              var state = labResult?.producerState?.toLowerCase() ?? 'all';
              var id = labResult?.producerLicenseNumber;
              if (id != null) context.go('/licenses/$state/$id');
            },
          ),
          Text('${labResult?.producerAddress}', style: fieldStyle),
          Text('${labResult?.producerLicenseNumber}', style: fieldStyle),
        ],
      ),
      gapH24,

      // Distributor details.
      KeyValueDataTable(
        tableName: 'Distributor',
        labels: [
          'Distributor',
          'Distributor Address',
          'Distributor License Number',
        ],
        values: [
          InkWell(
            child: Text('${labResult?.distributor}', style: fieldStyle),
            onTap: () {
              var state = labResult?.distributorState?.toLowerCase() ?? 'all';
              var id = labResult?.distributorLicenseNumber;
              if (id != null) context.go('/licenses/$state/$id');
            },
          ),
          Text('${labResult?.distributorAddress}', style: fieldStyle),
          Text('${labResult?.distributorLicenseNumber}', style: fieldStyle),
        ],
      ),
      gapH24,

      // Lab details.
      KeyValueDataTable(
        tableName: 'Lab',
        labels: [
          'Lab ID',
          'Lab',
          'LIMS',
          'Lab Address',
          'Lab Phone',
          'Lab Email',
          'Lab Website',
        ],
        values: [
          Text('${labResult?.labId}', style: fieldStyle),
          InkWell(
            child: Text('${labResult?.lab}', style: fieldStyle),
            onTap: () {
              var state = labResult?.producerState?.toLowerCase() ?? 'all';
              var id = labResult?.labLicenseNumber;
              if (id != null) context.go('/licenses/$state/$id');
            },
          ),
          Text('${labResult?.lims}', style: fieldStyle),
          Text('${labResult?.labAddress}', style: fieldStyle),
          Text('${labResult?.labPhone}', style: fieldStyle),
          Text('${labResult?.labEmail}', style: fieldStyle),
          Text('${labResult?.labWebsite}', style: fieldStyle),
        ],
      ),
      gapH24,

      // Parsing details.
      KeyValueDataTable(
        tableName: 'Details',
        labels: [
          'COA Algorithm',
          'COA Algorithm Version',
          'COA Parsed At',
          'Download URL',
          'Short URL',
        ],
        values: [
          Text('${labResult?.coaAlgorithm}', style: fieldStyle),
          Text('${labResult?.coaAlgorithmVersion}', style: fieldStyle),
          Text('${labResult?.coaParsedAt}', style: fieldStyle),
          InkWell(
            child: Text('${labResult?.downloadUrl}', style: fieldStyle),
            onTap: () {
              if (labResult?.downloadUrl != null) {
                launchUrl(Uri.parse(labResult?.downloadUrl ?? ''));
              }
            },
          ),
          InkWell(
            child: Text('${labResult?.shortUrl}', style: fieldStyle),
            onTap: () {
              if (labResult?.shortUrl != null) {
                launchUrl(Uri.parse(labResult?.shortUrl ?? ''));
              }
            },
          ),
        ],
      ),
      gapH48,
    ];

    // Text fields.
    var textFormFields = [
      // Sample details.
      Padding(
        padding: labelPadding,
        child: SelectableText('Sample', style: labelStyle),
      ),
      CustomTextField(
        label: 'Product Name',
        value: labResult?.productName,
        onChanged: (value) => _onEdit('product_name', value),
      ),
      CustomTextField(
        label: 'Strain Name',
        value: labResult?.strainName,
        onChanged: (value) => _onEdit('strain_name', value),
      ),
      CustomTextField(
        label: 'Product Type',
        value: labResult?.productType,
        onChanged: (value) => _onEdit('product_type', value),
      ),
      CustomTextField(
        label: 'Traceability IDs',
        value: labResult?.traceabilityIds,
        onChanged: (value) => _onEdit('traceability_ids', value),
      ),
      CustomTextField(
        label: 'Product Size',
        value: labResult?.productSize.toString(),
        onChanged: (value) => _onEdit('product_size', value),
        isNumeric: true,
      ),
      CustomTextField(
        label: 'Serving Size',
        value: labResult?.servingSize.toString(),
        onChanged: (value) => _onEdit('serving_size', value),
        isNumeric: true,
      ),
      CustomTextField(
        label: 'Servings Per Package',
        value: labResult?.servingsPerPackage.toString(),
        onChanged: (value) => _onEdit('servings_per_package', value),
        isNumeric: true,
      ),
      // Compound details.
      Padding(
        padding: labelPadding,
        child: SelectableText('Compound', style: labelStyle),
      ),
      CustomTextField(
        label: 'Total Cannabinoids',
        value: labResult?.totalCannabinoids.toString(),
        onChanged: (value) => _onEdit('total_cannabinoids', value),
        isNumeric: true,
      ),
      CustomTextField(
        label: 'Total THC',
        value: labResult?.totalThc.toString(),
        onChanged: (value) => _onEdit('total_thc', value),
        isNumeric: true,
      ),
      CustomTextField(
        label: 'Total CBD',
        value: labResult?.totalCbd.toString(),
        onChanged: (value) => _onEdit('total_cbd', value),
        isNumeric: true,
      ),
      CustomTextField(
        label: 'Total Terpenes',
        value: labResult?.totalTerpenes.toString(),
        onChanged: (value) => _onEdit('total_terpenes', value),
        isNumeric: true,
      ),

      // Analytics data.
      Padding(
        padding: labelPadding,
        child: SelectableText('Analytics', style: labelStyle),
      ),
      CustomTextField(
        label: 'Cannabinoid Type',
        value: labResult?.cannabinoidType,
        onChanged: (value) => _onEdit('cannabinoid_type', value),
      ),

      // Analysis data.
      Padding(
        padding: labelPadding,
        child: SelectableText('Analysis', style: labelStyle),
      ),
      CustomTextField(
        label: 'Analyses',
        value: labResult?.analyses,
        onChanged: (value) => _onEdit('analyses', value),
      ),
      CustomTextField(
        label: 'Status',
        value: labResult?.status,
        onChanged: (value) => _onEdit('status', value),
      ),
      CustomTextField(
        label: 'Batch Number',
        value: labResult?.batchNumber,
        onChanged: (value) => _onEdit('batch_number', value),
      ),
      CustomTextField(
        label: 'Analysis Status',
        value: labResult?.analysisStatus,
        onChanged: (value) => _onEdit('analysis_status', value),
      ),
      CustomTextField(
        label: 'Methods',
        value: labResult?.methods,
        onChanged: (value) => _onEdit('methods', value),
      ),
      CustomTextField(
        label: 'Date Collected',
        value: labResult?.dateCollected,
        onChanged: (value) => _onEdit('date_collected', value),
      ),
      CustomTextField(
        label: 'Date Tested',
        value: labResult?.dateTested,
        onChanged: (value) => _onEdit('date_tested', value),
      ),
      CustomTextField(
        label: 'Date Received',
        value: labResult?.dateReceived,
        onChanged: (value) => _onEdit('date_received', value),
      ),
      CustomTextField(
        label: 'Sample Weight',
        value: labResult?.sampleWeight.toString(),
        onChanged: (value) => _onEdit('sample_weight', value),
        isNumeric: true,
      ),

      // Producer details.
      Padding(
        padding: labelPadding,
        child: SelectableText('Producer', style: labelStyle),
      ),
      CustomTextField(
        label: 'Producer',
        value: labResult?.producer,
        onChanged: (value) => _onEdit('producer', value),
      ),
      CustomTextField(
        label: 'Producer License Number',
        value: labResult?.producerLicenseNumber,
        onChanged: (value) => _onEdit('producer_license_number', value),
      ),
      CustomTextField(
        label: 'Producer Address',
        value: labResult?.producerAddress,
        onChanged: (value) => _onEdit('producer_address', value),
      ),
      CustomTextField(
        label: 'Producer Street',
        value: labResult?.producerStreet,
        onChanged: (value) => _onEdit('producer_street', value),
      ),
      CustomTextField(
        label: 'Producer City',
        value: labResult?.producerCity,
        onChanged: (value) => _onEdit('producer_city', value),
      ),
      CustomTextField(
        label: 'Producer State',
        value: labResult?.producerState,
        onChanged: (value) => _onEdit('producer_state', value),
      ),
      CustomTextField(
        label: 'Producer Zipcode',
        value: labResult?.producerZipcode,
        onChanged: (value) => _onEdit('producer_zipcode', value),
      ),

      // Distributor details.
      Padding(
        padding: labelPadding,
        child: SelectableText('Distributor', style: labelStyle),
      ),
      CustomTextField(
        label: 'Distributor',
        value: labResult?.distributor,
        onChanged: (value) => _onEdit('distributor', value),
      ),
      CustomTextField(
        label: 'Distributor Address',
        value: labResult?.distributorAddress,
        onChanged: (value) => _onEdit('distributor_address', value),
      ),
      CustomTextField(
        label: 'Distributor Street',
        value: labResult?.distributorStreet,
        onChanged: (value) => _onEdit('distributor_street', value),
      ),
      CustomTextField(
        label: 'Distributor City',
        value: labResult?.distributorCity,
        onChanged: (value) => _onEdit('distributor_city', value),
      ),
      CustomTextField(
        label: 'Distributor State',
        value: labResult?.distributorState,
        onChanged: (value) => _onEdit('distributor_state', value),
      ),
      CustomTextField(
        label: 'Distributor Zipcode',
        value: labResult?.distributorZipcode,
        onChanged: (value) => _onEdit('distributor_zipcode', value),
      ),
      CustomTextField(
        label: 'Distributor License Number',
        value: labResult?.distributorLicenseNumber,
        onChanged: (value) => _onEdit('distributor_license_number', value),
      ),

      // Lab details.
      Padding(
        padding: labelPadding,
        child: SelectableText('Lab', style: labelStyle),
      ),
      CustomTextField(
        label: 'Lab ID',
        value: labResult?.labId,
        onChanged: (value) => _onEdit('lab_id', value),
      ),
      CustomTextField(
        label: 'Lab',
        value: labResult?.lab,
        onChanged: (value) => _onEdit('lab', value),
      ),
      CustomTextField(
        label: 'LIMS',
        value: labResult?.lims,
        onChanged: (value) => _onEdit('lims', value),
      ),
      CustomTextField(
        label: 'Lab Image',
        value: labResult?.labImageUrl,
        onChanged: (value) => _onEdit('lab_image_url', value),
      ),
      CustomTextField(
        label: 'Lab Address',
        value: labResult?.labAddress,
        onChanged: (value) => _onEdit('lab_address', value),
      ),
      CustomTextField(
        label: 'Lab Street',
        value: labResult?.labStreet,
        onChanged: (value) => _onEdit('lab_street', value),
      ),
      CustomTextField(
        label: 'Lab City',
        value: labResult?.labCity,
        onChanged: (value) => _onEdit('lab_city', value),
      ),
      CustomTextField(
        label: 'Lab County',
        value: labResult?.labCounty,
        onChanged: (value) => _onEdit('lab_county', value),
      ),
      CustomTextField(
        label: 'Lab State',
        value: labResult?.labState,
        onChanged: (value) => _onEdit('lab_state', value),
      ),
      CustomTextField(
        label: 'Lab Zipcode',
        value: labResult?.labZipcode,
        onChanged: (value) => _onEdit('lab_zipcode', value),
      ),
      CustomTextField(
        label: 'Lab Phone',
        value: labResult?.labPhone,
        onChanged: (value) => _onEdit('lab_phone', value),
      ),
      CustomTextField(
        label: 'Lab Email',
        value: labResult?.labEmail,
        onChanged: (value) => _onEdit('lab_email', value),
      ),
      CustomTextField(
        label: 'Lab Website',
        value: labResult?.labWebsite,
        onChanged: (value) => _onEdit('lab_website', value),
      ),
      gapH48,
    ];

    // View and edit form fields.
    var _viewForm = ViewForm(fields: fields);
    var _editForm = EditForm(textFormFields: textFormFields);

    // Tab bar.
    var _tabBar = TabBar(
      controller: _tabController,
      padding: EdgeInsets.all(0),
      labelPadding: EdgeInsets.symmetric(horizontal: 2, vertical: 0),
      isScrollable: true,
      unselectedLabelColor: Theme.of(context).textTheme.bodyMedium!.color,
      labelColor: Theme.of(context).textTheme.titleLarge!.color,
      splashBorderRadius: BorderRadius.circular(30),
      splashFactory: NoSplash.splashFactory,
      overlayColor: MaterialStateProperty.all<Color>(Colors.transparent),
      indicator: BoxDecoration(),
      dividerColor: Colors.transparent,
      tabs: [
        PillTabButton(
          text: 'Details',
          icon: Icons.bar_chart,
          isSelected: _tabController.index == 0,
        ),
        PillTabButton(
          text: 'Results',
          icon: Icons.science,
          isSelected: _tabController.index == 1,
        ),
        PillTabButton(
          text: 'COA',
          icon: Icons.description,
          isSelected: _tabController.index == 2,
        ),
        // PillTabButton(
        //   text: 'History',
        //   icon: Icons.history,
        //   isSelected: _tabController.index == 3,
        // ),
      ],
    );

    // Edit button.
    var _editButton = SecondaryButton(
      text: 'Edit',
      onPressed: () {
        setState(() {
          _isEditing = !_isEditing;
        });
      },
    );

    // Save button.
    var _saveButton = PrimaryButton(
      text: 'Save',
      isLoading: _updateFuture != null,
      onPressed: _saveEdit,
    );

    // Cancel editing button.
    var _cancelButton = SecondaryButton(
      text: 'Cancel',
      onPressed: _cancelEdit,
    );

    // Download button.
    var _downloadButton = DownloadButton(
      items: [labResult!.toMap()],
      text: 'Download',
      url: '/api/data/coas/download',
    );

    // Public/private choice.
    final subscription = ref.watch(userSubscriptionProvider).value;
    var _publicPrivateChoice = Align(
      alignment: Alignment.centerLeft,
      child: Padding(
        padding: EdgeInsets.only(left: 32, right: 32, top: 8, bottom: 48),
        child: ConstrainedBox(
          constraints: BoxConstraints(
            maxWidth: 130,
          ),
          child: PublicPrivateToggle(
            isPublic: labResult.public ?? false,
            disabled: subscription?['support'] != 'enterprise',
            onChanged: (newValue) {
              // Change public / private (only if the user has enterprise support).
              if (subscription?['support'] == 'enterprise') {
                var id = widget.labResultId ?? widget.labResult?.sampleId ?? '';
                var update = {'public': newValue};
                ref.read(resultService).updateResult(id, update);
              }
            },
          ),
        ),
      ),
    );

    // Label color.
    // FIXME: Initial color is not correct.
    final currentColor = ref.read(labelColorProvider);
    var _colorPicker = Row(
      children: [
        SelectionArea(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                'Label color',
                style: Theme.of(context).textTheme.bodyMedium,
              ),
              Text(
                'Color code for your results.',
                style: Theme.of(context).textTheme.bodySmall,
              ),
            ],
          ),
        ),
        Container(
          padding: EdgeInsets.only(left: 24, right: 24, bottom: 8),
          child: GestureDetector(
            onTap: () {
              showDialog(
                context: context,
                builder: (BuildContext context) {
                  return AlertDialog(
                    title: Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Text('Select a color'),
                        IconButton(
                          icon: Icon(
                            Icons.close,
                            color:
                                Theme.of(context).textTheme.bodyMedium?.color,
                          ),
                          onPressed: () => Navigator.of(context).pop(false),
                        ),
                      ],
                    ),
                    content: SingleChildScrollView(
                      child: MaterialColorPicker(
                        allowShades: false,
                        // Change color functionality.
                        onMainColorChange: (ColorSwatch<dynamic>? color) async {
                          if (color != null) {
                            String hexCode = StringUtils.colorToHexCode(color);
                            var update = {'label_color': hexCode};
                            update['updated_at'] =
                                DateTime.now().toUtc().toIso8601String();
                            _updateFuture =
                                await ref.read(resultService).updateResult(
                                      widget.labResultId ??
                                          widget.labResult?.sampleHash ??
                                          '',
                                      update,
                                    );
                            if (_updateFuture != 'success') {
                              ScaffoldMessenger.of(context).showSnackBar(
                                SnackBar(
                                  content: Text('Error changing label color!'),
                                  duration: Duration(seconds: 4),
                                  backgroundColor: isDark
                                      ? DarkColors.darkOrange
                                      : LightColors.darkOrange,
                                  showCloseIcon: true,
                                ),
                              );
                            }
                            setState(() {
                              _updateFuture = null;
                            });
                            Navigator.of(context).pop();
                          }
                        },
                        selectedColor: currentColor,
                        colors: [
                          Colors.red,
                          Colors.orange,
                          Colors.amberAccent,
                          Colors.green,
                          Colors.teal,
                          Colors.blue,
                          Colors.indigo,
                          Colors.purple,
                          Colors.brown,
                          Colors.grey,
                        ],
                      ),
                    ),
                  );
                },
              );
            },
            child: MouseRegion(
              cursor: SystemMouseCursors.click,
              child: CircleColor(
                color: currentColor,
                circleSize: 32,
              ),
            ),
          ),
        ),
      ],
    );
    var _labelColor = Align(
      alignment: Alignment.centerLeft,
      child: Padding(
        padding: EdgeInsets.only(left: 32, right: 32, top: 0, bottom: 24),
        child: _colorPicker,
      ),
    );

    // Actions.
    var _actions = FormActions(
      isMobile: isMobile,
      isEditing: _isEditing,
      tabBar: _tabBar,
      editButton: _editButton,
      saveButton: _saveButton,
      cancelButton: _cancelButton,
      downloadButton: _downloadButton,
    );

    // Initialize the COA, if it is empty.
    if (labResult.jobFileUrl != null) {
      _pdfUrl = labResult.jobFileUrl;
    } else {
      _pdfUrl = null;
    }

    // TEST:
    // _pdfUrl =
    //     'https://firebasestorage.googleapis.com/v0/b/cannlytics.appspot.com/o/users%2FqXRaz2QQW8RwTlJjpP39c1I8xM03%2Fparse_coa_jobs%2FiLv6S7sy6ewFU3qwMsSr?alt=media&token=eafb5266-f440-4bf5-ac90-51a7e5d4fc27';

    // Tabs.
    final pdfFile = ref.watch(pdfControllerProvider(_pdfUrl ?? ''));
    var _tabs = TabBarView(
      controller: _tabController,
      children: [
        // Details tab.
        CustomScrollView(
          slivers: [
            _breadcrumbs,
            SliverToBoxAdapter(child: _actions),
            _isEditing ? _editForm : _viewForm,
            SliverToBoxAdapter(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Padding(
                    padding: EdgeInsets.only(
                      left: 32,
                      right: 32,
                      bottom: 24,
                    ),
                    child: Text(
                      'Settings',
                      style: Theme.of(context).textTheme.titleMedium?.copyWith(
                            color:
                                Theme.of(context).textTheme.titleLarge?.color,
                            fontWeight: FontWeight.w600,
                          ),
                    ),
                  ),
                  _labelColor,
                  _publicPrivateChoice,
                ],
              ),
            ),
          ],
        ),

        // Results tab.
        CustomScrollView(
          slivers: [
            _breadcrumbs,
            SliverToBoxAdapter(child: _actions),
            SliverToBoxAdapter(
              child: AnalysisResultsTable(
                results: labResult.results,
                isEditing: _isEditing,
              ),
            ),
          ],
        ),

        // COA tab.
        CustomScrollView(
          slivers: [
            // Breadcrumbs.
            _breadcrumbs,
            SliverToBoxAdapter(child: _actions),

            // No PDF placeholder.
            // if (_pdfUrl == null)
            //   SliverToBoxAdapter(child: _placeholder(context, ref)),

            // Asynchronous PDF controller.
            SliverToBoxAdapter(
              child: pdfFile.when(
                data: (controller) {
                  if (controller != null) {
                    return Column(
                      children: [
                        /// COA actions.
                        CoaPdfActions(
                          pdfController: controller,
                          pdfUrl: _pdfUrl!,
                        ),

                        // COA PDF.
                        CoaPdf(pdfController: controller),
                      ],
                    );
                  } else {
                    return SearchPlaceholder(
                      title: 'No COA found',
                      subtitle: '',
                      imageUrl:
                          'https://firebasestorage.googleapis.com/v0/b/cannlytics.appspot.com/o/assets%2Fimages%2Ficons%2Fai-icons%2Fcertificate.png?alt=media&token=8aa0ebbd-1625-4ff4-9843-9bf9d5646490',
                    );
                  }
                },
                loading: () => Container(
                  height: 420,
                  child: CircularProgressIndicator(),
                ),
                error: (err, stack) => Container(
                  height: 420,
                  child: Text('Error: $err'),
                ),
              ),
            ),
          ],
        ),

        // TODO: Comments tab.

        // History tab.
        // CustomScrollView(
        //   slivers: [
        //     _breadcrumbs,
        //     SliverToBoxAdapter(child: _actions),
        //     SliverToBoxAdapter(
        //       child: ResultLogs(
        //         labResultId: widget.labResultId ?? '',
        //       ),
        //     ),
        //   ],
        // ),
      ],
    );

    // Render.
    return TabbedForm(tabCount: _tabCount, tabs: _tabs);
  }
}

/// A pill that displays the analysis type.
class AnalysisPill extends StatelessWidget {
  final String analysis;

  AnalysisPill(this.analysis);

  @override
  Widget build(BuildContext context) {
    // Map of analysis types to colors.
    var colorMap = {
      'cannabinoids': Colors.red.shade400,
      'potency': Colors.red.shade400,
      'terpenes': Colors.green.shade400,
      'pesticide': Colors.purple.shade400,
      'pesticides': Colors.purple.shade400,
      'microbiological': Colors.blue.shade400,
      'microbes': Colors.blue.shade400,
      'heavy_metals': Colors.grey.shade600,
      'mycotoxin': Colors.orange.shade400,
      'mycotoxins': Colors.orange.shade400,
      'water_activity': Colors.teal.shade400,
      'moisture_content': Colors.teal.shade400,
      'residual_solvents': Colors.amberAccent,
      'foreign_matter': Colors.brown.shade400,
    };

    // TODO: Have unknown analysis get color from color API.

    // Convert the analysis type to title case.
    var titleCase = analysis.split('_').map((word) {
      if (word.isEmpty) return ''; // handle empty words
      var lower = word.toLowerCase();
      return '${lower[0].toUpperCase()}${lower.substring(1)}';
    }).join(' ');

    return Container(
      padding: EdgeInsets.symmetric(vertical: 0, horizontal: 4),
      margin: EdgeInsets.all(1),
      decoration: BoxDecoration(
        color: colorMap[analysis] ?? Colors.grey.shade400,
        borderRadius: BorderRadius.circular(16.0),
      ),
      child: Text(
        titleCase,
        style: Theme.of(context).textTheme.bodySmall?.copyWith(
              color: Colors.white,
            ),
      ),
    );
  }
}

/// A pill that displays the status.
class StatusPill extends StatelessWidget {
  final String? status;

  StatusPill(this.status);

  @override
  Widget build(BuildContext context) {
    // Map of status types to colors.
    var colorMap = {
      'pass': Colors.green.shade400,
      'fail': Colors.red.shade400,
    };

    // Define default color as yellow.
    Color defaultColor = Colors.yellow.shade400;

    // Get the color for the current status, or default color if the status is unknown.
    Color backgroundColor = colorMap[status?.toLowerCase()] ?? defaultColor;

    // Convert the status to title case.
    var titleCase = status == null || status!.isEmpty
        ? ''
        : '${status![0].toUpperCase()}${status!.substring(1).toLowerCase()}';

    // Return a container with colored background and status text, if status is not null.
    return status == null
        ? Container()
        : Container(
            padding: EdgeInsets.symmetric(vertical: 0, horizontal: 4),
            margin: EdgeInsets.all(1),
            decoration: BoxDecoration(
              color: backgroundColor,
              borderRadius: BorderRadius.circular(16.0),
            ),
            child: Text(
              titleCase,
              style: Theme.of(context).textTheme.bodySmall?.copyWith(
                    color: Colors.white,
                  ),
            ),
          );
  }
}

/// A toggle that switches between public and private.
class PublicPrivateToggle extends StatefulWidget {
  final bool isPublic;
  final ValueChanged<bool>? onChanged;
  final bool disabled;

  PublicPrivateToggle({
    required this.isPublic,
    this.onChanged,
    this.disabled = false,
  });

  @override
  _PublicPrivateToggleState createState() => _PublicPrivateToggleState();
}

class _PublicPrivateToggleState extends State<PublicPrivateToggle> {
  bool _isPublic = false;

  @override
  void initState() {
    super.initState();
    _isPublic = widget.isPublic;
  }

  @override
  Widget build(BuildContext context) {
    return Tooltip(
      message:
          'Only Enterprise users have the ability to toggle between public/private status.',
      child: SecondaryButton(
        text: _isPublic ? 'Public' : 'Private',
        disabled: widget.disabled,
        onPressed: () {
          setState(() {
            _isPublic = !_isPublic;
            widget.onChanged?.call(_isPublic);
          });
        },
        leading: Icon(
          _isPublic ? Icons.public : Icons.public_off,
          size: 16,
          color: _isPublic ? Colors.blueAccent : Colors.grey.shade600,
        ),
      ),
    );
  }
}

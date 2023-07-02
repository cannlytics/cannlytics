// Cannlytics Data
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 6/11/2023
// Updated: 7/1/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>
import 'dart:js_interop';

import 'package:cannlytics_data/common/buttons/download_button.dart';
import 'package:cannlytics_data/common/buttons/primary_button.dart';
import 'package:cannlytics_data/common/buttons/secondary_button.dart';
import 'package:cannlytics_data/common/forms/custom_text_field.dart';
import 'package:cannlytics_data/common/forms/forms.dart';
import 'package:cannlytics_data/common/layout/breadcrumbs.dart';
import 'package:cannlytics_data/common/layout/loading_placeholder.dart';
import 'package:cannlytics_data/common/layout/pill_tab.dart';
import 'package:cannlytics_data/common/tables/key_value_datatable.dart';
import 'package:cannlytics_data/constants/design.dart';
import 'package:cannlytics_data/models/lab_result.dart';
import 'package:cannlytics_data/ui/layout/console.dart';
import 'package:cannlytics_data/ui/results/result_coa.dart';
import 'package:cannlytics_data/ui/results/result_table.dart';
import 'package:cannlytics_data/ui/results/results_service.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:pdfx/pdfx.dart';
import 'package:internet_file/internet_file.dart';

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
  static const int _initialPage = 1;
  late PdfController _pdfController;
  late String _pdfUrl;
  late final TabController _tabController;
  int _tabCount = 3;
  Future<void>? _updateFuture;

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
    _pdfController.dispose();
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
      error: (err, stack) => MainContent(
        child: SelectableText('Error: $err'),
      ),

      // Data loaded UI.
      data: (labResult) {
        // Initialize the COA, if it is empty.
        if (labResult?.coaUrls?.isNotEmpty == true) {
          _pdfUrl = labResult?.coaUrls?[0]?['url'] ?? '';
        } else {
          _pdfUrl = labResult?.labResultsUrl ?? '';
        }
        if (_pdfUrl.isNotEmpty && _pdfController.document.isNull) {
          _pdfController = PdfController(
            document: PdfDocument.openData(InternetFile.get(_pdfUrl)),
            initialPage: _initialPage,
          );
        }

        // Return the form.
        return _form(labResult);
      },
    );
  }

  /// Form.
  Widget _form(LabResult? labResult) {
    // Style.
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
        return LabResult.fromMap(update);
      });
    }

    /// Cancel edit.
    void _cancelEdit() {
      // Reset analysis results.
      ref.read(analysisResults.notifier).update((state) {
        return labResult?.results?.map((x) => x?.toMap()).toList() ?? [];
      });

      // Cancel editing.
      setState(() {
        _isEditing = !_isEditing;
      });
    }

    /// Save edit.
    void _saveEdit() {
      // Update any modified details and results.
      var update = ref.read(updatedLabResult)?.toMap() ?? {};
      update['results'] = ref.read(analysisResults);
      update['updated_at'] = DateTime.now().toUtc().toIso8601String();

      // Update the data in Firestore.
      _updateFuture = ref.read(resultService).updateResult(
            widget.labResultId ?? widget.labResult?.sampleHash ?? '',
            update,
          );

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
          {'label': 'Result', 'path': '/results/${labResult?.sampleHash}'},
        ],
      ),
    );

    // Detail data table.
    var fieldStyle = Theme.of(context).textTheme.bodySmall;
    var fields = [
      // Sample data.
      // TODO: Link to strains page (strains/{hash(strainName)}).
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
          Text('${labResult?.strainName}', style: fieldStyle),
          Text('${labResult?.productType}', style: fieldStyle),
          Text('${labResult?.traceabilityIds}', style: fieldStyle),
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

      // Producer details.
      // TODO: Link to producer (/licenses/{producerLicenseNumber}).
      // TODO: Try to get and render producer image.
      KeyValueDataTable(
        tableName: 'Producer',
        labels: [
          'Producer',
          'Producer Address',
          'Producer License Number',
        ],
        values: [
          Text('${labResult?.producer}', style: fieldStyle),
          Text('${labResult?.producerAddress}', style: fieldStyle),
          Text('${labResult?.producerLicenseNumber}', style: fieldStyle),
        ],
      ),
      gapH24,

      // Distributor details.
      // TODO: Link to producer (/licenses/{producerLicenseNumber}).
      // TODO: Try to get and render producer image.
      KeyValueDataTable(
        tableName: 'Distributor',
        labels: [
          'Distributor',
          'Distributor Address',
          'Distributor License Number',
        ],
        values: [
          Text('${labResult?.distributor}', style: fieldStyle),
          Text('${labResult?.distributorAddress}', style: fieldStyle),
          Text('${labResult?.distributorLicenseNumber}', style: fieldStyle),
        ],
      ),
      gapH24,

      // Lab details.
// TODO: Link to lab (/licenses/{labLicenseNumber}).
// TODO: Render lab image if there is one.
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
          Text('${labResult?.lab}', style: fieldStyle),
          Text('${labResult?.lims}', style: fieldStyle),
          Text('${labResult?.labAddress}', style: fieldStyle),
          Text('${labResult?.labPhone}', style: fieldStyle),
          Text('${labResult?.labEmail}', style: fieldStyle),
          Text('${labResult?.labWebsite}', style: fieldStyle),
        ],
      ),
      gapH24,

// Analysis data.
// TODO: Style analyses as pills.
// TODO: Format status as Pass / Fail
      KeyValueDataTable(
        tableName: 'Analysis',
        labels: [
          'Analyses',
          'Batch Number',
          'Date Collected',
          'Date Tested',
          'Date Received',
          'Sample Weight',
        ],
        values: [
          Text('${labResult?.analyses}', style: fieldStyle),
          Text('${labResult?.batchNumber}', style: fieldStyle),
          Text('${labResult?.dateCollected}', style: fieldStyle),
          Text('${labResult?.dateTested}', style: fieldStyle),
          Text('${labResult?.dateReceived}', style: fieldStyle),
          Text('${labResult?.sampleWeight}', style: fieldStyle),
        ],
      ),
      gapH24,

// Parsing details.
// TODO: Format URLs as links.
      KeyValueDataTable(
        tableName: 'Parsing details',
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
          Text('${labResult?.downloadUrl}', style: fieldStyle),
          Text('${labResult?.shortUrl}', style: fieldStyle),
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
        // _buildTab('Notes', 2, Icons.science),
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

    // Tabs.
    var _tabs = TabBarView(
      controller: _tabController,
      children: [
        // Details tab.
        CustomScrollView(
          slivers: [
            _breadcrumbs,
            SliverToBoxAdapter(child: _actions),
            _isEditing ? _editForm : _viewForm,
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
            _breadcrumbs,
            SliverToBoxAdapter(child: _actions),
            // No COA placeholder.
            if (_pdfUrl.isEmpty)
              SliverToBoxAdapter(child: _placeholder(context, ref)),
            if (_pdfUrl.isNotEmpty) ...[
              /// COA PDF actions.
              SliverToBoxAdapter(
                child: CoaPdfActions(
                  pdfController: _pdfController,
                  pdfUrl: _pdfUrl,
                ),
              ),

              /// COA PDF.
              SliverToBoxAdapter(
                child: CoaPdf(pdfController: _pdfController),
              ),
            ],
          ],
        ),

        // TODO: Notes tab.
      ],
    );

    // Render.
    return TabbedForm(tabCount: _tabCount, tabs: _tabs);
  }

  /// Message displayed when there is no COA.
  Widget _placeholder(BuildContext context, WidgetRef ref) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            // Image.
            // TODO: Use downloadUrl if available as an image.
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
                    'No COA available',
                    textAlign: TextAlign.center,
                    style: TextStyle(
                        fontSize: 20,
                        color: Theme.of(context).textTheme.titleLarge!.color),
                  ),
                  SelectableText(
                    'If you have a COA, then you can upload it to have it parsed and attached.',
                    textAlign: TextAlign.center,
                    style: Theme.of(context).textTheme.bodyMedium,
                  ),
                  gapH12,
                  PrimaryButton(
                    text: 'Parse results',
                    onPressed: () => context.push('/results'),
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

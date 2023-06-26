// Cannlytics Data
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 6/11/2023
// Updated: 6/25/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>
import 'package:cannlytics_data/common/buttons/download_button.dart';
import 'package:cannlytics_data/common/buttons/primary_button.dart';
import 'package:cannlytics_data/common/buttons/secondary_button.dart';
import 'package:cannlytics_data/constants/colors.dart';
import 'package:cannlytics_data/constants/design.dart';
import 'package:cannlytics_data/models/lab_result.dart';
import 'package:cannlytics_data/ui/layout/breadcrumbs.dart';
import 'package:cannlytics_data/ui/layout/console.dart';
import 'package:cannlytics_data/ui/results/result_table.dart';
import 'package:cannlytics_data/ui/results/results_service.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:pdfx/pdfx.dart';
import 'package:internet_file/internet_file.dart';
import 'package:url_launcher/url_launcher.dart';

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
  int _selectedIndex = 0;
  Future<void>? _updateFuture;

  // Define the TextEditingController instances.
  final _productNameController = TextEditingController();
  final _strainNameController = TextEditingController();
  final _productTypeController = TextEditingController();
  final _traceabilityIdsController = TextEditingController();
  final _productSizeController = TextEditingController();
  final _servingSizeController = TextEditingController();
  final _servingsPerPackageController = TextEditingController();
  final _totalCannabinoidsController = TextEditingController();
  final _totalThcController = TextEditingController();
  final _totalCbdController = TextEditingController();
  final _totalTerpenesController = TextEditingController();
  final _analysesController = TextEditingController();
  final _statusController = TextEditingController();
  final _batchNumberController = TextEditingController();
  final _analysisStatusController = TextEditingController();
  final _methodsController = TextEditingController();
  final _dateCollectedController = TextEditingController();
  final _dateTestedController = TextEditingController();
  final _dateReceivedController = TextEditingController();
  final _sampleWeightController = TextEditingController();
  final _producerController = TextEditingController();
  final _producerLicenseNumberController = TextEditingController();
  final _producerAddressController = TextEditingController();
  final _producerStreetController = TextEditingController();
  final _producerCityController = TextEditingController();
  final _producerStateController = TextEditingController();
  final _producerZipcodeController = TextEditingController();
  final _distributorController = TextEditingController();
  final _distributorAddressController = TextEditingController();
  final _distributorStreetController = TextEditingController();
  final _distributorCityController = TextEditingController();
  final _distributorStateController = TextEditingController();
  final _distributorZipcodeController = TextEditingController();
  final _distributorLicenseNumberController = TextEditingController();
  final _labIdController = TextEditingController();
  final _labController = TextEditingController();
  final _limsController = TextEditingController();
  final _labImageUrlController = TextEditingController();
  final _labAddressController = TextEditingController();
  final _labStreetController = TextEditingController();
  final _labCityController = TextEditingController();
  final _labCountyController = TextEditingController();
  final _labStateController = TextEditingController();
  final _labZipcodeController = TextEditingController();
  final _labPhoneController = TextEditingController();
  final _labEmailController = TextEditingController();
  final _labWebsiteController = TextEditingController();

  // Initialize the PDF document.
  @override
  void initState() {
    super.initState();

    // FIXME: Initialize PDF.
    _pdfUrl =
        'https://firebasestorage.googleapis.com/v0/b/cannlytics.appspot.com/o/tests%2Fassets%2Fcoas%2Facs%2F27675_0002355100.pdf?alt=media&token=bc9abde9-4fe6-4a45-8be4-68e92c8ea8f9';
    _pdfController = PdfController(
      document: PdfDocument.openData(InternetFile.get(_pdfUrl)),
      initialPage: _initialPage,
    );

    // Initialize tabs.
    _tabController = TabController(length: _tabCount, vsync: this);
    _tabController.addListener(() {
      setState(() {
        _selectedIndex = _tabController.index;
      });
    });
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
    if (widget.labResultId != null) {
      final asyncData = ref.watch(labResultProvider(widget.labResultId!));
      return asyncData.when(
        // Loading UI.
        loading: () => MainContent(
          child: _loadingPlaceholder(context, ref),
          fillRemaining: true,
        ),

        // Error UI.
        error: (err, stack) => MainContent(
          child: SelectableText('Error: $err'),
        ),

        // Data loaded UI.
        data: (labResult) {
          // Initialize the text editing controllers with values.
          _productNameController.text = labResult?.productName ?? '';
          _strainNameController.text = labResult?.strainName ?? '';
          _productTypeController.text = labResult?.productType ?? '';
          _traceabilityIdsController.text =
              labResult?.traceabilityIds.join(', ') ?? '';
          _productSizeController.text = labResult?.productSize.toString() ?? '';
          _servingSizeController.text = labResult?.servingSize.toString() ?? '';
          _servingsPerPackageController.text =
              labResult?.servingsPerPackage.toString() ?? '';
          _totalCannabinoidsController.text =
              labResult?.totalCannabinoids.toString() ?? '';
          _totalThcController.text = labResult?.totalThc.toString() ?? '';
          _totalCbdController.text = labResult?.totalCbd.toString() ?? '';
          _totalTerpenesController.text =
              labResult?.totalTerpenes.toString() ?? '';
          _analysesController.text = labResult?.analyses.join(', ') ?? '';
          _statusController.text = labResult?.status ?? '';
          _batchNumberController.text = labResult?.batchNumber ?? '';
          _analysisStatusController.text = labResult?.analysisStatus ?? '';
          _methodsController.text = labResult?.methods.join(', ') ?? '';
          _dateCollectedController.text = labResult?.dateCollected ?? '';
          _dateTestedController.text = labResult?.dateTested ?? '';
          _dateReceivedController.text = labResult?.dateReceived ?? '';
          _sampleWeightController.text =
              labResult?.sampleWeight.toString() ?? '';
          _producerController.text = labResult?.producer ?? '';
          _producerLicenseNumberController.text =
              labResult?.producerLicenseNumber ?? '';
          _producerAddressController.text = labResult?.producerAddress ?? '';
          _producerStreetController.text = labResult?.producerStreet ?? '';
          _producerCityController.text = labResult?.producerCity ?? '';
          _producerStateController.text = labResult?.producerState ?? '';
          _producerZipcodeController.text = labResult?.producerZipcode ?? '';
          _distributorController.text = labResult?.distributor ?? '';
          _distributorAddressController.text =
              labResult?.distributorAddress ?? '';
          _distributorStreetController.text =
              labResult?.distributorStreet ?? '';
          _distributorCityController.text = labResult?.distributorCity ?? '';
          _distributorStateController.text = labResult?.distributorState ?? '';
          _distributorZipcodeController.text =
              labResult?.distributorZipcode ?? '';
          _distributorLicenseNumberController.text =
              labResult?.distributorLicenseNumber ?? '';
          _labIdController.text = labResult?.labId ?? '';
          _labController.text = labResult?.lab ?? '';
          _limsController.text = labResult?.lims ?? '';
          _labImageUrlController.text = labResult?.labImageUrl ?? '';
          _labAddressController.text = labResult?.labAddress ?? '';
          _labStreetController.text = labResult?.labStreet ?? '';
          _labCityController.text = labResult?.labCity ?? '';
          _labCountyController.text = labResult?.labCounty ?? '';
          _labStateController.text = labResult?.labState ?? '';
          _labZipcodeController.text = labResult?.labZipcode ?? '';
          _labPhoneController.text = labResult?.labPhone ?? '';
          _labEmailController.text = labResult?.labEmail ?? '';
          _labWebsiteController.text = labResult?.labWebsite ?? '';

          // Return the form.
          return _form(labResult);
        },
      );
    } else {
      return _form(widget.labResult);
    }
  }

  /// Form.
  Widget _form(LabResult? labResult) {
    // Fonts.
    var labelMedium = Theme.of(context).textTheme.labelMedium?.copyWith(
          fontWeight: FontWeight.bold,
        );

    // Fields.
    var fields = [
      // Sample details.
      Text('Sample', style: labelMedium),
      Text('Product Name: ${labResult?.productName}'),
      // TODO: Link to strains page (strains/{hash(strainName)}).
      Text('Strain Name: ${labResult?.strainName}'),
      Text('Product Type: ${labResult?.productType}'),
      Text('Traceability IDs: ${labResult?.traceabilityIds}'),
      Text('Product Size: ${labResult?.productSize}'),
      Text('Serving Size: ${labResult?.servingSize}'),
      Text('Servings Per Package: ${labResult?.servingsPerPackage}'),
      gapH16,

      // Compound details.
      Text('Compounds', style: labelMedium),
      Text('Total Cannabinoids: ${labResult?.totalCannabinoids}'),
      Text('Total THC: ${labResult?.totalThc}'),
      Text('Total CBD: ${labResult?.totalCbd}'),
      Text('Total Terpenes: ${labResult?.totalTerpenes}'),
      gapH16,

      // Analysis data.
      // TODO: Style analyses as pills.
      // TODO: Format status as Pass / Fail
      Text('Analysis', style: labelMedium),
      Text('Analyses: ${labResult?.analyses}'),
      // Text('Status: ${labResult?.status}'),
      // Text('Analysis Status: ${labResult?.analysisStatus}'),
      // Text('Methods: ${labResult?.methods}'),
      Text('Batch Number: ${labResult?.batchNumber}'),
      Text('Date Collected: ${labResult?.dateCollected}'),
      Text('Date Tested: ${labResult?.dateTested}'),
      Text('Date Received: ${labResult?.dateReceived}'),
      Text('Sample Weight: ${labResult?.sampleWeight}'),
      gapH16,

      // Producer details.
      // TODO: Link to producer (/licenses/{producerLicenseNumber}).
      // TODO: Try to get and render producer image.
      Text('Producer', style: labelMedium),
      Text('Producer: ${labResult?.producer}'),
      Text('Producer License Number: ${labResult?.producerLicenseNumber}'),
      Text('Producer Address: ${labResult?.producerAddress}'),
      Text('Producer Street: ${labResult?.producerStreet}'),
      Text('Producer City: ${labResult?.producerCity}'),
      Text('Producer State: ${labResult?.producerState}'),
      Text('Producer Zipcode: ${labResult?.producerZipcode}'),
      gapH16,

      // Distributor details.
      // TODO: Link to producer (/licenses/{distributorLicenseNumber}).
      // TODO: Try to get and render producer image.
      Text('Distributor', style: labelMedium),
      Text('Distributor: ${labResult?.distributor}'),
      Text('Distributor Address: ${labResult?.distributorAddress}'),
      Text('Distributor Street: ${labResult?.distributorStreet}'),
      Text('Distributor City: ${labResult?.distributorCity}'),
      Text('Distributor State: ${labResult?.distributorState}'),
      Text('Distributor Zipcode: ${labResult?.distributorZipcode}'),
      Text(
          'Distributor License Number: ${labResult?.distributorLicenseNumber}'),
      gapH16,

      // Lab details.
      // TODO: Link to lab (/licenses/{labLicenseNumber}).
      // TODO: Render lab image if there is one.
      Text('Lab', style: labelMedium),
      Text('Lab ID: ${labResult?.labId}'),
      Text('Lab: ${labResult?.lab}'),
      Text('LIMS: ${labResult?.lims}'),
      Text('Lab Image URL: ${labResult?.labImageUrl}'),
      Text('Lab Address: ${labResult?.labAddress}'),
      Text('Lab Street: ${labResult?.labStreet}'),
      Text('Lab City: ${labResult?.labCity}'),
      Text('Lab County: ${labResult?.labCounty}'),
      Text('Lab State: ${labResult?.labState}'),
      Text('Lab Zipcode: ${labResult?.labZipcode}'),
      Text('Lab Phone: ${labResult?.labPhone}'),
      Text('Lab Email: ${labResult?.labEmail}'),
      Text('Lab Website: ${labResult?.labWebsite}'),
      Text('Lab Latitude: ${labResult?.labLatitude}'),
      Text('Lab Longitude: ${labResult?.labLongitude}'),
      gapH16,

      // Parsing details.
      Text('Parsing details', style: labelMedium),
      Text('Sample ID: ${labResult?.sampleId}'),
      Text('Sample Hash: ${labResult?.sampleHash}'),
      Text('Results Hash: ${labResult?.resultsHash}'),
      Text('COA Algorithm: ${labResult?.coaAlgorithm}'),
      Text('COA Algorithm Version: ${labResult?.coaAlgorithmVersion}'),
      Text('COA Parsed At: ${labResult?.coaParsedAt}'),
      // TODO: Format as links.
      Text('Download URL: ${labResult?.downloadUrl}'),
      Text('Short URL: ${labResult?.shortUrl}'),
      gapH48,
    ];

    // Text fields.
    var _textFormFields = [
      // Sample details.
      Padding(
        padding: EdgeInsets.only(left: 16, right: 16, top: 16, bottom: 8),
        child: SelectableText('Sample', style: labelMedium),
      ),
      _buildTextField(_productNameController, 'Product Name'),
      _buildTextField(_strainNameController, 'Strain Name'),
      _buildTextField(_productTypeController, 'Product Type'),
      _buildTextField(_traceabilityIdsController, 'Traceability IDs'),
      _buildTextField(_productSizeController, 'Product Size', isNumeric: true),
      _buildTextField(_servingSizeController, 'Serving Size', isNumeric: true),
      _buildTextField(_servingsPerPackageController, 'Servings Per Package',
          isNumeric: true),

      // Compound details.
      // TODO: Format as number.
      Padding(
        padding: EdgeInsets.only(left: 16, right: 16, top: 16, bottom: 8),
        child: SelectableText('Compound', style: labelMedium),
      ),
      _buildTextField(_totalCannabinoidsController, 'Total Cannabinoids',
          isNumeric: true),
      _buildTextField(_totalThcController, 'Total THC', isNumeric: true),
      _buildTextField(_totalCbdController, 'Total CBD', isNumeric: true),
      _buildTextField(_totalTerpenesController, 'Total Terpenes',
          isNumeric: true),

      // Analysis data.
      Padding(
        padding: EdgeInsets.only(left: 16, right: 16, top: 16, bottom: 8),
        child: SelectableText('Analysis', style: labelMedium),
      ),
      _buildTextField(_analysesController, 'Analyses'),
      _buildTextField(_statusController, 'Status'),
      _buildTextField(_batchNumberController, 'Batch Number'),
      _buildTextField(_analysisStatusController, 'Analysis Status'),
      _buildTextField(_methodsController, 'Methods'),
      _buildTextField(_dateCollectedController, 'Date Collected'),
      _buildTextField(_dateTestedController, 'Date Tested'),
      _buildTextField(_dateReceivedController, 'Date Received'),
      _buildTextField(_sampleWeightController, 'Sample Weight'),

      // Producer details.
      Padding(
        padding: EdgeInsets.only(left: 16, right: 16, top: 16, bottom: 8),
        child: SelectableText('Producer', style: labelMedium),
      ),
      _buildTextField(_producerController, 'Producer'),
      _buildTextField(
          _producerLicenseNumberController, 'Producer License Number'),
      _buildTextField(_producerAddressController, 'Producer Address'),
      _buildTextField(_producerStreetController, 'Producer Street'),
      _buildTextField(_producerCityController, 'Producer City'),
      _buildTextField(_producerStateController, 'Producer State'),
      _buildTextField(_producerZipcodeController, 'Producer Zipcode'),

      // Distributor details.
      Padding(
        padding: EdgeInsets.only(left: 16, right: 16, top: 16, bottom: 8),
        child: SelectableText('Distributor', style: labelMedium),
      ),
      _buildTextField(_distributorController, 'Distributor'),
      _buildTextField(_distributorAddressController, 'Distributor Address'),
      _buildTextField(_distributorStreetController, 'Distributor Street'),
      _buildTextField(_distributorCityController, 'Distributor City'),
      _buildTextField(_distributorStateController, 'Distributor State'),
      _buildTextField(_distributorZipcodeController, 'Distributor Zipcode'),
      _buildTextField(
          _distributorLicenseNumberController, 'Distributor License Number'),

      // Lab details.
      Padding(
        padding: EdgeInsets.only(left: 16, right: 16, top: 16, bottom: 8),
        child: SelectableText('Lab', style: labelMedium),
      ),
      _buildTextField(_labIdController, 'Lab ID'),
      _buildTextField(_labController, 'Lab'),
      _buildTextField(_limsController, 'LIMS'),
      _buildTextField(_labImageUrlController, 'Lab Image'),
      _buildTextField(_labAddressController, 'Lab Address'),
      _buildTextField(_labStreetController, 'Lab Street'),
      _buildTextField(_labCityController, 'Lab City'),
      _buildTextField(_labCountyController, 'Lab County'),
      _buildTextField(_labStateController, 'Lab State'),
      _buildTextField(_labZipcodeController, 'Lab Zipcode'),
      _buildTextField(_labPhoneController, 'Lab Phone'),
      _buildTextField(_labEmailController, 'Lab Email'),
      _buildTextField(_labWebsiteController, 'Lab Website'),
      gapH48,
    ];

    // View form fields.
    Widget _viewForm = SliverToBoxAdapter(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.start,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Padding(
            padding: EdgeInsets.only(left: 16, right: 16, top: 16, bottom: 8),
            child: SelectionArea(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.start,
                crossAxisAlignment: CrossAxisAlignment.start,
                children: fields,
              ),
            ),
          ),
        ],
      ),
    );

    // Edit form fields.
    Widget _editForm = SliverToBoxAdapter(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.start,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Column(
            mainAxisAlignment: MainAxisAlignment.start,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: _textFormFields,
          ),
        ],
      ),
    );

    // Breadcrumbs.
    Widget _breadcrumbs = SliverToBoxAdapter(
      child: Padding(
        padding: EdgeInsets.only(left: 16, top: 12),
        child: Row(
          children: [
            Breadcrumbs(
              items: [
                BreadcrumbItem(
                    title: 'Data',
                    onTap: () {
                      context.go('/');
                    }),
                BreadcrumbItem(
                    title: 'Lab Results',
                    onTap: () {
                      context.go('/results');
                    }),
                BreadcrumbItem(
                  title: 'Result',
                )
              ],
            ),
          ],
        ),
      ),
    );

    // Actions.
    Widget _actions = Padding(
      padding: EdgeInsets.only(top: 12, bottom: 12, left: 4, right: 16),
      child: Row(
        children: [
          TabBar(
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
              _buildTab('Details', 0, Icons.bar_chart),
              _buildTab('Results', 1, Icons.science),
              _buildTab('COA', 2, Icons.description),
              // _buildTab('Notes', 2, Icons.science),
            ],
          ),
          Spacer(),

          // Edit button.
          if (!_isEditing)
            SecondaryButton(
              text: 'Edit',
              onPressed: () {
                setState(() {
                  _isEditing = !_isEditing;
                });
              },
            ),

          // Save and cancel edit buttons.
          if (_isEditing) ...[
            PrimaryButton(
              text: 'Save',
              isLoading: _updateFuture != null,
              onPressed: () {
                // Get the values from the TextEditingController instances.
                final productName = _productNameController.text;
                final strainName = _strainNameController.text;
                final productType = _productTypeController.text;
                final traceabilityIds = _traceabilityIdsController.text
                    .split(',')
                    .map((item) => item.trim())
                    .where((item) => item.isNotEmpty)
                    .toList();
                final productSize = int.tryParse(_productSizeController.text);
                final servingSize = int.tryParse(_servingSizeController.text);
                final servingsPerPackage =
                    int.tryParse(_servingsPerPackageController.text);
                final totalCannabinoids =
                    double.tryParse(_totalCannabinoidsController.text);
                final totalThc = double.tryParse(_totalThcController.text);
                final totalCbd = double.tryParse(_totalCbdController.text);
                final totalTerpenes =
                    double.tryParse(_totalTerpenesController.text);
                final analyses = _analysesController.text
                    .split(',')
                    .map((item) => item.trim())
                    .where((item) => item.isNotEmpty)
                    .toList();
                final status = _statusController.text;
                final batchNumber = _batchNumberController.text;
                final analysisStatus = _analysisStatusController.text;
                final methods = _methodsController.text;
                final dateCollected = _dateCollectedController.text;
                final dateTested = _dateTestedController.text;
                final dateReceived = _dateReceivedController.text;
                final sampleWeight =
                    double.tryParse(_sampleWeightController.text);
                final producer = _producerController.text;
                final producerLicenseNumber =
                    _producerLicenseNumberController.text;
                final producerAddress = _producerAddressController.text;
                final producerStreet = _producerStreetController.text;
                final producerCity = _producerCityController.text;
                final producerState = _producerStateController.text;
                final producerZipcode = _producerZipcodeController.text;
                final distributor = _distributorController.text;
                final distributorAddress = _distributorAddressController.text;
                final distributorStreet = _distributorStreetController.text;
                final distributorCity = _distributorCityController.text;
                final distributorState = _distributorStateController.text;
                final distributorZipcode = _distributorZipcodeController.text;
                final distributorLicenseNumber =
                    _distributorLicenseNumberController.text;
                final labId = _labIdController.text;
                final lab = _labController.text;
                final lims = _limsController.text;
                final labImageUrl = _labImageUrlController.text;
                final labAddress = _labAddressController.text;
                final labStreet = _labStreetController.text;
                final labCity = _labCityController.text;
                final labCounty = _labCountyController.text;
                final labState = _labStateController.text;
                final labZipcode = _labZipcodeController.text;
                final labPhone = _labPhoneController.text;
                final labEmail = _labEmailController.text;
                final labWebsite = _labWebsiteController.text;

                // Prepare data for Firestore.
                Map<String, dynamic> update = {
                  'product_name': productName,
                  'strain_name': strainName,
                  'product_type': productType,
                  'traceability_ids': traceabilityIds,
                  'product_size': productSize,
                  'serving_size': servingSize,
                  'servings_per_package': servingsPerPackage,
                  'total_cannabinoids': totalCannabinoids,
                  'total_thc': totalThc,
                  'total_cbd': totalCbd,
                  'total_terpenes': totalTerpenes,
                  'analyses': analyses,
                  'status': status,
                  'batch_number': batchNumber,
                  'analysis_status': analysisStatus,
                  'methods': methods,
                  'date_collected': dateCollected,
                  'date_tested': dateTested,
                  'date_received': dateReceived,
                  'sample_weight': sampleWeight,
                  'producer': producer,
                  'producer_license_number': producerLicenseNumber,
                  'producer_address': producerAddress,
                  'producer_street': producerStreet,
                  'producer_city': producerCity,
                  'producer_state': producerState,
                  'producer_zipcode': producerZipcode,
                  'distributor': distributor,
                  'distributor_address': distributorAddress,
                  'distributor_street': distributorStreet,
                  'distributor_city': distributorCity,
                  'distributor_state': distributorState,
                  'distributor_zipcode': distributorZipcode,
                  'distributor_license_number': distributorLicenseNumber,
                  'lab_id': labId,
                  'lab': lab,
                  'lims': lims,
                  'lab_image_url': labImageUrl,
                  'lab_address': labAddress,
                  'lab_street': labStreet,
                  'lab_city': labCity,
                  'lab_county': labCounty,
                  'lab_state': labState,
                  'lab_zipcode': labZipcode,
                  'lab_phone': labPhone,
                  'lab_email': labEmail,
                  'lab_website': labWebsite,
                };

                // Update any modified results.
                update['results'] = ref.read(analysisResults);

                // Update the data in Firestore.
                _updateFuture = ref.read(resultService).updateResult(
                      widget.labResultId ?? '',
                      update,
                    );

                // Cancel editing.
                setState(() {
                  _isEditing = !_isEditing;
                  _updateFuture = null;
                });
              },
            ),
            gapW4,
            SecondaryButton(
              text: 'Cancel',
              onPressed: () {
                // Reset the values in the TextEditingController instances.
                _productNameController.text = labResult?.productName ?? '';

                // Cancel editing.
                setState(() {
                  _isEditing = !_isEditing;
                });
              },
            ),
          ],

          // Download button.
          if (!_isEditing) ...[
            gapW4,
            DownloadButton(
              items: [labResult!.toMap()],
              text: 'Download',
              url: '/api/data/coas/download',
            ),
          ]
        ],
      ),
    );

    var _tabs = TabBarView(
      controller: _tabController,
      children: [
        // Details tab.
        CustomScrollView(
          slivers: [
            // Breadcrumbs.
            _breadcrumbs,

            // Tab bar and actions.
            SliverToBoxAdapter(child: _actions),

            // Fields.
            _isEditing ? _editForm : _viewForm,
          ],
        ),

        // Results tab.
        CustomScrollView(
          slivers: [
            // Breadcrumbs.
            _breadcrumbs,

            // Tab bar and actions.
            SliverToBoxAdapter(child: _actions),

            // Results table.
            SliverToBoxAdapter(
              child: AnalysisResultsTable(
                results: labResult?.results,
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

            // Tab bar and actions.
            SliverToBoxAdapter(child: _actions),

            // PDF options.
            SliverToBoxAdapter(child: _pdfActions()),

            // COA PDF.
            SliverToBoxAdapter(child: _coaPDF()),
          ],
        ),

        // TODO: Notes tab.
      ],
    );

    // Render.
    return MainContent(
      child: SingleChildScrollView(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.start,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Container(
              height: MediaQuery.of(context).size.height,
              child: DefaultTabController(
                length: _tabCount,
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.start,
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Expanded(child: _tabs),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  /// Text form field.
  Widget _buildTextField(controller, labelText, {bool isNumeric = false}) {
    bool isDark = Theme.of(context).brightness == Brightness.dark;
    final screenWidth = MediaQuery.of(context).size.width;
    return Row(
      children: [
        Container(
          width: (screenWidth < Breakpoints.tablet)
              ? MediaQuery.of(context).size.width * 0.25
              : MediaQuery.of(context).size.width * 0.125,
          padding: EdgeInsets.only(left: 16, bottom: 8),
          child: SelectableText(
            labelText,
            style: Theme.of(context).textTheme.bodySmall,
          ),
        ),
        Container(
          width: isNumeric
              ? (screenWidth < Breakpoints.tablet)
                  ? MediaQuery.of(context).size.width * 0.25
                  : MediaQuery.of(context).size.width * 0.15
              : (screenWidth < Breakpoints.tablet)
                  ? MediaQuery.of(context).size.width * 0.7
                  : MediaQuery.of(context).size.width * 0.5,
          padding: EdgeInsets.only(left: 8, right: 8, bottom: 8),
          child: TextFormField(
            style: Theme.of(context).textTheme.bodySmall,
            controller: controller,
            keyboardType: isNumeric ? TextInputType.number : TextInputType.text,
            inputFormatters: isNumeric
                ? <TextInputFormatter>[FilteringTextInputFormatter.digitsOnly]
                : <TextInputFormatter>[],
            decoration: InputDecoration(
              isDense: true,
              contentPadding: EdgeInsets.only(
                top: 12,
                left: 4,
                right: 4,
                bottom: 4,
              ),
              filled: true,
              labelStyle: TextStyle(
                color: Theme.of(context).textTheme.bodyMedium!.color,
                fontSize: 16,
                fontWeight: FontWeight.w500,
              ),
              focusedBorder: OutlineInputBorder(
                borderSide: BorderSide(
                  color:
                      isDark ? DarkColors.accentGreen : LightColors.lightGreen,
                  width: 2.0,
                ),
              ),
              enabledBorder: OutlineInputBorder(
                borderSide: BorderSide(
                  color: Theme.of(context).dividerColor,
                  width: 1.0,
                ),
              ),
            ),
          ),
        ),
      ],
    );
  }

  // Pill tab button.
  Widget _buildTab(
    String text,
    int index,
    IconData icon,
  ) {
    bool isSelected = _selectedIndex == index;
    Color lightScreenGold = Color(0xFFFFBF5F);
    Color darkScreenGold = Color(0xFFFFD700);
    Color goldColor = Theme.of(context).brightness == Brightness.light
        ? lightScreenGold
        : darkScreenGold;
    ValueNotifier<bool> isHovered = ValueNotifier(false);
    return MouseRegion(
      onEnter: (_) => isHovered.value = true,
      onExit: (_) => isHovered.value = false,
      child: ValueListenableBuilder<bool>(
        valueListenable: isHovered,
        builder: (context, value, child) {
          return GestureDetector(
            onTap: () {
              _tabController.animateTo(index);
            },
            child: InkWell(
              borderRadius: BorderRadius.circular(30),
              splashColor: Colors.blue.withOpacity(0.5),
              hoverColor: Colors.blue.withOpacity(0.2),
              child: Container(
                padding: EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                decoration: BoxDecoration(
                  borderRadius: BorderRadius.circular(30),
                  color: isSelected
                      ? Colors.blue.withOpacity(0.1)
                      : (value
                          ? Colors.blue.withOpacity(0.05)
                          : Colors.transparent),
                ),
                child: Row(
                  children: [
                    Icon(icon,
                        size: 16,
                        color: isSelected
                            ? goldColor
                            : Theme.of(context).colorScheme.secondary),
                    SizedBox(width: 8),
                    Text(text),
                  ],
                ),
              ),
            ),
          );
        },
      ),
    );
  }

  /// Loading placeholder.
  Widget _loadingPlaceholder(BuildContext context, WidgetRef ref) {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          gapH48,
          SizedBox(
            height: 28,
            width: 28,
            child: CircularProgressIndicator(strokeWidth: 1.42),
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
        // child: LabResultForm(),
        child: Container(),
      ),
    );
  }
}
